from subprocess import Popen, PIPE
from threading import Thread
from xdata.static import sudoloop, error, ERROR
from xdata.items import Dict, EMPTY_DICT
from pathlib import Path


class PackageManager:
    def __init__(self, name: str, has_desktopdb=False) -> None:
        self.name = name
        self.__thread: Thread
        self.__result = ['', '']
        self.__joined = True
        self.query: list[str] = []
        self.home = Path.home()
        self.has_desktopdb = has_desktopdb

    def install(self, packages: list[str] | Dict, fail=False) -> bool:
        return False

    def remove(self, packages: list[str] | Dict, fail=False) -> bool:
        return False

    def update(self, packages: list[str] | None = None, fail=False) -> bool:
        return False

    def run_gc(self):
        pass

    def list_packages(self, user_installed: bool):
        pass

    def search(self, packages: list[str]):
        self.query = packages

    def search_response(self) -> Dict:
        self.join()
        return EMPTY_DICT

    def update_dekstop_db(self):
        pass

    def is_working(self):
        if self.__joined:
            return True
        if self.__thread.is_alive():
            return True
        self.join()
        return False

    def join(self):
        if not self.__joined:
            self.__thread.join()
            self.__joined = True

    def response(self, join=False) -> tuple[str, str]:
        if join:
            self.join()
        return tuple(self.__result) if self.__joined else ('', '')

    def _run(self, command: list[str], args: list[str] | Dict = [], sudo=False, pipe_out=False, pipe_err=False, threaded=False):
        if len(command) == 0:
            error(
                f'{self.name} tried to run a command when no command was given', type=ERROR)

        if sudo:
            if not sudoloop():
                error(f'{self.name!r} needs sudo to work!', type=1)
            command = ['sudo', '-n', '--'] + command

        if isinstance(args, Dict):
            args = args.pop_manager(self.name)
            if len(args) == 0:
                return False

        def run(args: list[str], stdout: bool, stderr: bool):
            process = Popen(args=args,
                            stdout=PIPE if stdout else None,
                            stderr=PIPE if stderr else None)
            out, err = process.communicate()
            self.__result[0] = out.decode() if stdout else ''
            self.__result[1] = err.decode() if stderr else ''

        run_args = (command + args, pipe_out, pipe_err)

        if threaded:
            self.join()
            self.__joined = False
            self.__thread = Thread(target=run, args=run_args)
            self.__thread.start()
        else:
            run(*run_args)
            if len(self.__result[1]) > 0:
                return False
        return True
