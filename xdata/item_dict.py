from typing import Any
from re import sub as sed
from re import IGNORECASE
from xdata import Color, Item


class ItemDict:
    def __init__(self, query: list[str]) -> None:
        self.query = query
        self.conf_number = 0
        self.dict: dict[str, Item] = {}
        self.list: list[Item] = []
        self.sorted = False

    def expand(self, items: dict[str, Item]):
        for key, item in items.items():
            self.add(item, key)

    def add(self, item: Item, name: str | None = None):
        if name == None:
            name = item.name().lower()  # type: ignore
        if name in self.dict:
            self.__merge_items__(name, item)
        else:
            self.dict[name] = item
        self.sorted = False

    def __merge_items__(self, in_dict: str, to_merge: Item):
        item = self.dict[in_dict]
        item.add(to_merge.data)
        item.confidence = (item.confidence + to_merge.confidence) // 2

    def sort_list(self, skip_managers: list[str] = []):
        if self.sorted:
            return
        self.list = [
            value for value in self.dict.values() if value.name(skip_managers)]
        self.list.sort(key=lambda value: value.confidence)
        self.sorted = True

    def to_string(self, reverse=True, main_manager=True, skip_managers: list[str] = []):
        result = ''
        aux: Any

        if not self.sorted:
            self.sort_list(skip_managers)

        if reverse:
            ordered_list = reversed(self.list)
            number = len(self.list)
            addend = -1
        else:
            ordered_list = self.list
            number = 1
            addend = 1

        for item in ordered_list:
            name = item.name(skip_managers)
            for query in self.query:
                name = sed(
                    f'({query})', f'{Color.UNDERLINE}\\1{Color.END}{Color.BOLD}', name, flags=IGNORECASE)  # type: ignore

            name = f'{Color.BOLD}{name}{Color.END} '

            aux = item.id(skip_managers)
            id = sed(f'({self.query})', f'{Color.UNDERLINE}\\1{Color.END}',
                     f' -> {aux} ', flags=IGNORECASE) if aux != None else ''

            aux = item.desc(skip_managers)
            desc = f'\n{"":<6}{aux}' if aux != None else ''

            aux = []
            for manager in item.data:
                aux.append(manager)

            main = f'{Color.RED}{Color.BOLD}{aux.pop(0)}{Color.END}/' if main_manager else ''
            managers = ''
            for manager in aux:
                managers += f',{manager}'
            managers = f'({Color.YELLOW}{managers[1:]}{Color.END}) ' if len(
                managers) > 0 else ''

            confidence = f'[{Color.GREEN}{item.confidence}{Color.END}]'

            count = f'{Color.BLUE}{number:>4}{Color.END} '

            result += f'\n{count}{main}{name}{id}{managers}{confidence}{desc}'
            number += addend

        return result[1:]
