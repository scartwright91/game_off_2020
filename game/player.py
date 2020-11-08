import pygame as pg
import math
from shapely.geometry import Polygon
from .settings import *



class DeflectMove(pg.sprite.Sprite):

    def __init__(self, mouse_pos, player_pos):
        self.mouse_pos = mouse_pos
        self.player_pos = player_pos

    def update(self):
        self.x_delta = (self.mouse_pos[0] - self.player_pos[0])
        self.y_delta = -(self.mouse_pos[1] - self.player_pos[1])
        self.theta = math.atan2(self.y_delta, self.x_delta) + math.pi/2
        self.shield = pg.Vector2(
            100 * math.sin(self.theta),
            100 * math.cos(self.theta)
        )



class Player(pg.sprite.Sprite):

    def __init__(self, pos, game):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE * TILE_SCALE, 2 * TILE_SIZE * TILE_SCALE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos)
        self.game = game
        self.grounded = False
        self.facing_right = True
        self.shielding = False
        self.speed = 6
        self.jump = 20
        self.vel = pg.Vector2(0, 0)

        # shield deflect
        self.shield_mask = None
        self.poly = None

    def update(self):
        
        pressed = pg.key.get_pressed()

        jump = pressed[pg.K_w]
        left = pressed[pg.K_a]
        right = pressed[pg.K_d]
        shield = pressed[pg.K_SPACE]

        if shield:
            self.shielding = True
        else:
            self.shielding = False
            self.shield_mask = None
            self.poly = None

        if jump and self.grounded:
            self.vel.y = -self.jump
            self.grounded = False
        if left:
            self.facing_right = False
            self.vel.x = -self.speed
        if right:
            self.facing_right = True
            self.vel.x = self.speed
        if not(left or right):
            self.vel.x = 0

        # Gravity logic
        if not self.grounded:
            self.vel.y += GRAVITY
            # Limit gravity
            if self.vel.y > 100:
                self.vel.y = 100

        # Adjust x offset
        self.rect.x += self.vel.x
        # check x-axis collision
        self.collide(self.vel.x, 0)

        # y-axis logic
        self.rect.top += self.vel.y
        # Check y-axis collision
        self.grounded = False
        self.collide(0, self.vel.y)

    def collide(self, xvel, yvel):
        for p in self.game.platforms:
            if pg.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.vel.y = 0
                    self.grounded = True
                if yvel < 0:
                    self.rect.top = p.rect.bottom

    def shield_deflect(self, screen):

        mouse_pos = pg.mouse.get_pos()
        center_pos = [screen.get_width()/2, screen.get_height()/2]

        x_delta = (mouse_pos[0] - center_pos[0])
        y_delta = (center_pos[1] - mouse_pos[1])
        theta = math.atan2(y_delta, x_delta) + math.pi/2
        self.theta_orthog = theta + math.pi/2

        shield_center = {
            "lower": pg.Vector2(
                center_pos[0] + 95 * math.sin(theta),
                center_pos[1] + 95 * math.cos(theta)
            ),
            "upper": pg.Vector2(
                center_pos[0] + 105 * math.sin(theta),
                center_pos[1] + 105 * math.cos(theta)
            )
        }
        shield_lower = {
            "lower": pg.Vector2(
                shield_center["lower"][0] - 50 * math.sin(self.theta_orthog),
                shield_center["lower"][1] - 50 * math.cos(self.theta_orthog)
            ),
            "upper": pg.Vector2(
                shield_center["upper"][0] - 50 * math.sin(self.theta_orthog),
                shield_center["upper"][1] - 50 * math.cos(self.theta_orthog)
            )
        }
        shield_upper = {
            "lower": pg.Vector2(
                shield_center["lower"][0] + 50 * math.sin(self.theta_orthog),
                shield_center["lower"][1] + 50 * math.cos(self.theta_orthog)
            ),
            "upper": pg.Vector2(
                shield_center["upper"][0] + 50 * math.sin(self.theta_orthog),
                shield_center["upper"][1] + 50 * math.cos(self.theta_orthog)
            )
        }

        # Shield coordinates
        shield_poly = [
            shield_lower["lower"],
            shield_lower["upper"],
            shield_upper["upper"],
            shield_upper["lower"]
        ]

        # Create surface and blit poly
        shield_surface = pg.Surface((1200, 800), pg.SRCALPHA)
        pg.draw.polygon(shield_surface, BLUE, shield_poly)

        # Create poly
        self.poly = Polygon(shield_poly)

        # Extract mask
        self.shield_mask = pg.mask.from_surface(shield_surface)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x + camera.x, self.rect.y + camera.y))
        if self.shielding:
            # Calculate shield position
            self.shield_deflect(screen)
            #print(list(zip(*self.poly.exterior.coords.xy)))
            #pg.draw.polygon(screen, BLUE, self.shield_poly)
            pg.draw.lines(screen, BLUE, 1, self.shield_mask.outline())
