from re import sub as sed
from xdata import Color
from sys import stderr
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep

DEFAULT = 0
ERROR = 1
WARNING = 2
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
    while run_sudo_loop:
        sleep(1)
        count += 1
        if count == 30:
            Popen(['sudo', 'echo', '""'], stdout=PIPE, stderr=PIPE)


sudo_loop_thread = Thread(target=_sudo_loop)


def sudoloop(run=True):
    global run_sudo_loop
    global sudo_loop_thread

    run_sudo_loop = run
    if run and not sudo_loop_thread.is_alive():
        _, err = Popen(['sudo', 'echo', '""'], stdout=PIPE,
                       stderr=PIPE).communicate()

        if len(err.decode()) > 0:
            run_sudo_loop = False
            return False

        sudo_loop_thread = Thread(target=_sudo_loop)
        sudo_loop_thread.start()
        return True
    elif not run and sudo_loop_thread.is_alive():
        sudo_loop_thread.join()
        return True
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
