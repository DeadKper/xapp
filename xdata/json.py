from types import SimpleNamespace
from typing import Any
from json import dumps, loads


class JSON():
    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__,
                     sort_keys=True, indent=4)


def fromJSON(data: str, type: Any = SimpleNamespace) -> Any:
    return type(**loads(data))
