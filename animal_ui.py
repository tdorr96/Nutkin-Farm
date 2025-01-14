import pygame
from util import import_image
from pygame.math import Vector2


class AnimalUI:

    # SETUP

    def __init__(self, animal_sprites):

        # Setup
        self.import_assets()
        self.display_surface = pygame.display.get_surface()
        self.animal_sprites = animal_sprites
        self.debug_string = 'Animal UI'

        # Animal object references, for if we are:
        # (i) hovering over an animal (i.e. left-shift + mouse over, or menu active for an animal)
        # (ii) showing menu for an animal (i.e. we right-clicked on the one we were hovering on)
        self.hovering_on = None     # Soft UI element
        self.menu_shown_for = None  # Hard UI element

    def import_assets(self):

        self.assets = {
            'animal_menu': import_image('graphics/ui/animals/animal_menu.png', scale=False),
            'full_heart': import_image('graphics/ui/animals/full_heart.png', scale=False),
            'empty_heart': import_image('graphics/ui/animals/empty_heart.png', scale=False),
            'hover_box': {
                'tl': import_image('graphics/ui/animals/hover_tl.png', scale=False),
                'tr': import_image('graphics/ui/animals/hover_tr.png', scale=False),
                'bl': import_image('graphics/ui/animals/hover_bl.png', scale=False),
                'br': import_image('graphics/ui/animals/hover_br.png', scale=False)
            }
        }

        self.font = pygame.font.Font('graphics/font/sproutLands.ttf', 16)

    # SUPPORT

    def is_active(self):
        # Considered active if hard UI elements are active

        return self.menu_shown_for is not None

    def disable_ui(self):
        # Disable both hard & soft UI elements

        self.hovering_on = None
        self.menu_shown_for = None

    # EVENTS & INPUT

    def events(self, event):

        self.menu_event(event)

    def inputs(self, camera_offset):

        self.hover_input(camera_offset)

    def menu_event(self, event):

        if not self.is_active():
            # Not active

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.hovering_on is not None:
                # Right click, and an animal is hovered over
                self.menu_shown_for = self.hovering_on

        else:
            # Active already

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Pressing escape, we are closing the UI, so it will no longer become the active one in the level
                # We are responsible for disabling all the components here, alongside setting the ones that define
                # it as not active
                self.disable_ui()

    def hover_input(self, camera_offset):

        if self.is_active():
            # Active
            # There are no interact-able components for the UI when we're active
            # We just block changing the animal hovered on, to keep it always lined up & drawn with what the menu
            # animal represents

            return

        else:
            # Not Active
            # We want to check for changing the hovered on animal

            if pygame.key.get_pressed()[pygame.K_LSHIFT]:

                mouse_pos = pygame.mouse.get_pos() + camera_offset
                animals_hovering_on = list(filter(
                    lambda s: s.interaction_rect.collidepoint(mouse_pos),
                    self.animal_sprites.sprites()
                ))

                if len(animals_hovering_on) > 0:
                    # Pick the one with the highest y coord, i.e. most 'on-top', 3D style
                    self.hovering_on = sorted(animals_hovering_on, key=lambda s: s.rect.centery, reverse=True)[0]
                else:
                    self.hovering_on = None

            else:
                self.hovering_on = None

    # LOGIC & DRAWING

    def build_menu_surf(self):

        menu_surf = self.assets['animal_menu'].copy()

        name_surf = self.font.render(self.menu_shown_for.name, False, 'black')
        name_rect = name_surf.get_rect(midtop=Vector2(menu_surf.get_width()/2, 35))

        status_surf = self.font.render("Status: %s" % self.menu_shown_for.status_pretty_string(), False, 'black')
        status_rect = status_surf.get_rect(midtop=name_rect.midbottom + Vector2(0, 10))

        menu_surf.blit(name_surf, name_rect)
        menu_surf.blit(status_surf, status_rect)

        hearts_to_draw = min(self.menu_shown_for.love_hearts, 5)

        for heart in range(hearts_to_draw):
            menu_surf.blit(
                self.assets['full_heart'],
                (23 + (17 * heart), 8)
            )

        for empty_heart in range(hearts_to_draw, 5):
            menu_surf.blit(
                self.assets['empty_heart'],
                (23 + (17 * empty_heart), 8)
            )

        return menu_surf

    def display(self, camera_offset):

        if self.hovering_on is not None:

            self.display_surface.blit(
                self.assets['hover_box']['tl'],
                self.assets['hover_box']['tl'].get_rect(topleft=self.hovering_on.interaction_rect.topleft - camera_offset)
            )

            self.display_surface.blit(
                self.assets['hover_box']['tr'],
                self.assets['hover_box']['tr'].get_rect(topright=self.hovering_on.interaction_rect.topright - camera_offset)
            )

            self.display_surface.blit(
                self.assets['hover_box']['bl'],
                self.assets['hover_box']['bl'].get_rect(bottomleft=self.hovering_on.interaction_rect.bottomleft - camera_offset)
            )

            self.display_surface.blit(
                self.assets['hover_box']['br'],
                self.assets['hover_box']['br'].get_rect(bottomright=self.hovering_on.interaction_rect.bottomright - camera_offset)
            )

        if self.menu_shown_for is not None:

            menu_surf = self.build_menu_surf()
            menu_rect = menu_surf.get_rect(midbottom=self.menu_shown_for.interaction_rect.midtop - camera_offset)

            self.display_surface.blit(menu_surf, menu_rect)
