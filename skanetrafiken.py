import logging
import threading
import time
import datetime
import sys
try:
    import trafiklab
except ModuleNotFoundError:
    print("trafiklab missing: python -m pip install git+https://github.com/kanflo/trafiklab.git")
    sys.exit(1)
import pymirror

"""A module for displaying upcoming bus trips using Trafiklab, in Swedish.
"""


info = None
last_refresh = None


def trafiklab_thread():
    """A thread for reloading the bus table every minute
    """
    global last_refresh
    while True:
        tlab.refresh()
        last_refresh = time.time()
        time.sleep(60)


def init(mirror: pymirror.Mirror, config: dict):
    global info
    global tlab
    del mirror
    info = config
    logging.info(f"Hello world from the skanetrafiken module with config {config}")

    tlab = trafiklab.tripmonitor()
    tlab.init(info["min_bus_time"], info["api_key"])
    # TODO: Take from conf
    try:
#        if not tlab.add_route("Dalby busstation (Lund kn)", "Lund Jupitergatan"):
        if not tlab.add_route("Dalby busstation (Lund kn)", "Lund Centralstation"):
            logging.error("Failed to add route")
    except Exception:
        logging.error("Crap", exc_info=True)
        return
    tlab.blacklist_line("174")
    tlab.blacklist_line("159")  # Dalby Söderskog :D

    t = threading.Thread(target = trafiklab_thread)
    t.daemon = True
    t.start()


def draw(mirror: pymirror.Mirror, locals: any):
    del locals
    y = 0
    max_trips = 3  # Max number of upcoming trips we will display
    count = 0  # Number of trips added to current string
    size = info["text_size"]
    spacing = 10
    last_line = ""
    string = ""

    strings = []
    now = datetime.datetime.now()
    for trip in tlab.trips:
        ts = (trip["time"] - now).total_seconds()
        hour: int = trip['time'].hour
        minute: int = trip['time'].minute
        if last_line == trip["line"]:
            if "samt" in string:
                string += f" och {hour:02d}:{minute:02d}"
            else:
                string += f" samt {hour:02d}:{minute:02d}"
        else:
            if string:
                strings.append(string)
                y += size + spacing
            string = f"{trip['line']} mot {trip['to']} avgår {hour:02d}:{minute:02d}"

        count += 1
        last_line = trip["line"]
        if count == max_trips:
            if string:
                strings.append(string)
            break  # Only list 'max_trips' upcoming trips

    if len(strings) == 1:
        # Center vertically
        y += size // 2

    for string in strings:
        mirror.draw_text(string, info["width"]//2, y, adjustment = pymirror.Adjustment.Center, size = size)
        y += size + spacing


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
