

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

    disabled_animations = {
        "left": [],
        "right": []
    }

    disabled_path = 'assets/animations/droid/disabled/'

    for image_path in os.listdir(disabled_path):
        frame = read_image(disabled_path + image_path, w=1.5*TILE_SIZE*TILE_SCALE, h=1.5*2*TILE_SIZE*TILE_SCALE)
        disabled_animations["right"].append(frame)
        disabled_animations["left"].append(pg.transform.flip(frame, True, False))

    turret_path = 'assets/animations/turret/disabled/'

    turret = []

    for image_path in os.listdir(turret_path):
        frame = read_image(turret_path + image_path, w=2*TILE_SIZE*TILE_SCALE, h=2*TILE_SIZE*TILE_SCALE)
        turret.append(frame)

    animation_images = {
        "standing": standing_animations,
        "disabled": disabled_animations,
        "turret": turret
    }

    return animation_images


