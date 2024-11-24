import logging
import threading
import time
import json
import requests
import pymirror


last_check = None
last_http_status = None
last_exception = None
num_peeps = None
info = None
icon = None
icon_width = None
icon_height = None


def space_peeps_thread():
    global last_check
    global last_http_status
    global last_exception
    global num_peeps
    while True:
        url =  "http://api.open-notify.org/astros.json"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
        }
        try:
            data = None
            last_check = time.time()
            r = requests.get(url, headers = headers)
            last_http_status = r.status_code
            if r.status_code != 200:
                logging.error(f"Spacepeeps failed with {r.status_code} for {url}")
                num_peeps = None
            if not r.text:
                logging.error("Spacepeeps returned no data")
                num_peeps = None
            else:
                data = json.loads(r.text)
                logging.debug(data)
                if data['message'] == 'success':
                    num_peeps = int(data['number'])
                    logging.debug(f"There are currently {num_peeps} persons in space")
                else:
                    num_peeps = None
        except Exception as e:
            logging.error("Peep fetch failed", exc_info=True)
            logging.error(f"data = {data}")
            num_peeps = None
        time.sleep(60*60)


def init(mirror: pymirror.Mirror, config: dict):
    global info
    global icon
    global icon_width
    global icon_height
    info = config
    logging.info(f"Hello world from the spacepeeps module with config {config}")
    t = threading.Thread(target = space_peeps_thread)
    t.daemon = True
    t.start()
    (icon, icon_width, icon_height) = mirror.load_image("among-us.png", invert = True, width = int(0.8 * info["text_size"]))


def draw(mirror: pymirror.Mirror, locals: any):
    global info
    global icon
    global icon_width
    global icon_height
    size = info["text_size"]
    if num_peeps:
        str = f"{num_peeps}"
        mirror.draw_text(str, icon_width + 10, 0, adjustment = pymirror.Adjustment.Left, size = size)
        mirror.blit_image(icon, 0, (size-icon_height)//2 - 10)



def get_debug_info(locals: dict) -> dict:
    """Get debug info of this module.

    Args:
        locals: The module locals

    Returns:
        dict: Dictionary with debug information
    """
    return {
        "last_check": last_check,
        "last_http_status": last_http_status,
        "num_peeps": num_peeps,
        "last_peeps_exception": last_exception
    }
