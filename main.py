import time
import pygame # type: ignore
from settings import *
from board import Board
from block import *
from button import Button


class Minesweeper:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set the window size and title
        self.screen = pygame.display.set_mode((WIDTH + 300, HEIGHT + 100))
        pygame.display.set_caption("2 Player Minesweeper")

        # Initialize buttons
        self.new_game_button = Button("New Game", WIDTH / 2 + 25, HEIGHT + 10, WIDTH / 2 - 50, 80, (100, 100, 100), self.new_game)
        self.rules_button = Button("Rules", 25, HEIGHT + 10,  WIDTH / 2 - 50, 80, (100, 100, 100), self.show_rules)
        
        self.player_1_banner = Button("Player 1 Turn", WIDTH + 25, 25, 250, 80, (0, 0, 255), None)
        self.player_2_banner = Button("Player 2 Turn", WIDTH + 25, 25, 250, 80, (0, 255, 0), None)
        self.player_1_wins = Button("Player 1 WINS!!", WIDTH + 25, 25, 250, 80, (0, 0, 255), None)
        self.player_2_wins = Button("Player 2 WINS!!", WIDTH + 25, 25, 250, 80, (0, 255, 0), None)

        self.display_scores = Button("", WIDTH + 25, 300, 250, 125, (100, 100, 100), None)

        # Initialize game attributes
        self.board = None
        self.start_time = None
        self.countdown_timer = 10
        self.current_player = 1
        self.winner = None
        self.player_scores = [0, 0]

    def new_game(self):
        """Starts a new game."""
        self.board = Board()
        self.start_time = None
        self.winner = None
        self.current_player = 1
        self.player_scores = [0, 0]

    def show_rules(self):
        """Displays the rules."""
        rules_screen = pygame.Surface((WIDTH + 300, HEIGHT + 100))
        rules_screen.fill(BG_COLOR)

        rules_text = [
            "Rules:",
            "1. The game follows the rules of minesweeper, with some additions!",
            f"2. Player 1 starts the game and plays for {self.countdown_timer} seconds.",
            f"3. After that ends, it's Player 2's turn for {self.countdown_timer} seconds.",
            "4. This cycle of switching turns repeats.",
            "5. The timer only starts for your turn when you first click/flag a block!",
            "6. Each player earns 1 point for each block that gets revealed (flags do not count).",
            "7. Avoid clicking on bombs, or you lose!",
            "8. If all blocks are cleared, the player with more points wins (player 2 wins tiebreakers)!",
            "9. Clearing the very last block gives some bonus points!",
            "10. Click New Game to start a new game."
        ]
        
        font = pygame.font.Font(pygame.font.get_default_font(), 18)
        y_offset = 50
        for rule in rules_text:
            rule_surface = font.render(rule, True, (255, 255, 255))
            rules_screen.blit(rule_surface, (25, y_offset))
            y_offset += 30

        # Create a back button
        back_button = Button("Back", WIDTH - 150, HEIGHT - 50, 100, 40, (100, 100, 100), self.new_game)

        # Display the rules screen
        self.screen.blit(rules_screen, (0, 0))
        back_button.display(self.screen)
        pygame.display.flip()

        # Handle events
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if back_button.clicked((x, y)):
                        return

    def run(self):
        """Starts the game loop."""
        self.new_game()
        self.running = True
        while self.running:
            self.handle_events()
            self.display()
        
        self.end_game()

    def handle_events(self):
        """Handles events during the game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button(event)

    def handle_mouse_button(self, event):
        """
        Handles mouse clicks during the game.
        :param event: User event
        """
        x, y = pygame.mouse.get_pos()

        if self.new_game_button.clicked((x, y)):
            return
        if self.rules_button.clicked((x, y)):
            return

        if y >= HEIGHT or x >= WIDTH:
            return
        
        if not self.start_time:
            self.start_time = pygame.time.get_ticks()

        x //= BLOCK_SIZE
        y //= BLOCK_SIZE

        if event.button == 1:
            self.handle_left_mouse_button(x, y)
        elif event.button == 3:
            self.handle_right_mouse_button(x, y)

        if self.all_cleared():
            # Handle game ending after all tiles are cleared
            self.running = False
            self.flag_remaining_tiles()
            self.player_scores[self.current_player - 1] += (ROWS * COLS) // 10
            if self.player_scores[0] > self.player_scores[1]:
                self.winner = 1
            else:
                self.winner = 2

    def all_cleared(self):
        """
        Checks if all non-bomb blocks are cleared.
        :return: True if all hint tiles in the board have been revealed
        """
        for i in range(ROWS):
            for j in range(COLS):
                if self.board.board[i][j].type == HINT and not self.board.board[i][j].revealed:
                    return False
        return True
    
    def flag_remaining_tiles(self):
        """Flags remaining tiles after game end."""
        for i in range(ROWS):
            for j in range(COLS):
                if not self.board.board[i][j].revealed:
                    self.board.board[i][j].flagged = True
    
    def handle_left_mouse_button(self, x, y):        
        """
        Handles left mouse button click.
        :param x: Location of the x coordinate on the board
        :param y: Location of the y coordinate on the board
        """
        if self.board.board[x][y].flagged:
            return
        
        if self.board.board[x][y].type == BOMB:
            # Handle when a bomb is clicked
            self.board.board[x][y].image = game_settings.images.boom
            self.explode()
            self.winner = 3 - self.current_player
        else:
            self.player_scores[self.current_player - 1] += self.board.floodfill(x, y)

    def explode(self):
        """Handles game explosion (when a bomb is clicked)."""
        for i in range(ROWS):
            for j in range(COLS):
                # Reveal all bombs that have not been flagged
                if self.board.board[i][j].type == BOMB and not self.board.board[i][j].flagged:
                    self.board.board[i][j].revealed = True
                # Reveal all incorrect flags
                elif self.board.board[i][j].type != BOMB and self.board.board[i][j].flagged:
                    self.board.board[i][j].image = game_settings.images.not_bomb
                    self.board.board[i][j].revealed = True
        self.running = False

    def handle_right_mouse_button(self, x, y):
        """
        Handles right mouse button click.
        :param x: Location of the x coordinate on the board
        :param y: Location of the y coordinate on the board
        """
        if not self.board.board[x][y].revealed:
            self.board.board[x][y].flagged = not self.board.board[x][y].flagged

    def display(self):
        """Displays the game."""
        self.screen.fill(BG_COLOR)
        self.board.display(self.screen)
        self.new_game_button.display(self.screen)
        self.rules_button.display(self.screen)
        self.display_scores.display(self.screen)
        self.timer()

        if self.winner== 1:
            self.player_1_wins.display(self.screen)
        elif self.winner == 2:
            self.player_2_wins.display(self.screen)
        elif self.current_player == 1:
            self.player_1_banner.display(self.screen)
        else:
            self.player_2_banner.display(self.screen)

        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        player1_score_text = f"Player 1 Score: {self.player_scores[0]}"
        player2_score_text = f"Player 2 Score: {self.player_scores[1]}"
        player1_surface = font.render(player1_score_text, True, (255, 255, 255))
        player2_surface = font.render(player2_score_text, True, (255, 255, 255))
        self.screen.blit(player1_surface, (WIDTH + 40, 320))
        self.screen.blit(player2_surface, (WIDTH + 40, 380))

        pygame.display.flip()

    def timer(self):
        """Displays the timer and switches the player turn."""
        if self.start_time:
            elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            remaining_time = max(self.countdown_timer - elapsed_time, 0)
            if remaining_time == 0:
                self.switch_player()
            timer_text = f"Timer: {remaining_time}"
        else:
            timer_text = f"Timer: {self.countdown_timer}"
        
        self.display_timer(timer_text)
    
    def display_timer(self, timer_text):
        """
        Displays the timer.
        :param timer_text: Text to display on the timer
        """
        font = pygame.font.Font(pygame.font.get_default_font(), 50)
        timer_surface = font.render(timer_text, True, (255, 0, 0))
        self.screen.blit(timer_surface, (WIDTH + 40, 175))

    def switch_player(self):
        """Switches the player turn and displays a stop screen."""
        # Create a new surface for the stop screen
        stop_screen = pygame.Surface((WIDTH + 300, HEIGHT + 100))
        stop_screen.fill(BG_COLOR)

        self.current_player = 3 - self.current_player

        # Render stop message
        font = pygame.font.Font(pygame.font.get_default_font(), 50)
        message = f"STOP! It's now Player {self.current_player}'s turn"
        message_surface = font.render(message, True, (255, 0, 0))
        stop_screen.blit(message_surface, (WIDTH / 2 - 225, HEIGHT / 2 - 50))

        # Display the stop screen
        self.screen.blit(stop_screen, (0, 0))
        pygame.display.flip()

        # Wait for 2 seconds
        time.sleep(2)
        
        self.start_time = None

    def end_game(self):
        """Handles the end of the game."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # Only start a new game when the new game button is clicked
                    if self.new_game_button.clicked((x, y)):
                        return

    def quit(self):
        """Quits the game."""
        pygame.quit()
        quit(0)


def main():
    minesweeper = Minesweeper()
    while True:
        minesweeper.run()


if __name__ == '__main__':
   main()