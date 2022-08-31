# https://pypi.org/project/rss-parser/
import os
import feedparser
from dotenv import load_dotenv


load_dotenv()

# If bot stops working, check if cookies in .env need updating first
headers = {"cookie":os.getenv("COOKIES")}

server_feed = feedparser.parse("https://shadowkingdom.org/forums/ban-mute-appeals.15.rss", 
                  request_headers=headers)

discord_feed = feedparser.parse("https://shadowkingdom.org/forums/discord-ban-mute-appeals.49.rss", 
                  request_headers=headers)

appeals = []

for item in server_feed.entries:
    appeals.append({"author":item.author,
                    "link":item.id})

for item in discord_feed.entries:
    appeals.append({"author":item.author,
                    "link":item.id})

print(appeals)
