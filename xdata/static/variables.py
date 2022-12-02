from os import environ
from pathlib import Path

DEFAULT = 0
ERROR = 1
WARNING = 2

MANAGER_LIST = ['dnf', 'flatpak', 'nix-env']

VERSION = '1.2-beta'

HOME = Path.home()
DATA = environ['XDG_DATA_HOME'] if len(
    environ['XDG_DATA_HOME']) > 0 else f'{HOME}/.local/share'
CACHE = environ['XDG_CACHE_HOME'] if len(
    environ['XDG_CACHE_HOME']) > 0 else f'{HOME}/.cache'
CONFIG = environ['XDG_CONFIG_HOME'] if len(
    environ['XDG_CONFIG_HOME']) > 0 else f'{HOME}/.config'


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
