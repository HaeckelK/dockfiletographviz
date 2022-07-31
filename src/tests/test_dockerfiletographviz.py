from dockerfiletographviz import __version__
from dockerfiletographviz.parser import DockerfileParser
from dockerfiletographviz.models import CopyTask


def test_version():
    assert __version__ == "0.1.0"


def test_dockerfile_parser_all_in_one():
    """Ugly all in one test to check all functionality."""
    content = """FROM ubuntu
FROM python as builder
FROM python as production
COPY source-abc target-abc
RUN ./some-command.sh
COPY source-def target-def
FROM builder as development
COPY source-123 source-456 /target-dir
FROM ubuntu as another
FROM another as testing"""
    parser = DockerfileParser(content)

    dockerinfo = parser.parse()

    assert dockerinfo.stages[0].name == "ubuntu"
    assert dockerinfo.stages[0].is_external is True
    assert dockerinfo.stages[0].copies == []

    assert dockerinfo.stages[1].name == "python"
    assert dockerinfo.stages[1].is_external is True
    assert dockerinfo.stages[1].copies == []

    assert dockerinfo.stages[2].name == "builder"
    assert dockerinfo.stages[2].is_external is False
    assert dockerinfo.stages[2].copies == []

    assert dockerinfo.stages[3].name == "production"
    assert dockerinfo.stages[3].is_external is False
    assert dockerinfo.stages[3].copies == [
        CopyTask(source_stage="filesystem", source=["source-abc"], target="target-abc"),
        CopyTask(source_stage="filesystem", source=["source-def"], target="target-def"),
    ]

    assert dockerinfo.stages[4].name == "development"
    assert dockerinfo.stages[4].is_external is False
    assert dockerinfo.stages[4].copies == [
        CopyTask(source_stage="filesystem", source=["source-123", "source-456"], target="/target-dir"),
    ]

    assert dockerinfo.terminal_stages == set(["production", "development", "testing"])
