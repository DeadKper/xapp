from xdata import ItemDict, PackageManager
from re import split


class flatpak(PackageManager):
    def __init__(self) -> None:
        super().__init__('flatpak')

    def install(self, packages: list[str] | ItemDict, fail=False):
        args = ['flatpak', 'install']
        if isinstance(packages, ItemDict):
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

    def remove(self, packages: list[str] | ItemDict, fail=False):
        args = ['flatpak', 'remove']
        if isinstance(packages, ItemDict):
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
        args = ['flatpak', 'update']
        if packages != None:
            args.extend(packages)
        args.append('-y')
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def run_gc(self):
        self.__execute__(['flatpak', 'uninstall', '--unused', '-y'], False)
        self.join()

    def list_packages(self, user_installed: bool, packages: list[str] | None = None):
        args = ['flatpak', 'list']
        self.__execute__(args, False)
        self.join()

    def search(self, package: list[str]):
        self.__searched_package__ = package
        args = ['flatpak', 'search',
                '--columns=name:f,application:f,description:f']
        args.extend(package)
        self.__execute__(args, True)

    def search_response(self, item_dict: ItemDict | None = None):
        if item_dict == None:
            item_dict = ItemDict(self.__searched_package__)

        result, _ = self.response(True)
        for line in result.splitlines(False):
            result = split(r'\t+', line)
            if len(result) != 3:
                continue
            name, id, description = result
            item_dict.add(self.name, name, description, id)
        return item_dict
