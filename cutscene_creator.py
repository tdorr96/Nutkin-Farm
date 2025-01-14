import sys
import time
import math
import pygame
from util import *
from settings import *
from pygame.math import Vector2
from sprites import Animated, Generic
from pytmx.util_pygame import load_pygame


# Custom Z_LAYERS, different from normal operation as we want, for example, player behind bridge in drawing order
Z_LAYERS_BOAT = {
    'water': 0,
    'ground': 1,
    'player': 2,
    'bridge': 3,
    'tree': 4,
    'npcs': 5,
    'text box': 6
}


class PlayerBoat(pygame.sprite.Sprite):
    # Regular sprite that animates and moves. Starts left/right of map depending on direction of travel

    def __init__(self, pos, frames, groups, travel_direction):

        super().__init__(groups)

        self.z = Z_LAYERS_BOAT['player']

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        if travel_direction == 'right':
            self.rect = self.image.get_rect(midright=pos)
            self.direction = Vector2(1, 0)
        else:
            self.rect = self.image.get_rect(midleft=pos)
            self.direction = Vector2(-1, 0)

        self.pos = Vector2(self.rect.center)
        self.speed = 175

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def move(self, dt):

        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt):

        self.move(dt)
        self.animate(dt)


class TextBox(pygame.sprite.Sprite):
    # Sprite representing a text box, that drops down in top-left corner
    # And once dropped-down animates through a string of text we render

    def __init__(self, pos, text_str, groups, z):

        super().__init__(groups)

        self.z = z

        self.bg_image = import_image('graphics/ui/cutscenes/dropdown_box/boat_cutscene_box.png', scale=False)
        self.image = self.bg_image.copy()

        self.rect = self.image.get_rect(topleft=pos)

        self.font = pygame.font.Font('graphics/font/sproutLands.ttf', 16)
        self.character_index = 0
        self.render_speed = 5
        self.text_str = text_str
        self.total_characters = len(self.text_str)

        self.y_offset = 0
        self.y_speed = 90
        self.y_max = 130
        self.original_y = pos[1]

    def update(self, dt):

        if self.y_offset < self.y_max:
            # Still moving down to dropped-down position

            self.y_offset += self.y_speed * dt
            self.rect.y = self.original_y + self.y_offset

        else:

            self.character_index += self.render_speed * dt

            if 0 < int(self.character_index) <= self.total_characters:
                string_to_render = self.text_str[:int(self.character_index)]
                text_surf = self.font.render(string_to_render, False, 'Black')
                text_surf.set_alpha(100)
                new_image = self.bg_image.copy()
                new_image.blit(text_surf, (15, 50))
                self.image = new_image


class BoatCutsceneCreator:
    # Main class to load in .tmx file and generate the required number of frames
    # Roughly generating 1 frame each time there is some movement/animation, to cut down on frames we load & store

    def __init__(self, travel_direction):

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.travel_direction = travel_direction
        self.import_assets()
        self.all_sprites = pygame.sprite.Group()
        self.setup()
        self.display_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    def import_assets(self):

        self.assets = {
            'background': import_image('data/tmx/boat_cutscene.png'),
            'water frames': import_folder('graphics/water'),
            'chicken frames': import_folder('graphics/chicken/light/left_peck'),
            'cow frames': import_folder('graphics/cow/light/right_graze'),
            'boat frames': import_folder('graphics/objects/boat/player_moving/%s' % self.travel_direction)
        }

    def setup(self):

        tmx_data = load_pygame('data/tmx/boat_cutscene.tmx')

        # Background
        Generic(
            pos=(0, 0),
            surf=self.assets['background'],
            groups=self.all_sprites,
            z=Z_LAYERS_BOAT['ground']
        )

        # Text Box
        TextBox(
            pos=(10, -130),
            text_str='Some time later ...',
            groups=self.all_sprites,
            z=Z_LAYERS_BOAT['text box']
        )

        # Water
        for x, y, _ in tmx_data.get_layer_by_name('Water').tiles():
            Animated(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                frames=self.assets['water frames'],
                groups=self.all_sprites,
                z=Z_LAYERS_BOAT['water']
            )

        # Bridge
        for x, y, surf in tmx_data.get_layer_by_name('Bridge').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_BOAT['bridge']
            )

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Generic(
                pos=(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR),
                surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_BOAT['tree']
            )

        # NPCs
        for obj in tmx_data.get_layer_by_name('NPCs'):
            Animated(
                pos=(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR),
                frames=self.assets['%s frames' % obj.name.lower()],
                groups=self.all_sprites,
                animation_speed=3,
                z=Z_LAYERS_BOAT['npcs']
            )

        # Player & Boat
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.properties['travel_direction'] == self.travel_direction:
                PlayerBoat(
                    pos=(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR),
                    frames=self.assets['boat frames'],
                    groups=self.all_sprites,
                    travel_direction=self.travel_direction
                )

    def run(self, frames_to_generate):

        for i in range(frames_to_generate):

            self.all_sprites.update(dt=1/25)
            self.output_frame(i)

    def output_frame(self, frame_number):

        self.display_image.fill('black')

        for sprite in sorted(self.all_sprites.sprites(), key=lambda s: (s.z, s.rect.centery, s.rect.centerx)):
            self.display_image.blit(sprite.image, sprite.rect)

        pygame.image.save(self.display_image, 'graphics/cutscene/boat/%s/%s.png' % (self.travel_direction, frame_number))


Z_LAYERS_SLEEPING = {
    'ground': 1,
    'main': 2,
    'player': 3,
    'zs': 4
}


class SleepyZ(pygame.sprite.Sprite):

    def __init__(self, pos, fonts, groups):

        super().__init__(groups)

        self.z = Z_LAYERS_SLEEPING['zs']

        self.fonts = fonts
        self.font_index = 0
        self.animation_speed = 1
        self.image = self.fonts[self.font_index].render('Z', False, 'White')

        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = Vector2(self.rect.center)
        self.direction = Vector2(1, -1).normalize()
        self.speed = 15

    def animate(self, dt):

        self.font_index += 3 * dt
        if self.font_index >= len(self.fonts):
            self.kill()
        else:
            self.image = self.fonts[int(self.font_index)].render('Z', False, 'White')
            self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, dt):

        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt):

        self.move(dt)
        self.animate(dt)


class PlayerSleeping(pygame.sprite.Sprite):

    def __init__(self, pos, frames, groups):

        super().__init__(groups)

        self.z = Z_LAYERS_SLEEPING['player']

        # Get just the head
        self.frames = []
        for f in frames:
            cropped_f = pygame.Surface((14 * ZOOM_FACTOR, 11 * ZOOM_FACTOR), pygame.SRCALPHA)
            cropped_f.blit(f, (0, 0), pygame.Rect((17 * ZOOM_FACTOR, 15 * ZOOM_FACTOR), (14 * ZOOM_FACTOR, 11 * ZOOM_FACTOR)))
            scaled_f = pygame.transform.scale_by(cropped_f, 0.8)
            self.frames.append(scaled_f)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 2
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):

        self.animate(dt)


class SleepingCutsceneCreator:
    # We use main map.tmx and offset all the tiles to put house in center of screen

    def __init__(self):

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.import_assets()
        self.all_sprites = pygame.sprite.Group()
        self.sleepyz_sprites = pygame.sprite.Group()
        self.map_offset = Vector2(TILE_SIZE * 14, 0)
        self.fonts = [
            pygame.font.Font('graphics/font/sproutLands.ttf', font_size) for font_size in [32, 16, 8]
        ]
        self.setup()
        self.display_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    def import_assets(self):

        self.assets = {
            'background': import_image('data/tmx/map.png'),
            'chicken frames': import_folder('graphics/chicken/light/left_sleep'),
            'cow 1 frames': import_folder('graphics/cow/light/right_sleep'),
            'cow 2 frames': import_folder('graphics/cow/brown/left_sleep'),
            'player frames': [import_image('graphics/player/down_idle/%s.png' % i) for i in range(1, 3)]
        }

    def setup(self):

        tmx_data = load_pygame('data/tmx/map.tmx')

        # Background
        Generic(
            pos=-self.map_offset,
            surf=self.assets['background'],
            groups=self.all_sprites,
            z=Z_LAYERS_SLEEPING['ground']
        )

        # Player
        self.player_head = PlayerSleeping(
            pos=(220 * ZOOM_FACTOR, 64 * ZOOM_FACTOR),
            frames=self.assets['player frames'],
            groups=self.all_sprites
        )

        # Sleeping Zs
        SleepyZ(
            pos=self.player_head.rect.topright,
            fonts=self.fonts,
            groups=[self.all_sprites, self.sleepyz_sprites]
        )

        # Hack in some animating animals to scene
        for animal in [
            ('chicken', (45 * ZOOM_FACTOR, 70 * ZOOM_FACTOR)),
            ('cow 1', (125 * ZOOM_FACTOR, 0.1 * ZOOM_FACTOR)),
            ('cow 2', (275 * ZOOM_FACTOR, 120 * ZOOM_FACTOR))
        ]:
            Animated(
                pos=animal[1],
                frames=self.assets['%s frames' % animal[0]],
                groups=self.all_sprites,
                animation_speed=3,
                z=Z_LAYERS_SLEEPING['main']
            )

        # Bushes
        for x, y, surf in tmx_data.get_layer_by_name('Bushes').tiles():
            Generic(
                pos=Vector2(x * TILE_SIZE, y * TILE_SIZE) - self.map_offset,
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

        # Fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(
                pos=Vector2(x * TILE_SIZE, y * TILE_SIZE) - self.map_offset,
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Generic(
                pos=Vector2(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR) - self.map_offset,
                surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

        # House Walls
        for x, y, surf in tmx_data.get_layer_by_name('House Walls').tiles():
            Generic(
                pos=Vector2(x * TILE_SIZE, y * TILE_SIZE) - self.map_offset,
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

        # House Furniture Top
        for x, y, surf in tmx_data.get_layer_by_name('House Furniture Top').tiles():
            Generic(
                pos=Vector2(x * TILE_SIZE, y * TILE_SIZE) - self.map_offset,
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

        # House Furniture Interaction
        for obj in tmx_data.get_layer_by_name('House Furniture Interaction'):
            if obj.name == 'Bed':
                Generic(
                    pos=Vector2(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR) - self.map_offset,
                    surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                    groups=self.all_sprites,
                    z=Z_LAYERS_SLEEPING['main']
                )

        # Decoration Top
        for obj in tmx_data.get_layer_by_name('Decoration Top'):
            Generic(
                pos=Vector2(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR) - self.map_offset,
                surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS_SLEEPING['main']
            )

    def run(self, frames_to_generate):

        for i in range(frames_to_generate):

            self.all_sprites.update(dt=1/5)
            if len(self.sleepyz_sprites.sprites()) == 0:
                SleepyZ(
                    pos=self.player_head.rect.topright,
                    fonts=self.fonts,
                    groups=[self.all_sprites, self.sleepyz_sprites]
                )
            self.output_frame(i)

    def output_frame(self, frame_number):

        self.display_image.fill('black')

        for sprite in sorted(self.all_sprites.sprites(), key=lambda s: (s.z, s.rect.centery, s.rect.centerx)):
            self.display_image.blit(sprite.image, sprite.rect)

        pygame.image.save(self.display_image, 'graphics/cutscene/sleeping/%s.png' % frame_number)


class CutsceneTestPlay:
    # Class for testing purposes, to just play through the cutscene we generated to view it
    # We set animation speed custom for each cutscene, which we worked out was the smoothest for least amount of frames
    # See level.py when initating transitions to know what this should be

    def __init__(self, path_to_cutscene_frames, animation_speed):

        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.all_sprites = pygame.sprite.Group()
        self.cutscene_animation = Animated(
            pos=(0, 0),
            frames=import_folder(path_to_cutscene_frames, scale=False),
            groups=self.all_sprites,
            animation_speed=animation_speed
        )

    def run(self):

        last_time = time.time()
        while True:

            dt = time.time() - last_time
            last_time = time.time()

            self.display_surface.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.all_sprites.update(dt)

            if self.cutscene_animation.frame_index == 0 and dt != 0.0:
                pygame.quit()
                sys.exit()

            self.all_sprites.draw(self.display_surface)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':

    SleepingCutsceneCreator().run(20)
    # CutsceneTestPlay('graphics/cutscene/sleeping', 3).run()

    # BoatCutsceneCreator('right').run(210)
    # CutsceneTestPlay('graphics/cutscene/boat/right', 25).run()
