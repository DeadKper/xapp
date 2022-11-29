from typing import Any
from re import sub as sed
from re import IGNORECASE
from xdata import Color, Item


class ItemDict:
    def __init__(self, query: list[str]) -> None:
        self.query = query
        self.conf_number = 0
        self.dict: dict[str, Item] = {}
        self.sorted = False
        self.keys_set = False
        self.skip: list[str] = []
        self.keys: list[str] = []

    def pop_manager(self, manager: str) -> list[str]:
        filter: list[str] = []
        i = 0
        while i < len(self.keys):
            item = self.index(i)
            if item.main() == manager:
                del self.keys[i]
                filter.append(item.identifier(
                    manager=manager))  # type: ignore
                continue
            i += 1
        if self.sorted and len(filter) > 0:
            self.sorted = False
            self.keys_set = False
        return filter

    def set_skip_managers(self, managers: list[str]):
        self.skip = managers

    def extend(self, items: dict[str, Item] | list[Item]):
        if isinstance(items, dict):
            for key, item in items.items():
                self.add(item, key)
        else:
            for item in items:
                self.add(item, item.name().lower())  # type: ignore

    def add(self, item: Item, name: str | None = None):
        if name == None:
            name = item.name().lower()  # type: ignore
        if name in self.dict:
            self.__merge_items__(name, item)
        else:
            self.dict[name] = item
        self.sorted = False
        self.keys_set = False

    def __merge_items__(self, in_dict: str, to_merge: Item):
        item = self.dict[in_dict]
        item.add(to_merge.data)
        item.confidence = (item.confidence + to_merge.confidence) // 2

    def set_keys(self):
        if self.keys_set:
            return
        if len(self.skip) > 0:
            self.keys = [key for key in self.dict.keys()]
        else:
            self.keys = list(self.dict.keys())
        self.keys_set = True

    def sort(self):
        if self.sorted:
            return
        self.set_keys()
        self.keys = sorted(
            self.keys, key=lambda key: self.dict[key].confidence)
        self.sorted = True

    def index(self, index: int):
        return self.dict[self.keys[index]]

    def to_string(self, reverse=True, main_manager=True, managers_order: list[str] | None = None):
        result = ''
        aux: Any

        if not self.sorted:
            self.sort()

        if reverse:
            ordered_list = reversed(self.keys)
            number = len(self.keys)
            addend = -1
        else:
            ordered_list = self.keys
            number = 1
            addend = 1

        for key in ordered_list:
            item = self.dict[key]
            item.set_keys(managers_order)
            name = item.name()
            for query in self.query:
                name = sed(
                    f'({query})', f'{Color.UNDERLINE}\\1{Color.END}{Color.BOLD}', name, flags=IGNORECASE)  # type: ignore

            name = f'{Color.BOLD}{name}{Color.END} '

            aux = item.id()
            id = ''
            # for query in self.query:
            #     id = sed(f'({query})', f'{Color.UNDERLINE}\\1{Color.END}',
            #              f'-> {aux} ', flags=IGNORECASE) if aux != None else ''

            aux = item.desc()
            desc = f'\n{"":<6}{aux}' if aux != None else ''

            if managers_order != None:
                aux = [man for man in managers_order if man in item.data]
            else:
                aux = [man for man in item.data]

            main = f'{Color.GREEN}{Color.BOLD}{aux.pop(0)}{Color.END}/' if main_manager else ''
            managers = ''
            for manager in aux:
                managers += f',{manager}'
            managers = f'({Color.YELLOW}{managers[1:]}{Color.END}) ' if len(
                managers) > 0 else ''

            # confidence = f'[{Color.GREEN}{item.confidence}{Color.END}]'
            confidence = ''

            count = f'{Color.BLUE}{number:>4}{Color.END} '

            result += f'\n{count}{main}{name}{id}{managers}{confidence}{desc}'
            number += addend

        return result[1:]

    def __len__(self):
        if not self.keys_set:
            self.set_keys()
        return len(self.keys)


EMPTY_ITEM_DICT = ItemDict([])
