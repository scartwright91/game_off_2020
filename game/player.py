

import pygame as pg
from .settings import *


class Player(pg.sprite.Sprite):

    def __init__(self, pos, game):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE * TILE_SCALE, TILE_SIZE * TILE_SCALE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos)
        self.game = game
        self.grounded = False
        self.facing_right = True
        self.speed = 8
        self.jump = 20
        self.vel = pg.Vector2(0, 0)

    def update(self):
        
        pressed = pg.key.get_pressed()

        jump = pressed[pg.K_w]
        left = pressed[pg.K_a]
        right = pressed[pg.K_d]

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

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x + camera.x, self.rect.y + camera.y))