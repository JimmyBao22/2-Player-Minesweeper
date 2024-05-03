import pygame # type: ignore


class Button:
    def __init__(self, text, x, y, width, height, color, function):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.function = function

    def display(self, screen):
        """
        Display the button.
        :param screen: Game screen
        """
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def clicked(self, pos):
        """
        Check if the button is clicked.
        :param pos: User mouse position
        :return: Whether the user mouse position is inside the button
        """
        if self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height:
            self.function()
            return True
        return False