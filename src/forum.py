"""
forum.py

Describes the structure of forum related objects that appear on shadowkingdom.org

Threads (of types: Application, Appeal, and Report)
Posts
"""


from abc import ABC, abstractmethod
from datetime import datetime as dt
from discord import Embed, Color
from enum import Enum
from math import floor
import requests

import bans


class ReportType(Enum):
    PLAYER  = 1
    STAFF   = 2
    BUG     = 3


class Post:
    def __init__(self,
                 id: str,                      # ID of the post.
                 content: str,                 # Post content.
                 author: str,                  # Name of the post author.
                 author_url: str,              # URL for author's page.
                 avatar: str,                  # URL for author's avatar.
                 time: dt) -> None:            # Date and time when post was published.
        
        self._id         = id
        self._content    = content
        self._author     = author
        self._author_url = author_url
        self._avatar     = avatar
        self._time       = time


    # def __str__(self) -> str:
    #     return super().__str__()


    def get_id(self) -> str:
        return self._id


    def get_content(self) -> str:
        return self._content
    

    def get_author(self) -> str:
        return self._author
    

    def get_author_URL(self) -> str:
        return self._author_url
    

    def get_author_avatar(self) -> str:
        return self._avatar
    

    def get_time_published(self) -> dt:
        return self._time


    # Calculates the time elapsed between now and the time the post was published.
    def time_elapsed(self) -> str:
        hours_elapsed = (dt.now() - self._time).total_seconds() / 3600

        if hours_elapsed >= 24:
            return str(floor(hours_elapsed / 24)) + " days ago"
        
        elif hours_elapsed < 1:
            return str(floor(hours_elapsed * 60)) + " minutes ago"

        else:
            return str(round(hours_elapsed, 1)) + " hours ago"


class Thread(ABC):
    def __init__(self,
                 url: str,                      # URL of the thread.
                 title: str,                    # Title of the thread.
                 posts: list[Post]) -> None:    # List of posts in the thread.
        
        self._url = url
        self._title = title
        self._posts = posts
        
        # Create base embed.
        self._embed = Embed(title=self._title)

        # Set thread author details (name, avatar, URL to author's profile).
        self._embed.set_author(name=posts[0].get_author(),
                               icon_url=posts[0].get_author_avatar(),
                               url=posts[0].get_author_URL())

        self._embed.set_footer(text=posts[0].time_elapsed())


    @abstractmethod
    def to_embed(self) -> Embed:
        pass


    def get_url(self) -> str:
        return self._url
    

    def get_title(self) -> str:
        return self._title
    

    def get_posts(self) -> list[Post]:
        return self._posts


class Application(Thread):
    def __init__(self, url: str, title: str, posts: list[Post]) -> None:
        super().__init__(url, title, posts)


    def to_embed(self) -> Embed:
        self._embed.description = "Staff Application\n[Click here to view]({})".format(self._url)
        self._embed.color = Color.from_str("#00f343")
        return (self._embed, None)


class Appeal(Thread):
    def __init__(self, url: str, title: str, posts: list[Post], ign: str) -> None:
        super().__init__(url, title, posts)
        self._ign = ign

        # Get the punished player's uuid to find their most recent punishment.
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(self._ign)).json()["id"]
        self._punishment = bans.get_most_recent_punishment(uuid)
        self._moderator = "<@{}>".format(self._punishment["mod_discord"])

    
    def get_moderator(self) -> str:
        return self._moderator


    def to_embed(self) -> Embed:        
        self._embed.description = "Punishment Appeal\n[Click here to view]({})".format(self._url)
        self._embed.color = Color.from_str("#ff2828")
        
        self._embed.add_field(name="Moderator", value=self._punishment["moderator"])
        self._embed.add_field(name="Punishment", value=self._punishment["type"])
        self._embed.add_field(name="Reason", value=self._punishment["reason"], inline=False)
        return self._embed
    

class Report(Thread):
    def __init__(self, url: str, title: str, posts: list[Post], report_type: ReportType) -> None:
        super().__init__(url, title, posts)
        self._type = report_type


    def to_embed(self) -> Embed:
        self._embed.description = "{} Report\n[Click here to view]({})".format(self._type.name.lower().capitalize(), self._url)
        self._embed.color = Color.from_str("#00f343")
        return self._embed
