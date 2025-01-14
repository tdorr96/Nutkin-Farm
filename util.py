import os
import pygame
import random
from settings import *
from pygame.math import Vector2


def list_folder(path_to_folder):
    # On Mac OS, get .DS_Store files, this function wraps around OS to filter those out in a packaged neat function
    # Use in place of any normal os.listdir function calls

    return filter(lambda f: not f.startswith('.'), os.listdir(path_to_folder))


def import_image(path_to_image, scale=True):

    image = pygame.image.load(path_to_image).convert_alpha()
    if scale:
        image = pygame.transform.scale_by(image, ZOOM_FACTOR)
    return image


def import_folder(path_to_folder, scale=True):

    frames = []

    for f in sorted(list_folder(path_to_folder), key=lambda f: int(f.split('.')[0])):
        path_to_file = os.path.join(path_to_folder, f)
        frames.append(import_image(path_to_file, scale=scale))

    return frames


def import_folder_as_dict(path_to_folder, scale=True):

    frames = {}

    for f in list_folder(path_to_folder):
        path_to_file = os.path.join(path_to_folder, f)
        frames[f.split('.')[0]] = import_image(path_to_file, scale=scale)

    return frames


def import_folders_as_lists(path_to_root_folder, scale=True):

    frames = {}

    for folder in list_folder(path_to_root_folder):
        frames[folder] = import_folder(os.path.join(path_to_root_folder, folder), scale=scale)

    return frames


def random_game_pixel_position():

    return random.randint(0, GAME_WIDTH), random.randint(0, GAME_HEIGHT)


def collide_line(start_point, end_point, collision_sprites, offset=None, interval=TILE_SIZE/10):
    # Checks if a line from the start to end point would collide with any of the collision sprites
    # We check at small intervals along line if any collision has taken place
    # We can add a offset, which basically shifts the line in a certain direction, useful as sometimes rects too broad
    # and want to narrow the collision line check

    if not isinstance(start_point, Vector2):
        start_point = Vector2(start_point)
    if not isinstance(end_point, Vector2):
        end_point = Vector2(end_point)

    if offset is None:
        current_point = start_point.copy()
    else:
        current_point = start_point + offset
        end_point = end_point + offset

    direction = (end_point - current_point).normalize()
    while True:
        current_point += direction * interval
        if any(s.hitbox.collidepoint(current_point) for s in collision_sprites.sprites()):
            return True
        if distance_between_vectors(end_point, current_point) < interval:
            return False


def distance_between_vectors(v1, v2):

    if not isinstance(v1, Vector2):
        v1 = Vector2(v1)
    if not isinstance(v2, Vector2):
        v2 = Vector2(v2)

    return (v1 - v2).magnitude()


def distance_between_sprites(s1, s2):

    return distance_between_vectors(s1.rect.center, s2.rect.center)
