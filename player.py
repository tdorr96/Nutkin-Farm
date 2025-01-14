import pygame
from util import *
from settings import *
from skills import Skills
from pygame.math import Vector2
from sprites import WateringCanParticleEffect


class Player(pygame.sprite.Sprite):

    # SETUP

    def __init__(self, pos, house_floor_sprites, collision_sprites, tree_sprites, all_sprites, is_transition_active, is_ui_active, disable_uis, groups):

        super().__init__(groups)

        # Image, Status & Animations
        self.import_assets()
        self.frame_index = 0
        self.facing = 'down'
        self.status = self.facing + '_idle'
        self.image = self.frames[self.status][self.frame_index]
        self.animation_speed = 7
        self.z = Z_LAYERS['main']

        # Extra Status Variables
        self.inside_house = False

        # Tool Variables
        self.active_tool = None
        self.has_performed_action = False

        # Rect & Hitbox
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.8, -self.rect.height * 0.7)

        # Float-Based Movement
        self.pos = Vector2(self.rect.center)
        self.direction = Vector2()
        self.speed = 250

        # Sprite groups
        self.house_floor_sprites = house_floor_sprites
        self.collision_sprites = collision_sprites
        self.tree_sprites = tree_sprites
        self.all_sprites = all_sprites

        # Function calls returning if any transition or UI is active (we block input in such case)
        self.is_transition_active = is_transition_active
        self.is_ui_active = is_ui_active

        # Function to call when we want to disable all UIs
        # (More specifically soft parts of UI, as couldn't start a tool action & disable if one was active anyway)
        self.disable_uis = disable_uis

        # Skills
        self.skills = Skills()

    def import_assets(self):

        self.frames = import_folders_as_lists('graphics/player')

        self.assets = {
            'watering particles': import_folders_as_lists('graphics/particles/player/watering')
        }

    # SUPPORT

    def is_facing_sprite(self, s):

        if s.rect.left <= self.pos.x <= s.rect.right and self.pos.y <= s.rect.top and self.is_facing('down'):
            return True

        if s.rect.top <= self.pos.y <= s.rect.bottom and self.pos.x <= s.rect.left and self.is_facing('right'):
            return True

        if s.rect.left <= self.pos.x <= s.rect.right and self.pos.y >= s.rect.bottom and self.is_facing('up'):
            return True

        if s.rect.top <= self.pos.y <= s.rect.bottom and self.pos.x >= s.rect.right and self.is_facing('left'):
            return True

        return False

    def is_facing(self, direction):

        return self.facing == direction

    def is_idling(self):

        return self.direction.magnitude() == 0

    def is_tool_use_active(self):

        return self.active_tool is not None

    def get_tool_target_pos(self):

        return self.pos + PLAYER_TOOL_OFFSET[self.active_tool][self.facing]

    def spawn_watering_can_particles(self):

        if self.facing == 'up':
            # No animation if facing up - we wouldn't see particle anyway
            return

        WateringCanParticleEffect(
            pos=self.get_tool_target_pos(),
            frames=self.assets['watering particles'][self.facing],
            groups=self.all_sprites,
            animation_speed=self.animation_speed
        )

    # INPUT

    def input(self):

        # Block input when any transition or UI active, or when in the middle of an action

        if self.is_transition_active() or self.is_ui_active():

            self.direction = Vector2()

        elif not self.is_tool_use_active():

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing = 'left'
            else:
                self.direction.x = 0

            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.facing = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.facing = 'down'
            else:
                self.direction.y = 0

            for action_key in PLAYER_TOOL_ACTION_KEY_MAP.keys():
                if not self.is_tool_use_active():
                    # Check for if we're pressing all 3 keys at the same time
                    if keys[action_key]:
                        self.active_tool = PLAYER_TOOL_ACTION_KEY_MAP[action_key]
                        self.direction = Vector2()
                        self.frame_index = 0
                        self.disable_uis()
                        if self.active_tool == 'water':
                            self.spawn_watering_can_particles()

    # MOVEMENT

    def move(self, dt):

        # Normalize direction vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal Movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('x')
        self.game_border_restrict('x')

        # Vertical Movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('y')
        self.game_border_restrict('y')

    def game_border_restrict(self, axis):
        # Stop player leaving the borders of the game map

        if axis == 'x':

            if self.hitbox.left < 0:
                self.hitbox.left = 0
                self.rect.centerx = self.hitbox.centerx
                self.pos.x = self.hitbox.centerx

            elif self.hitbox.right > GAME_WIDTH:
                self.hitbox.right = GAME_WIDTH
                self.rect.centerx = self.hitbox.centerx
                self.pos.x = self.hitbox.centerx

        elif axis == 'y':

            if self.hitbox.top < 0:
                self.hitbox.top = 0
                self.rect.centery = self.hitbox.centery
                self.pos.y = self.hitbox.centery

            elif self.hitbox.bottom > GAME_HEIGHT:
                self.hitbox.bottom = GAME_HEIGHT
                self.rect.centery = self.hitbox.centery
                self.pos.y = self.hitbox.centery

    def collision(self, axis):
        # Handle collisions between our hitbox and any hitboxes of sprites we deem as collideable

        for sprite in self.collision_sprites.sprites():
            if sprite.hitbox.colliderect(self.hitbox):

                if axis == 'x':

                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                elif axis == 'y':

                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def teleport(self, coordinate):

        self.hitbox.midbottom = coordinate
        self.rect.center = self.hitbox.center
        self.pos = Vector2(self.rect.center)

    # ANIMATION

    def animate(self, dt):

        self.frame_index += self.animation_speed * dt

        if self.is_tool_use_active() and int(self.frame_index) == PLAYER_TOOL_ACTION_FRAME_INDEX[self.active_tool] and not self.has_performed_action:
            # If we're doing a tool animation, and we're on the frame which we want to perform the action on
            # And we've not done this already for this animation (we only do tool action once for each animation)
            self.has_performed_action = True
            self.tool_action()

        if self.frame_index >= len(self.frames[self.status]):
            self.frame_index = 0
            if self.is_tool_use_active():
                self.active_tool = None
                self.has_performed_action = False
                self.update_status()

        self.image = self.frames[self.status][int(self.frame_index)]

    # TOOL USE

    def tool_action(self):

        if self.active_tool == 'axe':
            self.use_axe()

        elif self.active_tool == 'water':
            self.use_watering_can()

        elif self.active_tool == 'hoe':
            self.use_hoe()

    def use_axe(self):

        target_pos = self.get_tool_target_pos()

        # Prioritise trees, then stumps. And after that prioritise one with highest y coord (one drawn on top)
        hit_trees = [tree for tree in filter(lambda t: t.status == 'tree', self.tree_sprites.sprites()) if tree.is_hit(target_pos)]
        hit_stumps = [stump for stump in filter(lambda t: t.status == 'stump', self.tree_sprites.sprites()) if stump.is_hit(target_pos)]

        if len(hit_trees) > 0:
            chopped_tree = sorted(hit_trees, key=lambda t: t.rect.centery, reverse=True)[0]
            chopped_tree.chop(
                direction_from='right' if self.rect.centerx >= chopped_tree.rect.centerx else 'left'
            )
            self.skills.add_xp('Woodcutting', 50)
        elif len(hit_stumps) > 0:
            chopped_stump = sorted(hit_stumps, key=lambda s: s.rect.centery, reverse=True)[0]
            chopped_stump.chop(
                direction_from='right' if self.rect.centerx >= chopped_stump.rect.centerx else 'left'
            )
            self.skills.add_xp('Woodcutting', 25)

    def use_watering_can(self):

        pass

    def use_hoe(self):

        pass

    # UPDATES

    def update_status(self):
        # Update status

        if self.is_tool_use_active():
            action = self.active_tool
        elif self.is_idling():
            action = 'idle'
        else:
            action = 'run'

        self.status = self.facing + '_' + action

    def update_house_status(self):

        # We are considered inside the house if any 3 of our sides totally on house tiles
        bottom_inside = any(s.rect.collidepoint(self.hitbox.midbottom) for s in self.house_floor_sprites.sprites())
        top_inside = any(s.rect.collidepoint(self.hitbox.midtop) for s in self.house_floor_sprites.sprites())
        left_inside = any(s.rect.collidepoint(self.hitbox.midleft) for s in self.house_floor_sprites.sprites())
        right_inside = any(s.rect.collidepoint(self.hitbox.midright) for s in self.house_floor_sprites.sprites())

        self.inside_house = sum([bottom_inside, top_inside, left_inside, right_inside]) >= 3

    def update(self, dt):

        self.input()
        self.update_status()
        self.move(dt)
        self.update_house_status()
        # HOW CAN HOUSE STATUS BE GENERALIZED? WHERE DOES IT GO? STATUS BECOMES AN OBJECT?
        self.animate(dt)
