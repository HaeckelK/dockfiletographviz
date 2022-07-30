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

        copy_pattern = r"COPY\s([\S]+)\s([\S]+)"

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

            copy_matches = re.match(copy_pattern, line)
            if copy_matches:
                copy_task = CopyTask(
                    source_stage="filesystem", source=copy_matches.group(1).split(" "), target=copy_matches.group(2)
                )
                if current_stage:
                    current_stage.add_copy_task(copy_task)
                else:
                    print("Error copy task outside of a build stage")

        return dockerfile
