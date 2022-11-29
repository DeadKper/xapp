from subprocess import Popen, PIPE
from threading import Thread
from xdata import ItemDict, EMPTY_ITEM_DICT, sudoloop, error, ERROR


class PackageManager:
    def __init__(self, name: str) -> None:
        self.name = name
        self.__thread__: Thread
        self.__result__ = ['', '']
        self.__piped__ = False
        self.__joined__ = True
        self.use_sudo = False

    def install(self, packages: list[str] | ItemDict, fail=False) -> bool:
        return False

    def remove(self, packages: list[str] | ItemDict, fail=False) -> bool:
        return False

    def update(self, packages: list[str] | None = None, fail=False) -> bool:
        return False

    def run_gc(self):
        pass

    def list_packages(self, user_installed: bool, packages: list[str] | None = None) -> ItemDict:
        return EMPTY_ITEM_DICT

    def search(self, packages: list[str]):
        pass

    def search_response(self) -> ItemDict:
        return EMPTY_ITEM_DICT

    def is_working(self):
        if self.__joined__:
            return True
        if self.__thread__.is_alive():
            return True
        self.join()
        return False

    def join(self):
        if not self.__joined__:
            self.__thread__.join()
            self.__joined__ = True

    def should_respond(self):
        return self.__piped__

    def has_response(self):
        return self.__piped__ and self.__joined__

    def response(self, join=False) -> tuple[str, str]:
        if join:
            self.join()
        return tuple(self.__result__) if self.__joined__ else ('', '')

    def __execute__(self, args: list[str], pipe: bool, pipe_error=True, just_run=False):
        if self.use_sudo:
            if not sudoloop():
                error(f'{self.name!r} needs sudo to work!', type=ERROR)

        if just_run:
            Popen(args=args,
                  stdout=PIPE if pipe else None,
                  stderr=PIPE if pipe_error else None).communicate()
            return

        def run():
            process = Popen(args=args,
                            stdout=PIPE if pipe else None,
                            stderr=PIPE if pipe_error else None)
            stdout, stderr = process.communicate()
            self.__result__[0] = stdout.decode() if pipe else ''
            self.__result__[1] = stderr.decode() if pipe_error else ''

        self.join()
        self.__piped__ = pipe
        self.__joined__ = False
        self.__thread__ = Thread(target=run)
        self.__thread__.start()
