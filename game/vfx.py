
import pygame as pg



class Particle(pg.sprite.Sprite):

    def __init__(self, pos, radius_growth, radius_limit, colour, *groups):
        super().__init__(*groups)
        self.radius = 1
        self.colour = colour
        self.pos = pos
        self.radius_limit = radius_limit
        self.radius_growth = radius_growth

    def update(self):
        self.radius += self.radius_growth
        if self.radius > self.radius_limit:
            self.kill()

    def draw(self, screen, camera):
        #pg.draw.circle(screen, (34, 30, 49), (self.pos[0] + camera.x, self.pos[1] + camera.y), self.radius + 2)
        pg.draw.circle(screen, self.colour, (self.pos[0] + camera.x, self.pos[1] + camera.y), self.radius)
