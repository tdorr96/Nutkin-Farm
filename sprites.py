import pygame
import random
from settings import *
from pygame.math import Vector2


class Generic(pygame.sprite.Sprite):
    # Base class for all sprites we extend

    def __init__(self, pos, surf, groups, z=Z_LAYERS['main']):

        super().__init__(groups)

        self.z = z
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.25, -self.rect.height * 0.4)


class SelfDestructGeneric(Generic):

    def __init__(self, pos, surf, death_time, groups, z=Z_LAYERS['main']):

        super().__init__(pos, surf, groups, z)

        self.time_created = pygame.time.get_ticks()
        self.death_time = death_time

    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.time_created >= self.death_time:
            self.kill()


class Bed(Generic):
    # Generic sprite, but just slightly adjusted hitbox width

    def __init__(self, pos, surf, groups):

        super().__init__(pos, surf, groups)

        self.hitbox = self.rect.inflate(-self.rect.width * 0.1, -self.rect.height * 0.4)


class HouseWall(Generic):
    # Generic sprite, but we shift hitbox to center of wall for better collisions

    def __init__(self, pos, surf, groups):

        super().__init__(pos, surf, groups)

        bounding_rect = surf.get_bounding_rect().move(self.rect.topleft)
        self.hitbox.center = bounding_rect.center


class CollisionBlock(Generic):
    # Generic sprite, we do not draw, but we have a different scaled & shifted hitbox

    def __init__(self, pos, shift, groups):

        super().__init__(pos, pygame.Surface((TILE_SIZE, TILE_SIZE)), groups)

        self.hitbox = self.rect.inflate(-self.rect.width * 0.4, -self.rect.height * 0.4)

        if shift['right']:
            self.hitbox.x += self.rect.width * 0.2
        elif shift['left']:
            self.hitbox.x -= self.rect.width * 0.2

        # Because of top-down 3D effect, move up more than down
        if shift['up']:
            self.hitbox.y -= self.rect.height * 0.3
        elif shift['down']:
            self.hitbox.y += self.rect.height * 0.1


class Animated(Generic):
    # Generic sprite that animates

    def __init__(self, pos, frames, groups, animation_speed=5, z=Z_LAYERS['main']):

        self.frames = frames
        self.frame_index = 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):

        self.animate(dt)


class Boat(Animated):
    # Generic animated sprite that just has some extra variables

    def __init__(self, pos, frames, direction_facing, groups):

        super().__init__(pos, frames, groups, animation_speed=2)

        self.direction_facing = direction_facing


class StaticParticleEffect(Animated):
    # Static animated sprite that kills itself after a number of iterations through the frames, rather than looping

    def __init__(self, pos, frames, groups, animation_speed=5, animation_cycles_to_kill=1, start_on_random_frame=False, z=Z_LAYERS['main']):

        super().__init__(pos, frames, groups, animation_speed, z)

        if start_on_random_frame:
            self.frame_index = random.randint(0, len(self.frames)-1)
            self.image = self.frames[self.frame_index]

        self.cycles_played = 0
        self.animation_cycles_to_kill = animation_cycles_to_kill

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            self.cycles_played += 1
            if self.cycles_played == self.animation_cycles_to_kill:
                self.kill()

        self.image = self.frames[int(self.frame_index)]


class WateringCanParticleEffect(StaticParticleEffect):
    # Static particle effect, but lets us control positioning based on player a bit

    def __init__(self, pos, frames, groups, animation_speed):

        super().__init__(pos, frames, groups, animation_speed=animation_speed)

        self.rect = self.image.get_rect(center=pos)
        # Recalculate hitbox for completeness
        self.hitbox = self.rect.inflate(-self.rect.width * 0.25, -self.rect.height * 0.4)


class FallingTreeParticleEffect(StaticParticleEffect):
    # Static particle effect, but lets us control position for tree

    def __init__(self, pos, frames, groups):

        super().__init__(pos, frames, groups, animation_speed=9)

        self.rect = self.image.get_rect(midbottom=pos)
        # Recalculate hitbox for completeness
        self.hitbox = self.rect.inflate(-self.rect.width * 0.25, -self.rect.height * 0.4)


class MovingParticleEffect(Animated):
    # Moving animated sprite that kills itself after a certain time

    def __init__(self, pos, frames, direction, death_time, speed, groups, animation_speed=5, start_on_random_frame=False, func=None, z=Z_LAYERS['main']):

        super().__init__(pos, frames, groups, animation_speed, z)

        if start_on_random_frame:
            self.frame_index = random.randint(0, len(self.frames)-1)
            self.image = self.frames[self.frame_index]

        # Movement
        self.direction = direction.normalize()
        self.pos = Vector2(self.rect.center)
        self.speed = speed

        # Death
        self.death_time = death_time
        self.creation_time = pygame.time.get_ticks()
        self.func = func

    def move(self, dt):

        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time >= self.death_time:
            if self.func is not None:
                self.func(self.image, self.rect)
            self.kill()

        self.move(dt)
        self.animate(dt)
