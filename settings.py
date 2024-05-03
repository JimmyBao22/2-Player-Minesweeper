import pygame # type: ignore
import os


BG_COLOR = (40, 40, 40)
BLOCK_SIZE = 32
ROWS = 16
COLS = 16
BOMB_COUNT = 40
HEIGHT = BLOCK_SIZE * ROWS
WIDTH = BLOCK_SIZE * COLS


class Images:
    def __init__(self):
        self.numbers = [self.load_image(f"{i}.png") for i in range(1, 9)]
        self.zero = self.load_image("0.png")
        self.boom = self.load_image("boom.png")
        self.flag = self.load_image("flag.png")
        self.bomb = self.load_image("bomb.png")
        self.unknown = self.load_image("unknown.png")
        self.not_bomb = self.load_image("notBomb.png")

    def load_image(self, filename):
        return pygame.transform.scale(pygame.image.load(os.path.join("images", filename)), (BLOCK_SIZE, BLOCK_SIZE))


class GameSettings:
    def __init__(self):
        self.images = Images()


game_settings = GameSettings()