from xdata import JSON
from xdata.items import Info


class Item(JSON):
    def __init__(self, confidence: int, name: str | None = None, description: str | None = None, managers: dict[str, dict] = {}, _keys: list[str] | None = None) -> None:
        self.confidence = confidence
        self.name = name
        self.description = description
        self.managers: dict[str, Info] = {}
        for key, value in managers.items():
            self.managers[key] = Info(**value)
        self.keys = list(self.managers.keys()) if _keys == None else _keys

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, value: list[str] | None):
        if value == None:
            return
        self._keys = [key for key in value if key in self.managers]
        name = None
        description = None
        for key in self.keys:
            manager = self.managers[key]
            if name == None and manager.name:
                name = manager.name
            if description == None and manager.description:
                description = manager.description
        self.name = name
        self.description = description

    def add(self, manager: str, data: str, description: str | None = None, id: str | None = None):
        self.add_manager(manager, Info(data, description, id))

    def add_manager(self, manager: str, info: Info):
        self.managers[manager] = info
        if not self.name:
            self.name = info.name
        if not self.description and info.description:
            self.description = info.description
        self.keys.append(manager)

    def extend(self, managers: dict[str, Info]):
        for key, value in managers.items():
            self.add_manager(key, value)

    def id(self, manager: str | None = None):
        if len(self.keys) == 0:
            return None
        if manager == None:
            manager = self.keys[0]
        values = self.managers[manager]
        return values.id if values.id else values.name

    def main(self):
        return self.keys[0] if len(self.keys) > 0 else None
