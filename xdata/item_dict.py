from typing import Any
from re import sub as sed
from re import IGNORECASE
from xdata.Static import item_confidence, Color
from xdata import Item, JSON
from time import time


class ItemDict(JSON):
    def __init__(self, query: list[str], items: dict[str, dict] = {}, sorted=False, keys_set=False, keys: list[str] = [], expiration: int | None = None) -> None:
        self.query = query
        self.items: dict[str, Item] = {}
        self.managers: list[str] = []
        self.sorted = sorted
        self.keys_set = keys_set
        self.keys = keys
        self.expiration = time() + 21600 if not expiration else expiration
        for key, value in items.items():
            self.items[key] = Item(**value)

    def pop_manager(self, manager: str) -> list[str]:
        filter: list[str] = []
        i = 0
        while i < len(self.keys):
            item = self.index(i)
            if item.main() == manager:
                del self.keys[i]
                filter.append(item.id(manager=manager))  # type: ignore
                continue
            i += 1
        if self.sorted and len(filter) > 0:
            self.sorted = False
            self.keys_set = False
        return filter

    def extend(self, items: dict[str, Item] | list[Item]):
        if isinstance(items, dict):
            for key, item in items.items():
                self.add_item(key, item)
        else:
            for item in items:
                self.add_item(item.name.lower(), item)  # type: ignore

    def add(self, manager: str, name: str, description: str | None = None, id: str | None = None):
        item = Item(item_confidence(self.query, name, id))
        item.add(manager, name, description, id)
        self.add_item(item.name.lower(), item)  # type: ignore

    def add_item(self, key: str, item: Item):
        if len(self.managers) < 3:
            for manager in item.keys:
                if manager not in self.managers:
                    self.managers.append(manager)
        if key in self.items:
            self.__merge_items__(key, item)
        else:
            self.items[key] = item
        self.sorted = False
        self.keys_set = False

    def __merge_items__(self, in_dict: str, to_merge: Item):
        item = self.items[in_dict]
        item.extend(to_merge.managers)
        item.confidence = (item.confidence + to_merge.confidence) // 2

    def __set_keys__(self):
        if self.keys_set:
            return
        self.keys = list(self.items.keys())
        self.keys_set = True

    def sort(self):
        if self.sorted:
            return
        self.__set_keys__()
        self.keys = sorted(
            self.keys, key=lambda key: self.items[key].confidence)
        self.sorted = True

    def index(self, index: int):
        return self.items[self.keys[index]]

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
            item = self.items[key]
            item.keys = managers_order
            name = item.name
            for query in self.query:
                name = sed(
                    f'({query})', f'{Color.UNDERLINE}\\1{Color.END}{Color.BOLD}', name, flags=IGNORECASE)  # type: ignore

            name = f'{Color.BOLD}{name}{Color.END} '

            aux = item.id()
            id = ''
            # for query in self.query:
            #     id = sed(f'({query})', f'{Color.UNDERLINE}\\1{Color.END}',
            #              f'-> {aux} ', flags=IGNORECASE) if aux != None else ''

            aux = item.description
            desc = f'\n{"":<6}{aux}' if aux != None else ''

            if managers_order != None:
                aux = [man for man in managers_order if man in item.managers]
            else:
                aux = [man for man in item.managers]

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
            self.__set_keys__()
        return len(self.keys)


EMPTY_ITEM_DICT = ItemDict([])
