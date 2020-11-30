import random
import math
import arcade

from typing import cast, Dict, Tuple, List, Any

from asteroids.settings import *


class BulletSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def __init__(self, starting_angle: float, starting_position: Tuple[float, float]):
        """ Set up a bullet sprite. """
        # Call the parent Sprite constructor
        super().__init__(":resources:images/space_shooter/laserBlue01.png", SCALE)

        # Set GUID
        self.guid = "Bullet"

        # Set the starting states
        self.bullet_speed = 13
        self.change_y = math.cos(math.radians(starting_angle)) * self.bullet_speed
        self.change_x = -math.sin(math.radians(starting_angle)) * self.bullet_speed
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))

        self.center_x, self.center_y = starting_position

        # Update the bullet sprite
        self.update()

    @property
    def state(self) -> Dict[str, Tuple[float, float]]:
        return {
            "position": tuple(self.position),
            "velocity": tuple(self.velocity)
        }


class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(":resources:images/space_shooter/playerShip1_orange.png", SCALE)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.04

        # Manage respawns/firing vvia timers
        self.respawning = 0
        self.fire_limiter = 0

        # Mark that we are respawning.
        self.respawn()

    @property
    def state(self) -> Dict[str, Tuple]:
        return {
            "position": tuple(self.position),
            "velocity": tuple(self.velocity),
            "angle": self.angle
        }

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.speed = 0
        self.angle = 0

    def update(self):
        """
        Update our position and other particulars.
        """
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 255
        else:
            if self.alpha != 255:
                self.alpha = 255

        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        if self.left > SCREEN_WIDTH:
            self.right = 0

        if self.bottom < 0:
            self.top = SCREEN_HEIGHT

        if self.top > SCREEN_HEIGHT:
            self.bottom = 0

        """ Call the parent class. """
        super().update()


class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """
    def __init__(self, parent_asteroid=None):
        self.size = parent_asteroid.size-1 if parent_asteroid else 4

        # Images dict for lookup/selection of sprite images
        images = {
            4: (":resources:images/space_shooter/meteorGrey_big1.png",
                ":resources:images/space_shooter/meteorGrey_big2.png",
                ":resources:images/space_shooter/meteorGrey_big3.png",
                ":resources:images/space_shooter/meteorGrey_big4.png"),
            3: (":resources:images/space_shooter/meteorGrey_med1.png",
                ":resources:images/space_shooter/meteorGrey_med2.png"),
            2: (":resources:images/space_shooter/meteorGrey_small1.png",
                ":resources:images/space_shooter/meteorGrey_small2.png"),
            1: (":resources:images/space_shooter/meteorGrey_tiny1.png",
                ":resources:images/space_shooter/meteorGrey_tiny2.png")
        }

        # Call Sprite constructor
        super().__init__(random.choice(images[self.size]), scale=SCALE*1.5)

        # Set GUID
        self.guid = "Asteroid"

        # Set initial angle
        self.change_angle = (random.random() - 0.5) * 2

        # Set initial speed based off of scaling factor
        speed_scaler = 2.0 + (4.0 - self.size) / 4.0
        self.change_x = (random.random() * speed_scaler) - (speed_scaler / 2.0)
        self.change_y = (random.random() * speed_scaler) - (speed_scaler / 2.0)

        # Other settings for if the asteroid is based off a recently destroyed parent
        if parent_asteroid:
            self.center_x = parent_asteroid.center_x
            self.center_y = parent_asteroid.center_y
        else:
            self.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
            self.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)

    @property
    def state(self) -> Dict[str, Tuple[float, float]]:
        return {
            "position": tuple(self.position),
            "velocity": tuple(self.velocity)
        }

    def update(self):
        """ Move the asteroid around. """
        super().update()
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT
