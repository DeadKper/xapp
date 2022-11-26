#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Literal
from subprocess import Popen, PIPE
from pathlib import Path
from managers.manager import PackageManager
from managers.dnf import dnf
from managers.flatpak import flatpak
from managers.nixenv import nixenv
from data.data import Item, merge, Color
from re import sub as sed
from time import sleep
import sys

NONE = 0
WARNING = 1
ERROR = 2
SEPARATOR = '=-|-='


def error(text: str, type=NONE, code=1):
    lines = sed(r'^(\n)+', f'\\1{SEPARATOR}', text)
    if lines.find(SEPARATOR) != -1:
        lines, text = lines.split(SEPARATOR)
    else:
        lines = ''
    if type == WARNING:
        text = f'{Color.BOLD}{Color.YELLOW}Warning{Color.END}: {text}'
    elif type == ERROR:
        text = f'{Color.BOLD}{Color.RED}Error{Color.END}: {text}'
    print(f'{lines}{text}', file=sys.stderr)
    quit(code)


class FrozenDict(dict):
    def __hash__(self):
        return id(self)

    def __immutable__(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = __immutable__
    __delitem__ = __immutable__
    clear = __immutable__
    update = __immutable__
    setdefault = __immutable__  # type: ignore
    pop = __immutable__
    popitem = __immutable__


SUB_COMMANDS = (
    'help',
    'install',
    'remove',
    'update',
    'list',
    'search',
    'run-gc',
    'update-desktop-db',
    'clean-cache',
)

SKIP_NEXT_FLAGS = FrozenDict({
    '-m': 1
})


def run(args: list[str], pipe: bool, pipe_error=True):
    process = Popen(args=args,
                    stdout=PIPE if pipe else None,
                    stderr=PIPE if pipe_error else None)
    process.communicate()


def nix_env_db():
    run(['rsync', '-pqrLK', '--chmod=u+rwx', f'{Path.home()}/.nix-profile/share/',
        f'{Path.home()}/.local/share/nix-env/share/', '--delete-after'], True)
    run(['update-desktop-database',
        f'{Path.home()}/.local/share/nix-env/share/applications'], True)


MANAGERS_DESKTOP_DATABASE = FrozenDict({
    'nix-env': nix_env_db
})

MANAGERS: dict[str, PackageManager] = FrozenDict({
    'dnf': dnf('dnf', '', ''),
    'flatpak': flatpak('flatpak', '', ''),
    'nix-env': nixenv('nix-env', '', '')
})

HELP_STR = f'use \'{Color.YELLOW}-h{Color.END}\' for help'


class Command:

    def __init__(self, command: list[str]) -> None:
        self.unparsed: list[str] = command
        self.command: str = ''
        self.args: list[str] = []
        self.managers: list[str] = []
        self.auto_resolve: bool = False
        self.run_gc: bool = False
        self.update_db: bool = False
        self.__implicit_update_db__: bool = False
        self.assume: Literal[True, False, None] = None
        self.help: bool = False
        self.clean_cache: bool = False
        self.install_interactive: bool = False
        self.list_user: bool = False
        self.in_async: bool = False

    def __set_defaults__(self):
        self.assume = True
        self.auto_resolve = True
        self.install_interactive = True
        self.list_user = True
        if len(self.managers) == 0:
            self.managers = ['dnf', 'flatpak']
            self.__implicit_update_db__ = True

    def __get_flag_values__(self, i: int):
        dashes = '--' if self.unparsed[i].startswith('--') else '-'
        flag = self.unparsed[i].lstrip('-')
        equals_i = flag.find('=')
        if equals_i != -1:
            next = flag[equals_i + 1:]
            flag = flag[:equals_i]
            if next.startswith('\'') and next.endswith('\'') \
                    or next.startswith('\"') and next.endswith('\"'):
                next = next[1:len(next) - 1]
        else:
            next = None
            full_flag = f'{dashes}{flag}'
            if full_flag in SKIP_NEXT_FLAGS:
                skip_ammount = SKIP_NEXT_FLAGS[full_flag]
                if len(self.unparsed) <= i + skip_ammount:
                    error(
                        f'not enough arguments for flag \'{Color.BOLD}{full_flag}{Color.END}\'', type=ERROR)
                if skip_ammount == 1:
                    next = self.unparsed[i + 1]
                else:
                    next = self.unparsed[i + 1:i + 1 + skip_ammount]
        return (flag, next)

    def __base_flag__(self, flag: str) -> bool:
        if flag in ['h', 'help'] and not self.help:
            self.help
        elif flag in ['async'] and not self.in_async:
            self.in_async = True
        # elif flag in ['a', 'auto-resolve'] and not self.auto_resolve:
        #     self.auto_resolve = True
        # elif flag in ['c', 'clean-cache'] and not self.clean_cache:
        #     self.clean_cache = True
        elif flag in ['g', 'run-garbage-collector'] and not self.run_gc:
            self.run_gc
        elif flag in ['u', 'update-desktop-database'] and not self.update_db:
            self.update_db = True
        # elif flag in ['y', 'assume-yes'] and self.assume == None:
        #     self.assume = True
        # elif flag in ['n', 'assume-no'] and self.assume == None:
        #     self.assume = False
        else:
            return False
        return True

    def __install_flag__(self, flag: str, next: str) -> bool:
        if flag in ['i', 'interactive'] and not self.install_interactive:
            self.install_interactive
        else:
            return False
        return True

    def __list_flag__(self, flag: str, next: str) -> bool:
        if flag in ['u', 'user-installed'] and not self.list_user:
            self.list_user = True
        else:
            return False
        return True

    def __command_flag__(self, flag: str, next: str) -> bool:
        match self.command:
            case 'install':
                return self.__install_flag__(flag, next)
            case 'list':
                return self.__list_flag__(flag, next)
            case _:
                return False

    def __add_manager__(self, value: str):
        if value not in self.managers:
            self.managers.append(value)
            if value in MANAGERS_DESKTOP_DATABASE:
                self.__implicit_update_db__ = True

    def __manager_flag__(self, flag: str, next: str) -> bool:
        if len(self.managers) > 0:
            return False

        def check_manager(single_dash: bool, manager: str):
            match manager:
                case 'd' | 'dnf':
                    self.__add_manager__('dnf')
                case 'n' | 'nix-env':
                    self.__add_manager__('nix-env')
                case 'f' | 'flatpak':
                    self.__add_manager__('flatpak')
                # case 'x' | 'xapp':
                #     self.__add_manager__('xapp')
                case _:
                    error(
                        f'\'{Color.BOLD}{manager}{Color.END}\' is not a valid manager{" flag" if single_dash else ""}, {HELP_STR}', type=ERROR)

        match flag:
            case 'm':
                for letter in next:
                    check_manager(True, letter)
            case 'managers':
                for manager in next.split(','):
                    check_manager(False, manager)
            case _:
                return False
        return True

    def __check_flag__(self, i: int) -> int:
        parsed = False
        dashes = '--' if self.unparsed[i].startswith('--') else '-'
        flag, next = self.__get_flag_values__(i)

        if self.command:  # Check for sub command flag
            parsed = self.__command_flag__(flag, next)  # type: ignore

        if not parsed:  # Check for manager flag
            parsed = parsed or self.__manager_flag__(
                flag, next)  # type: ignore

        if not parsed:  # Check for base flag
            if dashes == '-':
                for letter in flag:
                    parsed = parsed or self.__base_flag__(letter)
            else:
                parsed = parsed or self.__base_flag__(flag)

        if not parsed:  # Not a valid flag
            error(
                f'\'{Color.BOLD}{dashes}{flag}{Color.END}\' is not a valid flag, {HELP_STR}', type=ERROR)

        return i + SKIP_NEXT_FLAGS.get(f'{dashes}{flag}', 0)

    def parse(self):
        sub_command_args = self.args
        i = 0
        args = self.unparsed
        size = len(args)
        while i < size:
            arg = args[i]
            if arg == '--':
                if self.command == '':
                    self.command = args[i+1]
                    i += 1
                sub_command_args[len(sub_command_args):] = args[i+1:]
                break

            if arg.startswith('-'):
                i = self.__check_flag__(i)
            elif self.command != '':
                sub_command_args.append(arg)
            elif arg in SUB_COMMANDS:
                self.command = arg
            else:
                error(
                    f'\'{Color.BOLD}{arg}{Color.END}\' is not a command, {HELP_STR}', type=ERROR)

            i += 1

        if self.command == '' and \
                (self.run_gc or self.update_db or self.help or self.clean_cache):
            self.command = 'xapp'

        self.__set_defaults__()

        if len(self.managers) == 0:
            self.__implicit_update_db__ = True
            self.managers = ['dnf', 'nix-env', 'flatpak']

        if self.command == '':
            self.help = True

    def __get_managers__(self) -> list[PackageManager]:
        managers = []
        for manager in self.managers:
            if manager in MANAGERS:
                managers.append(MANAGERS[manager])
        return managers

    def __help__(self):
        c = f'{Color.BOLD}> {Color.END}'
        message = f'{Color.BOLD}Usage{Color.END}: xapp <global flags> <command> <command flags> <arguments>'
        message += f'\n{Color.BOLD}Global flags{Color.END}:'
        message += f'\n{"":>2}{Color.BOLD}-g --run-garbage-collector{Color.END}'
        message += f'\n{"":>4}{c}Run garbage collector for each manager'
        message += f'\n{"":>2}{Color.BOLD}-u --update-desktop-database{Color.END}'
        message += f'\n{"":>4}{c}Update desktop database'
        message += f'\n{"":>2}{Color.BOLD}-h --help{Color.END}'
        message += f'\n{"":>4}{c}Print help for the command'
        message += f'\n{Color.BOLD}Commands{Color.END}:'
        message += f'\n{"":>2}{Color.BOLD}help{Color.END}:'
        message += f' Print help'
        message += f'\n{"":>2}{Color.BOLD}install{Color.END}:'
        message += f' Install a package/s'
        message += f'\n{"":>4}{Color.BOLD}-i --interactive{Color.END}'
        message += f'\n{"":>6}{c}Use interactive install'
        message += f'\n{"":>4}{Color.BOLD}--async{Color.END}'
        message += f'\n{"":>6}{c}Run interactive install asyncronously, will clear the console on each thread join'
        message += f'\n{"":>2}{Color.BOLD}search{Color.END}:'
        message += f' Search for a package/s'
        message += f'\n{"":>4}{Color.BOLD}--async{Color.END}'
        message += f'\n{"":>6}{c}Run searchs asyncronously, will clear the console on each thread join'
        message += f'\n{"":>2}{Color.BOLD}update{Color.END}:'
        message += f' Update a package/s'
        message += f'\n{"":>2}{Color.BOLD}remove{Color.END}:'
        message += f' Remove a package/s'
        message += f'\n{"":>2}{Color.BOLD}list{Color.END}:'
        message += f' List installed packages'
        message += f'\n{"":>4}{Color.BOLD}-u --user-installed{Color.END}'
        message += f'\n{"":>6}{c}Only print user installed packages'
        message += f'\n{"":>2}{Color.BOLD}run-gc{Color.END}:'
        message += f' Run garbage collector'
        message += f'\n{"":>2}{Color.BOLD}update-desktop-db{Color.END}:'
        message += f' Update desktop database'
        message += f'\n{"":>2}{Color.BOLD}clean-cache{Color.END}:'
        message += f' Clean and rebuild cache'
        print(message)

    def __no_arg_error__(self):
        if len(self.args) > 0:
            return
        error('No arguments given!', type=ERROR)

    def __install__(self):
        self.__no_arg_error__()
        managers = self.__get_managers__()
        if len(managers) == 1:
            managers[0].install(self.args)
            return

        for manager in managers:
            if manager.install(self.args, True):
                return

        print(f'\n{Color.RED}{Color.BOLD}ERROR:{Color.END} No package manager was able to install the program!\nUse interactive install (-i) or search for the exact name/id of the package')

    def __interactive_install__(self):
        self.__no_arg_error__()
        results = self.__search__()

        message = f'\n {Color.BLUE}::{Color.END} '
        message = f'{message}{Color.BOLD}Enter packages to install{Color.END}'
        message = f'{message} (eg: 1 2 3 5, 1-3 5) [0 to exit]'
        message = f'{message}\n {Color.BLUE}::{Color.END} {Color.BOLD}->{Color.END} '
        packages = input(message)

        if packages == '0':
            error('Installation cancelled!', type=WARNING, code=0)

        install_list: list[Item] = []
        for arg in packages.split(' '):
            if len(arg) == 1:
                install_list.append(results[int(arg) - 1])
            else:
                start, stop = arg.split('-')
                install_list.extend(
                    [results[i] for i in range(int(start) - 1, int(stop))])

        for manager in self.__get_managers__():
            manager.install(install_list)

    def __remove__(self):
        managers = self.__get_managers__()
        if len(managers) == 1:
            managers[0].remove(self.args)
            return

        for manager in managers:
            if manager.remove(self.args, True):
                return

        print(f'\n{Color.RED}{Color.BOLD}ERROR:{Color.END} No package manager was able to remove the program!\nUse \'list\' to search for the exact name/id of the package')

    def __update__(self):
        managers = self.__get_managers__()
        if len(self.args) == 0:
            for manager in managers:
                manager.update()
            return

        if len(managers) == 1:
            managers[0].update(self.args)
            return

        for manager in managers:
            if manager.update(self.args, True):
                return

        print(f'\n{Color.RED}{Color.BOLD}ERROR:{Color.END} No package manager was able to update the program!\nUse \'list\' to search for the exact name/id of the package')

    def __list__(self):
        for manager in self.__get_managers__():
            print(f'\n{Color.BOLD}{manager.name} packages:{Color.END}')
            manager.list_packages(self.list_user)

    def __search__(self):
        self.__no_arg_error__()
        managers = self.__get_managers__()
        for manager in managers:
            manager.search(self.args)

        prev_len = 0
        printed: list[str] = []

        result: list[Item] = []
        items: dict[str, list[Item]] = {}

        should_clear = False

        while len(printed) < len(managers):
            sleep(1)
            for manager in managers:
                if self.in_async and manager.is_working() or manager.name in printed:
                    continue

                for key, value in manager.search_response().items():
                    id = key.lower()
                    if id in items:
                        items[id].append(value)
                    else:
                        items[id] = [value]

                printed.append(manager.name)

            if prev_len == len(printed):
                continue
            prev_len = len(printed)

            result = [merge(value) for value in items.values()]

            result.sort(key=lambda item: item.confidence)

            message = ''
            for i in range(len(result) - 1, -1, -1):
                message += f'\n{result[i].to_string(i + 1, True)}'

            if should_clear:
                run(['clear'], False)
            else:
                should_clear = True
            print(message[1:])

        return result

    def __run_garbage_collector__(self):
        for manager in self.__get_managers__():
            manager.run_gc()

    def __update_desktop_database__(self):
        for manager in self.managers:
            if manager in MANAGERS_DESKTOP_DATABASE:
                MANAGERS_DESKTOP_DATABASE[manager]()

    def __build_cache__(self):
        pass

    def __clean_cache__(self):
        self.__build_cache__()

    def run(self):
        if self.help or self.command == 'help':
            self.__help__()
            return

        if self.clean_cache:
            self.__clean_cache__()

        match self.command:
            case 'search':
                self.__search__()
            case 'install':
                if self.install_interactive:
                    self.__interactive_install__()
                else:
                    self.__install__()
                    self.__clean_cache__()
            case 'remove':
                self.__remove__()
            case 'update':
                self.__update__()
            case 'list':
                self.__list__()
            case 'run-gc':
                self.run_gc = True
            case 'update-desktop-db':
                self.update_db = True
            case 'clean-cache':
                if not self.clean_cache:
                    self.__clean_cache__()

        if self.run_gc:
            self.__run_garbage_collector__()

        if self.update_db or self.__implicit_update_db__:
            self.__update_desktop_database__()


if __name__ == '__main__':
    try:
        command = Command(sys.argv[1:])
        command.parse()
        command.run()
    except KeyboardInterrupt:
        error('\nAction interrupted by user!', type=WARNING, code=0)
