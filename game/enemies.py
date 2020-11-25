import pygame as pg
import math
import random
import os
from shapely.geometry import Polygon
from .settings import *
from .utils import read_image
from .vfx import Particle



class RangeAttack(pg.sprite.Sprite):
    def __init__(self, sprite, pos, player, screen, platforms, game):
        super().__init__(game.projectiles, game.entities, game.camera)
        self.sprite = sprite
        self.pos = [pos[0], pos[1]]
        self.player = player
        self.screen = screen
        self.platforms = platforms
        self.game = game
        self.camera = game.camera
        self.enemies = game.enemies
        self.bosses = game.bosses
        self.player_pos = player.rect.center
        projectile_image = read_image("assets/images/projectile_sprite.png",
                                      w=24, h=24)
        self.image = pg.Surface((24, 24), pg.SRCALPHA)
        self.image.blit(projectile_image, (0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 12
        self.x_delta = (self.player_pos[0] - self.pos[0])
        self.y_delta = -(self.player_pos[1] - self.pos[1])
        self.theta = math.atan2(self.y_delta, self.x_delta) + math.pi/2
        self.sprite.theta = 180*(self.theta/math.pi)
        self.theta_change = False
        self.x = self.pos[0]
        self.y = self.pos[1]

    def update(self):

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
                self.game.sound_effects["deflect"].play()
                self.theta_change = True
                theta_delta = 2*self.player.theta_orthog - self.theta
                self.theta = theta_delta
        else:
            for e in self.enemies:
                if pg.sprite.collide_rect(self, e):
                    self.explode()
                    e.disabled = True
                    e.disabled_timer = pg.time.get_ticks()
                    e.current_frame = 0
            for boss in self.bosses:
                if pg.sprite.collide_rect(self, boss):
                    self.explode()
                    boss.image_index += 1

        # Write collision method (projectile is removed on collision)
        if pg.sprite.collide_rect(self, self.player):
            if self.player.alpha > 0:
                self.player.alpha -= min([75, self.player.alpha])
            else:
                self.player.alive = False
            self.explode()
        for p in self.platforms:
            if pg.sprite.collide_rect(self, p):
                self.explode()

        # Update sprite's theta
        self.sprite.theta = self.theta

    def explode(self):
        self.game.sound_effects["explosion"].play()
        Particle(self.rect.center, 10, 70, (65, 72, 93), self.game.particles, self.game.camera)
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
       self.disabled = False
       self.disabled_timer = pg.time.get_ticks()

       # Animations
       self.animation_images = game.animations["droid"]
       self.last_update = pg.time.get_ticks()
       self.current_frame = 0
       self.image.blit(self.animation_images["standing"]["right"][self.current_frame], (0, 0))

    def update(self):

        self.animate()

        now = pg.time.get_ticks()
        if now - self.disabled_timer > 2500:
            self.disabled = False

        if self.disabled:
            return None

        # Detect player logic
        if self.facing_left and self.rect.x > self.player.rect.x:
            self.detect_player()
        elif not self.facing_left and self.rect.x < self.player.rect.x:
            self.detect_player()

        # Patrolling
        if (now - self.patrol_timer > 1500) and not self.attacking:
            if self.facing_left:
                self.rect.x -= self.speed
                if self.rect.x <= self.patrol[self.patrol_index].x:
                    self.facing_left = False
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol)
                    self.patrol_timer = now
            else:
                self.rect.x += self.speed
                if self.rect.x >= self.patrol[self.patrol_index].x:
                    self.facing_left = True
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol)
                    self.patrol_timer = now

        # Attacking
        if self.attacking and (now - self.attacking_timer > 1500):
            self.game.sound_effects["laser"].play()
            self.attacking_timer = now
            self.attack()

    def detect_player(self):

        if abs(self.rect.x - self.player.rect.x) < 800:
            self.attacking = True
            for p in self.platforms:
                clip = p.rect.clipline(self.rect.center, self.player.rect.center)
                if clip:
                    self.attacking = False
                    break
        else:
            self.attacking = False

    def attack(self):
        RangeAttack(self,
                    self.rect.center,
                    self.player,
                    self.game.screen,
                    self.platforms,
                    self.game)

    def animate(self):

        now = pg.time.get_ticks()

        if self.disabled:
            if self.facing_left:
                if now - self.last_update > 100:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['disabled']["left"])
                    self.image = self.animation_images['disabled']["left"][self.current_frame]
            else:
                if now - self.last_update > 100:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.animation_images['disabled']["right"])
                    self.image = self.animation_images['disabled']["right"][self.current_frame]
        else:
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
        self.turret_mount = read_image("assets/images/turret_mount.png",
                                 w=2*TILE_SIZE*TILE_SCALE,
                                 h=2*TILE_SIZE*TILE_SCALE)
        self.turret_gun = read_image("assets/images/turret.png",
                                 w=2*TILE_SIZE*TILE_SCALE,
                                 h=2*TILE_SIZE*TILE_SCALE)
        self.image = pg.Surface(self.turret_gun.get_size(), pg.SRCALPHA)
        self.mount_image = pg.Surface(self.turret_mount.get_size(), pg.SRCALPHA)
        self.mount_image.blit(self.turret_mount, (0, 0))
        self.mount_image_copy = self.mount_image.copy()
        self.animation_images = game.animations["droid"]
        self.image.blit(self.turret_gun, (0, 0))
        self.pos = (pos[0] * TILE_SCALE, pos[1] * TILE_SCALE)
        self.rect = self.image.get_rect(midtop=(self.pos[0], self.pos[1] - 30))
        self.mount_rect = self.mount_image.get_rect(midtop=self.pos)
        self.game = game
        self.player = self.game.player
        self.platforms = self.game.platforms
        self.attacking = False
        self.attacking_timer = pg.time.get_ticks()
        self.theta = 2*math.pi
        self.disabled = False
        self.disabled_timer = pg.time.get_ticks()

        self.last_update = pg.time.get_ticks()
        self.current_frame = 0

    def update(self):

        self.animate()

        now = pg.time.get_ticks()
        if now - self.disabled_timer > 2500:
            self.disabled = False

        if self.disabled:
            return None

        # Detect player logic
        self.detect_player()

        # Attacking
        if self.attacking and (pg.time.get_ticks() - self.attacking_timer > 1500):
            self.game.sound_effects["laser"].play()
            self.attacking_timer = pg.time.get_ticks()
            self.attack()

    def animate(self):
        now = pg.time.get_ticks()
        if self.disabled:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.animation_images['turret'])
                self.mount_image_copy = self.animation_images['turret'][self.current_frame]
        else:
            self.mount_image_copy = self.mount_image


    def detect_player(self):

        if abs(self.rect.x - self.player.rect.x) > 800:
            self.attacking = False
        else:
            self.attacking = True
            for p in self.platforms:
                clip = p.rect.clipline(self.rect.center, self.player.rect.center)
                if clip:
                    self.attacking = False
                    break

    def attack(self):

        RangeAttack(self,
                    self.rect.center,
                    self.player,
                    self.game.screen,
                    self.platforms,
                    self.game)

        self.image = pg.transform.rotate(self.turret_gun, self.theta)
        self.rect = self.image.get_rect(midtop=(self.pos[0], self.pos[1] - 30))
        
    def draw(self, screen, camera):
        screen.blit(self.mount_image_copy, (self.mount_rect.x + camera.x, self.mount_rect.y + camera.y))



class ElectricField(pg.sprite.Sprite):

    def __init__(self, tile_meta, sound_effect, *groups):
        super().__init__(*groups)
        self.tile_meta = tile_meta
        self.sound_effect = sound_effect
        self.pos = [tile_meta["px"][0] * TILE_SCALE, tile_meta["px"][1] * TILE_SCALE]

        # images
        self.electric_field = read_image("assets/images/electric_field.png",
                                         w=2*TILE_SIZE*TILE_SCALE,
                                         h=4*TILE_SIZE*TILE_SCALE,
                                         create_surface=True)
        self.images = []
        for img_path in os.listdir("assets/animations/electric_field/"):
            self.images.append(
                read_image("assets/animations/electric_field/" + img_path,
                           w=2*TILE_SIZE*TILE_SCALE,
                           h=4*TILE_SIZE*TILE_SCALE,
                           create_surface=True)
            )
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=self.pos)

        # animations
        self.timer = pg.time.get_ticks()
        self.index = 0

        # activation
        self.active = True
        self.active_timer = pg.time.get_ticks()
        self.sound_effect.play()

    def update(self):

        now = pg.time.get_ticks()

        if self.active:
            if now - self.timer > 100:
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
                self.timer = pg.time.get_ticks()
            if now - self.active_timer > 1000:
                self.sound_effect.stop()
                self.active = False
                self.active_timer = pg.time.get_ticks()
        else:
            self.image = self.electric_field
            if now - self.active_timer > 1000:
                self.sound_effect.play(0)
                self.active = True
                self.active_timer = pg.time.get_ticks()



class Boss(pg.sprite.Sprite):

    def __init__(self, game, tile_meta, *groups):
        super().__init__(*groups)
        self.game = game
        self.pos = [tile_meta["px"][0] * TILE_SCALE, tile_meta["px"][1] * TILE_SCALE]
        self.boss_images = self.load_images()
        self.image = self.boss_images[0]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image_index = 0
        self.exploding = False
        self.explode_timer = pg.time.get_ticks()

    def update(self):

        if self.exploding:
            if pg.time.get_ticks() - self.explode_timer > 2000:
                self.kill()
            else:
                self.explode()
        else:
            if self.image_index > len(self.boss_images) - 1:
                self.explode_timer = pg.time.get_ticks()
                self.exploding = True
            else:
                self.image = self.boss_images[self.image_index]

    def load_images(self):
        boss_path = "assets/images/boss/"
        boss_images = []
        for img in os.listdir(boss_path):
            boss_images.append(
                read_image(boss_path + img, w=6*TILE_SIZE*TILE_SCALE, h=6*TILE_SIZE*TILE_SCALE, create_surface=True)
            )
        return boss_images

    def explode(self):
        pos = (self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-100, 100))
        radius = random.randint(50, 250)
        col = (65, 72, 93)
        self.game.sound_effects["explosion"].play()
        Particle(pos, radius/10, radius, col, self.game.camera, self.game.particles, self.game.entities)
