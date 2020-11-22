

import pygame as pg
import os
from .utils import *
from .settings import *


def load_droid_animations():

    standing_animations = {
        "left": [],
        "right": []
    } 

    standing_path = 'assets/animations/droid/standing/'

    for image_path in os.listdir(standing_path):
        frame = read_image(standing_path + image_path, w=1.5*TILE_SIZE*TILE_SCALE, h=1.5*2*TILE_SIZE*TILE_SCALE)
        standing_animations["right"].append(frame)
        standing_animations["left"].append(pg.transform.flip(frame, True, False))

    animation_images = {
        "standing": standing_animations
    }

    return animation_images


