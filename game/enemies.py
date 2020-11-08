import pygame as pg
import math
from shapely.geometry import Polygon
from .settings import *



class RangeAttack(pg.sprite.Sprite):
    def __init__(self, pos, player, screen, platforms, game):
        super().__init__(game.projectiles, game.camera)
        self.pos = [pos[0], pos[1]]
        self.player = player
        self.screen = screen
        self.platforms = platforms
        self.camera = game.camera
        self.player_pos = player.rect.center
        self.image = pg.Surface((30, 30), pg.SRCALPHA)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(midtop=pos)
        self.speed = 8
        self.x_delta = (self.player_pos[0] - self.pos[0])
        self.y_delta = -(self.player_pos[1] - self.pos[1])
        self.theta = math.atan2(self.y_delta, self.x_delta) + math.pi/2
        self.theta_change = False
        self.x = self.pos[0]
        self.y = self.pos[1]

    def update(self):

        # Delete if projectiles leaves screen
        if abs(self.rect.x - self.player.rect.x > self.screen.get_width()) or abs(self.rect.y - self.player.rect.y > self.screen.get_height()):
            self.kill() 

        # Make hypoteneuse equal to the speed value, calculate incremental x, y values
        h = self.speed
        
        # Calculate opposite and adjacent sides using SOHCAHTOA
        x_increment = h * math.sin(self.theta)
        y_increment = h * math.cos(self.theta)

        # Update x,y values
        self.x += x_increment
        self.y += y_increment

        self.rect.topleft = pg.Vector2(self.x, self.y)

        self.poly = Polygon([
            (self.rect.topleft[0]+ self.camera.cam.x, self.rect.topleft[1] + self.camera.cam.y),
            (self.rect.topright[0]+ self.camera.cam.x, self.rect.topright[1] + self.camera.cam.y),
            (self.rect.bottomright[0] + self.camera.cam.x, self.rect.bottomright[1] + self.camera.cam.y),
            (self.rect.bottomleft[0] + self.camera.cam.x, self.rect.bottomleft[1] + self.camera.cam.y),
        ])

        # If projectile collides with player's deflective shield, change
        # the angle of the projectile
        if self.player.poly is not None and not self.theta_change:
            if self.poly.intersects(self.player.poly):
                self.theta_change = True
                theta_delta = 2*self.player.theta_orthog - self.theta
                self.theta = theta_delta
                
                #self.kill()

        # Write collision method (projectile is removed on collision)
        if pg.sprite.collide_rect(self, self.player):
            self.kill()
        for p in self.platforms:
            if pg.sprite.collide_rect(self, p):
                self.kill()



class Droid(pg.sprite.Sprite):

    def __init__(self, pos, patrol, game, *groups):
       super().__init__(*groups)
       self.image = pg.Surface((TILE_SIZE * TILE_SCALE, 2 * TILE_SIZE * TILE_SCALE))
       self.image.fill(RED)
       self.rect = self.image.get_rect(topleft=[pos[0] * TILE_SCALE, pos[1] * TILE_SCALE])
       self.game = game
       self.player = self.game.player
       self.platforms = self.game.platforms
       self.patrol = patrol
       self.patrol_index = 0
       self.facing_left = True
       self.speed = 2
       self.patrol_timer = pg.time.get_ticks()
       self.attacking = False
       self.attacking_timer = pg.time.get_ticks()

    def update(self):

        # State logic
        if self.facing_left and (self.rect.x - self.player.rect.x) < 600:
            self.attacking = True
        else:
            self.attacking = False

        # Patrolling
        if (pg.time.get_ticks() - self.patrol_timer > 1500) and not self.attacking:
            if self.facing_left:
                self.rect.x -= self.speed
                if self.rect.x <= self.patrol[self.patrol_index].x:
                    self.facing_left = False
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol)
                    self.patrol_timer = pg.time.get_ticks()
            else:
                self.rect.x += self.speed
                if self.rect.x >= self.patrol[self.patrol_index].x:
                    self.facing_left = True
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol)
                    self.patrol_timer = pg.time.get_ticks()

        # Attacking
        if self.attacking and (pg.time.get_ticks() - self.attacking_timer > 1500):
            self.attacking_timer = pg.time.get_ticks()
            self.attack()

    def attack(self):
        RangeAttack(self.rect.center,
                    self.player,
                    self.game.screen,
                    self.platforms,
                    self.game)

