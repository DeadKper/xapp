from re import sub as sed
from sys import stderr
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep, time
from os.path import exists
from configparser import ConfigParser
from xdata.namespaces import ConfigNamespace
from xdata.static import *

SEPARATOR = '=-|-='


def error(text: str, type=DEFAULT, code=ERROR):
    lines = sed(r'^(\n)+', f'\\1{SEPARATOR}', text)
    if lines.find(SEPARATOR) != -1:
        lines, text = lines.split(SEPARATOR)
    else:
        lines = ''
    if type == WARNING:
        text = f'{Color.BOLD}{Color.YELLOW}Warning{Color.END}: {text}'
    elif type == ERROR:
        text = f'{Color.BOLD}{Color.RED}Error{Color.END}: {text}'
    print(f'{lines}{text}', file=stderr)
    quit(code)


run_sudo_loop = False


def _sudo_loop():
    count = 0
    start = time()
    while run_sudo_loop:
        loop = time()
        if loop - start > 30:
            start = loop
            Popen(['sudo', '--validate'], stdout=PIPE, stderr=PIPE)
        sleep(1)
        count += 1


sudo_loop_thread = Thread(target=_sudo_loop)


def sudoloop(run=True):
    global run_sudo_loop
    global sudo_loop_thread

    if run == sudo_loop_thread.is_alive():
        return True

    run_sudo_loop = run
    if run:
        _, err = Popen(['sudo', '-i', 'echo'], stdout=PIPE,
                       stderr=PIPE).communicate()

        if len(err.decode()) > 0:
            run_sudo_loop = False
            return False

        sudo_loop_thread = Thread(target=_sudo_loop)
        sudo_loop_thread.start()
    else:
        sudo_loop_thread.join()

    return True


def item_confidence(query_list: list[str], name: str, id: str | None = None):
    bonus = len(query_list) + 2
    penalty_count = 0
    result = 0
    query_negative = name
    for query in query_list:
        query = query.lower()
        query_negative = sed(query, '', query_negative)
        if name.find(query) == -1:
            penalty_count += 1
        else:
            bonus -= 1
    for c in query_negative:
        result += ord(c)
    result -= result // bonus
    if penalty_count > 0:
        result += 3000 // (len(query_list) - penalty_count + 1)

    if id != None:
        bonus = len(query_list) + 2
        penalty_count = 0
        id_result = 0
        query_negative = id
        for query in query_list:
            query = query
            query_negative = sed(query, '', query_negative)
            if id.find(query) == -1:
                penalty_count += 1
            else:
                bonus -= 1
        for c in query_negative:
            id_result += ord(c)
        id_result -= id_result // bonus
        if penalty_count > 0:
            id_result += 3000 // (len(query_list) - penalty_count + 1)
        if id_result < result:
            result = id_result

    return result


def make_default_config(file: str):
    if exists(file):
        return

    config = ConfigParser()

    config.add_section('general')
    config.set('general', '# interactive', 'True')
    config.set('general', '# garbage_collector', 'True')
    config.set('general', 'managers', 'dnf,flatpak')
    config.set('general', 'async_managers', 'nix-env')
    config.add_section('install')
    config.set('install', '# interactive', 'True')
    config.add_section('remove')
    config.set('remove', '# interactive', 'True')
    config.add_section('list')
    config.set('list', '# user_installed', 'True')
    config.add_section('search')
    config.set('search', '# async_search', 'True')

    with open(file, 'w') as config_file:
        config.write(config_file)

    return config


def get_config(file: str):
    config = make_default_config(file)
    if config == None:
        config = ConfigParser()
        config.read(file)
    return ConfigNamespace(**config.__dict__['_sections'])
