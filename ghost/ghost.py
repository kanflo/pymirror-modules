from typing import *
import logging
import datetime
import pymirror


def init(mirror: pymirror.Mirror, config: dict):
    logging.info(f"Hello world from the ghost module with config {config}")
    if "image" in config:
        (ghost_image, _, scare_height) = mirror.load_image(config["image"], width = mirror.width)
    else:
        (ghost_image, _, scare_height) = mirror.load_image("scare.jpg", width = mirror.width)
    next_scare = datetime.datetime.now() + datetime.timedelta(seconds = 20)
    logging.debug(f"Next scare at {next_scare}")
    return {"config": config,
            "ghost_image": ghost_image,
            "scare_height": scare_height,
            "scare_frame_counter": 0,
            "next_scare": next_scare
            }


def draw(mirror: pymirror.Mirror, locals: dict[str: str]):
    next_scare = locals["next_scare"]
    scare_frame_counter = locals["scare_frame_counter"]
    now = datetime.datetime.now()
    scare = now.hour == next_scare.hour and now.minute == next_scare.minute and now.second == next_scare.second

    if scare or scare_frame_counter > 0:
        if scare_frame_counter < locals["config"]["scare_frame_counter"]:
            logging.debug("Booh!!!")
            mirror.blit_image(locals["ghost_image"], 0, 0)
            # Would like bottom adjust but right now that's wonky
            # mirror.blit_image(ghost, 0, (info["height"] - scare_height))
            scare_frame_counter += 1
        else:
            scare_frame_counter = 0
            next_scare = datetime.datetime.now() + datetime.timedelta(hours = 24)
            next_scare = next_scare.replace(hour = 0, minute = 0, second = 0)
            logging.debug(f"Next scare at {next_scare}")
            locals["next_scare"] = next_scare
