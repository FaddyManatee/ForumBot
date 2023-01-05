import os
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()


def get_most_recent_punishment(uuid):
    record = requests.get("https://bans.shadowkingdom.org/history.php?uuid={}".format(uuid),
                           auth=HTTPBasicAuth(os.getenv("SK_USER"), os.getenv("SK_PASS")))

    soup = BeautifulSoup(record.content, "html.parser")
    punishments = soup.find_all("tr")

    for item in punishments:
        if "Kick" in item.text or "Warning" in item.text:
            punishments.remove(item)
    
    most_recent = punishments[0].find_all("td")

    return {"type": most_recent[0].find("span").get_text(),
            "moderator": most_recent[2].find("div").get_text(),
            "reason": most_recent[3].get_text()}
