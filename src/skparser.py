from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin
from skforum import *
import os
import re
import requests


load_dotenv()
header = { "cookie": os.getenv("COOKIE") }
URL = "https://shadowkingdom.org"


############################ APPEAL THREADS + POSTS ############################
def parse_appeals() -> list[Appeal]:
    feed = requests.get("https://shadowkingdom.org/forum/view/21-ban-appeals/", headers=header) 

    soup = BeautifulSoup(feed.text, "html.parser")
    elements = soup.find_all(class_="forum-link")

    threads = []

    for item in elements:
        url = urljoin(URL, item.get("href"))
        threads.append(_appeal_thread(url))
    
    return threads


def _appeal_thread(url):
    thread = requests.get(url, headers=header)
    soup = BeautifulSoup(thread.text, "html.parser")
    title = soup.find(class_="forum-topic-title")
    posts_raw = soup.find_all("div", attrs={ "id": re.compile(r"post-\d+") })

    posts = []

    for item in posts_raw:
        posts.append(_appeal_post(item))

    return Appeal(url, title.get_text().strip(), posts)


def _appeal_post(p):
    soup = BeautifulSoup(str(p), "html.parser")
    id = re.search(r"post-\d+", str(soup)).group()
    # id = id.removeprefix("post-")

    content = soup.find(class_="forum-post-content")
    content = re.sub('[\\n]+', '\\n\\n', content.get_text("\n"))

    author = soup.find(class_="username")
    author_url = urljoin(URL, author.get("href"))

    # Author's profile picture.
    avatar = soup.find(class_="avatar-img").get("src")
    if "dicebear" in avatar:
        avatar = avatar.replace(" ", "%20")
    else:
        avatar = urljoin(URL, soup.find(class_="avatar-img").get("src"))
    
    time = soup.find("span", attrs={"data-toggle": "tooltip"})
    time = dt.strptime(time.get("data-original-title"), "%d %b %Y, %H:%M")

    return Post(id, content, author.get_text(), author_url, avatar, time)
################################################################################


######################### APPLICATION THREADS + POSTS ##########################
def parse_applications() -> list[Application]:
    feed = requests.get("https://shadowkingdom.org/forum/view/13-staff-applications/", headers=header)
################################################################################


############################ REPORT THREADS + POSTS ############################
def parse_reports():
    pass
################################################################################
