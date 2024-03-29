from os import environ
from pathlib import Path
from shutil import which

DEFAULT = 0
ERROR = 1
WARNING = 2

MANAGER_LIST = tuple(
    [man for man in
        ('dnf', 'flatpak', 'nix-env')
        if which(man) is not None])

VERSION = '1.3-beta'

HOME = Path.home()
DATA = environ.get('XDG_DATA_HOME', f'{HOME}/.local/share')
CACHE = environ.get('XDG_CACHE_HOME', f'{HOME}/.cache')
CONFIG = environ.get('XDG_CONFIG_HOME', f'{HOME}/.config')

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
