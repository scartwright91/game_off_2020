
import pygame as pg
import math
from .settings import *


def read_image(path, w=None, h=None, create_surface=False):

    img = pg.image.load(path)

    if (w == None) and (h == None):
        pass
    elif h == None:
        scale = w / img.get_width()
        h = scale * img.get_height()
        img = pg.transform.scale(img, (int(w), int(h)))
    elif w == None:
        scale = h / img.get_height()
        w = scale * img.get_width()
        img = pg.transform.scale(img, (int(w), int(h)))
    else:
        img = pg.transform.scale(img, (int(w), int(h)))
    
    if create_surface:
        image = pg.Surface(img.get_rect().size, pg.SRCALPHA, 32)
        image.blit(img, (0, 0))
        return image
    else:
        return img

def draw_text(screen, text, color, x, y, center=False, size=None):
    font = pg.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_dialogue(screen, text, color, x, y, size=None):
    font = pg.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    
    # Background rect
    bg_rect = text_rect.copy()
    bg_rect.w += 20
    bg_rect.h += 50
    bg_rect.y -= 20
    bg_rect.x -= 10

    # Frame rect
    frame_rect = bg_rect.copy()
    frame_rect.center = bg_rect.center
    frame_rect.w += 10
    frame_rect.h += 10
    frame_rect.x -= 5
    frame_rect.y -= 5

    # Drawing
    pg.draw.rect(screen, (62, 44, 27), frame_rect)
    pg.draw.rect(screen, (184, 139, 97), bg_rect)
    screen.blit(text_surface, text_rect)

def wait_for_key(game):
    waiting = True
    while waiting:
        game.clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                game.playing = False
            if event.type == pg.KEYUP:
                waiting = False

def draw_circle_alpha(surface, color, center, radius, width):
    target_rect = pg.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pg.Surface(target_rect.size, pg.SRCALPHA)
    pg.draw.circle(shape_surf, color, (radius, radius), radius, width)
    surface.blit(shape_surf, target_rect)

