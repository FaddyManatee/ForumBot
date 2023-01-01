# https://feedparser.readthedocs.io/en/latest/
import feedparser
import re
import requests
import html
from datetime import datetime as dt
from bs4 import BeautifulSoup


class FetchRss:
    _lastThreads = []
    _threads = []
    _newThreads = []

    def __init__(self, cookie, agent):
        self.cookie = {"cookie": cookie}

        # Three pages of interest
        self.serverFeed = feedparser.parse("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss", 
                                            request_headers=self.cookie)

        self.discordFeed = feedparser.parse("https://shadowkingdom.org/forums/discord-ban-mute-appeals.49.rss", 
                                             request_headers=self.cookie)

        self.staffappFeed = feedparser.parse("https://shadowkingdom.org/forums/staff-applications.43.rss")


    def _parse(self, content):
        # Remove HTML tags
        tags = r"<[^<]+?>"
        parsed = re.sub(tags, "", content)

        parsed = html.unescape(parsed)
        return parsed

    
    def _formatAuthor(self, author):
        author = author.lower()
        author = author.replace(" ", "-")
        return author


    # https://stackoverflow.com/a/48600278
    def _findNumber(self, text, c):
        return re.findall(r"%s(\d+)" % c, text)


    def _getAuthorID(self, soup, author):
        authors = soup.find_all(class_="username")
        
        author = self._formatAuthor(author)
        author = author + "."

        for entry in authors:
            if author in str(entry):
                id = self._findNumber(str(entry), ".")[0]
                return id


    def _getAuthorAvatar(self, soup):
        author_avatars = soup.find_all("img")
        author_avatars.remove(author_avatars[0])  # Remove hidden img avatar of auth user
        
        for entry in author_avatars:
            if "96" in str(entry):
                return "https://shadowkingdom.org/{}".format(entry["src"])


    def _getMod(self, content):
        # Get the input after the field about who made the punishment
        lines = iter(list(filter(None, content.splitlines())))
        for line in lines:
            if line.startswith("Staff member who issued your punishment:"):
                header = line.replace("Staff member who issued your punishment:", "").strip()

                # Try the next line if the data was not inline with header 
                if header.isspace() or len(header) == 0:
                    l = next(lines)
                    header = l.replace("Staff member who issued your punishment:", "").strip()
                    
                return header
        return None


    def _getPlayer(self, content, status):
        sentence = ""
        if status == "banned":
            sentence = "Your in-game name:"
        elif status == "applying":
            sentence = "Your current IGN:"

        # Get the input after the field about who was punished
        lines = iter(list(filter(None, content.splitlines())))
        for line in lines:
            if line.startswith(sentence):
                header = line.replace(sentence, "").strip()

                # Try the next line if the data was not inline with header 
                if header.isspace() or len(header) == 0:
                    l = next(lines)
                    header = l.replace(sentence, "").strip()

                return header
        return None


    def _fetch(self):
        self._lastThreads.extend(self._threads)
        self._threads.clear()

        for item in self.serverFeed.entries:
            thread = requests.get(item.id, cookies=self.cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = self._parse(content)

            self._threads.append({"link": item.id,
                                  "type": "server-appeal",
                                  "title": item.title,
                                  "author_id": self._getAuthorID(soup, item.author),
                                  "author": item.author,
                                  "author_formatted": self._formatAuthor(item.author),
                                  "author_avatar": self._getAuthorAvatar(soup),
                                  "time": dt.strptime(item.published[:-6], "%a, %d %b %Y %H:%M:%S"),
                                  "player": self._getPlayer(content, "banned"),
                                  "moderator": self._getMod(content),
                                  "content": content
                                })

        for item in self.discordFeed.entries:
            thread = requests.get(item.id, cookies=self.cookie)
            soup = BeautifulSoup(thread.content, "html.parser")
            content = str(soup.find("blockquote"))
            content = self._parse(content)

            self._threads.append({"link": item.id,
                                  "type": "discord-appeal",
                                  "title": item.title,
                                  "author_id": self._getAuthorID(soup, item.author),
                                  "author": item.author,
                                  "author_formatted": self._formatAuthor(item.author),
                                  "author_avatar": self._getAuthorAvatar(soup),
                                  "time": dt.strptime(item.published[:-6], "%a, %d %b %Y %H:%M:%S"),
                                  "player": self._getPlayer(content, "banned"),
                                  "content": content
                                })

        # Skipping the first thread/entry in staff applications. It is a guide
        post = 0
        for item in self.staffappFeed.entries:
            if post != 0:
                thread = requests.get(item.id, cookies=self.cookie)
                soup = BeautifulSoup(thread.content, "html.parser")
                content = str(soup.find("blockquote"))
                content = self._parse(content)

                self._threads.append({"link": item.id,
                                      "type": "staff-app",
                                      "title": item.title,
                                      "author_id": self._getAuthorID(soup, item.author),
                                      "author": item.author,
                                      "author_formatted": self._formatAuthor(item.author),
                                      "author_avatar": self._getAuthorAvatar(soup),
                                      "time": dt.strptime(item.published[:-6], "%a, %d %b %Y %H:%M:%S"),
                                      "player": self._getPlayer(content, "applying"),
                                      "content": content
                                    })
            post += 1

    
    def getServerThreads(self):
        return [thread for thread in self._threads if thread["type"] == "server-appeal"]


    def getDiscordThreads(self):
        return [thread for thread in self._threads if thread["type"] == "discord-appeal"]


    def getApplicationThreads(self):
        return [thread for thread in self._threads if thread["type"] == "staff-app"]

    
    def getNewThreads(self):
        return self._newThreads


    def getOpenThreads(self):
        return self._threads


    def run(self):
        self._fetch()

        if len(self._threads) > len(self._lastThreads):            
            self._newThreads.clear()
            for item in self._threads:
                if item not in self._lastThreads:
                    self._newThreads.append(item)
            return len(self._threads) - len(self._lastThreads)
        else:
            return 0
