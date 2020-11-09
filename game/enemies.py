import pygame as pg
import math
from shapely.geometry import Polygon
from .settings import *
from .utils import read_image



class RangeAttack(pg.sprite.Sprite):
    def __init__(self, pos, player, screen, platforms, game):
        super().__init__(game.projectiles, game.camera)
        self.pos = [pos[0], pos[1]]
        self.player = player
        self.screen = screen
        self.platforms = platforms
        self.camera = game.camera
        self.enemies = game.enemies
        self.player_pos = player.rect.center
        projectile_image = read_image("assets/images/projectile_sprite.png",
                                      w=24, h=24)
        self.image = pg.Surface((24, 24), pg.SRCALPHA)
        self.image.blit(projectile_image, (0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
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
        if not self.theta_change:
            if self.poly.intersects(self.player.poly):
                self.theta_change = True
                theta_delta = 2*self.player.theta_orthog - self.theta
                self.theta = theta_delta
        else:
            for e in self.enemies:
                if pg.sprite.collide_rect(self, e):
                    self.kill()
                    e.kill()

        # Write collision method (projectile is removed on collision)
        if pg.sprite.collide_rect(self, self.player):
            self.kill()
        for p in self.platforms:
            if pg.sprite.collide_rect(self, p):
                self.kill()



class Droid(pg.sprite.Sprite):

    def __init__(self, pos, patrol, game, *groups):
       super().__init__(*groups)
       self.image = pg.Surface((1.5*TILE_SIZE * TILE_SCALE, 1.5*2 * TILE_SIZE * TILE_SCALE))
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

       # Animations
       self.animation_images = game.animations["droid"]
       self.last_update = pg.time.get_ticks()
       self.current_frame = 0
       self.image.blit(self.animation_images["standing"]["right"][self.current_frame], (0, 0))

    def update(self):

        self.animate()

        # Detect player logic
        if self.facing_left and self.rect.x > self.player.rect.x:
            self.detect_player()
        elif not self.facing_left and self.rect.x < self.player.rect.x:
            self.detect_player()

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

    def detect_player(self):

        self.attacking = True
        for p in self.platforms:
            clip = p.rect.clipline(self.rect.center, self.player.rect.center)
            if clip:
                self.attacking = False
                break

    def attack(self):
        RangeAttack(self.rect.center,
                    self.player,
                    self.game.screen,
                    self.platforms,
                    self.game)

    def animate(self):

        now = pg.time.get_ticks()

        if self.facing_left:
            if (pg.time.get_ticks() - self.patrol_timer < 1500):
                if now - self.last_update > 600:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['standing']["left"])
                    self.image = self.animation_images['standing']["left"][self.current_frame]
            else:
                self.image = self.animation_images['standing']["left"][0]
        else:
            if (pg.time.get_ticks() - self.patrol_timer < 1500):
                if now - self.last_update > 600:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['standing']["right"])
                    self.image = self.animation_images['standing']["right"][self.current_frame]
            else:
                self.image = self.animation_images['standing']["right"][0]



class Turret(pg.sprite.Sprite):

    def __init__(self, pos, game, *groups):
       super().__init__(*groups)
       self.image = pg.Surface((TILE_SIZE * TILE_SCALE, TILE_SIZE * TILE_SCALE))
       self.image.fill((255, 0, 255))
       self.rect = self.image.get_rect(topleft=[pos[0] * TILE_SCALE, pos[1] * TILE_SCALE])
       self.game = game
       self.player = self.game.player
       self.platforms = self.game.platforms
       self.attacking = False
       self.attacking_timer = pg.time.get_ticks()

    def update(self):

        # Detect player logic
        self.detect_player()

        # Attacking
        if self.attacking and (pg.time.get_ticks() - self.attacking_timer > 1500):
            self.attacking_timer = pg.time.get_ticks()
            self.attack()

    def detect_player(self):

        self.attacking = True
        for p in self.platforms:
            clip = p.rect.clipline(self.rect.center, self.player.rect.center)
            if clip:
                self.attacking = False
                break

    def attack(self):
        RangeAttack(self.rect.center,
                    self.player,
                    self.game.screen,
                    self.platforms,
                    self.game)