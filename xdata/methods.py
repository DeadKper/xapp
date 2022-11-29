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
sudo_loop_thread: Thread | None = None


def _sudo_loop():
    count = 0
    while run_sudo_loop:
        sleep(1)
        count += 1
        if count == 30:
            Popen(['sudo', 'echo', '""'], stdout=PIPE, stderr=PIPE)


def sudoloop(run=True):
    global run_sudo_loop
    global sudo_loop_thread

    def run_thread():
        global run_sudo_loop
        _, err = Popen(['sudo', 'echo', '""'], stdout=PIPE,
                       stderr=PIPE).communicate()

        if len(err.decode()) > 0:
            run_sudo_loop = False
            return False

        sudo_loop_thread = Thread(target=_sudo_loop)
        sudo_loop_thread.start()
        return True

    run_sudo_loop = run
    if sudo_loop_thread == None:
        return run_thread()
    else:
        if not run:
            sudo_loop_thread.join()
        elif not sudo_loop_thread.is_alive():
            return run_thread()
    return True
