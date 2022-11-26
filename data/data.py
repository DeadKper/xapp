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
        self.confidence = self.calc_confidence() + conf_decrease
        self.managers = []
        self.desc = ''
        self.archs = []
        self.id = id
        if not manager == None:
            self.add_manager(manager)
        if not desc == None:
            self.desc = desc

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

        if self.id != None:
            result = f'{result} -> {self.id}'

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
