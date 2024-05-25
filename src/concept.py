from bs4 import BeautifulSoup
from datetime import datetime as dt
from dotenv import load_dotenv
from urllib.parse import urljoin
import os
import re
import requests

load_dotenv()

######################### GET URL FOR EACH THREAD ##############################
header = {"cookie": os.getenv("COOKIE")}
url = "https://shadowkingdom.org"
appeals_feed = requests.get("https://shadowkingdom.org/forum/view/21-ban-appeals/", headers=header)

soup = BeautifulSoup(appeals_feed.text, "html.parser")
elements = soup.find_all("a", class_="forum-link")

thread_links = []

for item in elements:
    thread_links.append(urljoin(url, item.get("href")))
################################################################################


####################### EXTRACT POSTS FROM A THREAD ############################
thread = requests.get(thread_links[0], headers=header)
soup = BeautifulSoup(thread.text, "html.parser")
posts = soup.find_all("div", attrs={"id": re.compile(r"post-\d+")})
# print(posts)
################################################################################


##################### EXTRACT DETAILS FROM A POST ##############################
soup_a = BeautifulSoup(str(posts[0]), "html.parser")
soup_b = BeautifulSoup(str(posts[1]), "html.parser")

# Post id.
id = re.search(r"post-\d+", str(soup_a)).group()
print(id.removeprefix("post-"))

# Author's name.
username = soup_a.find(class_="username")
print(username.get_text())

# Author's profile picture (default avatar).
avatar = soup_a.find(class_="avatar-img")
print(avatar.get("src").replace(" ", "%20"))

# Author's profile picture (custom avatar).
avatar = soup_b.find(class_="avatar-img")
print(urljoin(url, avatar.get("src")))

# DateTime posted.
time = soup_a.find("span", attrs={"data-toggle": "tooltip"})
print(dt.strptime(time.get("data-original-title"), "%d %b %Y, %H:%M"))

# Post content.
soup = BeautifulSoup(str(posts[1]), "html.parser")
content = soup.find(class_="forum-post-content")
print(re.sub('[\\n]+', '\\n\\n', content.get_text("\n")))
################################################################################
