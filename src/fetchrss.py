# https://feedparser.readthedocs.io/en/latest/
import feedparser
import re
import requests
import html
from math import floor
from datetime import datetime as dt
from bs4 import BeautifulSoup


class FetchRss:
    _last_threads = []
    _threads = []
    _new_threads = []

    def __init__(self, cookie):
        self._cookie = {"cookie": cookie}

        # Three pages of interest
        self._server_feed = feedparser.parse("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss", 
                                             request_headers=self._cookie)

        self._discord_feed = feedparser.parse("https://shadowkingdom.org/forums/discord-ban-mute-appeals.49.rss", 
                                              request_headers=self._cookie)

        self._player_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-player.10.rss", 
                                                    request_headers=self._cookie)

        self._staff_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-staff.45.rss", 
                                                   request_headers=self._cookie)

        self._bug_report_feed = feedparser.parse("https://shadowkingdom.org/forums/report-a-staff.45.rss", 
                                                 request_headers=self._cookie)

        self._staffapp_feed = feedparser.parse("https://shadowkingdom.org/forums/staff-applications.43.rss")


    def _parse(self, content):
        # Remove HTML tags
        tags = r"<[^<]+?>"
        parsed = re.sub(tags, "", content)

        parsed = html.unescape(parsed)
        return parsed

    
    def _format_author(self, author):
        author = author.lower()
        author = author.replace(" ", "-")
        return author


    # https://stackoverflow.com/a/48600278
    def _find_number(self, text, c):
        return re.findall(r"%s(\d+)" % c, text)


    def _get_author_id(self, soup, author):
        authors = soup.find_all(class_="username")
        
        author = self._format_author(author)
        author = author + "."

        for entry in authors:
            if author in str(entry):
                id = self._find_number(str(entry), ".")[0]
                return id


    def _get_author_avatar(self, soup):
        author_avatars = soup.find_all("img")
        author_avatars.remove(author_avatars[0])  # Remove hidden img avatar of auth user
        
        for entry in author_avatars:
            if "96" in str(entry):
                return "https://shadowkingdom.org/{}".format(entry["src"])


    def _get_player(self, content, prefix):
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
        return None


    def _get_datetime(self, time_string):
        # Remove timezone information and get time object from string.
        datetime = dt.strptime(time_string[:-6], "%a, %d %b %Y %H:%M:%S")
        return datetime


    def _fetch(self):
        self._last_threads.extend(self._threads)
        self._threads.clear()

        for item in self._server_feed.entries:
            thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = self._parse(content)

            self._threads.append({"link": thread.url,
                                  "type": "server-appeal",
                                  "title": item.title,
                                  "author_id": self._get_author_id(soup, item.author),
                                  "author": item.author,
                                  "author_formatted": self._format_author(item.author),
                                  "author_avatar": self._get_author_avatar(soup),
                                  "time": self._get_datetime(item.published),
                                  "player": self._get_player(content, "Your in-game name:"),
                                  "content": content
                                })

        for item in self._discord_feed.entries:
            thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = self._parse(content)

            self._threads.append({"link": thread.url,
                                  "type": "discord-appeal",
                                  "title": item.title,
                                  "author_id": self._get_author_id(soup, item.author),
                                  "author": item.author,
                                  "author_formatted": self._format_author(item.author),
                                  "author_avatar": self._get_author_avatar(soup),
                                  "time": self._get_datetime(item.published),
                                  "player": self._get_player(content, "Your discord name (example#1111):"),
                                  "content": content
                                })

        # for item in self._player_report_feed.entries:
        #     thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
        #     soup = BeautifulSoup(thread.content, "html.parser")
        #     content = str(soup.find("blockquote"))
        #     content = self._parse(content)

        #     self._threads.append({"link": thread.url,
        #                           "type": "player-report",
        #                           "title": item.title,
        #                           "author_id": self._get_author_id(soup, item.author),
        #                           "author": item.author,
        #                           "author_formatted": self._format_author(item.author),
        #                           "author_avatar": self._get_author_avatar(soup),
        #                           "time": self._get_datetime(item.published),
        #                           "player": self._get_player(content, "Your name (In game/Discord/Forum):"),
        #                           "content": content
        #                         })

        # Skipping the first thread/entry in staff applications. It is a guide
        post = 0
        for item in self._staffapp_feed.entries:
            if post != 0:
                thread = requests.get(item.id.replace("http", "https"), cookies=self._cookie)
                soup = BeautifulSoup(thread.content, "html.parser")
                content = str(soup.find("blockquote"))
                content = self._parse(content)

                self._threads.append({"link": thread.url,
                                      "type": "staff-app",
                                      "title": item.title,
                                      "author_id": self._get_author_id(soup, item.author),
                                      "author": item.author,
                                      "author_formatted": self._format_author(item.author),
                                      "author_avatar": self._get_author_avatar(soup),
                                      "time": self._get_datetime(item.published),
                                      "player": self._get_player(content, "Your current IGN:"),
                                      "content": content
                                    })
            post += 1

    
    def get_appeal_threads(self):
        return [thread for thread in self._threads if "appeal" in thread["type"]]


    def get_application_threads(self):
        return [thread for thread in self._threads if thread["type"] == "staff-app"]


    def get_report_threads(self):
        return [thread for thread in self._threads if "report" in thread["type"]]

    
    def get_new_threads(self):
        return self._new_threads


    def get_open_threads(self):
        return self._threads


    def run(self):
        self._fetch()

        if len(self._threads) > len(self._last_threads):            
            self._new_threads.clear()
            for item in self._threads:
                if item not in self._last_threads:
                    self._new_threads.append(item)
            return len(self._threads) - len(self._last_threads)
        else:
            return 0


# Calculate the time elapsed since a thread was posted.
def time_elapsed(thread):
    hours_elapsed = (dt.now() - thread["time"]).total_seconds() / 3600

    if hours_elapsed >= 24:
        return str(floor(hours_elapsed / 24)) + " days ago"
    
    elif hours_elapsed < 1:
        return str(floor(hours_elapsed * 60)) + " minutes ago"

    else:
        return str(round(hours_elapsed, 1)) + " hours ago"
