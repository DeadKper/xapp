from dataclasses import dataclass


@dataclass
class Info:
    name: str
    description: str | None
    id: str | None
