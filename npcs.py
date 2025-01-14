import pygame
import random
from util import *
from settings import *
from timers import Timer
from pygame.math import Vector2


class Animal(pygame.sprite.Sprite):

    def __init__(self, pos, frames, name, walk_area, collision_sprites, groups):

        super().__init__(groups)

        # Image & Animations
        self.frames = frames
        self.frame_index = 0
        self.facing = random.choice(['right', 'left'])
        self.status = 'idle'
        self.image = self.frames[self.facing + '_' + self.status][self.frame_index]
        self.z = Z_LAYERS['main']
        self.animation_speed = random.randint(40, 50)/15

        # Rects
        # Interaction rect is where we have to click/hover over to interact with, a bit shrinked from original rect
        self.rect = self.image.get_rect(center=pos)
        self.interaction_rect = self.rect.inflate(0, -self.rect.height * 0.4)
        self.interaction_rect.midbottom = self.rect.midbottom

        # Float-based movement
        # Target position and direction will be non-None when status is running
        self.pos = Vector2(self.rect.center)
        self.target_pos = None
        self.direction = None

        # Extra attributes
        self.name = name
        self.walk_area = walk_area
        self.collision_sprites = collision_sprites

        # Love hearts
        self.love_hearts = 0
        self.love_timer = Timer(duration=5000)

    def is_idling(self):

        return self.status == 'idle'

    def is_running(self):

        return self.status == 'run'

    def love(self):

        self.status = 'love'
        self.frame_index = 0
        self.love_hearts += 1
        self.love_timer.activate()

    def pick_new_walk_location(self):
        # Called when we enter the run state, to know where we are running to
        # Keep picking randomly until at least 3 tiles away and would not lead us to collide with anything along
        # the line from current center (interaction rect) to final position

        picked_new_pos = False
        while not picked_new_pos:
            random_tile = random.choice(self.walk_area)
            random_x = random.randint(random_tile.left, random_tile.right)
            random_y = random.randint(random_tile.top, random_tile.bottom)
            if distance_between_vectors((random_x, random_y), self.pos) < 3 * TILE_SIZE:
                continue
            if collide_line(self.pos, (random_x, random_y), self.collision_sprites, offset=Vector2(self.interaction_rect.center)-self.pos):
                continue
            picked_new_pos = True

        if random_x < self.pos.x:
            self.facing = 'left'
        else:
            self.facing = 'right'

        self.target_pos = Vector2(random_x, random_y)
        self.direction = (self.target_pos - self.pos).normalize()

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(self.frames[self.facing + '_' + self.status]):
            self.frame_index = 0
            self.refresh_status()

        self.image = self.frames[self.facing + '_' + self.status][int(self.frame_index)]

    def move(self, dt):

        if self.is_running():

            self.pos += self.direction * self.speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))
            self.interaction_rect.midbottom = self.rect.midbottom

            if distance_between_vectors(self.target_pos, self.pos) < TILE_SIZE / 20:
                self.pos = self.target_pos
                self.rect.center = self.target_pos
                self.interaction_rect.midbottom = self.rect.midbottom
                self.direction = None
                self.target_pos = None
                self.frame_index = 0
                self.status = 'idle'

    def update(self, dt):

        self.love_timer.update()
        self.move(dt)
        self.animate(dt)


class Chicken(Animal):

    def __init__(self, pos, frames, name, walk_area, collision_sprites, groups):

        super().__init__(pos, frames, name, walk_area, collision_sprites, groups)

        self.speed = 100

    def refresh_status(self):
        # Whenever we finish an animation, we update the status

        if self.status == 'idle':
            # 20% chance to peck, 10% chance to run somewhere, 70% chance to stay idling
            chance = random.randint(0, 9)
            if chance < 2:
                self.status = 'peck'
            elif chance == 2:
                self.pick_new_walk_location()
                self.status = 'run'
            else:
                self.status = 'idle'

        elif self.status == 'peck':
            # 30% chance to go to idle, 20% chance to go jump down, 50% chance to stay pecking
            chance = random.randint(0, 9)
            if chance <= 2:
                self.status = 'idle'
            elif 3 <= chance <= 4:
                self.status = 'jump_down'
            else:
                self.status = 'peck'

        elif self.status == 'jump_down':
            # Always move to sleep
            self.status = 'sleep'

        elif self.status == 'sleep':
            # 20% chane to jump up from sleep, 80% chance to stay sleeping
            chance = random.randint(0, 9)
            if chance <= 1:
                self.status = 'jump_up'
            else:
                self.status = 'sleep'

        elif self.status == 'jump_up':
            # Always go to idle
            self.status = 'idle'

        elif self.status == 'love':
            # Always go back to idle (love is sort of a type of idle)
            self.status = 'idle'

    def status_pretty_string(self):

        if self.status == 'idle' or self.status == 'love':
            return "idling"

        elif self.status == 'run':
            return "running"

        elif self.status == 'peck':
            return "pecking"

        elif self.status == 'jump_down':
            return "jumping down"

        elif self.status == 'jump_up':
            return "jumping up"

        elif self.status == 'sleep':
            return "sleeping"


class Cow(Animal):

    def __init__(self, pos, frames, name, walk_area, collision_sprites, groups):

        super().__init__(pos, frames, name, walk_area, collision_sprites, groups)

        self.speed = 75

    def refresh_status(self):
        # Whenever we finish an animation, we update the status

        if self.status == 'idle':
            # 20% chance to graze, 10% chance to run somewhere, 20% chance to rest, 50% chance to stay idling
            chance = random.randint(0, 9)
            if chance < 2:
                self.status = 'graze'
            elif chance == 2:
                self.pick_new_walk_location()
                self.status = 'run'
            elif 3 <= chance <= 4:
                self.status = 'rest'
            else:
                self.status = 'idle'

        elif self.status == 'graze':
            # 40% chance to idle, 30% chance to sleep, 30% chance to stay grazing
            chance = random.randint(0, 9)
            if chance <= 3:
                self.status = 'idle'
            elif 4 <= chance <= 6:
                self.status = 'sleep'
            else:
                self.status = 'graze'

        elif self.status == 'sleep':
            # 70% chance to stay sleeping, 30% chance to go back to idle
            chance = random.randint(0, 9)
            if chance <= 6:
                self.status = 'sleep'
            else:
                self.status = 'idle'

        elif self.status == 'rest':
            # 70% chance to stay resting, 30% chance to go back to idle
            chance = random.randint(0, 9)
            if chance <= 6:
                self.status = 'rest'
            else:
                self.status = 'idle'

        elif self.status == 'love':
            # Always go back to idling (love is a kind of idle)
            self.status = 'idle'

    def status_pretty_string(self):

        if self.status == 'idle' or self.status == 'love':
            return "idling"

        elif self.status == 'run':
            return "running"

        elif self.status == 'graze':
            return "grazing"

        elif self.status == 'rest':
            return "resting"

        elif self.status == 'sleep':
            return "sleeping"
