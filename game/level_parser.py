
import json
import pygame as pg
from .settings import *
from .utils import read_image
from .enemies import Droid, Turret


def find_player_pos(level):

    for layer in level_data["levels"][level]["layerInstances"]:
        if layer["__identifier"] == "Entities":
            for entity in layer["entityInstances"]:
                if entity["__identifier"] == "Player":
                    player_pos = [entity["px"][level] * TILE_SCALE, entity["px"][1] * TILE_SCALE]

    return player_pos


def create_level(game, level):

    # read tileset
    tileset = read_image("assets/tileset/spaceship_spritesheet.png")
    tileset = pg.transform.scale(tileset, (tileset.get_width() * TILE_SCALE, tileset.get_height() * TILE_SCALE))

    # iterate through layers
    for layer in level_data["levels"][level]["layerInstances"]:

        # Platforms
        if layer["__identifier"] == "Platforms":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.platforms, game.camera)

        # Foreground
        if layer["__identifier"] == "Foreground":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.foreground, game.camera)
        
        # Background
        if layer["__identifier"] == "Background":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.background, game.camera)
        
        # Entities
        if layer["__identifier"] == "Entities":
            for entity in layer["entityInstances"]:
                if entity["__identifier"] == "Droid":
                    patrol = [pg.Vector2(patrol["cx"] * TILE_SIZE * TILE_SCALE, patrol["cy"] * TILE_SIZE * TILE_SCALE) for patrol in entity["fieldInstances"][0]["__value"].copy()]
                    Droid(entity["px"], patrol, game, game.enemies, game.camera)
                if entity["__identifier"] == "Turret":
                    Turret(entity["px"], game, game.enemies, game.camera)

class Tile(pg.sprite.Sprite):

    def __init__(self, tile_meta, tileset, *groups):
        super().__init__(*groups)
        self.tile_meta = tile_meta
        self.tileset = tileset
        self.pos = [self.tile_meta["px"][0] * TILE_SCALE, self.tile_meta["px"][1] * TILE_SCALE]
        self.image = pg.Surface((TILE_SIZE * TILE_SCALE, TILE_SIZE * TILE_SCALE), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image.blit(self.tileset, (0, 0), (self.tile_meta["src"][0] * TILE_SCALE,
                                               self.tile_meta["src"][1] * TILE_SCALE,
                                               self.image.get_width(),
                                               self.image.get_height()))

    def update(self):
        pass


