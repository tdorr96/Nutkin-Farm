import pygame
import random


class Timer:

    def __init__(self, duration, autostart=False, repeat=False, func=None):

        self.active = False
        self.start_time = None
        self.duration = duration
        self.repeat = repeat
        self.func = func

        if autostart:
            self.activate()

    def activate(self):

        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):

        self.active = False
        self.start_time = None

    def update(self):

        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.duration:
                self.deactivate()
                if self.func is not None:
                    self.func()
                if self.repeat:
                    self.activate()
