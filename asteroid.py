# asteroid.py
import random
import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_SPEED,
    ASTEROID_COLOR, ASTEROID_RADIUS
)


class Asteroid:
    def __init__(self, speed: float = None, radius: int = None):
        # --- позиция спавна за экраном ---
        side = random.randint(0, 3)
        if side == 0:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -ASTEROID_RADIUS
        elif side == 1:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + ASTEROID_RADIUS
        elif side == 2:
            self.x = -ASTEROID_RADIUS
            self.y = random.randint(0, SCREEN_HEIGHT)
        else:
            self.x = SCREEN_WIDTH + ASTEROID_RADIUS
            self.y = random.randint(0, SCREEN_HEIGHT)

        # --- скорость ---
        spd = float(speed) if speed is not None else float(ASTEROID_SPEED)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = spd * math.cos(angle)
        self.vy = spd * math.sin(angle)

        # --- радиус ---
        self.radius = int(radius) if radius is not None else random.randint(15, 30)

        # --- кратеры: генерируем ОДИН раз, чтобы не мерцали в draw() ---
        self.craters = []
        n = random.randint(2, 4)
        for _ in range(n):
            a = random.uniform(0, 2 * math.pi)
            d = random.randint(3, max(4, self.radius - 5))
            self.craters.append((
                d * math.cos(a),
                d * math.sin(a),
                random.randint(2, 5),
            ))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.circle(
            screen, ASTEROID_COLOR,
            (int(self.x), int(self.y)), self.radius
        )
        for cx, cy, cr in self.craters:
            pygame.draw.circle(
                screen, (100, 100, 100),
                (int(self.x + cx), int(self.y + cy)), cr
            )