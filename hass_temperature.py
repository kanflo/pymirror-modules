#!/usr/bin/env python3
# -*- coding: utf-8 -*- i
#
# Copyright (c) 2021 Johan Kanflo (github.com/kanflo)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#
# Read sensor data from HASS and display
#

import logging
import sys
import time
import logging
import threading
import datetime
from dateutil.parser import parse
from requests import get
import pymirror


# Consider sensor as awol when it has not been updated in this time
MAX_AGE = 4*3600

# Encapsulating the module data in an object allows for us to have more than one
# hass_temperature on screen displaying different measurements.
class hass_sensor:
    _current_temperature = None
    _mod_info = None    # Module info dict
    _last_check = None  # Unix timestamp when we last checked the sensor
    _last_completed_check = None  # Unix timestamp when we last got a response from the sensor
    _age = None         # Age of measurement in seconds
    _error_count = 0    # Number of times we failed to read the sensor
    _last_error_time = None  # Unix timestamp of last error
    _last_str = None    # Last drawn string
    _icon = None
    _icon_width = 0
    _icon_height = 0

    def __init__(self, mirror: pymirror.Mirror, mod_info: dict):
        self._mod_info = mod_info
        self._current_temperature = None
        if "icon" in mod_info:
            (self._icon, self._icon_width, self._icon_height) = mirror.load_image(mod_info["icon"], invert = True, width = int(0.8 * mod_info["font_size"]))


def temperature_thread(hass_host: str, token: str, sensor: hass_sensor, sensor_name: str):
    """A thread for periodically reading the temperature for 'sensor' from HASS

    Args:
        hass_host (str): HASS host name (from global mirror config)
        token (str): Your 'long lived' token (from global mirror config)
        sensor (str): Name of sensor
    """
    while True:
        sensor._last_check = time.time()
        url = "http://%s/api/states/%s" % (hass_host, sensor_name)
        headers = {
            "Authorization": "Bearer %s" % token,
            "content-type": "application/json",
        }
        try:
            j = None
            response = get(url, headers = headers)
            j = response.json()
            dt = parse(j["last_changed"])
            now = datetime.datetime.utcnow()
            age = now.replace(tzinfo=datetime.timezone.utc) - dt
            if age.total_seconds() < MAX_AGE:
                sensor._current_temperature = float(j["state"])
                sensor._age = age.total_seconds()
        except Exception as e:
            logging.error("Sensor fetch failed: " + str(e))
            logging.error("j = %s" % (j))
            sensor._current_temperature = None
            sensor._error_count += 1
            sensor._last_error_time = time.time()
            time.sleep(5)
            continue
        else:
            if age.total_seconds() >= MAX_AGE:
                # Temperature sensor went awol
                # (or temperature did not change, no way of knowing with HASS it seems)
                sensor._current_temperature = None
                sensor._error_count += 1
                sensor._last_error_time = time.time()
        sensor._last_completed_check = time.time()
        time.sleep(60)


def init(mirror: pymirror.Mirror, mod_info: dict) -> hass_sensor:
    sensor = hass_sensor(mirror, mod_info)
    logging.info("Hello world from the hass_temperature module with mod_info %s" % mod_info)
    host = mirror.get_config("hass_host")
    token = mirror.get_config("hass_token")
    t = threading.Thread(target = temperature_thread, args = (host, token, sensor, mod_info["sensor"], ))
    t.daemon = True
    t.start()
    return sensor


def draw(mirror: pymirror.Mirror, sensor: hass_sensor):
    if sensor._current_temperature is not None:
        if abs(sensor._current_temperature) > 2 or round(sensor._current_temperature) == sensor._current_temperature:
            str = "%d°" % round(sensor._current_temperature)
        else:
            str = "%.1f°" % sensor._current_temperature
        sensor._last_str = str
        x_pos: int = 0
        if sensor._icon:
            mirror.blit_image(sensor._icon, 0, 16)
            x_pos += sensor._icon_width + 12
        mirror.draw_text(str, x_pos, 0, adjustment = pymirror.Adjustment.Left, size = sensor._mod_info["font_size"])


def get_debug_info(sensor: hass_sensor) -> dict:
    """Get debug info of this module.

    Args:
        sensor (hass_sensor): The sensor we want info about

    Returns:
        dict: Dictionary with debug information
    """
    return {
        "last_check": sensor._last_check,
        "last_completed_check": sensor._last_completed_check,
        "age": sensor._age,
        "error_count": sensor._error_count,
        "last_error_time": sensor._last_error_time,
        "last_str": sensor._last_str
    }


def main():
    """For testing
    """
    level = logging.DEBUG
    logging.basicConfig(level=level, stream=sys.stdout,
                        format='%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
                        datefmt='%Y%m%d %H:%M:%S')
    logging.info("---[ Starting %s ]---------------------------------------------" % sys.argv[0])

    conf = {
        "conf": {
                "broker": "nano.local",
                "topic": "aazero/outdoor/temperature"
            }
    }
    init(None, conf)
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
