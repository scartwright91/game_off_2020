import pygame as pg
from .settings import *


class Droid(pg.sprite.Sprite):

    def __init__(self, pos, game, *groups):
       super().__init__(*groups)
       self.image = pg.Surface((TILE_SIZE * TILE_SCALE, TILE_SIZE * TILE_SCALE))
       self.image.fill(RED)
       self.rect = self.image.get_rect(topleft=pos)
       self.game = game

    def update(self):
        pass

