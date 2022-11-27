from dataclasses import dataclass, field
from typing import Any
from re import sub as sed
from re import IGNORECASE


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


class Item:
    def __init__(self,
                 query_name: list[str],
                 name: str,
                 conf_decrease: int = 0,
                 manager: str | None = None,
                 desc: str | None = None,
                 id: str | None = None) -> None:
        self.query = query_name
        self.name = name
        self.managers = []
        self.desc = ''
        self.archs = []
        self.id = id
        if not manager == None:
            self.add_manager(manager)
        if not desc == None:
            self.desc = desc
        self.confidence = self.calc_confidence() + conf_decrease

    def add_manager(self, manager: str):
        if manager not in self.managers:
            self.managers.append(manager)

    def to_string(self, number=0, main_manager=False):
        result = ''

        managers = ''
        for manager in self.managers:
            managers = f'{managers},{manager}'
        managers = managers[1:]

        result = f'{result}{Color.BOLD}{self.name}'

        if self.id != None:
            result = f'{result} -> {self.id}'

        for query in self.query:
            result = sed(
                f'({query})', f'{Color.UNDERLINE}\\1{Color.END}{Color.BOLD}', result, flags=IGNORECASE)
        result = f'{result}{Color.END}'

        if main_manager:
            result = f'{Color.BOLD}{Color.CYAN}{self.managers[0]}{Color.END}/{result}'
            found = managers.find(',')
            if found == -1:
                managers = ''
            else:
                managers = managers[found+1:]

        if number > 0:
            result = f'{Color.BLUE}{number:>3} {Color.END}{result}'

        if managers != '':
            result = f'{result} ({Color.YELLOW}{managers}{Color.END})'
        result = f'{result} [{Color.GREEN}{self.confidence}{Color.END}]'

        if self.desc != '':
            result = f'{result}\n{"":<6}{self.desc}'

        return result

    def calc_confidence(self):
        bonus = len(self.query) + 2
        penalty_count = 0
        result = 0
        name = self.name.lower()
        query_negative = name
        for query in self.query:
            query = query.lower()
            query_negative = sed(query, '', query_negative)
            if name.find(query) == -1:
                penalty_count += 1
            else:
                bonus -= 1
        for c in query_negative:
            result += ord(c)
        result -= result // bonus
        if penalty_count > 0:
            result += 3000 // (len(self.query) - penalty_count + 1)

        if self.id != None:
            bonus = len(self.query) + 2
            penalty_count = 0

            id_result = 0
            id = self.id.lower()
            query_negative = id
            for query in self.query:
                query = query.lower()
                query_negative = sed(query, '', query_negative)
                if id.find(query) == -1:
                    penalty_count += 1
                else:
                    bonus -= 1
            for c in query_negative:
                id_result += ord(c)
            id_result -= id_result // bonus
            if penalty_count > 0:
                id_result += 3000 // (len(self.query) - penalty_count + 1)
            if id_result < result:
                result = id_result

        return result


def merge(items: list[Item]):
    item = Item(
        query_name=items[0].query,
        name=items[0].name)

    conf = 0

    for to_merge in items:
        for manager in to_merge.managers:
            item.add_manager(manager)

        if item.desc == '' and to_merge.desc != '':
            item.desc = to_merge.desc

        if item.id == None and to_merge.id != None:
            item.id = to_merge.id

        conf += to_merge.confidence

    item.confidence = conf // len(items) if conf > 0 else 0

    return item


@dataclass
class ManagerInfo:
    name: str
    description: str | None
    id: str | None

    def identifier(self):
        return self.id if self.id != None else self.name


class Itemv2:
    def __init__(self, query: list[str], name: str, manager: str, desc: str | None = None, id: str | None = None, conf_addend=0) -> None:
        self.data: dict[str, ManagerInfo] = {}
        self.data[manager] = ManagerInfo(name, desc, id)
        self.confidence = self.calc_confidence(
            query, name.lower(), id.lower() if id != None else None)
        self.confidence += conf_addend

    def main(self, skip_mans: list[str] = []):
        for man in self.data.keys():
            if man in skip_mans:
                continue
            return man
        return None

    def identifier(self, skip_mans: list[str] = [], manager: str | None = None):
        if manager == None:
            manager = self.main(skip_mans)
        return self.data[manager].identifier() if manager != None else None

    def name(self, skip_mans: list[str] = []):
        for man, data in self.data.items():
            if man in skip_mans:
                continue
            return data.name
        return None

    def desc(self, skip_mans: list[str] = []):
        for man, data in self.data.items():
            if man in skip_mans:
                continue
            if data.description != None:
                return data.description
        return None

    def id(self, skip_mans: list[str] = []):
        for man, data in self.data.items():
            if man in skip_mans:
                continue
            if data.id != None:
                return data.id
        return None

    def add(self, info: dict[str, ManagerInfo]):
        for id, data in info.items():
            self.data[id] = data

    def calc_confidence(self, query_list: list[str], name: str, id: str | None = None):
        bonus = len(query_list) + 2
        penalty_count = 0
        result = 0
        query_negative = name
        for query in query_list:
            query = query.lower()
            query_negative = sed(query, '', query_negative)
            if name.find(query) == -1:
                penalty_count += 1
            else:
                bonus -= 1
        for c in query_negative:
            result += ord(c)
        result -= result // bonus
        if penalty_count > 0:
            result += 3000 // (len(query_list) - penalty_count + 1)

        if id != None:
            bonus = len(query_list) + 2
            penalty_count = 0
            id_result = 0
            query_negative = id
            for query in query_list:
                query = query
                query_negative = sed(query, '', query_negative)
                if id.find(query) == -1:
                    penalty_count += 1
                else:
                    bonus -= 1
            for c in query_negative:
                id_result += ord(c)
            id_result -= id_result // bonus
            if penalty_count > 0:
                id_result += 3000 // (len(query_list) - penalty_count + 1)
            if id_result < result:
                result = id_result

        return result


class ItemDict:
    def __init__(self, query: list[str]) -> None:
        self.query = query
        self.conf_number = 0
        self.dict: dict[str, Itemv2] = {}
        self.list: list[Itemv2] = []
        self.sorted = False

    def expand(self, items: dict[str, Itemv2]):
        for key, item in items.items():
            self.add(item, key)

    def add(self, item: Itemv2, name: str | None = None):
        if name == None:
            name = item.name().lower()  # type: ignore
        if name in self.dict:
            self.__merge_items__(name, item)
        else:
            self.dict[name] = item
        self.sorted = False

    def __merge_items__(self, in_dict: str, to_merge: Itemv2):
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
