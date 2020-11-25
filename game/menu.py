
import pygame as pg
import sys
import random
from .utils import *



class StartMenu:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()

        # Load background
        self.background_images = {
            "moon": read_image("assets/images/moon.png", w=128*TILE_SCALE, h=128*TILE_SCALE)
        }
        
        # Create stars
        self.small_stars = []
        for _ in range(40):
            x = random.randint(0, self.screen_size[0])
            y = random.randint(0, self.screen_size[1])
            star_type = random.choice(["star1", "star2"])
            star_dim = random.randint(2, 5)
            star = read_image("assets/images/{}.png".format(star_type), w=star_dim, h=star_dim)

            self.small_stars.append({"star": star, "xy": (x, y)})
        self.big_stars = []
        for _ in range(10):
            x = random.randint(0, self.screen_size[0])
            y = random.randint(0, self.screen_size[1])
            star_type = random.choice(["star1", "star2"])
            star_dim = random.randint(5, 15)
            star = read_image("assets/images/{}.png".format(star_type), w=star_dim, h=star_dim)

            self.big_stars.append({"star": star, "xy": (x, y)})

    def run(self):
        self.menu_running = True
        while self.menu_running:
            self.clock.tick(60)
            self.update()
            self.draw()
        return True

    def update(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.menu_running = False
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

    def draw(self):

        mouse_pos = pg.mouse.get_pos()

        self.screen.fill((0, 0, 0))

        for star in self.small_stars:
            self.screen.blit(star["star"], (star["xy"][0] - mouse_pos[0] * 0.03, star["xy"][1] - mouse_pos[1] * 0.03))
        for star in self.big_stars:
            self.screen.blit(star["star"], (star["xy"][0] - mouse_pos[0] * 0.1, star["xy"][1] - mouse_pos[1] * 0.1))

        draw_text(self.screen,
                  'Start menu',
                  color=(255, 255, 255),
                  x=self.screen_size[0]*0.5,
                  y=self.screen_size[1]*0.3,
                  center=True,
                  size=100)

        pg.display.flip()



class GameMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()
        self.playing = True

    def run(self):
        self.menu_running = True
        while self.menu_running:
            self.clock.tick(60)
            self.update()
            self.draw()
        return self.playing

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.menu_running = False
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    self.menu_running = False

    def draw(self):

        self.screen.fill((0, 0, 0))

        draw_text(self.screen,
                  'Game menu',
                  color=(255, 255, 255),
                  x=self.screen_size[0]*0.5,
                  y=self.screen_size[1]*0.3,
                  center=True,
                  size=100)

        pg.display.flip()



class EndGameMenu:
    def __init__(self, screen, clock, start_timer):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()
        end_timer = pg.time.get_ticks()
        self.completion_timer = (end_timer - start_timer)/1000
        self.playing = True

    def run(self):
        self.menu_running = True
        while self.menu_running:
            self.clock.tick(60)
            self.update()
            self.draw()
        return self.playing

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

    def draw(self):

        self.screen.fill((0, 0, 0))

        draw_text(self.screen,
                  'Completed in {} seconds'.format(round(self.completion_timer, 2)),
                  color=(255, 255, 255),
                  x=self.screen_size[0]*0.5,
                  y=self.screen_size[1]*0.3,
                  center=True,
                  size=100)

        pg.display.flip()