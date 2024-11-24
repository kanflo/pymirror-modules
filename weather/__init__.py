"""
Display forecast for the coming 12 hours given the specified lat/lon
Uses the Swedish Meteorological and Hydrological Institute (SMHI) meaning it's
probably mostly useful for us Swedes ;)
"""

from . import smhi
import datetime
import logging
import threading
import time
import pymirror

# Current forecast
forecast = None
# Module info from init(...)
info = None
# Cache icons here
icon_cache = {}
# Cache angle icons here based on wind direction
angle_cache = None
last_refresh = None


def arrow_key(wind_direction: float):
    global angle_cache
    steps = 22.5
    if not angle_cache:
        angle_cache = []
        for i in range(360//int(steps)):
            angle = steps * i
            angle_cache.append(angle)
        angle_cache.append(360.0)

    # wind_direction is the direction from which the wind is blowing from
    angle = wind_direction + 180
    if angle > 360:
        angle -= 360

    for i in range(len(angle_cache)):
        alfa = angle_cache[i]
        beta = angle_cache[i+1]
        if angle >= alfa and angle <= beta:
            return f"arrow-{int(round(int(10 * angle_cache[i]))):04d}"


def smhi_thread(latitude: float, longitude: float):
    global forecast
    global last_refresh
    while True:
        forecast = smhi.get_forecast(latitude, longitude)
        last_refresh = time.time()
        time.sleep(60*60)


def init(mirror: pymirror.Mirror, config: dict):
    global info
    info = config
    logging.info(f"Hello world from the weather module with config {config}")

    steps = 22.5
    for i in range(360//int(steps)):
        angle = 10 * steps * i

        (icon_cache[f"arrow-{int(round(int(angle))):04d}"], width, height) = mirror.load_image(f"arrows/arrow-{int(round(int(angle))):04d}.png", invert = True, width = 30)
    t = threading.Thread(target = smhi_thread, args = (mirror.latitude, mirror.longitude))
    t.daemon = True
    t.start()


def draw(mirror: pymirror.Mirror, locals: any):
    global icon_cache
    del locals
    # Display forecasts for the coming 12 hours with the option of
    # skipping the first forecast and/or forecasts betwen 02:00..05:00
    counter = 12
    # Keep a margin of 5 pixels
    x_margin = 5
    # Width of each hourly forecast
    width = (mirror.width - 2*x_margin) / counter
    # X position of current hourly forecast
    x_pos = x_margin
    text_size = info["text_size"]
    if forecast:
        dots_drawn = False
        for f in forecast:
            now = datetime.datetime.now()
            # Is the current forecast getting old?
            if f["time"].hour == now.hour and now.minute > 30:
                continue

            if "skip_night" in info and info["skip_night"]:
                if f["time"].hour > 1 and f["time"].hour < 6:
                    if not dots_drawn:
                        dots_drawn = True
                        mirror.draw_text("...", x_pos - 44 + width//2, -10, adjustment = pymirror.Adjustment.Center, size = text_size)
                    continue
            if not f["icon"] in icon_cache:
                (icon_cache[f["icon"]], iwidth, height) = mirror.load_image(f"rns-weather-icons/{f['icon']}", invert = True, width = width)

            hour = f"{f['time'].hour:02d}"
            mirror.draw_text(hour, x_pos+width//2, 0, adjustment = pymirror.Adjustment.Center, size = text_size)
            mirror.blit_image(icon_cache[f["icon"]], x_pos, 40)

            temperature = f"{int(round(f['temperature']))}°"
            mirror.draw_text(temperature, x_pos+width//2, 140, adjustment = pymirror.Adjustment.Center, size = text_size)
            mirror.blit_image(icon_cache[arrow_key(f["wind_direction"])], x_pos+40//2 + 15, 200)

            wind = f"{f['wind_speed']} ({f['wind_gust']})"
            mirror.draw_text(wind, x_pos+width//2, 240, adjustment = pymirror.Adjustment.Center, size = text_size*0.5)

            if f["precipitation"] > 0.0:
                precip = f"{f['precipitation']:.1f} mm"
                mirror.draw_text(precip, x_pos+width//2, 290, adjustment = pymirror.Adjustment.Center, size = text_size*0.5)

            x_pos += width
            counter -= 1
            if counter == 0:
                return


def get_debug_info(locals: dict) -> dict:
    """Get debug info of this module.

    Args:
        locals: The module locals

    Returns:
        dict: Dictionary with debug information
    """
    del locals
    return {
        "last_refresh": last_refresh
    }
