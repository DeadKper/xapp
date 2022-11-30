from types import SimpleNamespace


class XNamespace(SimpleNamespace):
    database: bool
    async_search: bool
    interactive: bool
    garbage_collector: bool
    user_installed: bool
    command: list[str]
    managers: list[str]
    packages: list[str]
    dnf: bool
    flatpak: bool
    nix_env: bool
