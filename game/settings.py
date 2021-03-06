
import json

# Game settings
TILE_SIZE = 16
TILE_SCALE = 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
FONT_SIZE = 50
DIALOGUE_SIZE = 20
GRAVITY = 1

with open("levels/level.json") as f:
    level_data = json.load(f)
