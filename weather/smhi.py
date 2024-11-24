#
# Pull current weather forecast for given lat/lon from the
# Swedish Meteorological and Hydrological Institute (SMHI)
# Will only work for places in Sweden. Uses API version 2.
#

from typing import *
import sys
import requests
import json
import logging
from dateutil.parser import parse
import pymirror.sunrise as sunrise
try:
    import pytz
except ModuleNotFoundError:
    print("sudo -H pip3 install pytz")
    sys.exit(1)

symbol_table = {
    1:     # SMHI: Clear sky
        "clear",
    2:     # SMHI: Nearly clear sky
        "partly_cloudy", # todo: shold have a symbol with a smaller cloud
    3:     # SMHI: Variable cloudness
        "variable_cloudy",
    4:     # SMHI: Halfclear sky
        "halfclear",
    5:     # SMHI: Cloudy sky
        "cloudy",
    6:     # SMHI: Overcast
        "cloudy",
    7:     # SMHI: Fog
        "fog",
    8:     # SMHI: Light rain showers
        "light_showers",
    9:     # SMHI: Moderate rain showers
        "moderate_showers",
    10:    # SMHI: Heavy rain showers
        "heavy_showers",
    11:    # SMHI: Thunderstorm
        "thunderstorm",
    12:    # SMHI: Light sleet showers
        "light_sleet",
    13:    # SMHI: Moderate sleet showers
        "moderate_sleet",
    14:    # SMHI: Heavy sleet showers
        "heavy_sleet",
    15:    # SMHI: Light snow fall
        "light_snow",
    16:    # SMHI: Moderate snow fall
        "moderate_snow",
    17:    # SMHI: Heavy snow fall
        "heavy_snow",
    18:    # SMHI: Light rain
        "light_rain",
    19:    # SMHI: Moderate rain
        "moderate_rain",
    20:    # SMHI: Heavy rain
        "heavy_rain",
    21:    # SMHI: Thunder
        "lightning",
    22:    # SMHI: Light sleet
        "light_sleet",
    23:    # SMHI: Moderate sleet
        "moderate_sleet",
    24:    # SMHI: Heavy sleet
        "heavy_sleet",
    25:    # SMHI: Light snowfall
        "light_snow",
    26:    # SMHI: Moderate snowfall
        "moderate_snow",
    27:    # SMHI: Heavy snowfall
        "heavy_snow",
}

icon_table = {
        # Mapping to rns-weather-icons [<day id>, <night id>]
        "clear" : [0, 4],
         # SMHI: Nearly clear sky
        "partly_cloudy" : [16, 17],
         # SMHI: Variable cloudness
        "variable_cloudy" : [16, 17],
         # SMHI: Halfclear sky
        "halfclear" : [16, 17],
         # SMHI: Cloudy sky
        "cloudy" : [15, 17],
         # SMHI: Overcast
#        "cloudy" : [day, night],
         # SMHI: Fog
        "fog" : [38, 40],
         # SMHI: Light rain showers
        "light_showers" : [47, 49],
         # SMHI: Moderate rain showers
        "moderate_showers" : [44, 46],
        # SMHI: Heavy rain showers
        "heavy_showers" : [53, 55],
        # SMHI: Thunderstorm
        "thunderstorm" : [27, 29],
        # SMHI: Light sleet showers
        "light_sleet" : [50, 52],
        # SMHI: Moderate sleet showers
        "moderate_sleet" : [50, 52],
        # SMHI: Heavy sleet showers
        "heavy_sleet" : [53, 55],
        # SMHI: Light snow fall
        "light_snow" : [30, 32],
        # SMHI: Moderate snow fall
        "moderate_snow" : [30, 32],
        # SMHI: Heavy snow fall
        "heavy_snow" : [67, 67],
        # SMHI: Light rain
        "light_rain" : [24, 26],
        # SMHI: Moderate rain
        "moderate_rain" : [18, 20],
        # SMHI: Heavy rain
        "heavy_rain" : [21, 23],
        # SMHI: Thunder
        "lightning" : [27, 29]
}
"""
Return SMHI forecast for given position.
The forecast is an array of dictionaries with the following content:

    time:           <datetime>
    precipitation:  <float>
    temperature:    <float>
    visibility:     <float>
    wind_speed:     <float>
    wind_gust:      <float>
    wind_direction: <float>
    symbol:         <string>
    units:          <dictionary string -> string>

Note: <wind_direction> is hte direction from which it blows ;)

Eg.
    {
        'time': datetime.datetime,
        'precipitation': 0.0,
        'temperature': 15.6,
        'visibility': 18.2,
        'wind_direction': 228.0,
        'wind_speed': 7.6,
        'wind_gust': 13.6,
        'symbol': 'day_sunny_overcast',
        'units': {
            'precipitation': 'mm/h',
            'temperature': '°C',
            'visibility': 'km',
            'wind_direction': 'deg',
            'wind_speed': 'm/s',
            'wind_gust': 'm/s'
        }
    }
"""

def get_forecast(lat: float, lon: float) -> Dict:
    """Get SMHI forecase for given location

    Arguments:
        lat {double} -- Latitude of location
        lon {double} -- Longitude of location

    Returns:
        [Dict] -- The forecast. I know, this documentation is lousy
    """
    fcs = []
    url =  f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    headers = {
        'Cookie': '_ga=GA1.2.289062950.1559249760; _gid=GA1.2.36071933.1559592625',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Host': 'opendata-download-metfcst.smhi.se',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15',
        'Accept-Language': 'en-gb',
        'Accept-Encoding': 'br, gzip, deflate',
        'Connection': 'keep-alive',
    }
    try:
        r = requests.get(url, headers = headers)
    except Exception:
        logging.error("Caught exception", exc_info = True)
        return None
    if r.status_code != 200:
        logging.error(f"SMHI failed with {r.status_code} for {url}")
        return None
    if not r.text:
        logging.error("SMHI returned no data")
        return None
    else:
        if sunrise.is_day():
            index = 0
        else:
            index = 1
        forecast = json.loads(r.text)
        try:
            for w in forecast["timeSeries"]:
                fc = {}
                # Its SMHI after all...
                local_tz = pytz.timezone("Europe/Stockholm")
                fc["time"] = parse(w["validTime"]).astimezone(local_tz)

                # todo: differ between day and night by sunrise
                if fc["time"].hour > 22 or fc["time"].hour < 5:
                    index = 1
                else:
                    index = 0

                for i in w["parameters"]:
                    # From https://opendata.smhi.se/apidocs/metfcst/parameters.html:
                    # pmean	mm/h	hl	0	Mean precipitation intensity	Decimal number, one decimal
                    # pmedian	mm/h	hl	0	Median precipitation intensity	Decimal number, one decimal
                    #
                    # SMHI shows the pmedian value in their app
                    if i["name"] == "pmedian":
                        fc["precipitation"] = float(i["values"][0])
                    elif i["name"] == "t":
                        fc["temperature"] = float(i["values"][0])
                    elif i["name"] == "vis":
                        fc["visibility"] = float(i["values"][0])
                    elif i["name"] == "wd":
                        fc["wind_direction"] = float(i["values"][0])
                    elif i["name"] == "ws":
                        fc["wind_speed"] = float(i["values"][0])
                    elif i["name"] == "gust":
                        fc["wind_gust"] = float(i["values"][0])
                    elif i["name"] == "Wsymb2":
                        fc["symbol_id"] = int(i["values"][0])
                        fc["symbol"] = symbol_table[int(i["values"][0])] # [index]
#                        fc["symbol"] = fc["symbol"].replace("day_", "")
#                        fc["symbol"] = fc["symbol"].replace("night_", "")
                        if fc["symbol"] in icon_table:
                            fc["icon"] = f"weather_icons-{icon_table[fc['symbol']][index]}.png"
                        else:
                            fc["icon"] = "weather_icons-14.png"

                if "snow" in fc["symbol"]:
                    # Well known fact
                    fc["precipitation"] *= 10

                fc["units"] = {}
                fc["units"]['precipitation'] = "mm/h"
                fc["units"]["temperature"] = "°C"
                fc["units"]["visibility"] = "km"
                fc["units"]["wind_direction"] = "deg"
                fc["units"]["wind_speed"] = "m/s"
                fc["units"]["wind_gust"] = "m/s"
                fcs.append(fc)
        except Exception as e:
            logging.exception(e)
            return None
        return fcs
