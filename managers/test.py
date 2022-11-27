from data.manager import PackageManager
from data.data import Item, Itemv2, ItemDict


class test(PackageManager):
    def install(self, packages: list[str] | list[Itemv2], fail=False):
        args = ['sudo', '--', 'dnf', 'install']
        found = False
        if isinstance(packages[0], Itemv2):
            item: Itemv2
            for item in packages:  # type: ignore
                if item.main() == self.name:
                    args.append(item.identifier(
                        manager=self.name))  # type: ignore
                    found = True
        else:
            if len(packages) > 0:
                found = True
            args.extend(packages)  # type: ignore
        if not found:
            return
        args.append('-y')
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def remove(self, packages: list[str], fail=False):
        args = ['sudo', '--', 'dnf', 'remove']
        args.extend(packages)
        args.append('-y')
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def update(self, packages: list[str] | None = None, fail=False):
        args = ['sudo', '--', 'dnf', 'update']
        if packages != None:
            args.extend(packages)
        args.append('-y')
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def run_gc(self):
        self.__execute__(['sudo', 'dnf', 'autoremove', '-y'], False)
        self.join()

    def list_packages(self, user_installed: bool):
        args = ['dnf', 'repoquery', '--qf', r'%{name}']
        if user_installed:
            args.append('--userinstalled')
        self.__execute__(args, False)
        self.join()

    def search(self, package: list[str]):
        self.__searched_package__ = package
        args = ['dnf', 'search']
        args.extend(package)
        self.__execute__(args, True)

    def search_response(self, item_dict: ItemDict | None = None):
        if item_dict == None:
            item_dict = ItemDict(self.__searched_package__)

        result, error = self.response(True)
        for line in result.splitlines(False):
            if line.startswith('=====') \
                    or line.startswith('Last metadata expiration check:') \
                    or line == '':
                continue

            double_dot = line.find(':')
            dot = line[:double_dot].rfind('.')
            name = line[:dot]
            if name in item_dict.dict:
                continue
            desc = line[double_dot + 2:]
            conf = len(item_dict.dict)
            item_dict.add(Itemv2(self.__searched_package__, name,
                          self.name, desc, conf_addend=conf))
        return item_dict
