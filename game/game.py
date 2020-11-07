
import pygame as pg
import sys
from .level_parser import create_level, find_player_pos
from .player import Player
from .camera import CameraAwareLayeredUpdates


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()

        # Create sprite groups
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        # Create player, camera and level
        pos = find_player_pos()
        self.player = Player(pos, self)
        self.camera = CameraAwareLayeredUpdates(self.player, self.screen_size)
        create_level(self)

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
        self.camera.draw(self.screen, self.platforms)
        self.camera.draw(self.screen, self.enemies)
        self.player.draw(self.screen, self.camera.cam)
        pg.display.flip()

