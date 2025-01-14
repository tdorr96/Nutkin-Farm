import pygame
from util import *
from settings import *


class SkillsUI:

    # SETUP

    def __init__(self, skills):

        self.import_assets()
        self.display_surface = pygame.display.get_surface()
        self.debug_string = 'Skills UI'
        self.font = pygame.font.Font('graphics/font/sproutLands.ttf', 16)
        self.skills = skills

        # Hard UI element determining if UI is active or not
        self.open = False

    def import_assets(self):

        self.assets = {
            'icons': import_folder_as_dict('graphics/ui/skills/icons/', scale=False),
            'buttons': import_folder_as_dict('graphics/ui/skills/buttons/', scale=False),
            'interface': import_image('graphics/ui/skills/interface.png', scale=False)
        }

        self.button_rect = self.assets['buttons']['open'].get_rect(bottomleft=UI_POSITIONING['skills']['offset'])
        self.interface_rect = self.assets['interface'].get_rect(bottomleft=self.button_rect.topleft - Vector2(0, 5))

    # SUPPORT

    def is_active(self):

        return self.open

    def disable_ui(self):

        self.open = False

    # EVENTS & INPUTS

    def events(self, event):

        self.button_event(event)

    def inputs(self, camera_offset):

        pass

    def button_event(self, event):

        if not self.is_active():
            # Not active

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.button_rect.collidepoint(event.pos):
                # Left click and clicking on button to open
                self.open = True

        else:
            # Already active

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.disable_ui()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.button_rect.collidepoint(event.pos):
                self.disable_ui()

    # LOGIC & DRAWING

    def build_skills_surf(self):

        skill_interface = self.assets['interface'].copy()
        skill_vars = self.skills.get_all_vars()

        woodcutting_text = self.font.render(
            'Level: %s  Exp: %s' % (skill_vars['Woodcutting']['level'], skill_vars['Woodcutting']['xp']),
            False, (241, 243, 229)
        )
        skill_interface.blit(woodcutting_text, (54, 105))

        farming_text = self.font.render(
            'Level: %s  Exp: %s' % (skill_vars['Farming']['level'], skill_vars['Farming']['xp']),
            False, (241, 243, 229)
        )
        skill_interface.blit(farming_text, (54, 180))

        return skill_interface

    def display(self, camera_offset):

        if self.is_active():

            self.display_surface.blit(self.assets['buttons']['open'], self.button_rect)

            skills_surf = self.build_skills_surf()
            self.display_surface.blit(skills_surf, self.interface_rect)

        else:

            self.display_surface.blit(self.assets['buttons']['closed'], self.button_rect)
