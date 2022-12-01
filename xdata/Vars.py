from os import environ
from pathlib import Path

DEFAULT = 0
ERROR = 1
WARNING = 2

HOME = Path.home()
DATA = environ['XDG_DATA_HOME'] if len(
    environ['XDG_DATA_HOME']) > 0 else f'{HOME}/.local/share'
CACHE = environ['XDG_CACHE_HOME'] if len(
    environ['XDG_CACHE_HOME']) > 0 else f'{HOME}/.cache'
CONFIG = environ['XDG_CONFIG_HOME'] if len(
    environ['XDG_CONFIG_HOME']) > 0 else f'{HOME}/.config'
