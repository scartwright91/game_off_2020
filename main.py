 
import pygame as pg
from game.game import Game
from game.menu import StartMenu, GameMenu, EndGameMenu
import pygame, os

os.environ['SDL_VIDEO_CENTERED'] = '1'


def main():

    running = True
    playing = False

    pg.init()
    pg.mixer.init()
    #screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    screen = pg.display.set_mode((1200, 800), pg.SRCALPHA)
    clock = pg.time.Clock()

    start_menu = StartMenu(screen, clock)
    game_menu = GameMenu(screen, clock)

    while running:

        start_menu = StartMenu(screen, clock)
        start_timer = pg.time.get_ticks()
        game_menu = GameMenu(screen, clock)
        game = Game(screen, clock)

        playing = start_menu.run()
        while playing:
            complete, lost = game.run()
            if complete:
                end_game_menu = EndGameMenu(screen, clock, start_timer)
                end_game_menu.run()
                running = False
            elif lost:
                playing = False
            else:
                playing = game_menu.run()

if __name__ == '__main__':
    main()
