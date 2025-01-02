"""
parser.py

Builds Thread objects, each with their own list of Post objects.

All HTML content is parsed here.
"""


from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin
from datetime import datetime as dt
import re
import requests

import forum


BASE_URL = "https://shadowkingdom.org"
STAFF_APP_PATH = "/forum/view/13-staff-applications/"
REPORT_PLAYER_PATH = "/forum/view/16-player-reports/"
REPORT_STAFF_PATH = "/forum/view/17-staff-reports/"
REPORT_BUG_PATH = "/forum/view/18-bug--glitch-reports/"
APPEAL_PATH = "/forum/view/21-ban-appeals/"


def _parse_post(p) -> list[forum.Post]:
    soup = BeautifulSoup(str(p), "html.parser")
    id = re.search(r"post-\d+", str(soup)).group()
    # id = id.removeprefix("post-")

    content = soup.find(class_="forum-post-content")
    content = re.sub('[\\n]+', '\\n\\n', content.get_text("\n"))

    author = soup.find(class_="username")
    author_url = urljoin(BASE_URL, author.get("href"))

    # Author's profile picture.
    avatar = soup.find(class_="avatar-img").get("src")
    if "dicebear" in avatar:
        avatar = avatar.replace(" ", "%20")
    
    elif "crafatar" in avatar:
        avatar = f"https://minotar.net/helm/{author.get_text()}/128.png"

    else:
        avatar = urljoin(BASE_URL, soup.find(class_="avatar-img").get("src"))
    
    time = soup.find("span", attrs={"data-toggle": "tooltip"})
    time = dt.strptime(time.get("data-original-title"), "%d %b %Y, %H:%M")

    return forum.Post(id, content, author.get_text(), author_url, avatar, time)


################################# APPEAL THREADS ###############################
def get_appeals(cookie) -> list[forum.Appeal]:
    feed = requests.get(urljoin(BASE_URL, APPEAL_PATH), headers=cookie) 

    soup = BeautifulSoup(feed.text, "html.parser")
    elements = soup.find_all(class_="forum-link")

    threads = []

    for item in elements:
        url = urljoin(BASE_URL, item.get("href"))
        threads.append(_appeal_thread(url, cookie))
    
    return threads


def _appeal_thread(url, cookie):
    thread = requests.get(url, headers=cookie)
    soup = BeautifulSoup(thread.text, "html.parser")

    title = soup.find(class_="forum-topic-title")

    # Remove all <span> elements within the title.
    for span in title.find_all("span"):
        span.decompose()

    posts_raw = soup.find_all("div", attrs={ "id": re.compile(r"post-\d+") })

    posts = []
    ign = "bigwilyhaver"

    for item in posts_raw:
        posts.append(_parse_post(item))

    return forum.Appeal(url, title.get_text().strip(), posts, ign)
#==============================================================================#



############################# APPLICATION THREADS ##############################
def get_applications(cookie) -> list[forum.Application]:
    feed = requests.get(urljoin(BASE_URL, STAFF_APP_PATH), headers=cookie)

    soup = BeautifulSoup(feed.text, "html.parser")
    elements = soup.find_all(class_="forum-link")

    threads = []

    for item in elements:
        url = urljoin(BASE_URL, item.get("href"))
        threads.append(_application_thread(url, cookie))
    
    return threads


def _application_thread(url, cookie):
    thread = requests.get(url, headers=cookie)
    soup = BeautifulSoup(thread.text, "html.parser")

    title = soup.find(class_="forum-topic-title")

    # Remove all <span> elements within the title.
    for span in title.find_all("span"):
        span.decompose()

    posts_raw = soup.find_all("div", attrs={ "id": re.compile(r"post-\d+") })

    posts = []

    for item in posts_raw:
        posts.append(_parse_post(item))

    return forum.Application(url, title.get_text().strip(), posts)
#==============================================================================#



################################ REPORT THREADS ################################
def get_reports(cookie) -> list[forum.Report]:
    feed_player = requests.get(urljoin(BASE_URL, REPORT_PLAYER_PATH), headers=cookie)
    feed_staff = requests.get(urljoin(BASE_URL, REPORT_STAFF_PATH), headers=cookie)
    feed_bug = requests.get(urljoin(BASE_URL, REPORT_BUG_PATH), headers=cookie)

    soup_player = BeautifulSoup(feed_player.text, "html.parser")
    soup_staff = BeautifulSoup(feed_staff.text, "html.parser")
    soup_bug = BeautifulSoup(feed_bug.text, "html.parser")
    
    elements_player = soup_player.find_all(class_="forum-link")
    elements_staff = soup_staff.find_all(class_="forum-link")
    elements_bug = soup_bug.find_all(class_="forum-link")

    threads = []

    for item in elements_player:
        url = urljoin(BASE_URL, item.get("href"))
        threads.append(_report_thread(url, cookie, forum.ReportType.PLAYER))

    for item in elements_staff:
        url = urljoin(BASE_URL, item.get("href"))
        threads.append(_report_thread(url, cookie, forum.ReportType.STAFF))

    for item in elements_bug:
        url = urljoin(BASE_URL, item.get("href"))
        threads.append(_report_thread(url, cookie, forum.ReportType.BUG))
    
    return threads


def _report_thread(url, cookie, t):
    thread = requests.get(url, headers=cookie)
    soup = BeautifulSoup(thread.text, "html.parser")
    title = soup.find(class_="forum-topic-title")
    posts_raw = soup.find_all("div", attrs={ "id": re.compile(r"post-\d+") })

    posts = []

    for item in posts_raw:
        posts.append(_parse_post(item))

    return forum.Report(url, title.get_text().strip(), posts, t)
#==============================================================================#
