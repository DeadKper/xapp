from managers.manager import PackageManager
from data.data import Item
from re import sub as sed


class nixenv(PackageManager):
    def install(self, packages: list[str] | list[Item], fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-iA']
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
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def remove(self, packages: list[str], fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-e']
        args.extend(packages)
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def update(self, packages: list[str] | None = None, fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-uA']
        if packages != None:
            args.extend(packages)
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        return True

    def run_gc(self):
        self.__execute__(
            ['nix-collect-garbage', '--delete-older-than', '30d'], False)
        self.join()

    def list_packages(self, user_installed: bool):
        args = ['nix-env', '-q']
        self.__execute__(args, False)
        self.join()

    def search(self, package: list[str]):
        self.__searched_package__ = package
        args = args = ['nix-env', '-f', '<nixpkgs>', '-qa']
        args.extend([f'.*{value}.*' for value in package])
        self.__execute__(args, True)

    def search_response(self):
        output: dict[str, Item] = {}
        result, error = self.response(True)
        skip = True
        for line in result.splitlines(False):
            name = sed(r'-[0-9]+\..*$', '', line)
            if name in output:
                continue
            conf = len(output)
            output[name] = Item(self.__searched_package__,
                                name, conf, self.name)
        return output
