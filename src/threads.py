import requests
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime as dt
from discord import Embed, Member, utils, Color
from skbans import get_most_recent_punishment
from math import floor


class AppealType(Enum):
    Server  = 1
    Discord = 2


class ReportType(Enum):
    Player = 1
    Staff  = 2


class GameMode(Enum):
    Towny    = 1
    Creative = 2


class Thread(ABC):
    def __init__(self, 
                 link: str, 
                 title: str, 
                 author_id: str, 
                 author_raw: str,
                 author_http: str, 
                 avatar: str, 
                 player: str, 
                 content: str, 
                 time_posted: str) -> None:
        
        self._link = link
        self._title = title
        self._author_id = author_id
        self._author_raw = author_raw
        self._author_http = author_http
        self._author_avatar = avatar
        self._player = player
        self._content = content
        self._time_posted = self._set_time_posted(time_posted)
        
        # Create base embed.
        self._embed = Embed(title=self._title)

        # Use another image if the avatar is a default xenforo avatar.
        if "xenforo" in avatar:
            self._embed.set_author(name=author_raw,
                                   icon_url="https://i.postimg.cc/cJQnqTsS/unknown.jpg".format(self._player),
                                   url="https://shadowkingdom.org/members/{}.{}/".format(
                                      self._author_http,
                                      author_id))
        else:
            self._embed.set_author(name=author_raw,
                                   icon_url=avatar,
                                   url="https://shadowkingdom.org/members/{}.{}/".format(
                                       self._author_http,
                                       author_id))

        # Set the embed thumbnail to the thread author's player head.
        thumb = requests.get("https://minotar.net/helm/{}.png".format(player))

        if thumb.status_code != 200:
            # Display fallback player image.
            self._embed.set_thumbnail("https://i.postimg.cc/PfgQtxvC/unknown-ign.png")
        else:
            self._embed.set_thumbnail(url=thumb.url)
        
        self._embed.add_field(name="Player", value=utils.escape_markdown(player))
        self._embed.set_footer(text=self._time_elapsed())

    @abstractmethod
    def to_embed(self) -> tuple[Embed, Member]:
        pass

    # Calculate the time elapsed since a thread was posted.
    def _time_elapsed(self):
        hours_elapsed = (dt.now() - self._time_posted).total_seconds() / 3600

        if hours_elapsed >= 24:
            return str(floor(hours_elapsed / 24)) + " days ago"
        
        elif hours_elapsed < 1:
            return str(floor(hours_elapsed * 60)) + " minutes ago"

        else:
            return str(round(hours_elapsed, 1)) + " hours ago"

    def _set_time_posted(self, time_string):
        # Remove timezone information and get time object from string.
        datetime = dt.strptime(time_string[:-6], "%a, %d %b %Y %H:%M:%S")
        return datetime


class Application(Thread):
    def __init__(self, 
                 link: str, 
                 title: str, 
                 author_id: str, author_raw: str, author_http: str, avatar: str, player: str,
                 content: str,
                 time_posted: str) -> None:
        super().__init__(link, title, author_id, author_raw, author_http, avatar, player, content, time_posted)

    def to_embed(self) -> tuple[Embed, Member]:
        self._embed.description = "Staff application\n[Click here to view]( {} )".format(self._link)
        self._embed.color = Color.from_str("#00f343")
        return (self._embed, None)


class Appeal(Thread):
    def __init__(self, 
                 link: str, 
                 title: str,
                 type: AppealType,
                 author_id: str, author_raw: str, author_http: str, avatar: str, player: str,
                 content: str, 
                 time_posted: str) -> None:
        super().__init__(link, title, author_id, author_raw, author_http, avatar, player, content, time_posted)
        self._type = type

    def to_embed(self, members: list[Member]) -> tuple[Embed, Member]:
        match self._type:
            case AppealType.Server:
                self._embed.description = "Server punishment appeal\n[Click here to view]( {} )".format(self._link)
            case AppealType.Discord:
                self._embed.description = "Discord punishment appeal\n[Click here to view]( {} )".format(self._link)
        
        self._embed.description = "Server punishment appeal\n[Click here to view]( {} )".format(self._link)
        self._embed.color = Color.from_str("#ff2828")

        # Get the punished player's uuid to find their most recent punishment.
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/{}".format(self._player)).json()["id"]
        punishment = get_most_recent_punishment(uuid, members)

        self._embed.add_field(name="Staff member", value=utils.escape_markdown(punishment["moderator"]))
        self._embed.add_field(name="Punishment", value=punishment["type"])
        self._embed.add_field(name="Reason", value=punishment["reason"], inline=False)
        return (self._embed, punishment["mod_discord"])


class PlayerReport(Thread):
    def __init__(self, 
                 link: str, 
                 title: str,
                 type: ReportType,
                 defendant: str,
                 author_id: str, author_raw: str, author_http: str, avatar: str, player: str,
                 content: str, 
                 time_posted: str) -> None:
        super().__init__(link, title, author_id, author_raw, author_http, avatar, player, content, time_posted)
        self._type = type
        self._defendant = defendant


class BugReport(Thread):
    def __init__(self, 
                 link: str, 
                 title: str, 
                 author: str, author_id: str, avatar: str, player: str, 
                 mode: GameMode, 
                 content: str, 
                 time_posted: str) -> None:
        super().__init__(link, title, author, author_id, avatar, player, content, time_posted)
        self._mode = mode
