import random
import pygame # type: ignore
from settings import *
from block import *


class Board:
    def __init__(self):
        # Initialize the board and displayed_board
        self.displayed_board = pygame.Surface((WIDTH, HEIGHT))
        self.board = [[None] * COLS for i in range(ROWS)]
        self.init_board()
        self.init_bombs()
        self.init_hints()

    def init_board(self):
        """Initializes the game board."""
        for i in range(ROWS):
            for j in range(COLS):
                self.board[i][j] = Block(i, j)

    def init_bombs(self):
        """Initializes bomb locations."""
        bombs_placed = 0
        while bombs_placed < BOMB_COUNT:
            i = random.randint(0, ROWS - 1)
            j = random.randint(0, COLS - 1)

            if self.board[i][j].type == UNKNOWN:
                self.board[i][j].type = BOMB
                self.board[i][j].image = game_settings.images.bomb
                bombs_placed += 1

    def init_hints(self):
        """Initializes hint numbers."""
        for i in range(ROWS):
            for j in range(COLS):
                if self.board[i][j].type == UNKNOWN:
                    surrounding_bombs = self.count_bombs(i, j)
                    if surrounding_bombs > 0:
                        self.board[i][j].type = HINT
                        self.board[i][j].image = game_settings.images.numbers[surrounding_bombs - 1]

    def out_of_bounds(self, x, y):
        """
        Checks if the given coordinates are out of bounds.
        :param x: Location of the x coordinate on the board
        :param y: Location of the y coordinate on the board
        :return: If the coordinate (x,y) are within the board's boundaries
        """
        return x < 0 or x >= ROWS or y < 0 or y >= COLS

    def count_bombs(self, x, y):
        """
        Counts the number of bombs surrounding a block.
        :param x: Location of the x coordinate on the board
        :param y: Location of the y coordinate on the board
        :return: Number of bombs surrounding coordinate (x,y)
        """
        dirx = [-1, -1, -1, 0, 0, 1, 1, 1]
        diry = [-1, 0, 1, -1, 1, -1, 0, 1]
        count = 0
        for i in range(len(dirx)):
            if not self.out_of_bounds(x + dirx[i], y + diry[i]) and self.board[x + dirx[i]][y + diry[i]].type == BOMB:
                count += 1
        return count
    
    def display(self, screen):
        """
        Displays the game board.
        :param screen: Game screen
        """
        for i in range(ROWS):
            for j in range(COLS):
                self.board[i][j].display(self.displayed_board)

        screen.blit(self.displayed_board, (0, 0))

    def floodfill(self, x, y):
        """
        Performs a flood fill algorithm to reveal open squares from (x,y).
        :param x: Location of the x coordinate on the board
        :param y: Location of the y coordinate on the board
        :return: Number of blocks revealed from the flood fill algorithm
        """
        queue = [[x, y]]
        dirx = [-1, -1, -1, 0, 0, 1, 1, 1]
        diry = [-1, 0, 1, -1, 1, -1, 0, 1]
        blocks_revealed = 0
        while len(queue):
            top = queue.pop()
            x = top[0]
            y = top[1]

            if self.board[x][y].type == BOMB or self.board[x][y].flagged or self.board[x][y].revealed:
                continue

            self.board[x][y].revealed = True
            blocks_revealed += 1

            if self.board[x][y].type == HINT:
                continue

            # Flood towards nearby regions
            for i in range(len(dirx)):
                if not self.out_of_bounds(x + dirx[i], y + diry[i]):
                    queue.append([x + dirx[i], y + diry[i]])

        return blocks_revealed
