"""
scraper.py 

Implements the Scraper class

A Scraper object is used to monitor shadowkingdom.org for new forum
activity by periodically calling method run()
"""


import forum
import parser


class Scraper:
    def __init__(self, cookie):
        self._last_threads = []
        self._threads = []
        self._new_threads = []
        self._cookie = { "cookie": cookie }


    def _fetch(self):
        self._last_threads.extend(self._threads)
        self._threads.clear()

        self._threads.extend(parser.get_appeals())
        self._threads.extend(parser.get_applications())
        self._threads.extend(parser.get_reports())


    def get_appeal_threads(self) -> list[forum.Appeal]:
        return [thread for thread in self._threads if isinstance(thread, forum.Appeal)]


    def get_application_threads(self) -> list[forum.Application]:
        return [thread for thread in self._threads if isinstance(thread, forum.Application)]
    

    def get_new_threads(self) -> list[forum.Thread]:
        return self._new_threads


    def get_open_threads(self) -> list[forum.Thread]:
        return self._threads


    def run(self) -> int:
        self._fetch()

        # Only scrape the forum if there are new posts.
        if len(self._threads) > len(self._last_threads):            
            self._new_threads.clear()
            for item in self._threads:
                if item not in self._last_threads:
                    self._new_threads.append(item)
            return len(self._threads) - len(self._last_threads)
        else:
            return 0
