import pygame
from util import *
from settings import *


class DayUI:
    # This is a static, non-interact-able UI widget Bit of a dummy UI. It's never 'active' but we always draw it.
    # It is always visible in the top-left of the display surface, and does not interfere with other UIs or block inputs

    # SETUP

    def __init__(self, day):

        self.import_assets()
        self.display_surface = pygame.display.get_surface()
        self.day = day
        self.debug_string = 'Day UI'

        self.day_surf, self.day_vars = self.build_daytime_surf()

    def import_assets(self):

        self.assets = {
            'base': import_image('graphics/ui/days/daytime_ui.png', scale=False),
            'weather': {
                weather_type: import_folder_as_dict('graphics/ui/days/weather/%s/' % weather_type, scale=False)
                for weather_type in ['hot', 'night', 'normal']
            },
            'thermometer': import_folder_as_dict('graphics/ui/days/thermometer', scale=False),
            'days_of_week': import_folder_as_dict('graphics/ui//days/days_of_week', scale=False),
            'arrows': import_folder_as_dict('graphics/ui/days/arrows', scale=False)
        }

        # Text for some reason has white background. Give all of them transparent background & text a bit less opaque
        for day in self.assets['days_of_week'].values():
            day.set_colorkey((255, 255, 255))
            day.set_alpha(175)

    # SUPPORT

    def is_active(self):
        # Can never be active

        return False

    def disable_ui(self):
        # Nothing to disable

        pass

    # EVENTS & INPUTS

    def events(self, event):

        pass

    def inputs(self, camera_offset):

        pass

    # LOGIC & DRAWING

    def build_daytime_surf(self):
        # This build a new surface from scratch for the UI, when it's the right time to build a new one
        # We only call this when it has changed, and to know that we keep track of the day variables when creating
        # We return the surface for drawing, and the variables we used to create it

        # Get all the variables needed to build the surface
        day_vars = self.day.get_all_vars()

        # Start with a new surface of the right size
        day_surf = pygame.Surface(self.assets['base'].get_size(), pygame.SRCALPHA)

        # Thermometer has to go first under base image
        day_surf.blit(self.assets['thermometer']['base'], (-6, 49))
        day_surf.blit(self.assets['thermometer'][day_vars['temp']], (-6, 49))

        # General base image
        day_surf.blit(self.assets['base'], (0, 0))

        # Weather
        day_surf.blit(self.assets['weather'][day_vars['weather']['category']][day_vars['weather']['type']], (8, 8))

        # Day of week
        weekday_surf = self.assets['days_of_week'][day_vars['day of week']]
        weekday_rect = weekday_surf.get_rect(center=(42, 61))
        day_surf.blit(weekday_surf, weekday_rect)

        # Time of day arrow
        arrow_index = day_vars['time division']
        arrow_surf = self.assets['arrows'][str(arrow_index)]
        if arrow_index == 0:
            arrow_rect = arrow_surf.get_rect(midleft=(54, 20))
        elif arrow_index == 1:
            arrow_rect = arrow_surf.get_rect(midleft=(54, 21))
        elif arrow_index == 2:
            arrow_rect = arrow_surf.get_rect(midleft=(54, 24))
        elif arrow_index == 3:
            arrow_rect = arrow_surf.get_rect(midleft=(54, 27))
        elif arrow_index == 4:
            arrow_rect = arrow_surf.get_rect(midleft=(54, 27))
        day_surf.blit(arrow_surf, arrow_rect)

        return day_surf, day_vars

    def display(self, camera_offset):

        current_day_vars = self.day.get_all_vars()
        if current_day_vars != self.day_vars:
            self.day_surf, self.day_vars = self.build_daytime_surf()

        self.display_surface.blit(self.day_surf, UI_POSITIONING['daytime']['offset'])
