from xdata import XNamespace
from xdata.items import Dict
from xdata.managers import MANAGERS
from xdata.static import CONFIG, DEFAULT, ERROR, WARNING, Color, sudoloop, get_config, error
from typing import Sequence, Callable
from argparse import ArgumentParser as Parser
from time import sleep
from sys import argv, stderr

VERSION = '1.1-beta'

SUB_COMMANDS = (
    'install',
    'remove',
    'update',
    'list',
    'search',
    'dummy'
)


class XApp:
    def __init__(self, args: Sequence[str]) -> None:
        parser = Parser(prog='xapp', allow_abbrev=True,
                        description='a simple package manager wrapper',
                        usage='xapp [options] command [packages ...], \'xapp -h\' for full help',
                        epilog='if no manager is enable, all will be used; nix-env won\'t be used in search unless specified or flags -i and -a are present')
        # parser.add_argument('-c', '--cache', action='store_true',
        #                     help='clean and build package cache')
        parser.add_argument('-d', '--database', action='store_true',
                            help='update desktop dabase for all managers')
        parser.add_argument('-v', '--version', action='version',
                            version=f'%(prog)s v{VERSION}')
        parser.add_argument('-a', '--async-search', action='store_true',
                            help='use async search, use ctrl+c to stop the search')
        parser.add_argument('-i', '--interactive', action='store_true',
                            help='use interactive install')
        parser.add_argument('-g', '--garbage-collector', action='store_true',
                            help='run garbage collector at the end of the transaction')
        parser.add_argument('-u', '--user-installed', action='store_true',
                            help='only list user installed packages')
        for manager in MANAGERS:
            parser.add_argument(f'--{manager}', action='store_true',
                                help=f'enable {manager}')
        parser.add_argument('command', nargs=1, choices=SUB_COMMANDS,
                            help='command to execute')
        parser.add_argument('packages', nargs='*',
                            help='packages to install, remove, etc...')
        self.args = parser.parse_args(args=args, namespace=XNamespace)

        self.managers: list[str] | None = None
        self.async_managers: list[str] | None = None
        managers: list[str] = []
        for manager in MANAGERS:
            if self.args.__dict__[manager.replace('-', '_')]:
                managers.append(manager)

        if len(managers) > 0:
            self.managers = managers if len(managers) > 0 else None
            self.async_managers = []

        self.set_configs()

        self.actioned = False
        self.joined: list[str] = []

    def set_configs(self):
        configs = get_config(f'{CONFIG}/xapp')

        match self.args.command:
            case ['install']:
                if configs.install.interactive != None and not self.args.interactive:
                    self.args.interactive = configs.install.interactive
            case ['remove']:
                if configs.remove.interactive != None and not self.args.interactive:
                    self.args.interactive = configs.remove.interactive
            case ['list']:
                if configs.list.user_installed != None and not self.args.user_installed:
                    self.args.user_installed = configs.list.user_installed

        if configs.search.async_search != None and not self.args.async_search:
            self.args.async_search = configs.search.async_search

        if configs.general.async_managers and self.async_managers == None:
            self.async_managers = configs.general.async_managers
        if configs.general.managers and self.managers == None:
            self.managers = configs.general.managers
        if configs.general.interactive != None and not self.args.interactive:
            self.args.interactive = configs.general.interactive
        if configs.general.garbage_collector != None and not self.args.garbage_collector:
            self.args.garbage_collector = configs.general.garbage_collector

    def get_managers(self, include_slow: bool = True):
        managers = self.managers

        if managers == None:
            managers = self.managers

            if not managers:
                managers = ['dnf', 'flatpak']

            self.managers = managers

        async_managers = self.async_managers
        if async_managers == None:
            if not async_managers:
                async_managers = ['nix-env']
            self.async_managers = async_managers

        return [man for man in (
            managers + async_managers if include_slow else managers) if man in MANAGERS]

    def check_args(self, args):
        if len(args) > 0:
            return
        error('No arguments given!', type=ERROR)

    def install(self, packages: list[str] | Dict):
        self.check_args(packages)

        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} installing...', file=stderr)
            MANAGERS[manager].install(packages)

    def remove(self, packages: list[str] | Dict):
        self.check_args(packages)

        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} removing...', file=stderr)
            MANAGERS[manager].remove(packages)

    def run_gc(self):
        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} running garbage collector...', file=stderr)
            MANAGERS[manager].run_gc()

    def update_desktopdb(self):
        for manager in self.get_managers():
            if not MANAGERS[manager].has_desktopdb:
                continue
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} is updating it\'s desktop database...', file=stderr)
            MANAGERS[manager].update_dekstop_db()

    def update(self, packages: list[str] | None):
        if packages != None and len(packages) == 0:
            packages = None

        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} updating...', file=stderr)
            MANAGERS[manager].update(packages)

    def list_packages(self, packages: list[str] | None, dict: Dict | None = None) -> Dict | None:
        if dict != None:
            return dict

        if packages != None and len(packages) == 0:
            packages = None

        aux: Dict
        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{MANAGERS[manager].name.upper()}{Color.END} listing:', file=stderr)
            aux = MANAGERS[manager].list_packages(
                self.args.user_installed, packages)
            if dict == None:
                dict = aux
            else:
                dict.add_manager(aux.managers)
                dict.extend(aux.items)
        return dict

    def search(self, packages: list[str], dict: Dict | None = None) -> Dict | None:
        self.check_args(packages)
        managers = self.get_managers(
            self.args.interactive and self.args.async_search)

        if not self.actioned:
            for manager in managers:
                MANAGERS[manager].search(packages)
            self.actioned = True

        aux: Dict
        is_async = self.args.command != ['search'] and self.args.async_search
        for manager in managers:
            if is_async and (manager in self.joined or MANAGERS[manager].is_working()):
                continue
            self.joined.append(manager)
            aux = MANAGERS[manager].search_response()
            if dict == None:
                dict = aux
            else:
                dict.add_manager(aux.managers)
                dict.extend(aux.items)

        if dict and not is_async:
            print(dict.to_string(managers_order=managers))

        return dict

    def interactive(self, dict_func: Callable[[list[str], Dict | None], Dict | None], run_func: Callable[[list[str] | Dict], None]):
        aux: Dict | None = None
        package_list: list[str] = self.args.packages
        managers: list[str] = self.get_managers()
        manager_dict = {manager[:1]: manager for manager in managers}
        item_dict: Dict | None = None

        if self.args.async_search:
            try:
                print(f'{Color.YELLOW}Waiting{Color.END} for a response ...')
                aux = None
                while len(self.joined) < len(managers):
                    sleep(0.5)
                    aux = dict_func(package_list, None)
                    if aux == None:
                        continue
                    if item_dict == None:
                        item_dict = aux
                    print(f' {"":{"-"}<15} Response found! {"":{"-"}<15}')
                    if len(aux) == 0:
                        continue
                    item_dict.add_manager(aux.managers)
                    item_dict.extend(aux.items)
                    print(item_dict.to_string(managers_order=managers))
            except KeyboardInterrupt:
                pass
        else:
            item_dict = dict_func(package_list, None)

        if not item_dict or len(item_dict) == 0:
            error('No packages were found!', type=ERROR, code=DEFAULT)

        prefix = f' {Color.BLUE}::{Color.END} '
        message = f'\n{prefix}Enter packages to install (eg: 1 2 3 5, 1-3 5) [0 to exit]'
        message += f'\n{prefix}Use d, n or f to specify the package manager (eg: 1n, 2, 3-6f)'
        message += f'\n{prefix}{Color.BOLD} >{Color.END} '

        packages = input(message)
        if packages == '0':
            error('Action cancelled!', type=WARNING, code=DEFAULT)

        try:
            package_dict: Dict = Dict(package_list, [])
            for arg in packages.split(' '):
                char = arg[-1:]
                has_manager = char.isalpha()

                if has_manager:
                    arg = arg[:-1]

                if len(arg) < 3:
                    items = [item_dict.index(int(arg) - 1)]
                else:
                    start, stop = arg.split('-')
                    items = [item_dict.index(i) for i in
                             range(int(start) - 1, int(stop))]

                if has_manager:
                    for item in items:
                        item.keys = [manager_dict[char]]
                else:
                    for item in items:
                        item.keys = [item.keys[0]]

                package_dict.add_manager(items[0].keys[0])
                package_dict.extend(items)

            self.managers = package_dict.managers
            run_func(package_dict)
        except KeyboardInterrupt:
            pass
        except:
            error('Invalid package was entered!', type=ERROR, code=ERROR)

    def run(self):
        match self.args.command:
            case ['install']:
                if self.args.interactive:
                    self.interactive(self.search, self.install)
                else:
                    self.install(self.args.packages)
            case ['remove']:
                # if self.args.interactive:
                #     self.interactive(self.list_packages, self.remove)
                # else:
                self.remove(self.args.packages)
            case ['update']:
                self.update(self.args.packages)
            case ['list']:
                self.list_packages(self.args.packages)
            case ['search']:
                self.search(self.args.packages)

        if self.args.garbage_collector:
            self.run_gc()

        if self.args.database:
            self.update_desktopdb()

        sudoloop(False)


if __name__ == '__main__':
    try:
        xapp = XApp(argv[1:])
        xapp.run()
    except KeyboardInterrupt:
        error('\nAction interrupted by user!', type=WARNING, code=DEFAULT)
