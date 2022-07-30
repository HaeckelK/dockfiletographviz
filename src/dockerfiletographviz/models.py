from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class Stage:
    name: str
    parent: str

    @property
    def is_external(self) -> bool:
        return not self.has_parent

    @property
    def has_parent(self) -> bool:
        return self.parent != ""


@dataclass
class Dockerfile:
    stages: list[Stage] = field(default_factory=list)

    def add_stage(self, stage: Stage) -> None:
        self.stages.append(stage)
        return

    @property
    def stage_names(self) -> List[str]:
        return [x.name for x in self.stages]

    @property
    def terminal_stages(self) -> Set[str]:
        parents = [x.parent for x in self.stages if x.has_parent]
        return set(x for x in self.stage_names if x not in parents)
