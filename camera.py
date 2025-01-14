import pygame
from settings import *


class Camera(pygame.sprite.Group):
    # YSort, Player Centered, with Z Depth, Snapping at window edges

    def __init__(self):

        # Setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

        self.borders = {
            'left': 0,
            'top': 0,
            'bottom': GAME_HEIGHT - WINDOW_HEIGHT,
            'right': GAME_WIDTH - WINDOW_WIDTH
        }

    def custom_draw(self, player, day):

        # Work out the camera offset so we can draw player at center of screen, making sure to snap at sides of screen

        self.offset.x = player.rect.centerx - WINDOW_WIDTH/2
        if self.offset.x < self.borders['left']:
            self.offset.x = self.borders['left']
        elif self.offset.x > self.borders['right']:
            self.offset.x = self.borders['right']

        self.offset.y = player.rect.centery - WINDOW_HEIGHT/2
        if self.offset.y < self.borders['top']:
            self.offset.y = self.borders['top']
        elif self.offset.y > self.borders['bottom']:
            self.offset.y = self.borders['bottom']

        # If we're inside a house, filter out from all the sprites the roof tiles so we don't draw them
        if player.inside_house:
            all_sprites = filter(lambda s: s.z != Z_LAYERS['house roof'], self.sprites())
        else:
            all_sprites = self.sprites()

        # Draw in order of z depth layer, and then within each z layer right-down
        for sprite in sorted(all_sprites, key=lambda s: (s.z, s.rect.centery, s.rect.centerx)):
            self.display_surface.blit(sprite.image, sprite.rect.move(-self.offset))

        # Draw the sky luminance
        day.display()

