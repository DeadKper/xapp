from xdata import FrozenDict
from xdata.managers.package_manager import PackageManager
from xdata.managers.dnf import dnf
from xdata.managers.flatpak import flatpak
from xdata.managers.nixenv import nixenv

COUNT = 3

MANAGERS: dict[str, PackageManager] = FrozenDict({
    'dnf': dnf(),
    'flatpak': flatpak(),
    'nix-env': nixenv(),
})

__all__ = ['COUNT', 'MANAGERS', 'PackageManager', 'dnf', 'flatpak', 'nixenv']
