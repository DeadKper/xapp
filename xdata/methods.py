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
sudo_loop_thread: Thread


def _sudo_loop():
    while run_sudo_loop:
        sleep(30)
        Popen(['sudo', 'echo', '""'], stdout=PIPE, stderr=PIPE)


def sudoloop(run=True):
    global run_sudo_loop
    global sudo_loop_thread
    run_sudo_loop = run
    if run and not sudo_loop_thread.is_alive():
        sudo_loop_thread = Thread(target=_sudo_loop)
        sudo_loop_thread.run()
