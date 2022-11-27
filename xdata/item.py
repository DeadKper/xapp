from re import sub as sed
from xdata import ManagerInfo


class Item:
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
