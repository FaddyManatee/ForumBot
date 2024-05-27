from skforum import *
import skparser


class Scraper:
    def __init__(self, cookie):
        self._last_threads = []
        self._threads = []
        self._new_threads = []
        self._cookie = { "cookie": cookie }


    def _fetch(self):
        self._last_threads.extend(self._threads)
        self._threads.clear()

        self._threads.append(skparser.parse_appeals())
        self._threads.append(skparser.parse_applications())
        # self._threads.append(skparser.parse_reports())


    def get_appeal_threads(self) -> list[Appeal]:
        return [thread for thread in self._threads if isinstance(thread, Appeal)]


    def get_application_threads(self) -> list[Application]:
        return [thread for thread in self._threads if isinstance(thread, Application)]
    

    def get_new_threads(self) -> list[Thread]:
        return self._new_threads


    def get_open_threads(self) -> list[Thread]:
        return self._threads


    def run(self) -> int:
        self._fetch()

        if len(self._threads) > len(self._last_threads):            
            self._new_threads.clear()
            for item in self._threads:
                if item not in self._last_threads:
                    self._new_threads.append(item)
            return len(self._threads) - len(self._last_threads)
        else:
            return 0
