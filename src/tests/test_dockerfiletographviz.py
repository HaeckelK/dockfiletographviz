import pytest

from dockerfiletographviz import __version__
from dockerfiletographviz.parser import DockerfileParser, copy_task_parser
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


def test_copy_task_parser_single():
    # GIVEN a COPY line with single source file
    line = "COPY abc def"
    # WHEN parsing into CopyTask
    copy_task = copy_task_parser(line)
    # THEN
    assert copy_task == CopyTask(source_stage="filesystem", source=["abc"], target="def")


def test_copy_task_parser_multiple():
    # GIVEN a COPY line with multiple source files
    line = "COPY abc def ghi xyz"
    # WHEN parsing into CopyTask
    copy_task = copy_task_parser(line)
    # THEN
    assert copy_task == CopyTask(source_stage="filesystem", source=["abc", "def", "ghi"], target="xyz")


@pytest.mark.xfail
def test_copy_task_parser_chown():
    # GIVEN a COPY line with chown
    line = "COPY --chown=55:mygroup files* /somedir/"
    # WHEN parsing into CopyTask
    copy_task = copy_task_parser(line)
    # THEN chown is not included in source elements
    assert copy_task == CopyTask(source_stage="filesystem", source=["files*"], target="/somedir/")


@pytest.mark.xfail
def test_copy_task_parser_from_multiple():
    # GIVEN a COPY line with multiple source files and from another build stage
    line = "COPY --from=some-stage abc def xyz"
    # WHEN parsing into CopyTask
    copy_task = copy_task_parser(line)
    # THEN source stage is parsed, and from= not included in source elements
    assert copy_task == CopyTask(source_stage="filesystem", source=["abc", "def"], target="xyz")
