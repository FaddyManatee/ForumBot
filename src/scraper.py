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
        self._current_threads = []
        self._new_threads = []
        self._new_posts = {}
        self._cookie = { "cookie": cookie }


    def _find_new_posts(self, thread_history):
        self._new_posts.clear()

        # Compare the number of posts for each thread between the previous scan and the current scan.
        for url, thread_versions in thread_history.items():
            if len(thread_versions) == 1:
                continue

            # Calculate the difference in the number of posts.
            diff = len(thread_versions[1].get_posts()) - len(thread_versions[0].get_posts())

            if diff <= 0:
                continue

            # Extract the new post objects.
            previous_posts = thread_versions[0].get_posts()
            current_posts = thread_versions[1].get_posts()

            # The new posts are those that exist in the current version but not in the previous version.
            new_posts = current_posts[len(previous_posts):]

            # Add the new posts to the dictionary under the thread they appeared in.
            self._new_posts[thread_versions[1]] = new_posts


    def _read_forum(self):
        self._last_threads = self._current_threads.copy()
        self._current_threads.clear()
        self._new_threads.clear()

        self._current_threads.extend(parser.get_appeals())
        self._current_threads.extend(parser.get_applications())
        self._current_threads.extend(parser.get_reports())

        # Group previous and current thread objects by common URL.
        grouped_by_url = {}

        for item in self._last_threads + self._current_threads:
            if item.get_url() not in grouped_by_url:
                grouped_by_url[item.get_url()] = []
            grouped_by_url[item.get_url()].append(item)

        new_items = []

        # URLs associated with a single thread object must be new threads.
        for url, items in grouped_by_url.items():
            if len(items) == 1:
                new_items.append(items[0])

        if len(new_items) > 0: 
            self._new_threads.extend(new_items)

        self._find_new_posts(grouped_by_url)


    def get_new_posts(self) -> dict[forum.Thread, list[forum.Post]]:
        return self._new_posts


    def get_appeal_threads(self) -> list[forum.Appeal]:
        return [thread for thread in self._current_threads if isinstance(thread, forum.Appeal)]


    def get_application_threads(self) -> list[forum.Application]:
        return [thread for thread in self._current_threads if isinstance(thread, forum.Application)]
    

    def get_report_threads(self) -> list[forum.Report]:
        return [thread for thread in self._current_threads if isinstance(thread, forum.Report)]
    

    def get_new_appeal_threads(self) -> list[forum.Appeal]:
        return [thread for thread in self._new_threads if isinstance(thread, forum.Appeal)]
    

    def get_new_application_threads(self) -> list[forum.Application]:
        return [thread for thread in self._new_threads if isinstance(thread, forum.Application)]


    def get_new_report_threads(self) -> list[forum.Report]:
        return [thread for thread in self._current_threads if isinstance(thread, forum.Report)]


    def get_all_threads(self) -> list[forum.Thread]:
        return self._current_threads


    def run(self) -> tuple[int, int]:
        self._read_forum()

        # Return number of new threads and posts found.
        return (len(self._new_threads), len(self._new_posts))
