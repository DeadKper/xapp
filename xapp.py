#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xdata.items import Dict
from xdata.managers import MANAGERS
from xdata.static import *
from typing import Sequence, Callable
from time import sleep
from sys import argv, stderr


class XApp:
    def __init__(self, args: Sequence[str]) -> None:
        self.managers = {k: v for k, v in MANAGERS.items()
                         if k in MANAGER_LIST}

        self.parser, self.args = parse_args(args)
        self.run_flags = self.args.garbage_collector or self.args.update_desktop_db
        self.args.set_configs(get_config(f'{CONFIG}/xapp'))

        self.args.async_managers = [
            man for man in self.args.async_managers if man in MANAGER_LIST]

        if len(self.args.managers) == 0:
            self.args.managers = [
                man for man in self.managers if man not in self.args.async_managers]
        else:
            self.args.managers = [
                man for man in self.args.managers if man in MANAGER_LIST]

        if len(self.args.managers) == 1:
            self.main = MANAGERS[self.args.managers[0]]
        elif len(self.args.default_managers) == 0:
            self.main = MANAGERS[self.args.managers[0]]
        else:
            self.main = MANAGERS[self.args.default_managers[0]]

        if len(self.get_managers(self.args.async_search)) == 0:
            error('No valid package manager was selected', type=ERROR)

        self.actioned = False
        self.joined: list[str] = []

    def get_managers(self, include_slow: bool = True):
        managers = self.args.managers + \
            self.args.async_managers if include_slow else self.args.managers
        return managers

    def check_args(self, args):
        if len(args) > 0:
            return
        error('No arguments given!', type=ERROR)

    def install(self, packages: list[str] | Dict):
        self.check_args(packages)

        if isinstance(packages, list):
            print(
                f'\n{Color.BOLD}{self.main.name.upper()}{Color.END} installing...', file=stderr)
            self.main.install(packages)
        else:
            for manager in self.get_managers():
                usable = packages.pop_manager(manager)
                if len(usable) == 0:
                    continue

                print(
                    f'\n{Color.BOLD}{manager.upper()}{Color.END} installing...', file=stderr)
                self.managers[manager].install(usable)

    def remove(self, packages: list[str] | Dict):
        self.check_args(packages)

        if isinstance(packages, list):
            print(
                f'\n{Color.BOLD}{self.main.name.upper()}{Color.END} removing...', file=stderr)
            self.main.remove(packages)
        else:
            for manager in self.get_managers():
                usable = packages.pop_manager(manager)
                if len(usable) == 0:
                    continue

                print(
                    f'\n{Color.BOLD}{manager.upper()}{Color.END} removing...', file=stderr)
                self.managers[manager].remove(usable)

    def run_gc(self):
        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{self.managers[manager].name.upper()}{Color.END} running garbage collector...', file=stderr)
            self.managers[manager].run_gc()

    def update_desktopdb(self):
        for manager in self.get_managers():
            if not self.managers[manager].has_desktopdb:
                continue
            print(
                f'\n{Color.BOLD}{self.managers[manager].name.upper()}{Color.END} is updating it\'s desktop database...', file=stderr)
            self.managers[manager].update_dekstop_db()

    def update(self, packages: list[str]):
        if len(packages) > 0:
            print(
                f'\n{Color.BOLD}{self.main.name.upper()}{Color.END} is updating...', file=stderr)
            self.main.update(packages)
        else:
            for manager in self.get_managers():
                print(
                    f'\n{Color.BOLD}{self.managers[manager].name.upper()}{Color.END} is updating...', file=stderr)
                self.managers[manager].update(packages)

    def list_packages(self):
        for manager in self.get_managers():
            print(
                f'\n{Color.BOLD}{self.managers[manager].name.upper()}{Color.END} listing:', file=stderr)

            self.managers[manager].list_packages(
                self.args.user_installed)

    def search(self, packages: list[str]) -> Dict:
        self.check_args(packages)
        managers = self.get_managers(self.args.async_search)

        if not self.actioned:
            for manager in managers:
                self.managers[manager].search(packages)
            self.actioned = True

        dict = Dict(packages, [])
        replaced = r'{}'
        managers_message = f'{replaced}/{len(managers)} managers responded!'
        message_size = len(managers_message.format(len(managers)))
        section_message = f' {"":{"-"}<15} {Color.BOLD}{replaced}{Color.END} {"":{"-"}<15}'

        def get_search():
            for manager in managers:
                if self.args.async_search and (manager in self.joined or self.managers[manager].is_working()):
                    continue
                self.joined.append(manager)
                aux = self.managers[manager].search_response()
                if self.args.async_search and len(managers) > 1:
                    print(section_message.format(
                        f'{managers_message.format(len(self.joined)):^{message_size}}'))
                    if len(aux) == 0:
                        continue
                    print(aux.to_string())
                elif len(aux) == 0:
                    continue
                dict.add_manager(aux.managers)
                dict.extend(aux.items)

        if self.args.async_search:
            try:
                print(f'{Color.YELLOW}Waiting{Color.END} for a response ...')
                while len(self.joined) < len(managers):
                    sleep(0.5)
                    get_search()
            except KeyboardInterrupt:
                print()
            package_count = len(dict)
            if package_count > 0:
                package_message = f'{package_count} package{"s" if package_count > 1 else ""} found!'
                print(section_message.format(
                    f'{package_message:^{message_size}}'))
        else:
            get_search()

        if len(dict) == 0:
            error('No packages were found!', type=ERROR, code=DEFAULT)

        dict.sorted = len(managers) == 1

        print(dict.to_string(managers_order=managers))

        return dict

    def interactive(self, dict_func: Callable[[list[str]], Dict], run_func: Callable[[list[str] | Dict], None]):
        package_list: list[str] = self.args.packages
        managers: list[str] = self.get_managers()
        manager_dict = {manager[:1]: manager for manager in managers}
        dict: Dict

        dict = dict_func(package_list)

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

                if arg.find('-') == -1:
                    items = [dict.index(int(arg) - 1)]
                else:
                    start, stop = arg.split('-')
                    items = [dict.index(i) for i in
                             range(int(start) - 1, int(stop))]

                if has_manager:
                    for item in items:
                        item.keys = [manager_dict[char]]
                else:
                    for item in items:
                        item.keys = [item.keys[0]]

                package_dict.add_manager(items[0].keys[0])
                package_dict.extend(items)

            self.args.managers = package_dict.managers
            self.args.async_managers = []
            run_func(package_dict)
        except KeyboardInterrupt:
            pass
        except:
            error('Invalid package was entered!', type=ERROR, code=ERROR)

    def run(self):
        match self.args.command:
            case None:
                if not self.run_flags:
                    self.parser.print_help()
                    exit(0)
            case 'install':
                if self.args.interactive:
                    self.interactive(self.search, self.install)
                else:
                    self.install(self.args.packages)
            case 'remove':
                self.remove(self.args.packages)
            case 'update':
                self.update(self.args.packages)
            case 'list':
                self.list_packages()
            case 'search':
                self.search(self.args.packages)

        if self.args.garbage_collector:
            self.run_gc()

        if self.args.update_desktop_db:
            self.update_desktopdb()

        sudoloop(False)


if __name__ == '__main__':
    try:
        env_args = argv[1:].copy()
        commands = ('install', 'remove', 'update', 'list', 'search')
        for i in range(len(env_args)):
            if env_args[i] not in commands:
                continue
            if i > 0:
                env_args.insert(0, env_args.pop(i))
            break
        xapp = XApp(env_args)
        xapp.run()
    except KeyboardInterrupt:
        error('\nAction interrupted by user!', type=WARNING, code=DEFAULT)
