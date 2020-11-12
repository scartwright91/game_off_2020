
import pygame as pg
import sys
import random
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

        # Load background
        self.background_images = {
            "moon": read_image("assets/images/moon.png", w=128*TILE_SCALE, h=128*TILE_SCALE)
        }
        
        self.stars = []
        for _ in range(30):
            x = random.randint(0, self.screen_size[0])
            y = random.randint(0, self.screen_size[1]/2)
            star_type = random.choice(["star1", "star2"])
            star_dim = random.randint(2, 15)
            star = read_image("assets/images/{}.png".format(star_type), w=star_dim, h=star_dim)

            self.stars.append({"star": star, "xy": (x, y)})

        # Create sprite groups
        self.entities = pg.sprite.Group()
        self.endpoints = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.foreground = pg.sprite.Group()
        self.background = pg.sprite.Group()

        # Create player, camera and level
        self.level = 0
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

        # Create new level if player touches endpoint
        for endpoint in self.endpoints:
            if pg.sprite.collide_rect(self.player, endpoint):
                self.level = endpoint.connected_level
                pos = find_player_pos(self.level)
                self.camera.world_size = calculate_world_size(self.level)
                self.player.rect.topleft = pos
                create_level(self, self.level)

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Background
        for star in self.stars:
            self.screen.blit(star["star"], star["xy"])
        self.screen.blit(self.background_images["moon"], (700 + self.camera.cam.x*0.05, 100 + self.camera.cam.y*0.05))

        self.camera.draw(self.screen, self.background)
        self.camera.draw(self.screen, self.platforms)
        self.camera.draw(self.screen, self.enemies)
        self.camera.draw(self.screen, self.foreground)
        self.camera.draw(self.screen, self.projectiles)
        self.player.draw(self.screen, self.camera.cam)
        pg.display.flip()

