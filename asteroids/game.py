"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroids
"""
import arcade
import os
import sys
import random
from typing import cast, Dict, Tuple, List, Any

from asteroids.sprites import AsteroidSprite, BulletSprite, ShipSprite
from asteroids.settings import *
from asteroids.util import Score, Scenario, Map


class AsteroidGame(arcade.Window):
    """
    Main application class.

    Based on Asteroid Smasher Example provied in arcade.examples/asteroids

    Shoot space rocks in this demo program created with
    Python and the Arcade library.

    Artwork from http://kenney.nl
    """
    def __init__(self, settings: Dict[str, Any] = None, game_map: Map = None, scenario: Scenario=None):
        settings = settings if settings else {}

        # Map
        self.game_map = game_map if game_map else Map()

        # Store scenario
        self.scenario = scenario if scenario else Scenario(num_asteroids=3)

        # Store game settingsf
        self.frequency = settings.get("frequency", 60)  # Hz
        self.real_time_multiplier = settings.get("real_time_multiplier", 1)
        self.sound_on = settings.get("sound_on", False)  # Whether sounds should play
        self.graphics_on = settings.get("graphics_on", True)  # Whether graphics should be on
        self.lives = settings.get("lives", 3)  # Number of starting lives
        self.prints = settings.get("prints", True)
        self.allow_key_presses = settings.get("allow_key_presses", True)

        if self.real_time_multiplier:
            self.timestep = (1 / float(self.frequency + 1E-6)) / float(self.real_time_multiplier)
        else:
            self.timestep = float(1E-9)

        super().__init__(width=SCREEN_WIDTH,
                         height=SCREEN_HEIGHT,
                         title=SCREEN_TITLE, update_rate=self.timestep, visible=False)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        self.directory = os.path.dirname(os.path.abspath(__file__))

        # Sprite lists
        self.player_sprite_list = None
        self.asteroid_list = None
        self.bullet_list = None
        self.ship_life_list = None

        # Set up the game instance
        self.game_over = None
        self.life_count = None
        self.player_sprite = None

        # Evaluation analytics
        self.score = None

        # Track active keys (from eligible controls)
        self.available_keys = (arcade.key.SPACE, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN)
        self.active_key_presses = list()

        # Register sounds within the game
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

    def _play_sound(self, sound):
        # Private sound playing function (checks stored sound_on) using globally specified volume
        if self.sound_on:
            sound.play(VOLUME)

    def _print_terminal(self, msg: str):
        if self.prints:
            print(msg)

    def start_new_game(self, *args, **kwargs) -> None:
        """ Set up the game and initialize the variables. """
        # Instantiate blank score
        self.score = Score()
        self.score.max_asteroids = self.scenario.max_asteroids

        # Set trackers used for game over checks
        self.life_count = self.lives
        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = ShipSprite(self.frequency, self.game_map.center)
        self.player_sprite_list.append(self.player_sprite)

        # Set up the little icons that represent the player lives.
        cur_pos = 50
        for i in range(self.life_count):
            life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height + 5
            cur_pos += life.width
            self.ship_life_list.append(life)

        # Get the asteroids from the Scenario (which builds them based ont he Scenario settings)
        self.asteroid_list.extend(self.scenario.asteroids(self.frequency))

    def on_draw(self) -> None:
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.asteroid_list.draw()
        self.ship_life_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score.asteroids_hit}"
        arcade.draw_text(output, 10, 110, arcade.color.WHITE, 13)

        output = f"Bullets Fired: {self.score.bullets_fired}"
        arcade.draw_text(output, 10, 90, arcade.color.WHITE, 13)

        output = f"Accuracy (%): {int(100.0 * self.score.accuracy)}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

        output = f"Lives: "
        arcade.draw_text(output, 10, 10, arcade.color.WHITE, 13)

    def fire_bullet(self) -> None:
        """Call to fire a bullet"""

        # Check to see if the ship is allowed to fire based on its built in rate limiter
        if self.player_sprite.can_fire:
            self.score.bullets_fired += 1

            # Skip past the respawning timer
            self.player_sprite.respawning = 0

            self.bullet_list.append(self.player_sprite.fire_bullet())
            self._play_sound(self.laser_sound)

    def on_key_press(self, symbol, modifiers) -> None:
        """ Called whenever a key is pressed. """
        if self.allow_key_presses:
            # Track active keys
            if symbol in self.available_keys:
                self.active_key_presses.append(symbol)

            # Shoot if the player hit the space bar and we aren't respawning.
            if symbol == arcade.key.SPACE:
                self.fire_bullet()

            if symbol == arcade.key.LEFT:
                self.player_sprite.change_angle = self.player_sprite.turn_rate_range[1] / self.frequency
            elif symbol == arcade.key.RIGHT:
                self.player_sprite.change_angle = self.player_sprite.turn_rate_range[0] / self.frequency

            if symbol == arcade.key.UP:
                self.player_sprite.thrust = self.player_sprite.thrust_range[1]
                print(self.player_sprite.thrust)
            elif symbol == arcade.key.DOWN:
                self.player_sprite.thrust = self.player_sprite.thrust_range[0]

    def on_key_release(self, symbol, modifiers) -> None:
        """ Called whenever a key is released. """
        if self.allow_key_presses:

            # Remove released key from active keys list
            if symbol in self.available_keys:
                self.active_key_presses.pop(self.active_key_presses.index(symbol))

            if symbol == arcade.key.LEFT and arcade.key.RIGHT not in self.active_key_presses:
                self.player_sprite.change_angle = 0
            elif symbol == arcade.key.RIGHT and arcade.key.LEFT not in self.active_key_presses:
                self.player_sprite.change_angle = 0
            elif symbol == arcade.key.UP and arcade.key.DOWN not in self.active_key_presses:
                self.player_sprite.thrust = 0
            elif symbol == arcade.key.DOWN and arcade.key.UP not in self.active_key_presses:
                self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite) -> None:
        """ Split an asteroid into chunks. """
        # Add to score
        self.score.asteroids_hit += 1

        if asteroid.size == 4:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, parent_asteroid=asteroid) for i in range(3)])
            self._play_sound(self.hit_sound1)

        elif asteroid.size == 3:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, parent_asteroid=asteroid) for i in range(3)])
            self._play_sound(self.hit_sound2)

        elif asteroid.size == 2:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, parent_asteroid=asteroid) for i in range(3)])
            self._play_sound(self.hit_sound3)

        elif asteroid.size == 1:
            self._play_sound(self.hit_sound4)

        # Remove asteroid from sprites
        asteroid.remove_from_sprite_lists()

    def on_update(self, delta_time: float = 1/60) -> None:
        """
        Move everything

        :param delta_time: Time since last time step
        """
        # print("on_update() game, delta time", delta_time)
        # self.fire_bullet()

        self.score.frame_count += 1

        # Check to see if there any asteroids left
        self.game_over = self.game_over or len(self.asteroid_list) == 0

        # Check if the game is over
        if not self.game_over:
            # Update all sprites
            self.asteroid_list.on_update(delta_time)
            self.bullet_list.on_update(delta_time)
            self.player_sprite_list.on_update(delta_time)

            # Check for collisions between bullets and asteroids
            for bullet in self.bullet_list:
                asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

                # Break up and remove asteroids if there are bullet-asteroid collisions
                for asteroid in asteroids:
                    self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                    bullet.remove_from_sprite_lists()

            # Perform checks on the player sprite if it is not respawning
            if not self.player_sprite.respawn_time_left:

                self.score.distance_travelled += (self.player_sprite.change_x**2+ self.player_sprite.change_y**2)**0.5 # meters

                # Check for collisions with the asteroids (returns collisions)
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)

                # Check if there are ship-asteroid collisions detected
                if len(asteroids) > 0:
                    if self.life_count > 0:
                        self.score.deaths += 1
                        self.life_count -= 1
                        self.player_sprite.respawn(self.game_map.center)
                        self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
                        self.ship_life_list.pop().remove_from_sprite_lists()
                        self._print_terminal("Crash")
                    else:
                        self.game_over = True
                        self._print_terminal("Game over")
                        self.score.max_distance = self.score.frame_count * self.player_sprite.max_speed

    def enable_consistent_randomness(self, seed: int = 0) -> None:
        """
        Call this before environment evaluation to seed the random number generator to provide consistent results

        See [Python ``random`` docs] (https://docs.python.org/3/library/random.html) to learn more

        :param seed: Integer seed value
        :return:
        """
        random.seed(seed)

    def run_single_game(self, *args, **kwargs) -> Score:
        """
        Run a single instance of the game.

        Note: This is the recommended function to use to run the game without graphics

        :return: Score from the environment
        """
        self.start_new_game()

        if self.graphics_on:
            self.on_draw()

        while not self.game_over:
            self.on_update(1 / self.frequency)

        return self.score

    def run_no_graphics(self, *args, **kwargs) -> Score:
        """
        Run a single instance of the game.

        Note: This is the recommended function to use to run the game without graphics

        :return: Score from the environment
        """
        self.start_new_game()

        while not self.game_over:
            self.on_update(1 / self.frequency)

        return self.score

    def run(self) -> None:
        """
        Run a "blocking" version of the game which does not close upon completion.

        Note: This is the recommended way to run the game with graphics on.
        :return:
        """
        self.start_new_game()
        self.center_window()
        arcade.run()


if __name__ == "__main__":
    """ Start the game """
    settings = {
        "frequency": 10,
        "sound_on": False
    }
    window = AsteroidGame(settings, scenario=Scenario(num_asteroids=3))
    window.run()
    # window.run_single_game()

