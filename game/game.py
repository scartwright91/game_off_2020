
import pygame as pg
import sys
from .level_parser import create_level, find_player_pos, calculate_world_size
from .player import Player
from .camera import CameraAwareLayeredUpdates
from .animations import *


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()

        # Load animations
        self.animations = {
            "droid": load_droid_animations()
        }

        # Create sprite groups
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.foreground = pg.sprite.Group()
        self.background = pg.sprite.Group()

        # Create player, camera and level
        self.level = 1
        pos = find_player_pos(self.level)
        self.world_size = calculate_world_size(self.level)
        self.player = Player(pos, self)
        self.camera = CameraAwareLayeredUpdates(self.player, self.screen_size, self.world_size)
        create_level(self, self.level)

    def run(self):
        # main game loop
        self.playing = True
        self.game_complete = False

        while self.playing:
            self.clock.tick(60)
            self.events()
            self.update()
            self.draw()

        return self.game_complete

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False

    def update(self):
        self.camera.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.camera.draw(self.screen, self.background)
        self.camera.draw(self.screen, self.platforms)
        self.camera.draw(self.screen, self.enemies)
        self.camera.draw(self.screen, self.foreground)
        self.camera.draw(self.screen, self.projectiles)
        self.player.draw(self.screen, self.camera.cam)
        pg.display.flip()

