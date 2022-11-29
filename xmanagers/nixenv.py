from xdata import Item, ItemDict, PackageManager
from re import sub as sed


class nixenv(PackageManager):
    def __init__(self) -> None:
        super().__init__('nix-env', True)

    def install(self, packages: list[str] | ItemDict, fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-iA', '-Q']
        if isinstance(packages, ItemDict):
            packages = packages.pop_manager(self.name)
            if len(packages) == 0:
                return False
        args.extend(packages)
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        self.update_dekstop_db()
        return True

    def remove(self, packages: list[str] | ItemDict, fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-e']
        if isinstance(packages, ItemDict):
            packages = packages.pop_manager(self.name)
            if len(packages) == 0:
                return False
        args.extend(packages)
        self.__execute__(args, False, fail)
        self.join()
        if len(self.__result__[1]) > 0:
            return False
        self.update_dekstop_db()
        return True

    def update(self, packages: list[str] | None = None, fail=False):
        args = ['nix-env', '-f', '<nixpkgs>', '-uA', '-Q']
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

    def list_packages(self, user_installed: bool, packages: list[str] | None = None):
        args = ['nix-env', '-q']
        self.__execute__(args, False)
        self.join()

    def search(self, package: list[str]):
        self.__searched_package__ = package
        args = args = ['nix-env', '-f', '<nixpkgs>', '-qa', '--description']
        args.extend([f'.*{value}.*' for value in package])
        self.__execute__(args, True)

    def search_response(self, item_dict: ItemDict | None = None):
        if item_dict == None:
            item_dict = ItemDict(self.__searched_package__)

        result, _ = self.response(True)
        for line in result.splitlines(False):
            name, desc = sed(r'([^ ]+) {2,}(.*)',
                             r'\1\n\2.', line).splitlines()
            name = sed(r'-[0-9a-zA-Z]+\.[^ ]+$', '', name)
            if name in item_dict.dict:
                continue
            conf = len(item_dict.dict)
            item_dict.add(Item(self.__searched_package__, name,
                          self.name, desc, conf_addend=conf))
        return item_dict

    def update_dekstop_db(self):
        self.__execute__(['rsync', '-prLK', '--chmod=u+rwx', '--include', 'share', '--include',
                          'share/applications/***', '--exclude', '*', f'{self.home}/.nix-profile/',
                          f'{self.home}/.local/share/nix-env/', '--delete-before'], False, False, just_run=True)
        self.__execute__(['update-desktop-database',
                         f'{self.home}/.local/share/nix-env/share/applications'], False, False, True)
