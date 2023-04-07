# https://feedparser.readthedocs.io/en/latest/
import feedparser
import re
import requests
import html
from bs4 import BeautifulSoup
from threads import Thread, Application, Appeal, AppealType


def _parse(content):
    # Remove HTML tags
    tags = r"<[^<]+?>"
    parsed = re.sub(tags, "", content)

    parsed = html.unescape(parsed)
    return parsed


# https://stackoverflow.com/a/48600278
def _find_number(text, c):
    return re.findall(r"%s(\d+)" % c, text)


def _format_author(author):
    author = author.lower()
    author = author.replace(" ", "-")
    return author


def _get_author_avatar(soup):
    author_avatars = soup.find_all("img")
    author_avatars.remove(author_avatars[0])  # Remove hidden img avatar of auth user
    
    for entry in author_avatars:
        # All avatar images have dimensions 96x96.
        if "96" in str(entry):
            return "https://shadowkingdom.org/{}".format(entry["src"])


def _get_player(content, prefix):
    # Get the input after the field about who is making the report
    lines = iter(list(filter(None, content.splitlines())))
    for line in lines:
        if line.startswith(prefix):
            header = line.replace(prefix, "").strip()

            # Try the next line if the data was not inline with header 
            if header.isspace() or len(header) == 0:
                l = next(lines)
                header = l.replace(prefix, "").strip()

            return header
    return "N/A"


def _get_author_id(soup, author):
    authors = soup.find_all(class_="username")
    
    author = _format_author(author)
    author = author + "."

    for entry in authors:
        if author in str(entry):
            id = _find_number(str(entry), ".")[0]
            return id


class FetchRss:
    def __init__(self, cookie):
        self._last_threads = []
        self._threads = []
        self._new_threads = []

        self._cookie = {"cookie": cookie}

        # Three pages of interest
        self._server_feed = feedparser.parse("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss", 
                                              request_headers=self._cookie)

        self._discord_feed = feedparser.parse("https://shadowkingdom.org/forums/discord-ban-mute-appeals.49.rss", 
                                               request_headers=self._cookie)
        
        self._staffapp_feed = feedparser.parse("https://shadowkingdom.org/forums/staff-applications.43.rss")

        # self._player_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-player.10.rss", 
        #                                              request_headers=self._cookie)

        # self._staff_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-staff.45.rss", 
        #                                             request_headers=self._cookie)

        # self._bug_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-staff.45.rss", 
        #                                           request_headers=self._cookie)


    def _fetch(self):
        self._last_threads.extend(self._threads)
        self._threads.clear()

        for item in self._server_feed.entries:
            thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = _parse(content)

            self._threads.append(
                Appeal(thread.url, 
                       item.title, 
                       AppealType.Server, 
                       _get_author_id(soup, item.author), 
                       item.author, 
                       _format_author(item.author), 
                       _get_author_avatar(soup), 
                       _get_player(content, "Your in-game name:"), 
                       content, 
                       item.published))

        for item in self._discord_feed.entries:
            thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = _parse(content)

            self._threads.append(
                Appeal(thread.url, 
                       item.title, 
                       AppealType.Discord, 
                       _get_author_id(soup, item.author), 
                       item.author, 
                       _format_author(item.author), 
                       _get_author_avatar(soup), 
                       _get_player(content, "Your discord name (example#1111):"), 
                       content, 
                       item.published))

        # Skipping the first thread/entry in staff applications. It is a guide
        post = 0
        for item in self._staffapp_feed.entries:
            if post != 0:
                thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
                soup = BeautifulSoup(thread.content, "html.parser")
                content = str(soup.find("blockquote"))
                content = self._parse(content)

                self._threads.append(
                    Application(thread.url, 
                                item.title, 
                                _get_author_id(soup, item.author), 
                                item.author, 
                                _format_author(item.author), 
                                _get_author_avatar(soup), 
                                _get_player(content, "Your current IGN:"), 
                                content, 
                                item.published))
            post += 1

    
    def get_appeal_threads(self) -> list[Appeal]:
        return [thread for thread in self._threads if isinstance(thread, Appeal)]


    def get_application_threads(self) -> list[Application]:
        return [thread for thread in self._threads if isinstance(thread, Application)]


    # def get_report_threads(self):
    #     return [thread for thread in self._threads if "report" in thread["type"]]

    
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
