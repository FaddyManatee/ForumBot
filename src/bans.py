from bs4 import BeautifulSoup
from discord import utils
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import json
import os
import requests


load_dotenv()


def _get_discord_id(ign):
    with open("staff.json", "r") as f:
        data = json.load(f)

    # Search for the IGN and return the corresponding Discord User ID.
    for staff_member in data["staff"]:
        if staff_member["ign"] == ign:
            return staff_member["discord"]
    
    return None


def get_most_recent_punishment(uuid: str):
    # Securely transmit credentials over HTTPS.
    record = requests.get("https://bans.shadowkingdom.org/history.php?uuid={}".format(uuid),
                           auth=HTTPBasicAuth(os.getenv("BANS_USER"), os.getenv("BANS_PASS")))

    soup = BeautifulSoup(record.content, "html.parser")
    punishments = soup.find_all("tr")

    # We are only interested in the player's most recent ban or mute.
    for item in punishments:
        if "Kick" in item.text or "Warning" in item.text:
            punishments.remove(item)
    
    most_recent = punishments[0].find_all("td")
    moderator = utils.escape_markdown(most_recent[2].find("div").get_text())
    
    return {
        "type": most_recent[0].find("span").get_text(),
        "moderator": moderator,
        "mod_discord": _get_discord_id(moderator),
        "reason": most_recent[3].get_text()
    }
