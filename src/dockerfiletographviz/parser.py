import re

from dockerfiletographviz.models import Dockerfile, Stage


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

        for line in self._content.splitlines():
            matches = re.match(from_pattern, line)
            as_matches = re.match(from_as_pattern, line)
            if matches:
                stage_name = matches.group(1)
                if stage_name not in dockerfile.stage_names:
                    dockerfile.add_stage(Stage(name=stage_name, parent=""))

            if as_matches:
                dockerfile.add_stage(
                    Stage(name=as_matches.group(2), parent=as_matches.group(1))
                )

        return dockerfile
