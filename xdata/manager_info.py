from dataclasses import dataclass


@dataclass
class ManagerInfo:
    name: str
    description: str | None
    id: str | None
