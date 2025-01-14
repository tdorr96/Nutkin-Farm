import pygame
from settings import *


class Transition:

    def __init__(self):

        self.display_surface = pygame.display.get_surface()
        self.image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.color = 255
        self.speed = -300

        self.active = False
        self.func = None  # We will set this everytime we 'activate' the transition

    def activate(self, func):

        self.active = True
        self.func = func

    def deactivate(self):

        self.active = False
        self.func = None

    def update(self, dt):

        if self.active:

            self.color += self.speed * dt

            if self.color < 0:
                self.speed *= -1
                self.color = 0
                self.func()

            elif self.color > 255:
                self.color = 255
                self.speed *= -1
                self.deactivate()

    def display(self):

        if self.active:

            self.image.fill((self.color, self.color, self.color))
            self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class TransitionWithCutscene:

    def __init__(self, cutscene_frames, animation_speed):
        # Each transition with cutscene object is associated with one of many possible cutscenes,
        # E.g. if we want to pick between facing left or right in cutscene down river
        # When we activate we'll pass in the key for the specific cutscene we want to play

        self.display_surface = pygame.display.get_surface()
        self.image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.color = 255
        self.speed = -300

        self.cutscene_options = {key: Cutscene(value, animation_speed) for key, value in cutscene_frames.items()}

        # We will set func & cutscene everytime we 'activate' the transition
        self.active = False
        self.func = None
        self.cutscene = None

    def activate(self, func, cutscene_key):

        self.active = True
        self.func = func
        self.cutscene = self.cutscene_options[cutscene_key]

    def deactivate(self):

        self.active = False
        self.func = None
        self.cutscene = None

    def cutscene_active(self):

        return self.cutscene is not None and self.cutscene.active

    def playing_cutscene_without_transition(self):

        return self.cutscene.active and not self.cutscene.reached_end() and self.color == 255

    def update(self, dt):

        if self.active:

            self.cutscene.update(dt)

            if self.playing_cutscene_without_transition():
                return

            self.color += self.speed * dt

            if self.color < 0:
                self.speed *= -1
                self.color = 0
                if not self.cutscene.active:
                    self.cutscene.play()
                else:
                    self.cutscene.stop()
                    self.func()

            elif self.color > 255:
                self.color = 255
                self.speed *= -1
                if not self.cutscene.active:
                    self.deactivate()

    def display(self):

        if self.active:
            self.cutscene.display()
            if not self.playing_cutscene_without_transition():
                self.image.fill((self.color, self.color, self.color))
                self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class Cutscene:
    # Basically just an animated image covering entire screen, which loops on the last frame

    def __init__(self, frames, animation_speed):

        self.display_surface = pygame.display.get_surface()

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Animation speed worked out when generating frames for the smoothest look with the least amount of frames
        self.animation_speed = animation_speed

        self.active = False

    def play(self):

        self.active = True
        pygame.mouse.set_visible(False)

    def reached_end(self):
        # Small tolerance to if we reached the end, to allow transition to begin fading while still animating

        return self.frame_index >= len(self.frames) * 0.9

    def stop(self):

        self.active = False
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        pygame.mouse.set_visible(True)

    def update(self, dt):

        if self.active:
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1
            self.image = self.frames[int(self.frame_index)]

    def display(self):

        if self.active:

            # Draw the current frame
            self.display_surface.blit(self.image, (0, 0))
