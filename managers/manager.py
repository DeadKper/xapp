from subprocess import Popen, PIPE
from threading import Thread
from data.data import Item


class PackageManager():
    def __init__(self, name: str, config: str, cache: str) -> None:
        self.name = name
        self.config = config
        self.cache = cache
        self.__thread__: Thread
        self.__result__ = ['', '']
        self.__piped__ = False
        self.__joined__ = True

    def install(self, packages: list[str] | list[Item], fail=False) -> bool:
        return False

    def remove(self, packages: list[str], fail=False) -> bool:
        return False

    def update(self, packages: list[str] | None = None, fail=False) -> bool:
        return False

    def run_gc(self):
        pass

    def list_packages(self, user_installed: bool):
        pass

    def search(self, package: list[str]):
        pass

    def search_response(self) -> dict[str, Item]:
        return {}

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

    def __execute__(self, args: list[str], pipe: bool, pipe_error=True, shell=False):
        def run():
            process = Popen(args=args,
                            stdout=PIPE if pipe else None,
                            stderr=PIPE if pipe_error else None,
                            shell=shell)
            stdout, stderr = process.communicate()
            self.__result__[0] = stdout.decode() if pipe else ''
            self.__result__[1] = stderr.decode() if pipe_error else ''

        self.join()
        self.__piped__ = pipe
        self.__joined__ = False
        self.__thread__ = Thread(target=run)
        self.__thread__.start()
