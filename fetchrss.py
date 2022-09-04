# https://feedparser.readthedocs.io/en/latest/
import feedparser
import re
import html
from copy import deepcopy


class FetchRss:
    _lastThreads = []
    threads = []
    newThreads = []

    def __init__(self, cookies):
        self.headers = {"cookie":cookies}

        # Three pages of interest
        self.serverFeed = feedparser.parse("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss", 
                                            request_headers=self.headers)

        self.discordFeed = feedparser.parse("https://shadowkingdom.org/forums/discord-ban-mute-appeals.49.rss", 
                                             request_headers=self.headers)

        self.staffappFeed = feedparser.parse("https://shadowkingdom.org/forums/staff-applications.43.rss")


    def _parse(self, title, content):
        # Remove HTML tags
        tags = r"<[^<]+?>"
        parsed = re.sub(tags, "", content)

        # Remove title suffix in content
        parsed = parsed.replace("\n\n" + title, "")
        return parsed


    def _getMod(self, content):
        # Remove HTML tags
        tags = r"<[^<]+?>"
        parsed = re.sub(tags, "", content)

        # Unescape any HTML escaped characters
        parsed = html.unescape(parsed)

        # Get the input after the field about who made the punishment
        lines = list(filter(None, parsed.splitlines()))
        for line in lines:
            if line.startswith("Staff member who issued your punishment:"):
                return line.replace("Staff member who issued your punishment:", "").strip()


    def _getThreads(self):
        # Get difference between the threads fetched now and previously to tell what is new
        self._lastThreads = deepcopy(self.threads)

        for item in self.serverFeed.entries:
            self.threads.append({"link":item.id,
                                 "type":"server-appeal",
                                 "title":item.title,
                                 "author":item.author,
                                 "date":item.published,
                                 "moderator":self._getMod(item.content[0].get("value")),
                                 "content":self._parse(item.title, item.content[0].get("value"))
                                })

        for item in self.discordFeed.entries:
            self.threads.append({"link":item.id,
                                 "type":"discord-appeal",
                                 "title":item.title,
                                 "author":item.author,
                                 "date":item.published,
                                 "content":self._parse(item.title, item.content[0].get("value"))
                                })

        # Skipping the first thread/entry in staff applications. It is a guide
        post = 0
        for item in self.staffappFeed.entries:
            if post != 0:
                self.threads.append({"link":item.id,
                                     "type":"staff-app",
                                     "title":item.title,
                                     "author":item.author,
                                     "date":item.published,
                                     "content":self._parse(item.title, item.content[0].get("value"))
                                    })
            post += 1


    def run(self):
        self._getThreads()

        if len(self.threads) > len(self._lastThreads):            
            self.newThreads.clear()
            for item in self.threads:
                if item not in self._lastThreads:
                    self.newThreads.append(item)
            return len(self.threads) - len(self._lastThreads)
        else:
            return 0
