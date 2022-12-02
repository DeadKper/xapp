from xdata.items import Dict
from xdata.managers import PackageManager
from re import sub as sed


class nixenv(PackageManager):
    def __init__(self) -> None:
        super().__init__('nix-env', True)

    def install(self, packages: list[str] | Dict, fail=False):
        if not super()._run(['nix-env', '-f', '<nixpkgs>', '-iA', '-Q'],
                            args=packages,
                            pipe_err=fail):
            return False
        self.update_dekstop_db()
        return True

    def remove(self, packages: list[str] | Dict, fail=False):
        if not super()._run(['nix-env', '-f', '<nixpkgs>', '-e', '-Q'],
                            args=packages,
                            pipe_err=fail):
            return False
        self.update_dekstop_db()
        return True

    def update(self, packages: list[str] = [], fail=False):
        return super()._run(['nix-env', '-f', '<nixpkgs>', '-uA', '-Q'],
                            args=packages,
                            pipe_err=fail)

    def run_gc(self):
        return super()._run(['nix-collect-garbage', '--delete-older-than', '30d'])

    def list_packages(self, user_installed: bool):
        return super()._run(['nix-env', '-q'])

    def search(self, packages: list[str]):
        super().search(packages)
        return super()._run(['nix-env', '-f', '<nixpkgs>', '-qa', '--description'],
                            args=[f'.*{value}.*' for value in packages],
                            pipe_out=True,
                            pipe_err=True,
                            threaded=True)

    def search_response(self, item_dict: Dict | None = None):
        if item_dict == None:
            item_dict = Dict(self.query, self.name)

        result, _ = self.response(True)
        for line in result.splitlines(False):
            name, desc = sed(r'([^ ]+) {2,}(.*)',
                             r'\1\n\2.', line).splitlines()
            name = sed(r'-[0-9a-zA-Z]+\.[^ ]+$', '', name)
            if name in item_dict.items:
                continue
            item_dict.add(self.name, name,
                          desc[:-1] if len(desc) > 1 else None)
        return item_dict

    def update_dekstop_db(self):
        self._run(['rsync', '-prLK', '--chmod=u+rwx', '--include', 'share', '--include',
                   'share/applications/***', '--exclude', '*', f'{self.home}/.nix-profile/',
                   f'{self.home}/.local/share/nix-env/', '--delete-before'])
        self._run(['update-desktop-database',
                   f'{self.home}/.local/share/nix-env/share/applications'])
