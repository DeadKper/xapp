from managers.manager import PackageManager
from data.data import Item
from re import split


class flatpak(PackageManager):
    def install(self, packages: list[str] | list[Item], fail=False):
        args = ['flatpak', 'install']
        found = False
        if isinstance(packages[0], Item):
            for item in packages:
                if item.managers[0] == self.name:  # type: ignore
                    args.append(item.id)  # type: ignore
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
        args = ['flatpak', 'remove']
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
        self.__execute__(['flatpak', 'uninstall', '--unused'], False)
        self.join()

    def list_packages(self, user_installed: bool):
        args = ['flatpak', 'list']
        self.__execute__(args, False)
        self.join()

    def search(self, package: list[str]):
        self.__searched_package__ = package
        args = ['flatpak', 'search',
                '--columns=name:f,application:f,description:f']
        args.extend(package)
        self.__execute__(args, True)

    def search_response(self):
        output: dict[str, Item] = {}
        result, error = self.response(True)
        for line in result.splitlines(False):
            result = split(r'\t+', line)
            if len(result) != 3:
                return output
            name, id, desc = split(r'\t+', line)
            conf = len(output)
            output[name] = Item(self.__searched_package__,
                                name, conf, self.name, desc, id)
        return output
