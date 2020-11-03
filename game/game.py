
import pygame as pg
import sys
from .level_parser import create_level


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()

        # Create sprite groups
        self.platforms = pg.sprite.Group()

        # Create level
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
        pass

    def draw(self):
        self.screen.fill((255, 255, 255))
        for p in self.platforms:
            p.draw(self.screen)
        pg.display.flip()

