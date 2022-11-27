from dataclasses import dataclass


@dataclass
class ManagerInfo:
    name: str
    description: str | None
    id: str | None

    def identifier(self):
        return self.id if self.id != None else self.name
