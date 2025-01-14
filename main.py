import time
import pygame
from settings import *
from level import Level


class Game:

    def __init__(self):

        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.SCALED, vsync=1)
        pygame.display.set_caption('Cup Nooble')
        self.clock = pygame.time.Clock()

        # Custom mouse cursor
        mouse_surf = pygame.transform.scale_by(pygame.image.load('graphics/ui/mouse_icon.png').convert_alpha(), 1.5)
        cursor = pygame.cursors.Cursor((5, 5), mouse_surf)
        pygame.mouse.set_cursor(cursor)

        # Create the level
        self.level = Level()

    def run(self):

        last_time = time.time()
        while True:

            # Delta-Time
            dt = time.time() - last_time
            last_time = time.time()

            # Clear Frame
            self.display_surface.fill('black')

            # Run Level
            self.level.run(dt)

            # Update Display Surface
            pygame.display.update()

            # Limit Max Frame Rate
            self.clock.tick(FPS)


if __name__ == '__main__':

    Game().run()
