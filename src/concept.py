from bs4 import BeautifulSoup
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
print(posts)
################################################################################
