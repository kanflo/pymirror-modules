import logging
import datetime
import pymirror

_config = None


def init(mirror: pymirror.Mirror, config: dict[str: str]):
    del mirror
    global _config
    _config = config
    logging.info(f"Hello world from the time2 module with config {config}")
    return None


def draw(mirror: pymirror.Mirror, locals: any):
    del locals
    global _config
    now = datetime.datetime.now()
    str = f"{now.hour:02d}:{now.minute:02d}"
    mirror.draw_text(str, _config["width"], 0, adjustment = pymirror.Adjustment.Right, size = _config["font_size"])
