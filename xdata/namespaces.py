from types import SimpleNamespace
from typing import Any


class XNamespace(SimpleNamespace):
    database: bool
    async_search: bool
    interactive: bool
    garbage_collector: bool
    user_installed: bool
    command: list[str]
    managers: list[str] | None
    packages: list[str]
    dnf: bool
    flatpak: bool
    nix_env: bool


def to_bool(value: str | None):
    if not value:
        return None
    value = value.lower()
    if value == 'false' or value == 'no' or value == '0':
        return False
    elif value == 'true' or value == 'yes' or value == '1':
        return True
    else:
        return None


def to_list(value: str | None):
    if not value:
        return None
    return value.split(',')


def to_int(value: str | None):
    if not value or not value.isdigit():
        return None
    return int(value)


def to_decimal(value: str | None):
    if not value or not value.isdecimal():
        return None
    return float(value)


class General(SimpleNamespace):
    def __init__(self, interactive: str | None = None, garbage_collector: str | None = None, managers: str | None = None, async_managers: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.interactive = to_bool(interactive)
        self.garbage_collector = to_bool(garbage_collector)
        self.managers = to_list(managers)
        self.async_managers = to_list(async_managers)


class Install(SimpleNamespace):
    def __init__(self, interactive: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.interactive = to_bool(interactive)


class Remove(SimpleNamespace):
    def __init__(self, interactive: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.interactive = to_bool(interactive)


class List(SimpleNamespace):
    def __init__(self, user_installed: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user_installed = to_bool(user_installed)


class Search(SimpleNamespace):
    def __init__(self, async_search: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.async_search = to_bool(async_search)


class ConfigNamespace(SimpleNamespace):
    def __init__(self, general: dict, install: dict, remove: dict, list: dict, search: dict) -> None:
        self.general = General(**general)
        self.install = Install(**install)
        self.remove = Remove(**remove)
        self.list = List(**list)
        self.search = Search(**search)
