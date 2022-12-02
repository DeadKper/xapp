from types import SimpleNamespace
from typing import Any


class ArgsNamespace(SimpleNamespace):
    database: bool
    garbage_collector: bool
    async_search: bool
    interactive: bool
    user_installed: bool
    command: str
    managers: list[str]
    packages: list[str]

    def __init__(self, database=False, garbage_collector=False, async_search=False, interactive=False, user_installed=False, dnf=False, flatpak=False, nix_env=False, command: str | None = None, packages: list[str] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.database = database
        self.garbage_collector = garbage_collector
        self.async_search = async_search
        self.interactive = interactive
        self.user_installed = user_installed
        self.command = command if command != None else ''
        self.packages = packages if packages != None else []
        self.managers = []
        self.async_managers = []
        if dnf:
            self.managers.append('dnf')
        if flatpak:
            self.managers.append('flatpak')
        if nix_env:
            self.managers.append('nix-env')


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
