from xdata.items import Dict
from xdata.managers import PackageManager


class dnf(PackageManager):
    def __init__(self) -> None:
        super().__init__('dnf')

    def install(self, packages: list[str] | Dict, fail=False):
        args = ['sudo', '--', 'dnf', 'install']
        if isinstance(packages, Dict):
            packages = packages.pop_manager(self.name)
            if len(packages) == 0:
                return False
        args.extend(packages)
        args.append('-y')
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def remove(self, packages: list[str] | Dict, fail=False):
        args = ['sudo', '--', 'dnf', 'remove']
        if isinstance(packages, Dict):
            packages = packages.pop_manager(self.name)
            if len(packages) == 0:
                return False
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

    def list_packages(self, user_installed: bool, packages: list[str] | None = None):
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

    def search_response(self, item_dict: Dict | None = None):
        if item_dict == None:
            item_dict = Dict(self.__searched_package__, self.name)

        result, _ = self.response(True)
        for line in result.splitlines(False):
            if line.startswith('=====') \
                    or line.startswith('Last metadata expiration check:') \
                    or line == '':
                continue

            double_dot = line.find(':')
            dot = line[:double_dot].rfind('.')
            name = line[:dot]
            if name in item_dict.items:
                continue
            description = line[double_dot + 2:]
            item_dict.add(self.name, name, description)
        return item_dict
