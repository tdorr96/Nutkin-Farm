import pygame
from settings import *


class DebugCamera:

    def __init__(self, day, player, collision_sprites, tree_sprites, animal_sprites, is_transition_active, is_cutscene_playing, get_active_ui, get_camera_offset):

        self.display_surface = pygame.display.get_surface()

        self.day = day
        self.player = player
        self.collision_sprites = collision_sprites
        self.tree_sprites = tree_sprites
        self.animal_sprites = animal_sprites
        self.is_transition_active = is_transition_active
        self.is_cutscene_playing = is_cutscene_playing
        self.get_active_ui = get_active_ui
        self.get_camera_offset = get_camera_offset

        self.big_font = pygame.font.Font('graphics/font/sproutLands.ttf', 32)
        self.small_font = pygame.font.Font('graphics/font/sproutLands.ttf', 16)

        self.y_top = 5
        self.buffer = 5

    def draw_text_box(self, text_str, font):

        surf = font.render(text_str, False, 'White')
        rect = surf.get_rect(topright=(WINDOW_WIDTH-self.buffer, self.y_top))
        pygame.draw.rect(self.display_surface, 'black', rect)
        self.display_surface.blit(surf, rect)
        self.y_top += rect.height + self.buffer

    def draw(self, dt):

        if not DEBUG:
            return

        self.y_top = 5
        camera_offset = self.get_camera_offset()

        # Delta Time/Frames Per Second
        if DEBUG_OPTIONS['fps']:
            self.draw_text_box(str(1/dt if dt > 0 else dt)[:6], self.big_font)

        # Player
        if DEBUG_OPTIONS['player']['rect']:
            pygame.draw.rect(self.display_surface, 'blue',self.player.rect.move(-camera_offset), 1)
        if DEBUG_OPTIONS['player']['hitbox']:
            pygame.draw.rect(self.display_surface, 'red', self.player.hitbox.move(-camera_offset), 1)
        if DEBUG_OPTIONS['player']['tool_target_pos'] and self.player.is_tool_use_active():
            target_pos_offset = self.player.get_tool_target_pos() - camera_offset
            pygame.draw.line(self.display_surface, 'green', target_pos_offset+Vector2(-3, 3), target_pos_offset+Vector2(3, -3), 2)
            pygame.draw.line(self.display_surface, 'green', target_pos_offset+Vector2(-3, -3), target_pos_offset+Vector2(3, 3), 2)
        if DEBUG_OPTIONS['player']['status vars']:
            for variable, variable_str in [
                (self.player.status, 'Status: '),
                (self.player.active_tool, 'Active Tool: '),
                (self.player.has_performed_action, 'Has Performed Tool Action: '),
                (self.player.inside_house, 'Inside House: ')
            ]:
                self.draw_text_box(variable_str + str(variable), self.small_font)

        # UIs
        if DEBUG_OPTIONS['uis']['active ui']:
            active_ui = self.get_active_ui()
            ui_str = 'Active UI: %s' % 'None' if active_ui is None else active_ui.debug_string
            self.draw_text_box(ui_str, self.small_font)

        # Transitions
        if DEBUG_OPTIONS['transitions']['is_active']:
            transition_str = 'Transition Active: %s' % self.is_transition_active()
            self.draw_text_box(transition_str, self.small_font)
        if DEBUG_OPTIONS['transitions']['is_cutscene_playing']:
            cutscene_str = 'Cutscene Playing: %s' % self.is_cutscene_playing()
            self.draw_text_box(cutscene_str, self.small_font)

        # Day/Time/Weather
        if DEBUG_OPTIONS['day']['time']:
            self.draw_text_box('Time of Day: %s' % str(self.day.current_time)[:5], self.small_font)
        if DEBUG_OPTIONS['day']['time_division']:
            self.draw_text_box('Time Division: %s' % self.day.get_time_division(), self.small_font)
        if DEBUG_OPTIONS['day']['current_luminance']:
            self.draw_text_box('Sky Luminance: %s' % self.day.get_sky_luminance(), self.small_font)
        if DEBUG_OPTIONS['day']['weather']:
            self.draw_text_box('Weather Category: %s' % self.day.weather_category, self.small_font)
            self.draw_text_box('Weather Type: %s' % self.day.weather_type, self.small_font)
        if DEBUG_OPTIONS['day']['temp']:
            self.draw_text_box('Temperature: %s' % self.day.temp, self.small_font)

        # Collisions
        if DEBUG_OPTIONS['collisions']['hitbox']:
            for sprite in self.collision_sprites.sprites():
                pygame.draw.rect(self.display_surface, 'red', sprite.hitbox.move(-camera_offset), 1)
        if DEBUG_OPTIONS['collisions']['rect']:
            for sprite in self.collision_sprites.sprites():
                pygame.draw.rect(self.display_surface, 'blue', sprite.rect.move(-camera_offset), 1)

        # Trees
        if DEBUG_OPTIONS['trees']['interaction_rect']:
            for tree in self.tree_sprites.sprites():
                pygame.draw.rect(self.display_surface, 'yellow', tree.interaction_rect.move(-camera_offset), 1)

        # NPCs
        if DEBUG_OPTIONS['npcs']['running']:
            for animal in self.animal_sprites.sprites():
                if animal.is_running():
                    pygame.draw.line(self.display_surface, 'black', animal.pos - camera_offset, animal.target_pos - camera_offset, 1)
        if DEBUG_OPTIONS['npcs']['rect']:
            for animal in self.animal_sprites.sprites():
                pygame.draw.rect(self.display_surface, 'blue', animal.rect.move(-camera_offset), 1)
        if DEBUG_OPTIONS['npcs']['interaction_rect']:
            for animal in self.animal_sprites.sprites():
                pygame.draw.rect(self.display_surface, 'yellow', animal.interaction_rect.move(-camera_offset), 1)

