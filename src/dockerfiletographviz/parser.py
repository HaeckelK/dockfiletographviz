import re
from typing import Optional

from dockerfiletographviz.models import Dockerfile, Stage, CopyTask


class DockerfileParser:
    def __init__(self, content: str) -> None:
        """


        content: str
            Single string containing Dockerfile contents.
        """
        self._content = content
        return

    def parse(self) -> Dockerfile:
        dockerfile = Dockerfile()

        from_pattern = r"FROM\s([\S]+)"
        from_as_pattern = r"FROM\s([\S]+) as ([\S]+)"

        stage_name = ""
        current_stage: Optional[Stage] = None

        for line in self._content.splitlines():
            matches = re.match(from_pattern, line)
            as_matches = re.match(from_as_pattern, line)
            if matches:
                stage_name = matches.group(1)
                if stage_name not in dockerfile.stage_names:
                    current_stage = Stage(name=stage_name, parent="")
                    dockerfile.add_stage(current_stage)

            if as_matches:
                stage_name = as_matches.group(2)
                current_stage = Stage(name=stage_name, parent=as_matches.group(1))
                dockerfile.add_stage(current_stage)

            if line.startswith("COPY "):
                copy_task = copy_task_parser(line)

                if current_stage:
                    current_stage.add_copy_task(copy_task)
                else:
                    print("Error copy task outside of a build stage")

        return dockerfile


def copy_task_parser(line: str) -> CopyTask:
    """Examples needed
    YES
    COPY <src>... <dest>
    COPY ["<src>",... "<dest>"]

    NO
    COPY [--chown=<user>:<group>] <src>... <dest>
    COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
    COPY [--from=<name>] <src>... <dest>
    COPY [--from=<name>] ["<src>",... "<dest>"]

    Aim is to match cases defined by Docker: https://docs.docker.com/engine/reference/builder/#copy
    """
    copy_matches = [x for x in re.findall(r"[\S]+", line)]
    # Last position is destination
    target = copy_matches[-1]

    # First position is COPY
    source = copy_matches[1:-1]

    return CopyTask(source_stage="filesystem", source=source, target=target)
