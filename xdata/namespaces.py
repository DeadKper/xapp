from types import SimpleNamespace
from typing import Any


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
    def __init__(self, update_desktop_db: str | None = None, garbage_collector: str | None = None, managers: str | None = None, async_managers: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.update_desktop_db = to_bool(update_desktop_db)
        self.garbage_collector = to_bool(garbage_collector)
        self.managers = to_list(managers)
        self.async_managers = to_list(async_managers)


class Install(General):
    def __init__(self, interactive: str | None = None, async_search: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.interactive = to_bool(interactive)
        self.async_search = to_bool(async_search)


class Remove(General):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class List(General):
    def __init__(self, user_installed: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user_installed = to_bool(user_installed)


class Search(General):
    def __init__(self, async_search: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.async_search = to_bool(async_search)


class Update(General):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class ConfigNamespace(SimpleNamespace):
    def __init__(self, general: dict, install: dict, remove: dict, list: dict, search: dict, update: dict) -> None:
        self.general = General(**general)
        self.install = Install(**install)
        self.remove = Remove(**remove)
        self.list = List(**list)
        self.search = Search(**search)
        self.update = Update(**update)


class ArgsNamespace(SimpleNamespace):
    update_desktop_db: bool
    garbage_collector: bool
    command: str | None
    managers: list[str]
    async_managers: list[str]
    packages: list[str]
    async_search: bool
    interactive: bool
    user_installed: bool

    def __init__(self, managers: list[str] | None = None, packages=[], **kwargs: Any) -> None:
        self.async_search = False
        self.interactive = False
        self.user_installed = False
        self.packages = packages
        self.async_managers = []
        if managers is None:
            managers = []
        else:
            managers = managers[0].split(',')

        super().__init__(managers=managers, **kwargs)

    def set_configs(self, config: ConfigNamespace):
        def get_value(config_val: Any, self_val: Any):

            if config_val != None and \
                    (not self_val or hasattr(self_val, '__len__') and len(self_val) == 0):
                return config_val
            return self_val

        def set_general(confs: General):
            if len(self.managers) == 0:
                self.async_managers = get_value(
                    confs.async_managers, self.async_managers)
                self.managers = get_value(confs.managers, self.managers)
            self.garbage_collector = get_value(
                confs.garbage_collector, self.garbage_collector)
            self.update_desktop_db = get_value(
                confs.update_desktop_db, self.update_desktop_db)

        set_general(config.general)

        match self.command:
            case 'list':
                set_general(config.list)
                self.user_installed = get_value(
                    config.list.user_installed, self.user_installed)
            case 'install':
                set_general(config.install)
                self.interactive = get_value(
                    config.install.interactive, self.interactive)
                self.async_search = get_value(
                    config.install.async_search, self.async_search)
            case 'search':
                set_general(config.search)
                self.async_search = get_value(
                    config.search.async_search, self.async_search)
            case 'remove':
                set_general(config.remove)
            case 'update':
                set_general(config.update)
