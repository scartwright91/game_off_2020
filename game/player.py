import pygame as pg
import math
import os
from shapely.geometry import Polygon
from .settings import *
from .utils import *



class Player(pg.sprite.Sprite):

    def __init__(self, pos, game):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE * TILE_SCALE, 2 * TILE_SIZE * TILE_SCALE), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.game = game
        self.grounded = False
        self.jump_active = True
        self.double_jump_active = True
        self.facing_right = True
        self.shielding = False
        self.speed = 6
        self.jump_val = 20
        self.jump_timer = pg.time.get_ticks()
        self.vel = pg.Vector2(0, 0)
        self.alive = True

        # shield deflect
        self.alpha = 255
        self.poly = None
        self.shield_available = True

        # Animations
        self.animation_images = self.load_animations()
        self.last_update = pg.time.get_ticks()
        self.current_frame = 0
        self.image.blit(self.animation_images["standing"]["right"][self.current_frame], (0, 0))

    def update(self):

        self.animate()
        
        pressed = pg.key.get_pressed()

        jump = pressed[pg.K_SPACE]
        left = pressed[pg.K_a]
        right = pressed[pg.K_d]

        if jump and (pg.time.get_ticks() - self.jump_timer > 300) and self.shield_available: self.jump()

        # Movement logic
        if left:
            self.image = self.animation_images['running']["left"][self.current_frame]
            self.facing_right = False
            self.vel.x = -self.speed
        if right:
            self.image = self.animation_images['running']["right"][self.current_frame]
            self.facing_right = True
            self.vel.x = self.speed
        if not(left or right):
            self.vel.x = 0

        # Electric field logic
        self.shield_available = True
        for ef in self.game.electric_fields:
            if ef.active:
                if pg.sprite.collide_rect(self, ef):
                    self.vel.x = 0
                    self.shield_available = False

        # Gravity logic
        if not self.grounded:
            self.vel.y += GRAVITY
            # Limit gravity
            if self.vel.y > 100:
                self.vel.y = 100

        # Adjust x offset
        if self.rect.x <= 0 and self.vel.x < 0:
            pass
        else:
            self.rect.x += self.vel.x
        # check x-axis collision
        self.collidex(self.vel.x)

        # y-axis logic
        self.rect.top += self.vel.y
        # Check y-axis collision
        self.grounded = False
        self.collidey(self.vel.y)

    def jump(self):
        self.jump_timer = pg.time.get_ticks()
        # jump and double jump logic
        if self.jump_active:
            self.vel.y -= self.jump_val
            self.jump_active = False
        elif self.double_jump_active:
            self.vel.y = -self.jump_val
            self.double_jump_active = False

    def collidex(self, xvel):
        for p in self.game.platforms:
            if pg.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right

    def collidey(self, yvel):
        for p in self.game.platforms:
            if pg.sprite.collide_rect(self, p):
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.vel.y = 0
                    self.grounded = True
                    self.jump_active = True
                    self.double_jump_active = True
                    if p.moving and self.shield_available:
                        self.rect.x += self.speed
                if yvel < 0:
                    self.rect.top = p.rect.bottom

    def shield_deflect(self, screen):

        mouse_pos = pg.mouse.get_pos()
        center_pos = (self.rect.centerx + self.game.camera.cam.x, self.rect.centery + self.game.camera.cam.y)

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
        self.shield_poly = [
            shield_lower["lower"],
            shield_lower["upper"],
            shield_upper["upper"],
            shield_upper["lower"]
        ]

        # Create surface and blit poly
        shield_surface = pg.Surface((1200, 800), pg.SRCALPHA)
        pg.draw.polygon(shield_surface, BLUE, self.shield_poly)

        # Create poly
        self.poly = Polygon(self.shield_poly)

        # Extract mask
        self.shield_mask = pg.mask.from_surface(shield_surface)

    def load_animations(self):

        standing_animations = {
            "left": [],
            "right": []
        }
        img_dir = "assets/animations/player/standing/"
        for img_path in os.listdir(img_dir):
            img = read_image(img_dir + img_path,
                             w=TILE_SIZE*TILE_SCALE,
                             h=2*TILE_SIZE*TILE_SCALE)
            standing_animations["right"].append(img)
            standing_animations["left"].append(pg.transform.flip(img, True, False))

        running_animations = {
            "left": [],
            "right": []
        }
        img_dir = "assets/animations/player/running/"
        for img_path in os.listdir(img_dir):
            img = read_image(img_dir + img_path,
                             w=TILE_SIZE*TILE_SCALE,
                             h=2*TILE_SIZE*TILE_SCALE)
            running_animations["right"].append(img)
            running_animations["left"].append(pg.transform.flip(img, True, False))

        animation_images = {
            "standing": standing_animations,
            "running": running_animations
        }

        return animation_images

    def animate(self):

        now = pg.time.get_ticks()

        if self.vel.x != 0:
            if self.facing_right:
                if now - self.last_update > 200:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['running']["right"])
                    self.image = self.animation_images['running']["right"][self.current_frame]
            else:
                if now - self.last_update > 200:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['running']["left"])
                    self.image = self.animation_images['running']["left"][self.current_frame]
        else:
            if self.facing_right:
                if now - self.last_update > 600:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['standing']["right"])
                    self.image = self.animation_images['standing']["right"][self.current_frame]
            else:
                if now - self.last_update > 600:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['standing']["left"])
                    self.image = self.animation_images['standing']["left"][self.current_frame]

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x + camera.x, self.rect.y + camera.y))
        if self.shield_available:
            # Calculate shield position
            self.shield_deflect(screen)
        pg.draw.polygon(screen, (197, 219, 212, self.alpha), self.shield_poly)
        draw_circle_alpha(screen,
                          (197, 219, 212, self.alpha),
                          (self.rect.centerx + camera.x, self.rect.centery + camera.y),
                          100,
                          3)
