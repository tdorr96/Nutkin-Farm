import pygame
from util import *
from settings import *
from sprites import FallingTreeParticleEffect


class NormalTree(pygame.sprite.Sprite):

    def __init__(self, pos, all_sprites, groups):

        super().__init__(groups)

        self.import_assets()
        self.z = Z_LAYERS['main']

        self.status = 'tree'
        self.health = TREE_MAX_HEALTH

        # Rects same across stump & tree, just use either to init rect
        self.rect = self.frames['tree'].get_rect(topleft=pos)
        self.refresh_image_and_rects()

        self.all_sprites = all_sprites

    def import_assets(self):

        self.frames = {
            'tree': import_image('graphics/trees/normal_tree/tree.png'),
            'stump': import_image('graphics/trees/normal_tree/stump.png'),
            'falling animation': import_folders_as_lists('graphics/trees/normal_tree/falling'),
        }

    def refresh_image_and_rects(self):

        self.image = self.frames[self.status]

        if self.status == 'tree':

            self.hitbox = self.rect.inflate(-self.rect.width * 0.4, -self.rect.height * 0.4)

            self.interaction_rect = self.rect.inflate(-self.rect.width * 0.4, -self.rect.height * 0.1)
            self.interaction_rect.midbottom = self.rect.midbottom

        elif self.status == 'stump':

            # Hitbox is a shrunken version of tree hitbox, if we moved it too much, we would get collision bugs
            # It can shrink & move, as long it does not expand out fron previous hitbox borders
            new_hitbox = self.hitbox.inflate(-self.hitbox.width*0.4, -self.hitbox.height*0.6)
            new_hitbox.midbottom = self.hitbox.midbottom
            self.hitbox = new_hitbox

            self.interaction_rect = self.rect.inflate(-self.rect.width * 0.6, -self.rect.height * 0.6)
            self.interaction_rect.midbottom = self.rect.midbottom

    def refresh_new_day(self):

        if self.status == 'tree':
            self.health = TREE_MAX_HEALTH

        elif self.status == 'stump':
            self.status = 'tree'
            self.refresh_image_and_rects()
            self.health = TREE_MAX_HEALTH

    def spawn_falling_tree_animation(self, direction_to_fall):

        FallingTreeParticleEffect(
            pos=self.rect.midbottom,
            frames=self.frames['falling animation'][direction_to_fall],
            groups=self.all_sprites
        )

    def is_hit(self, target_pos):

        return self.interaction_rect.collidepoint(target_pos)

    def chop(self, direction_from):

        self.health -= 1

        if self.health == 0:

            if self.status == 'tree':
                self.status = 'stump'
                self.refresh_image_and_rects()
                self.health = STUMP_HEALTH
                self.spawn_falling_tree_animation('left' if direction_from == 'right' else 'right')

            elif self.status == 'stump':
                self.kill()
