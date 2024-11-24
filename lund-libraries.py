import logging
import threading
import time
import json
import requests
import pymirror
from bs4 import BeautifulSoup

"""
WORK IN PROGRESS !!!
"""

info = None

def get_lund_library_opening_hours(name: str):
    url = f"https://biblioteksportalen.lund.se/web/arena/{name}-bibliotek"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    s = soup.find_all(class_="custom-article")
    for t in s:
        if name in t.get_text().lower():
            days = [None] * 7
            d = 0
            hours = t.select("table")[0].find_all("td")
            for h in hours:
                #print(h.get_text())
                temp = h.get_text()
                h = temp.split(" ")[0]
                if h != "Stängt":
                    days[d] = h
                d += 1
            return days


def library_thread():
    global num_peeps
    while True:
        url =  "http://api.open-notify.org/astros.json"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
        }
        try:
            r = requests.get(url, headers = headers)
        except Exception:
            logging.error("library_thread caused exception", exc_info = True)
            num_peeps = None
        if r.status_code != 200:
            logging.error(f"library_thread failed with {r.status_code} for {url}")
            num_peeps = None
        if not r.text:
            logging.error("library_thread returned no data")
            num_peeps = None
        else:
            data = json.loads(r.text)
            logging.debug(data)
            if data["message"] == "success":
                num_peeps = int(data["number"])
            else:
                num_peeps = None
        time.sleep(60*60)


def init(mirror: pymirror.Mirror, conf: dict):
    global info
    del mirror
    info = conf
    logging.info(f"Hello world from the library module with conf {conf}")
    t = threading.Thread(target = library_thread, args = (info["library_name"], ))
    t.daemon = True
    t.start()


def draw(mirror: pymirror.Mirror, locals: any):
    del locals
    size = info["text_size"]
    if num_peeps:
        str = f"{num_peeps}"
        logging.info(f"{num_peeps} ppl in space")
        mirror.draw_text(str, 60, 0, adjustment = pymirror.Adjustment.Left, size = size)
