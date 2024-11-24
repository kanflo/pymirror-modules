from typing import *
try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    print("python -m pip install BeautifulSoup4")
import requests
import logging

"""
WORK IN PROGRESS !!!
"""

"""
# TODO: Add this to requirements.txt
requests==2.23.0
beautifulsoup4==4.9.0
"""

"""This module scrapes opening hours for the recycling centers run by Sysav in Sweden
"""

def scrape(location_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Scrape opening hours for given Sysav location

    Arguments:
        location_name {str} -- The location part of the URL, eg. "Lund-Gastelyckans-atervinningscentral"

    Returns:
        Tuple[Optional[str], Optional[str]] -- Today's opening hours as "HH:00-HH:00" or None if currently closed
                                              and the same for tomorrows opening hours
    """
    r = requests.get(f"https://www.sysav.se/Privat/Atervinningscentraler/{location_name}")
    if r.status_code != 200:
        logging.error(f"Unknown recycling station '{location_name}'")
        return (None, None)

    soup = BeautifulSoup(r.text, 'html.parser')

    # TODO: Broken as of Marth 17th 2024

    is_open = False
    opening_hours_today = None
    opening_hours_tomorrow = None
    for el in soup.find_all(attrs={"class": "recyclecenterstatus-topmessage"}):
        #print(el.get_text().lstrip().rstrip())
        is_open = el.get_text().lstrip().rstrip() == "Nu har vi öppet!"

    for el in soup.find_all(attrs={"class": "hours"}):
        #print(el.get_text().lstrip().rstrip())
        opening_hours_today = el.get_text().lstrip().rstrip()

    for el in soup.find_all(attrs={"class": "recyclecenterstatus-bottommessage"}):
        #print(el.get_text().lstrip().rstrip())
        temp = el.get_text().lstrip().rstrip()
        opening_hours_tomorrow = temp.split(":")[1].lstrip().rstrip()

    if opening_hours_today is None and opening_hours_tomorrow is None:
        logging.error("Failed to parse response")
    return (opening_hours_today, opening_hours_tomorrow)


if __name__ == "__main__":
    (opening_hours_today, opening_hours_tomorrow) = scrape("gastelyckan")
    if opening_hours_today is not None:
        print(f"Öppet idag    : {opening_hours_today}")
    if opening_hours_tomorrow is not None:
        print(f"Öppet imorgon : {opening_hours_tomorrow}")
    else:
        if opening_hours_today is None or opening_hours_tomorrow is None:
            print("API-knas!")
        else:
            print("Helstängt")
