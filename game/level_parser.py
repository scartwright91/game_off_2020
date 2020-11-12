
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
                    player_pos = [entity["px"][0] * TILE_SCALE, entity["px"][1] * TILE_SCALE]

    return player_pos

def calculate_world_size(level):

    xs, ys = [], []

    # iterate through layers
    for layer in level_data["levels"][level]["layerInstances"]:
        # Platforms
        if layer["__identifier"] == "Platforms":
            for tile in layer["autoLayerTiles"]:
                xs.append(tile["px"][0] * TILE_SCALE)
                ys.append(tile["px"][1] * TILE_SCALE)

    max_x = max(xs)
    max_y = max(ys)

    return (max_x, max_y)

def create_level(game, level):

    # Delete all current entities
    for e in game.entities: e.kill()

    # read tileset
    tileset = read_image("assets/tileset/spaceship_spritesheet.png")
    tileset = pg.transform.scale(tileset, (tileset.get_width() * TILE_SCALE, tileset.get_height() * TILE_SCALE))

    # iterate through layers
    for layer in level_data["levels"][level]["layerInstances"]:

        # Platforms
        if layer["__identifier"] == "Platforms":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.platforms, game.camera, game.entities)

        # Foreground
        if layer["__identifier"] == "Foreground":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.foreground, game.camera, game.entities)
        
        # Background
        if layer["__identifier"] == "Background":
            for tile in layer["autoLayerTiles"]:
                Tile(tile, tileset, game.background, game.camera, game.entities)
        
        # Entities
        if layer["__identifier"] == "Entities":
            for entity in layer["entityInstances"]:
                if entity["__identifier"] == "Droid":
                    patrol = [pg.Vector2(patrol["cx"] * TILE_SIZE * TILE_SCALE, patrol["cy"] * TILE_SIZE * TILE_SCALE) for patrol in entity["fieldInstances"][0]["__value"].copy()]
                    Droid(entity["px"], patrol, game, game.enemies, game.camera, game.entities)
                if entity["__identifier"] == "Turret":
                    Turret(entity["px"], game, game.enemies, game.camera, game.entities)
                if entity["__identifier"] == "Endpoint":
                    Endpoint(entity, game.endpoints, game.camera, game.entities)

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

class Endpoint(pg.sprite.Sprite):

    def __init__(self, tile_meta, *groups):
        super().__init__(*groups)
        self.connected_level = tile_meta["fieldInstances"][0]["__value"]
        self.pos = [tile_meta["px"][0] * TILE_SCALE, tile_meta["px"][1] * TILE_SCALE]
        self.image = pg.Surface((TILE_SIZE * TILE_SCALE, TILE_SIZE * TILE_SCALE), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        pass

