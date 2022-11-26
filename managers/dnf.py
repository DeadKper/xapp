from managers.manager import PackageManager
from data.data import Item


class dnf(PackageManager):
    def install(self, packages: list[str] | list[Item], fail=False):
        args = ['sudo', '--', 'dnf', 'install']
        found = False
        if isinstance(packages[0], Item):
            for item in packages:
                if item.managers[0] == self.name:  # type: ignore
                    args.append(item.name)  # type: ignore
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

    def search_response(self):
        output: dict[str, Item] = {}
        result, error = self.response(True)
        for line in result.splitlines(False):
            if line.startswith('=====') \
                    or line.startswith('Last metadata expiration check:') \
                    or line == '':
                continue

            dot = line.find('.')
            name = line[:dot]
            if name in output:
                continue
            double_dot = line.find(':')
            desc = line[double_dot + 2:]
            conf = len(output)
            output[name] = Item(self.__searched_package__,
                                name, conf, self.name, desc)
        return output
