from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime as dt
from discord import Embed, Member, utils, Color
from math import floor
from skbans import get_most_recent_punishment
import requests


class ReportType(Enum):
    Player = 1
    Staff  = 2
    Bug    = 3


class Post:
    def __init__(self,
                 id: str,                      # ID of post.
                 content: str,                 # Post content.
                 author: str,                  # Name of post author.
                 author_url: str,              # URL for author's page.
                 avatar: str,                  # URL for author's avatar.
                 time: dt) -> None:            # Date and time when published.
        
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
                 url: str,                      # URL to thread.
                 title: str,                    # Title of thread.
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

        # Set the embed thumbnail to the author's player head.
        # thumb = requests.get("https://minotar.net/helm/{}.png".format(ign))

        # if thumb.status_code != 200:
        #     # Display fallback player image.
        #     self._embed.set_thumbnail("https://i.postimg.cc/PfgQtxvC/unknown-ign.png")
        # else:
        #     self._embed.set_thumbnail(url=thumb.url)
        
        # self._embed.add_field(name="Player", value=utils.escape_markdown(self._ign))
        self._embed.set_footer(text=posts[0].time_elapsed())


    @abstractmethod
    def to_embed(self) -> tuple[Embed, Member]:
        pass


    def get_url(self) -> str:
        return self._url
    

    def get_title(self) -> str:
        return self._title
    

    def get_posts(self) -> list[Post]:
        return self._posts


class Application(Thread):
    def __init__(self, 
                 url: str, 
                 title: str,
                 posts: list[Post]) -> None:
        super().__init__(url, title, posts)


    def to_embed(self) -> tuple[Embed, Member]:
        self._embed.description = "Staff application\n[Click here to view]( {} )".format(self._url)
        self._embed.color = Color.from_str("#00f343")
        return (self._embed, None)


class Appeal(Thread):
    def __init__(self, 
                 url: str, 
                 title: str,
                 posts: list[Post]) -> None:
        super().__init__(url, title, posts)


    def to_embed(self, members: list[Member]) -> tuple[Embed, Member]:        
        self._embed.description = "Punishment appeal\n[Click here to view]( {} )".format(self._url)
        self._embed.color = Color.from_str("#ff2828")

        # Get the punished player's uuid to find their most recent punishment.
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(self._ign)).json()["id"]
        punishment = get_most_recent_punishment(uuid, members)

        self._embed.add_field(name="Staff member", value=utils.escape_markdown(punishment["moderator"]))
        self._embed.add_field(name="Punishment", value=punishment["type"])
        self._embed.add_field(name="Reason", value=punishment["reason"], inline=False)
        return (self._embed, punishment["mod_discord"])
