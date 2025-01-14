import os
import random
import sys

import pygame
from settings import *
from util import *
from pytmx.util_pygame import load_pygame


def import_sprite_sheet(cols, rows, path):

    frames = {}
    surf = pygame.image.load(path).convert_alpha()

    cell_width = surf.get_width()/cols
    cell_height = surf.get_height()/rows

    for col in range(cols):
        for row in range(rows):

            x, y = col*cell_width, row*cell_height
            cutout_rect = pygame.Rect(x, y, cell_width, cell_height)
            cutout_surf = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
            cutout_surf.blit(surf, (0, 0), cutout_rect)
            frames[(col, row)] = cutout_surf

    return frames


def tighten_bounding_rect(path):

    surf = pygame.image.load(path).convert_alpha()

    bounding_rect = surf.get_bounding_rect()

    new_surf = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
    new_surf.blit(surf, (0, 0), bounding_rect)

    pygame.image.save(new_surf, path)


def scale_by(path, scale):

    surf = pygame.image.load(path).convert_alpha()
    surf = pygame.transform.scale_by(surf, scale)
    pygame.image.save(surf, path)


def flip(path, x, y):

    surf = pygame.image.load(path).convert_alpha()
    surf = pygame.transform.flip(surf, x, y)
    pygame.image.save(surf, path)


if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    #
    # frames = import_sprite_sheet(4, 3, 'graphics/ui/skills/icons/tools-n-meterial-items.png')

    woodcutting = pygame.image.load('graphics/ui/skills/icons/woodcutting.png').convert_alpha()
    farming = pygame.image.load('graphics/ui/skills/icons/farming.png').convert_alpha()

    base = pygame.image.load('graphics/ui/skills/interface_base.png').convert_alpha()

    base.blit(woodcutting, (15, 95))
    base.blit(farming, (15, 170))

    pygame.image.save(base, 'graphics/ui/skills/interface.png')





