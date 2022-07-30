from dataclasses import asdict

from dockerfiletographviz import __version__
from dockerfiletographviz.parser import DockerfileParser
from dockerfiletographviz.models import Dockerfile, Stage


def test_version():
    assert __version__ == "0.1.0"


def test_dockerfile_parser_all_in_one():
    """Ugly all in one test to check all functionality."""
    content = """FROM ubuntu
FROM python as builder
FROM python as production
FROM builder as development
FROM ubuntu as another
FROM another as testing"""
    parser = DockerfileParser(content)

    dockerinfo = parser.parse()

    assert dockerinfo.stages[0].name == "ubuntu"
    assert dockerinfo.stages[0].is_external is True

    assert dockerinfo.stages[1].name == "python"
    assert dockerinfo.stages[1].is_external is True

    assert dockerinfo.stages[2].name == "builder"
    assert dockerinfo.stages[2].is_external is False

    assert dockerinfo.stages[3].name == "production"
    assert dockerinfo.stages[3].is_external is False

    assert dockerinfo.stages[4].name == "development"
    assert dockerinfo.stages[4].is_external is False

    assert dockerinfo.terminal_stages == set(["production", "development", "testing"])
