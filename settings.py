import math

import pygame
from pygame.math import Vector2


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ZOOM_FACTOR = 4
TILE_SIZE = 16 * ZOOM_FACTOR
TILES_WIDE, TILE_HIGH = 50, 50
FPS = 60  # Max frame rate
GAME_WIDTH = TILE_SIZE * TILES_WIDE
GAME_HEIGHT = TILE_SIZE * TILE_HIGH


Z_LAYERS = {
    'water': 0,
    'ground': 1,
    'weather floor particles': 2,
    'main': 3,
    'house roof': 4,
    'weather falling particles': 5
}

PLAYER_TOOL_OFFSET = {
    # Map from tool and direction facing to a vector offset from center of player where the action position happens
    'axe': {
        'left': Vector2(-45, 40),
        'right': Vector2(45, 40),
        'down': Vector2(-10, 60),
        'up': Vector2(10, -40)
    },
    'water': {
        'left': Vector2(-80, 40),
        'right': Vector2(80, 40),
        'down': Vector2(-10, 60),
        'up': Vector2(10, -40)
    },
    'hoe': {
        'left': Vector2(-50, 40),
        'right': Vector2(50, 40),
        'down': Vector2(-10, 50),
        'up': Vector2(10, -40)
    }
}

PLAYER_TOOL_ACTION_FRAME_INDEX = {
    # Frame index for each tool animation we want to activate the action on
    'axe': 5,
    'water': 3,
    'hoe': 5
}

PLAYER_TOOL_ACTION_KEY_MAP = {
    # Map from keyboard key press to which tool starts animation for
    pygame.K_c: 'axe',
    pygame.K_w: 'water',
    pygame.K_h: 'hoe'
}

TREE_MAX_HEALTH = 5
STUMP_HEALTH = 2

UI_POSITIONING = {
    'daytime': {
        'offset': (5, 5)
    },
    'skills': {
        'offset': (10, WINDOW_HEIGHT - 10)
    }
}

DAYS_OF_WEEK = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
DAY_LENGTH = 100
DAY_SPEED = 5
DAY_INTERVALS = 5  # We keep this at 5 to correspond with how many arrows are in UI
DAY_DIVISIONS = [i/DAY_INTERVALS for i in range(1, DAY_INTERVALS+1)]
TEMPERATURE_RANGE = list(range(9))  # There are 9 corresponding files for temperature thermometer options, 0-8.png
SNOW_TEMPERATURE = 1
HOT_TEMPERATURE = 7
assert HOT_TEMPERATURE >= SNOW_TEMPERATURE + 3  # We drop temperature by 2 at night

SKY_MAX_LUMINANCE = 255
SKY_MIN_LUMINANCE = 175
SKY_LUMINANCE_COEFFICIENT = (math.pi * 3) / (2 * DAY_LENGTH)

WEATHER_PARTICLES = {
    'frequency': 150,  # Defines a timer duration that every time-out we add some weather particles
    'rain': {
        # Medium rain drops
        'duration': {'min': 4000, 'max': 8000},
        'amount': 400,
        'speed': {'min': 110, 'max': 140},
        'animation_speed': 4,
        'direction': (-1, 1)
    },
    'snowy': {
        # Medium snowflakes
        'duration': {'min': 3000, 'max': 7000},
        'amount': 400,
        'speed': {'min': 90, 'max': 120},
        'animation_speed': 4,
        'direction': (-1, 1)
    },
    'thunder': {
        # Medium-high rain drops
        'duration': {'min': 4000, 'max': 8000},
        'amount': 1000,
        'speed': {'min': 110, 'max': 140},
        'animation_speed': 4,
        'direction': (-1, 1)
    },
    'heavy_rain': {
        # High rain drops
        'duration': {'min': 4000, 'max': 8000},
        'amount': 1600,
        'speed': {'min': 140, 'max': 180},
        'animation_speed': 4,
        'direction': (-1, 1)
    },
    'default': {
        # Any other weather is low grass blowing
        'duration': {'min': 4000, 'max': 6000},
        'amount': 100,
        'speed': {'min': 60, 'max': 80},
        'animation_speed': 3,
        'direction': (1, 0.2)
    }
}


WEATHER_THUNDER = {
    'duration': 200,     # If thunder active, how long the flashes last for
    'frequency': {       # How frequently we activate thunder (random duration between these two numbers)
        'min': 500,      # I.e. gaps between start of flashes
        'max': 2000
    },
    'intensity': 3       # Number between 0 and 10 (inclusive): how frequently thunder flashes white if it's active
}

# Ensures a good gap between thunder stopping & starting again
assert WEATHER_THUNDER['duration'] * 2 < WEATHER_THUNDER['frequency']['min']

DEBUG = False
DEBUG_OPTIONS = {
    'fps': True,
    'player': {
        'rect': True,
        'hitbox': True,
        'tool_target_pos': True,
        'status vars': True
    },
    'collisions': {
        'hitbox': True,
        'rect': True
    },
    'trees': {
      'interaction_rect': True
    },
    'npcs': {
        'running': False,
        'rect': False,
        'interaction_rect': False
    },
    'uis': {
        'active ui': True
    },
    'transitions': {
        'is_active': True,
        'is_cutscene_playing': True
    },
    'day': {
        'time': True,
        'time_division': True,
        'current_luminance': True,
        'weather': True,
        'temp': True
    },
}
