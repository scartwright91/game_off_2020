
import pygame as pg


# Complex camera class
class CameraAwareLayeredUpdates(pg.sprite.LayeredUpdates):
    def __init__(self, target, screen_size):
        super().__init__()
        self.target = target
        self.cam = pg.Vector2(0, 0)
        self.screen_size = screen_size
        if self.target:
            self.add(target)

    def update(self, *args):
        super().update(*args)
        if self.target:
            x = -self.target.rect.center[0] + self.screen_size[0]/2
            y = -self.target.rect.center[1] + self.screen_size[1]/2
            self.cam += (pg.Vector2((x, y)) - self.cam) * 0.15

    def draw(self, surface, spritegroup):
        spritedict = self.spritedict
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in spritegroup:
            rec = spritedict[spr]
            draw_pos = spr.rect.move(self.cam)
            newrect = surface.blit(spr.image, draw_pos)
            # # If sprite has additional draw method
            # if hasattr(spr, 'draw'):
            #     spr.draw(surface, draw_pos)
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty