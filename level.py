import sys
import regex
import pygame
from util import *
from day import Day
from settings import *
from day_ui import DayUI
from camera import Camera
from player import Player
from trees import NormalTree
from npcs import Chicken, Cow
from debug import DebugCamera
from animal_ui import AnimalUI
from skills_ui import SkillsUI
from pytmx.util_pygame import load_pygame
from transition import TransitionWithCutscene, Transition
from sprites import Generic, Animated, CollisionBlock, HouseWall, Boat, Bed


class Level:

    # SETUP

    def __init__(self):

        # General Setup
        self.display_surface = pygame.display.get_surface()
        self.import_assets()

        # Transitions
        self.boat_transport_transition = TransitionWithCutscene(self.assets['cutscenes']['boat transport'], animation_speed=25)
        self.sleep_transition = Transition()
        # self.sleep_transition = TransitionWithCutscene(self.assets['cutscenes']['sleeping'], animation_speed=2)
        self.all_transitions = [self.boat_transport_transition, self.sleep_transition]
        self.all_transitions_with_cutscenes = [self.boat_transport_transition]

        # Groups
        self.all_sprites = Camera()
        self.collision_sprites = pygame.sprite.Group()
        self.house_floor_sprites = pygame.sprite.Group()
        self.animal_sprites = pygame.sprite.Group()
        self.boat_sprites = pygame.sprite.Group()
        self.bed_sprite = pygame.sprite.GroupSingle()
        self.tree_sprites = pygame.sprite.Group()

        # Extra Positional Information
        self.weather_floor_particle_rects = []

        # Import Tiled
        self.setup()

        # Day, Time, and Weather
        self.day = Day(self.weather_floor_particle_rects, self.all_sprites)

        # UIs
        self.active_ui = None
        self.day_ui = DayUI(self.day)
        self.skills_ui = SkillsUI(self.player.skills)
        self.animal_ui = AnimalUI(self.animal_sprites)
        self.all_uis = [self.day_ui, self.animal_ui, self.skills_ui]

        # Debug Camera
        self.debug_camera = DebugCamera(
            day=self.day,
            player=self.player,
            collision_sprites=self.collision_sprites,
            tree_sprites=self.tree_sprites,
            animal_sprites=self.animal_sprites,
            is_transition_active=self.is_transition_active,
            is_cutscene_playing=self.is_transition_playing_cutscene,
            get_active_ui=self.get_active_ui,
            get_camera_offset=self.get_camera_offset
        )

    def import_assets(self):

        self.assets = {
            'background': import_image('data/tmx/map.png'),
            'water frames': import_folder('graphics/water'),
            'boat frames': {
                'right': import_folder('graphics/objects/boat/right'),
                'left': import_folder('graphics/objects/boat/left')
            },
            'npc frames': {
                'chicken': {
                    color: import_folders_as_lists('graphics/chicken/%s' % color)
                    for color in list_folder('graphics/chicken')
                },
                'cow': {
                    color: import_folders_as_lists('graphics/cow/%s' % color)
                    for color in list_folder('graphics/cow')
                }
            },
            'cutscenes': {
                'boat transport': {
                    'left': import_folder('graphics/cutscene/boat/left', scale=False),
                    'right': import_folder('graphics/cutscene/boat/right', scale=False)
                },
                'sleeping': {
                    'normal': import_folder('graphics/cutscene/sleeping', scale=False)
                }
            }
        }

    def setup(self):

        tmx_data = load_pygame('data/tmx/map.tmx')

        # Background
        Generic(
            pos=(0, 0),
            surf=self.assets['background'],
            groups=self.all_sprites,
            z=Z_LAYERS['ground']
        )

        # Water
        for x, y, _ in tmx_data.get_layer_by_name('Water').tiles():
            Animated(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                frames=self.assets['water frames'],
                groups=self.all_sprites,
                z=Z_LAYERS['water']
            )

        # Bushes
        for x, y, surf in tmx_data.get_layer_by_name('Bushes').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # Water Trays
        for x, y, surf in tmx_data.get_layer_by_name('Water Trays').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # Fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # Trees
        for obj in tmx_data.get_layer_by_name('Normal Trees'):
            NormalTree(
                pos=(obj.x * ZOOM_FACTOR, obj.y * ZOOM_FACTOR),
                all_sprites=self.all_sprites,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites]
            )

        # House Walls
        for x, y, surf in tmx_data.get_layer_by_name('House Walls').tiles():
            HouseWall(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # House Furniture Top
        for x, y, surf in tmx_data.get_layer_by_name('House Furniture Top').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # House Furniture Interaction
        for obj in tmx_data.get_layer_by_name('House Furniture Interaction'):
            if obj.name == 'Bed':
                Bed(
                    pos=(obj.x*ZOOM_FACTOR, obj.y*ZOOM_FACTOR),
                    surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                    groups=[self.all_sprites, self.bed_sprite, self.collision_sprites]
                )

        # Decoration Top
        for obj in tmx_data.get_layer_by_name('Decoration Top'):
            Generic(
                pos=(obj.x*ZOOM_FACTOR, obj.y*ZOOM_FACTOR),
                surf=pygame.transform.scale_by(obj.image, ZOOM_FACTOR),
                groups=[self.all_sprites, self.collision_sprites]
            )

        # Boats
        for obj in tmx_data.get_layer_by_name('Boats'):
            Boat(
                pos=(obj.x*ZOOM_FACTOR, obj.y*ZOOM_FACTOR),
                frames=self.assets['boat frames'][obj.properties['orientation']],
                direction_facing=obj.properties['orientation'],
                groups=[self.all_sprites, self.boat_sprites]
            )

        # House Roof
        for x, y, surf in tmx_data.get_layer_by_name('House Roof').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.transform.scale_by(surf, ZOOM_FACTOR),
                groups=self.all_sprites,
                z=Z_LAYERS['house roof']
            )

        # Collision sprites. Not drawn.
        # There are 4 collision layers, depending on if we want to shift collision hitboxes, and these effects stack
        # E.g. for corner of river we want to shift up/down AND left/right
        # Build a mapping from tile index to a shift dictionary

        collision_map = [
            [{'has_tile': False, 'right': False, 'left': False, 'up': False, 'down': False} for col in range(TILES_WIDE)]
            for row in range(TILE_HIGH)
        ]

        for layer in ['Collisions 1', 'Collisions 2', 'Collisions 3', 'Collisions 4']:
            shift_direction = tmx_data.get_layer_by_name(layer).properties['shift']
            for x, y, _ in tmx_data.get_layer_by_name(layer).tiles():
                collision_map[y][x]['has_tile'] = True
                collision_map[y][x][shift_direction] = True

        for y, row in enumerate(collision_map):
            for x, tile in enumerate(row):
                if tile['has_tile']:
                    CollisionBlock(
                        pos=(x*TILE_SIZE, y*TILE_SIZE),
                        shift=tile,
                        groups=self.collision_sprites
                    )

        # House Tiles
        for x, y, _ in tmx_data.get_layer_by_name('House Tiles').tiles():
            Generic(
                pos=(x*TILE_SIZE, y*TILE_SIZE),
                surf=pygame.Surface((TILE_SIZE, TILE_SIZE)),
                groups=self.house_floor_sprites
            )

        # NPCs. Divided up into Pens, which have two relevant layers (walk area + NPC markers)

        pen_ids = []
        pen_id_regex = regex.compile(r'^Pen ([0-9]+)$')
        for layer in tmx_data.layernames:
            regex_match = pen_id_regex.match(layer)
            if regex_match is not None:
                pen_ids.append(regex_match.group(1))

        for id in pen_ids:

            walk_area = []
            for x, y, _ in tmx_data.get_layer_by_name('Pen %s Walk Area' % id).tiles():
                walk_area.append(pygame.Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)).inflate(-TILE_SIZE * 0.5, -TILE_SIZE * 0.5))

            for obj in tmx_data.get_layer_by_name('Pen %s NPCs' % id):
                animal_class = Chicken if obj.name == 'Chicken' else Cow
                animal_class(
                    pos=(obj.x*ZOOM_FACTOR, obj.y*ZOOM_FACTOR),
                    frames=self.assets['npc frames'][obj.name.lower()][obj.properties['color']],
                    name=obj.properties['nickname'],
                    walk_area=walk_area,
                    collision_sprites=self.collision_sprites,
                    groups=[self.all_sprites, self.animal_sprites]
                )

        # Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x*ZOOM_FACTOR, obj.y*ZOOM_FACTOR),
                    house_floor_sprites=self.house_floor_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    all_sprites=self.all_sprites,
                    is_transition_active=self.is_transition_active,
                    is_ui_active=self.is_ui_active,
                    disable_uis=self.disable_uis,
                    groups=self.all_sprites
                )

        # Weather Floor Particle Positional Information
        # Generate a list of rects for all the tiles weather floor particles CANNOT land on
        # We do the opposite way around, as it is quicker computation-wise
        # Essentially we cannot land a weather particle on the water or the house floor

        valid_weather_floor_particle_positions = []  # List of top-left tile positions where we can place a particle
        for land_able_layer in ['Grass', 'Bridge']:
            for x, y, _ in tmx_data.get_layer_by_name(land_able_layer).tiles():
                valid_top_left = (x*TILE_SIZE, y*TILE_SIZE)
                if all(s.rect.topleft != valid_top_left for s in self.house_floor_sprites.sprites()):
                    valid_weather_floor_particle_positions.append(valid_top_left)
        for x in range(TILES_WIDE):
            for y in range(TILE_HIGH):
                invalid_top_left = (x*TILE_SIZE, y*TILE_SIZE)
                if invalid_top_left not in valid_weather_floor_particle_positions:
                    self.weather_floor_particle_rects.append(
                        pygame.Rect(invalid_top_left, (TILE_SIZE, TILE_SIZE))
                    )

    # SUPPORT

    def get_camera_offset(self):

        return self.all_sprites.offset

    # TRANSITIONS

    def is_transition_active(self):

        return any(t.active for t in self.all_transitions)

    def is_transition_playing_cutscene(self):

        return any(t.cutscene_active() for t in self.all_transitions_with_cutscenes)

    def update_transitions(self, dt):

        for t in self.all_transitions:
            t.update(dt)

    def display_transitions(self):

        for t in self.all_transitions:
            t.display()

    def activate_transition(self, transition_to_activate, func, cutscene_key=None):
        # We put in this function so we can group together the operation of
        # (i) activating transition
        # (ii) disabling UIs, so any transition starting disables them & we don't forget to do this manually around code

        self.disable_uis(skip_active_ui=False)

        if cutscene_key is None:
            transition_to_activate.activate(func=func)
        else:
            transition_to_activate.activate(func=func, cutscene_key=cutscene_key)

    # UIs

    def display_uis(self):
        # To simplify logic, just iterate and display all UIs
        # Up to UI class to not draw anything if it's not active

        for ui in self.all_uis:
            ui.display(self.get_camera_offset())

    def disable_uis(self, skip_active_ui=False):
        # Disable all UI components. Called when:
        # (i) starting a transition - disable them all (there shouldn't be an active one anyway)
        # (ii) activate a UI, and we want to disable all the other UIs soft components - shouldn't be another active one
        # (iii) starting a tool use (like transition there won't be a -hard- active one anyway)

        if not skip_active_ui:
            self.active_ui = None

        for ui in self.all_uis:
            if not skip_active_ui or ui != self.active_ui:
                ui.disable_ui()

    def is_ui_active(self):

        return self.active_ui is not None

    def ui_events(self, event):
        # For UI events, if there is no UI currently active, they all parse the event
        # If one is active, ony the active one takes events

        for ui in self.all_uis:
            if self.active_ui is None or ui == self.active_ui:

                active_before = ui.is_active()
                ui.events(event)
                active_after = ui.is_active()

                if not active_before and active_after:
                    # This ui becomes the active one
                    assert self.active_ui is None
                    self.active_ui = ui
                    self.disable_uis(skip_active_ui=True)  # Don't disable one we just activated

                elif active_before and not active_after:
                    # This was the active one, but no longer
                    # UI is responsible for disabling itself
                    assert self.active_ui is not None
                    self.active_ui = None

    def ui_inputs(self):
        # For UI inputs, if there is no UI currently active, they all parse inputs
        # If one is active, ony the active one parses the input

        for ui in self.all_uis:
            if self.active_ui is None or ui == self.active_ui:

                active_before = ui.is_active()
                ui.inputs(self.get_camera_offset())
                active_after = ui.is_active()

                if not active_before and active_after:
                    # This ui becomes the active one
                    assert self.active_ui is None
                    self.active_ui = ui
                    self.disable_uis(skip_active_ui=True)  # Don't disable one we just activated

                elif active_before and not active_after:
                    # This was the active one, but no longer
                    # UI is responsible for disabling itself
                    assert self.active_ui is not None
                    self.active_ui = None

    def get_active_ui(self):

        return self.active_ui

    # EVENTS

    def event_loop(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not self.is_transition_active() and not self.player.is_tool_use_active():

                self.ui_events(event)

                if not self.is_ui_active():

                    self.boat_transport(event)
                    self.sleep(event)
                    self.animal_love_event(event)

    def sleep(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Pressing return

            # Can only go to sleep if we're in the final division of the day and idling
            if self.day.is_night_time() and self.player.is_idling():

                # Player must be inside house & near the bed
                if self.player.inside_house and distance_between_sprites(self.bed_sprite.sprite, self.player) < TILE_SIZE:

                    # Player must also be facing the bed
                    if self.player.is_facing_sprite(self.bed_sprite.sprite):

                        self.activate_transition(
                            transition_to_activate=self.sleep_transition,
                            func=self.next_day
                        )

    def boat_transport(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Pressing return

            if self.player.is_idling():
                # Player not moving

                # There are only 2 boats. Get the nearby boat, if there is one, and then we know the other one

                nearby_boats = list(filter(
                    lambda s: distance_between_sprites(s, self.player) < TILE_SIZE * 2,
                    self.boat_sprites.sprites()
                ))

                if len(nearby_boats) > 0:

                    nearby_boat = nearby_boats[0]

                    if self.player.is_facing_sprite(nearby_boat):
                        # Check we are facing it

                        other_boat = list(filter(lambda s: s != nearby_boat, self.boat_sprites.sprites()))[0]
                        self.activate_transition(
                            transition_to_activate=self.boat_transport_transition,
                            func=lambda: self.player.teleport(other_boat.rect.midtop),
                            cutscene_key=nearby_boat.direction_facing
                        )

    def animal_love_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left click

            # Get all the animals our mouse is clicking on
            click_pos_on_map = event.pos + self.get_camera_offset()
            clicked_on_animals = list(filter(
                lambda a: a.interaction_rect.collidepoint(click_pos_on_map),
                self.animal_sprites.sprites()
            ))

            # Filter those animals to ones that can be liked
            # i.e. been a while since last liked, currently idling, and close enough to player
            animals_can_like = list(filter(
                lambda a: not a.love_timer.active and a.is_idling() and distance_between_vectors(a.interaction_rect.center, self.player.rect.center) <= TILE_SIZE,
                clicked_on_animals
            ))

            # Once we have all the candidates for animals that are valid for liking, if there is at least one
            # Pick the one with the highest y, i.e. the one drawn highest on camera order
            if len(animals_can_like) > 0:

                animal = sorted(animals_can_like, key=lambda a: a.rect.centery, reverse=True)[0]
                animal.love()

    # INPUTS

    def inputs(self):

        if not self.is_transition_active() and not self.player.is_tool_use_active():

            self.ui_inputs()

    # GAME LOGIC

    def next_day(self):

        # Transition to next day
        self.day.next_day()

        # Refresh all the trees
        for tree in self.tree_sprites.sprites():
            tree.refresh_new_day()

    def run(self, dt):

        # Event Loop & Inputs
        self.event_loop()
        self.inputs()

        # Update
        self.day.update(dt)
        self.all_sprites.update(dt)
        self.update_transitions(dt)

        # Rendering

        if not self.is_transition_playing_cutscene():
            # We only want to draw normal stuff if no cutscene is being played by transitions

            self.all_sprites.custom_draw(self.player, self.day)
            self.debug_camera.draw(dt)
            self.display_uis()

        self.display_transitions()
