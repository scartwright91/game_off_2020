
import pygame as pg
import sys
import random
from .level_parser import create_level, find_player_pos, calculate_world_size
from .player import Player
from .camera import CameraAwareLayeredUpdates
from .animations import *
from .utils import draw_text


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.screen_size = self.screen.get_size()

        # Load animations
        self.animations = {
            "droid": load_droid_animations()
        }

        # Load sound effects
        self.sound_effects = {
            "laser": pg.mixer.Sound('assets/music/laserSmall_001.ogg'),
            "explosion": pg.mixer.Sound('assets/music/explosionCrunch_000.ogg'),
            "deflect": pg.mixer.Sound('assets/music/forceField_002.ogg')
        }
        self.sound_effects["laser"].set_volume(0.5)
        self.sound_effects["explosion"].set_volume(0.1)
        self.sound_effects["deflect"].set_volume(0.1)

        # Load background
        self.background_images = {
            "moon": read_image("assets/images/moon.png", w=128*TILE_SCALE, h=128*TILE_SCALE)
        }
        
        # Create stars
        self.stars = []
        for _ in range(40):
            x = random.randint(0, self.screen_size[0])
            y = random.randint(0, self.screen_size[1])
            star_type = random.choice(["star1", "star2"])
            star_dim = random.randint(2, 5)
            star = read_image("assets/images/{}.png".format(star_type), w=star_dim, h=star_dim)

            self.stars.append({"star": star, "xy": (x, y)})
        for _ in range(10):
            x = random.randint(0, self.screen_size[0])
            y = random.randint(0, self.screen_size[1])
            star_type = random.choice(["star1", "star2"])
            star_dim = random.randint(5, 15)
            star = read_image("assets/images/{}.png".format(star_type), w=star_dim, h=star_dim)

            self.stars.append({"star": star, "xy": (x, y)})

        # Create sprite groups
        self.entities = pg.sprite.Group()
        self.endpoints = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.foreground = pg.sprite.Group()
        self.background = pg.sprite.Group()

        # Create player, camera and level
        self.level = 3
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

        self.camera.update(self.level)
        self.particles.update()

        if not self.player.alive:
            self.playing = False

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

        # sprites
        self.camera.draw(self.screen, self.background)
        self.camera.draw(self.screen, self.enemies)
        for particle in self.particles:
            particle.draw(self.screen, self.camera.cam)
        self.camera.draw(self.screen, self.platforms)
        self.camera.draw(self.screen, self.foreground)
        self.camera.draw(self.screen, self.projectiles)
        self.player.draw(self.screen, self.camera.cam)
        draw_text(self.screen, "{}".format(self.clock.get_fps()), (255, 0, 0), 50, 50)
        pg.display.flip()

