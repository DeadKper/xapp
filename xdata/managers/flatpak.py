from xdata.items import Dict
from xdata.managers import PackageManager
from re import split


class flatpak(PackageManager):
    def __init__(self) -> None:
        super().__init__('flatpak')

    def install(self, packages: list[str] | Dict, fail=False):
        return super()._run(['flatpak', 'install', '-y'],
                            args=packages,
                            pipe_err=fail)

    def remove(self, packages: list[str] | Dict, fail=False):
        return super()._run(['flatpak', 'remove', '-y'],
                            args=packages,
                            pipe_err=fail)

    def update(self, packages: list[str] = [], fail=False):
        return super()._run(['flatpak', 'update', '-y'],
                            args=packages,
                            pipe_err=fail)

    def run_gc(self):
        return super()._run(['flatpak', 'uninstall', '--unused', '-y'])

    def list_packages(self, user_installed: bool):
        return super()._run(['flatpak', 'list'])

    def search(self, packages: list[str]):
        super().search(packages)
        return super()._run(['flatpak', 'search',
                             '--columns=name:f,application:f,description:f'],
                            args=packages,
                            pipe_out=True,
                            pipe_err=True,
                            threaded=True)

    def search_response(self, item_dict: Dict | None = None):
        if item_dict == None:
            item_dict = Dict(self.query, self.name)

        result, _ = self.response(True)
        for line in result.splitlines(False):
            result = split(r'\t+', line)
            if len(result) != 3:
                continue
            name, id, description = result
            item_dict.add(self.name, name, description, id)
        return item_dict
