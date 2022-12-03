from xdata.items import Dict
from xdata.managers import PackageManager


class dnf(PackageManager):
    def __init__(self) -> None:
        super().__init__('dnf')

    def install(self, packages: list[str] | Dict, fail=False):
        return super()._run(['dnf', 'install', '-y'],
                            args=packages,
                            sudo=True,
                            pipe_err=fail)

    def remove(self, packages: list[str] | Dict, fail=False):
        return super()._run(['dnf', 'remove', '-y'],
                            args=packages,
                            sudo=True,
                            pipe_err=fail)

    def update(self, packages: list[str] = [], fail=False):
        return super()._run(['dnf', 'update', '-y'],
                            args=packages,
                            sudo=True,
                            pipe_err=fail)

    def run_gc(self):
        return super()._run(['dnf', 'autoremove', '-y'],
                            sudo=True)

    def list_packages(self, user_installed: bool):
        return super()._run(['dnf', 'repoquery', '--qf', r'%{name}'],
                            args=['--userinstalled'] if user_installed else [])

    def search(self, packages: list[str]):
        super().search(packages)
        return super()._run(['dnf', 'search'],
                            args=packages,
                            pipe_out=True,
                            pipe_err=True,
                            threaded=True)

    def search_response(self, item_dict: Dict | None = None):
        super().search_response()

        if item_dict == None:
            item_dict = Dict(self.query, self.name)

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
