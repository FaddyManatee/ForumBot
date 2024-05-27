from requests.auth import HTTPBasicAuth
from discord import Member
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re
import requests


load_dotenv()


def get_most_recent_punishment(uuid: str, staff_list: list[Member]):
    record = requests.get("https://bans.shadowkingdom.org/history.php?uuid={}".format(uuid),
                           auth=HTTPBasicAuth(os.getenv("BANS_USER"), os.getenv("BANS_PASS")))

    soup = BeautifulSoup(record.content, "html.parser")
    punishments = soup.find_all("tr")

    # Only interested in the player's most recent ban/mute.
    for item in punishments:
        if "Kick" in item.text or "Warning" in item.text:
            punishments.remove(item)
    
    most_recent = punishments[0].find_all("td")
    moderator = most_recent[2].find("div").get_text()

    staff_member = None
    for member in staff_list:
        # Attempt to find the closest matching staff discord username from the IGN.
        if SequenceMatcher(None, re.sub(r"\s\(.*?\)", "", member.display_name), moderator).ratio() >= 0.5:
            staff_member = member
            break

    return {"type": most_recent[0].find("span").get_text(),
            "moderator": moderator,
            "mod_discord": staff_member,
            "reason": most_recent[3].get_text()}
