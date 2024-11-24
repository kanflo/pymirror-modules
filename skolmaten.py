import threading
import time
import sys
import requests
import logging
import datetime
import pymirror
from dateutil.parser import parse
try:
    import xmltodict
except ModuleNotFoundError:
    print("mqttwrapper missing: sudo -H python -m pip install xmltodict")
    sys.exit(1)


menu = None
info = None
schools = []

"""
Return the menu for the coming days for the given school/schools. The menu is a
list of dictionaries of arrays, keyed on datetime.datetime objects. The list is used
to keep track of multiple schools (something that probably is not handled very well).

[
    {
    <date> : [ <non vegetarian>, <vegetarian> ], # Mon
    <date> : [ <non vegetarian>, <vegetarian> ], # Tue
    <date> : [ <non vegetarian>, <vegetarian> ], # Wed
    <date> : [ <non vegetarian>, <vegetarian> ]  # Thu
    <date> : [ <non vegetarian>, <vegetarian> ]  # Fri
    }
]
"""
def get_menu(school_name: str = "nyvangskolan", limit: int = 7):
    menu = {}
    url =  f"https://skolmaten.se/{school_name}/rss/days/?limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
    }
    try:
        r = requests.get(url, headers = headers)
    except Exception:
        logging.error("get_menu caused exception", exc_info = True)
        return None
    if r.status_code == 200:
        data = r.text
        result = xmltodict.parse(data)
        holidays = ["NATIONALDAG", "LOV", "MIDSOMMAR", "GLAD PÅSK!"]
        # If today is a holiday, we will display the alternatives for the coming
        # shool day
        for k in result["rss"]["channel"]["item"]:
            alternatives = k["description"].split("<br/>")
            date = parse(k["pubDate"]).replace(hour = 0, minute = 0, second = 0, microsecond = 0, tzinfo = None)
            if not alternatives[0] in holidays:
                # Fix various common typos and other annoyances
                alternatives[0] = alternatives[0].replace("&", " & ")
                alternatives[0] = alternatives[0].replace("  ", " ")
                alternatives[0] = alternatives[0].replace("serveras med", "med")
                if len(alternatives) > 1:
                    alternatives[1] = alternatives[1].replace("&", " & ")
                    alternatives[1] = alternatives[1].replace("  ", " ")
                    alternatives[1] = alternatives[1].replace("serveras med", "med")
                else:
                    logging.warning("Only one meal today")
                menu[date] = alternatives
    else:
        logging.error(f"Skolmaten failed with {r.status_code} for {url}\n")
    return menu


def canteen_thread(school_name: str):
    global menu
    school_idx = 0
    while True:
        try:
            new_menu = []
            for school in school_name.split(","):
                school = school.lower()
                school = school.replace("å", "a").replace("ä", "a").replace("ö", "o")
                m = get_menu(school)
                new_menu.append(m)
                school_idx += 1
        except Exception:
            logging.error("canteen caused exception", exc_info = True)
        menu = new_menu
        time.sleep(24*60*60)


def init(mirror: pymirror.Mirror, config: dict):
    global info
    global schools

    info = config
    for school in info["school_name"].split(","):
        schools.append(school.replace("skolan", ""))
    logging.info(f"Hello world from the canteen module with config {config}")
    t = threading.Thread(target = canteen_thread, args = (info["school_name"], ))
    t.daemon = True
    t.start()


def draw(mirror: pymirror.Mirror, locals: any):
    # TODO: This frunction probably does not handle multiple schools as expected...
    if not menu:
        return

    size = info["text_size"]
    now = datetime.datetime.now()
    today = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0, tzinfo = None)
    wd = today.weekday
    m = None
    if today in menu[0]:
        if now.hour > 16:
            # Display tomorrow's menu
            pass
        else:
            day_offset = 0
            date = today
            m = menu[0][today]
    if not m: # Actually else: but we might come here even though today is in menu
        for day_offset in range(1, 7):
            date = today + datetime.timedelta(days = day_offset)
            if date in menu[0]:
                m = menu[0][date]
                break
    if m:
        if day_offset == 0:
            if now.hour < 12:
                header = "Idag serveras"
            else:
                header = "Idag serverades"
        elif day_offset == 1:
            header = "Imorgon serveras"
        elif day_offset == 2:
            header = "I övermorgon serveras"
        else:
            days = ["måndag", "tisdag", "onsdag", "torsdag", "fredag"]
            header = f"På {days[date.weekday()]} serveras"

        first_lower = lambda s: s[:1].lower() + s[1:] if s else ""
        dishes = []
        for i in range(len(m)//2):
            non_veg = m[2*i]
            if len(m) > 1:
                veg = first_lower(m[2*i+1])
                if veg == non_veg:
                    str = f"{non_veg}"
                else:
                    str = f"{non_veg} / {veg}"
            else:
                str = f"{non_veg}"
            if str not in dishes:
                dishes.append(str)

        i = 0
        # Now draw the menu "bottom adjusted" in the frame. if the different
        # schools have different menus, prefix the menus with the scool name.
        y_pos = info["height"] - 2*size*(1+len(dishes))
        mirror.draw_text(header, info["width"]//2, y_pos, adjustment = pymirror.Adjustment.Center, size = size)
        y_pos += 2*size
        for d in dishes:
            if i >= len(schools):
                break
            if len(dishes) > 1:
                d = schools[i] + " : " + d
            mirror.draw_text(d, info["width"]//2, y_pos, adjustment = pymirror.Adjustment.Center, size = size)
            y_pos += 2*size
            i += 1
