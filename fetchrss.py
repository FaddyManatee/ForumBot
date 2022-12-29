# https://feedparser.readthedocs.io/en/latest/
import feedparser
import re
import html


class FetchRss:
    _lastThreads = []
    _threads = []
    _newThreads = []

    def __init__(self, cookies):
        self.headers = {"cookie": cookies}

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


    def _formatThreads(self):
        self._lastThreads.extend(self._threads)
        self._threads.clear()

        for item in self.serverFeed.entries:
            self._threads.append({"link": item.id,
                                  "type": "server-appeal",
                                  "title": item.title,
                                  "author": item.author,
                                  "date": item.published,
                                  "moderator": self._getMod(item.content[0].get("value")),
                                  "content": self._parse(item.title, item.content[0].get("value"))
                                })

        for item in self.discordFeed.entries:
            self._threads.append({"link": item.id,
                                  "type": "discord-appeal",
                                  "title": item.title,
                                  "author": item.author,
                                  "date": item.published,
                                  "content": self._parse(item.title, item.content[0].get("value"))
                                })

        # Skipping the first thread/entry in staff applications. It is a guide
        post = 0
        for item in self.staffappFeed.entries:
            if post != 0:
                self._threads.append({"link": item.id,
                                      "type": "staff-app",
                                      "title": item.title,
                                      "author": item.author,
                                      "date": item.published,
                                      "content": self._parse(item.title, item.content[0].get("value"))
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
        self._formatThreads()

        if len(self._threads) > len(self._lastThreads):            
            self._newThreads.clear()
            for item in self._threads:
                if item not in self._lastThreads:
                    self._newThreads.append(item)
            return len(self._threads) - len(self._lastThreads)
        else:
            return 0
