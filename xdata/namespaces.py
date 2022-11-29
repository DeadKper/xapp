from types import SimpleNamespace


class ItemNamespace(SimpleNamespace):
    name: str
    description: str | None
    id: str | None


class XNamespace(SimpleNamespace):
    database: bool
    async_search: bool
    interactive: bool
    garbage_collector: bool
    user_installed: bool
    command: list[str]
    managers: list[str]
    packages: list[str]
