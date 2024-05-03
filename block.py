from settings import *


# Define constants for tile types
UNKNOWN = "."
BOMB = "X"
HINT = "H"


class Block:
    def __init__(self, x, y):
        self.x = x * BLOCK_SIZE
        self.y = y * BLOCK_SIZE
        self.flagged = False
        self.revealed = False
        self.image = game_settings.images.zero
        self.type = UNKNOWN

    def display(self, board):
        """
        Display the block.
        :param board: Game board
        """
        image = self.image
        if not self.revealed:
            if self.flagged:
                image = game_settings.images.flag
            else:
                image = game_settings.images.unknown

        board.blit(image, (self.x, self.y))