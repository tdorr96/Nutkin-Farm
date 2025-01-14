import random
import pygame
from util import *
from settings import *
from timers import Timer
from sprites import MovingParticleEffect, StaticParticleEffect, SelfDestructGeneric


class Day:

    # SETUP

    def __init__(self, weather_floor_particle_rects, all_sprites):
        # Requires:
        # - List of rects where floor particles (i.e. puddles, etc.) can NOT land on, e.g. water or house floor
        # - All sprites group, to add weather particles into there for updating & drawing

        # Setup
        self.import_assets()
        self.display_surface = pygame.display.get_surface()
        self.weather_floor_particle_rects = weather_floor_particle_rects

        # Groups
        self.all_sprites = all_sprites
        self.weather_falling_particles = pygame.sprite.Group()
        self.weather_floor_particles = pygame.sprite.Group()

        # For drawing day luminance cycle
        self.sky_luminance_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Thunder timers
        self.thunder_timer = Timer(WEATHER_THUNDER['duration'])
        self.thunder_activation_timer = Timer(
            duration=random.randint(WEATHER_THUNDER['frequency']['min'], WEATHER_THUNDER['frequency']['max']),
            autostart=True,
            repeat=True,
            func=self.activate_thunder
        )

        # Day counter since start of game
        self.day = 0

        # Time of day
        self.current_time = 0

        # Initialise temperature and weather variables
        self.new_temperature_and_weather()

        # Initialise all the weather particles on screen for the first day
        self.initialise_weather_particles()

        # Weather particle timer
        self.weather_particle_timer = Timer(
            duration=WEATHER_PARTICLES['frequency'],
            autostart=True,
            repeat=True,
            func=self.refresh_weather_particles
        )

    def import_assets(self):

        self.assets = {
            'weather particles': import_folders_as_lists('graphics/particles/weather', scale=False)
        }

    # SUPPORT

    def get_particle_type(self):
        # Returns particle type for falling particle depending on weather

        return self.weather_type if self.weather_type in WEATHER_PARTICLES else 'default'

    def get_floor_particle_function(self):
        # Returns function to call when the falling particle for current weather type dies
        # And we want to create the corresponding floor particle (e.g. rain drop -> puddle)

        particle_type = self.get_particle_type()

        if particle_type == 'default':
            return self.create_grass_pile
        elif particle_type == 'snowy':
            return self.create_snow_pile
        else:
            return self.create_puddle

    def get_all_vars(self):
        # Returns string format of all the variables that define the day, for UI

        return {
            'temp': str(self.temp),
            'weather': {
                'category': self.weather_category,
                'type': self.weather_type
            },
            'day of week': self.get_day_of_week(),
            'time division': self.get_time_division()
        }

    def get_day_of_week(self):
        # Converts day integer from when we started game to a day of the week string (mon-sun)

        return DAYS_OF_WEEK[self.day % 7]

    def get_time_division(self):
        # Depending on the current time and the length of the day, see what portion of the day we are in
        # The day is broken down into intervals, which is going to be 5 to correspond with arrows on UI
        # In our case of 5 intervals, we return a number between 0 and 4 to correspond with arrow file

        fraction_of_time = self.current_time / DAY_LENGTH

        for index in range(DAY_INTERVALS):
            if fraction_of_time <= DAY_DIVISIONS[index]:
                return index

    def get_sky_luminance(self):
        # Returns integer between the minimum and maximum luminance values for our day, in a sin wave fashion
        # Mild dusk in the morning, bright for most of the day, darkening towards evening

        return int(((SKY_MAX_LUMINANCE - SKY_MIN_LUMINANCE) / 2) *
                   math.sin(self.current_time * SKY_LUMINANCE_COEFFICIENT) +
                   ((SKY_MAX_LUMINANCE + SKY_MIN_LUMINANCE) / 2))

    def is_valid_floor_particle_position(self, rect):

        return not any(s.colliderect(rect) for s in self.weather_floor_particle_rects)

    def is_night_time(self):

        return self.get_time_division() == DAY_INTERVALS - 1

    def transitioned_to_night_time(self, before_time_division, after_time_division):
        # Considered nighttime if we are in the last day interval

        return before_time_division == (DAY_INTERVALS - 2) and after_time_division == (DAY_INTERVALS - 1)

    # UPDATING & LOGIC

    def new_temperature_and_weather(self):
        # Called at the beginning of a day (either init, or on next_day function call)
        # Sets temperature, weather category & type

        # Temperature
        self.temp = random.choice(TEMPERATURE_RANGE)

        # Weather category, depends on temperature
        self.weather_category = 'hot' if self.temp >= HOT_TEMPERATURE else 'normal'

        # Weather type depends on the temperature and the category

        if self.weather_category == 'hot':
            # Equal chance among the 3 weather types
            self.weather_type = random.choice(['cloudy', 'rain', 'sunny'])

        elif self.weather_category == 'normal':
            # Equal chance to be any of the weather types
            # But if we chose raining, and temp is low enough, change to snow
            self.weather_type = random.choice(['cloudy', 'heavy_rain', 'rain', 'sunny_cloudy', 'sunny'])
            if 'rain' in self.weather_type and self.temp <= SNOW_TEMPERATURE:
                self.weather_type = 'snowy'

    def night_time_temperature_and_weather(self):
        # Called when we transition from day time to nighttime, defined as last portion of the day's intervals
        # Updates temperature, weather category & type

        # Deactivate thunder timer
        # Technically can never have thunder in the day time that causes us to need to deactivate it, but good practice
        self.thunder_timer.deactivate()

        # Decrease temperature by 2
        self.temp = max(0, self.temp - 2)

        # Update the weather category & type. The type depends on current category, type, and temperature

        if self.weather_category == 'hot':

            # Update the weather category
            self.weather_category = 'night'

            if self.weather_type == 'cloudy':
                self.weather_type = random.choice(['clear', 'cloudy', 'rain'])
            elif self.weather_type == 'rain':
                self.weather_type = random.choice(['cloudy', 'rain', 'thunder'])
            elif self.weather_type == 'sunny':
                self.weather_type = random.choice(['clear', 'cloudy'])

        elif self.weather_category == 'normal':

            # Update the weather category
            self.weather_category = 'night'

            if self.weather_type == 'cloudy':
                self.weather_type = random.choice(['clear', 'cloudy', 'rain'])
                if self.weather_type == 'rain' and self.temp <= SNOW_TEMPERATURE:
                    self.weather_type = 'snowy'
            elif self.weather_type == 'heavy_rain':
                # Heavy rain a bit unique: if cannot snow, randomly pick rain or thunder. Otherwise always pick snow
                if self.temp >= (SNOW_TEMPERATURE + 1):
                    self.weather_type = random.choice(['rain', 'thunder'])
                else:
                    self.weather_type = 'snowy'
            elif self.weather_type == 'rain':
                self.weather_type = random.choice(['cloudy', 'rain'])
                if self.weather_type == 'rain' and self.temp <= SNOW_TEMPERATURE:
                    self.weather_type = 'snowy'
            elif self.weather_type == 'snowy':
                self.weather_type = random.choice(['cloudy', 'snowy'])
            elif self.weather_type in ['sunny_cloudy', 'sunny']:
                self.weather_type = random.choice(['clear', 'cloudy'])

    def next_day(self):

        # Increment day counter
        self.day += 1

        # Reset time of day
        self.current_time = 0

        # Kill all weather particles
        for particle in self.weather_falling_particles.sprites():
            particle.kill()
        for particle in self.weather_floor_particles.sprites():
            particle.kill()

        # Turn thunder effect off
        self.thunder_timer.deactivate()

        # New temperature & weather for the day
        self.new_temperature_and_weather()

        # Initialise all the weather particles on screen for the next day
        self.initialise_weather_particles()

    def activate_thunder(self):
        # Called every time the thunder activation timer ticks
        # We change duration of the ticking timer so thunders have randomness in gaps between them
        # Also, see if we need to actually activate thunder flashing based on weather

        self.thunder_activation_timer.duration = random.randint(WEATHER_THUNDER['frequency']['min'], WEATHER_THUNDER['frequency']['max'])

        if self.weather_type == 'thunder':
            self.thunder_timer.activate()

    def create_puddle(self, surf, rect):

        if surf is None and rect is None:
            start_on_random_frame = True
            animation_cycles_to_kill = 2
            rect = self.assets['weather particles']['puddle'][0].get_rect(topleft=random_game_pixel_position())
        else:
            animation_cycles_to_kill = 1
            start_on_random_frame = False

        if self.is_valid_floor_particle_position(rect):
            # Check we can create one here (i.e. on grass, not inside house, etc.)

            StaticParticleEffect(
                pos=rect.topleft,
                frames=self.assets['weather particles']['puddle'],
                groups=[self.all_sprites, self.weather_floor_particles],
                animation_speed=2.5,
                animation_cycles_to_kill=animation_cycles_to_kill,
                start_on_random_frame=start_on_random_frame,
                z=Z_LAYERS['weather floor particles']
            )

    def create_snow_pile(self, surf, rect):

        if surf is None and rect is None:
            surf = random.choice(self.assets['weather particles']['snowy'])
            rect = surf.get_rect(topleft=random_game_pixel_position())

        if self.is_valid_floor_particle_position(rect):
            # Check we can create one here (i.e. on grass, not inside house, etc.)

            SelfDestructGeneric(
                pos=rect.topleft,
                surf=surf,
                death_time=10000,
                groups=[self.all_sprites, self.weather_floor_particles],
                z=Z_LAYERS['weather floor particles']
            )

    def create_grass_pile(self, surf, rect):

        if surf is None and rect is None:
            surf = random.choice(self.assets['weather particles']['default'])
            rect = surf.get_rect(topleft=random_game_pixel_position())

        if self.is_valid_floor_particle_position(rect):
            # Check we can create one here (i.e. on grass, not inside house, etc.)

            SelfDestructGeneric(
                pos=rect.topleft,
                surf=surf,
                death_time=10000,
                groups=[self.all_sprites, self.weather_floor_particles],
                z=Z_LAYERS['weather floor particles']
            )

    def create_weather_particle(self, particle_type, particle_info, start_on_random_frame):
        # Creates a single weather particle

        # Get the relevant function needed to create a floor particle when this falling particle dies
        floor_particle_func = self.get_floor_particle_function()

        MovingParticleEffect(
            pos=random_game_pixel_position(),
            frames=self.assets['weather particles'][particle_type],
            direction=Vector2(particle_info['direction']),
            death_time=random.randint(particle_info['duration']['min'], particle_info['duration']['max']),
            speed=random.randint(particle_info['speed']['min'], particle_info['speed']['max']),
            groups=[self.all_sprites, self.weather_falling_particles],
            animation_speed=particle_info['animation_speed'],
            start_on_random_frame=start_on_random_frame,
            func=floor_particle_func,
            z=Z_LAYERS['weather falling particles']
        )

    def initialise_weather_particles(self):
        # Create lots of falling & floor particles at starts of day so player sees something

        particle_type = self.get_particle_type()
        particle_info = WEATHER_PARTICLES[particle_type]
        floor_particle_func = self.get_floor_particle_function()

        for i in range(particle_info['amount']):
            self.create_weather_particle(particle_type, particle_info, True)
            floor_particle_func(surf=None, rect=None)

    def refresh_weather_particles(self):
        # We have a constantly ticking timer, which calls this function every time it ticks
        # This function tops up falling particles based on the weather

        particle_type = self.get_particle_type()
        particle_info = WEATHER_PARTICLES[particle_type]

        max_weather_particles = particle_info['amount']
        current_weather_particles = len(self.weather_falling_particles.sprites())

        if current_weather_particles < max_weather_particles:

            # If we're near the maximum, create all the remaining particles to get there
            # If we are quite far away, take a fraction of that, to do it incrementally
            number_to_create = max_weather_particles - current_weather_particles
            if number_to_create > 100:
                number_to_create = int(number_to_create/4)

            for i in range(number_to_create):
                self.create_weather_particle(particle_type, particle_info, False)

    def update(self, dt):

        # Update timers
        self.thunder_timer.update()
        self.thunder_activation_timer.update()
        self.weather_particle_timer.update()

        # Increment time of day
        before_time_division = self.get_time_division()
        self.current_time += dt * DAY_SPEED
        after_time_division = self.get_time_division()

        # Cap at day's length
        if self.current_time >= DAY_LENGTH:
            self.current_time = DAY_LENGTH

        # Update weather & temperature if we crossed into nighttime
        elif self.transitioned_to_night_time(before_time_division, after_time_division):
            self.night_time_temperature_and_weather()

    # DRAWING

    def draw_sky(self):

        sky_lum = self.get_sky_luminance()
        self.sky_luminance_image.fill((sky_lum, sky_lum, sky_lum))
        self.display_surface.blit(self.sky_luminance_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw_thunder(self):

        if self.thunder_timer.active:
            if random.randint(0, 9) < WEATHER_THUNDER['intensity']:
                self.display_surface.fill((255, 255, 255))

    def display(self):

        self.draw_thunder()
        self.draw_sky()
