# asteroid.py
import random
import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_RADIUS,
    ASTEROID_SPEED, ASTEROID_COLOR
)


class Asteroid:
    def __init__(self):
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

        angle = random.uniform(0, 2 * math.pi)
        self.vx = ASTEROID_SPEED * math.cos(angle)
        self.vy = ASTEROID_SPEED * math.sin(angle)
        self.radius = random.randint(15, 30)   # ← ВОТ ЭТА СТРОКА

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.circle(screen, ASTEROID_COLOR, (int(self.x), int(self.y)), self.radius)
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(5, self.radius - 5)
            crater_x = int(self.x + dist * math.cos(angle))
            crater_y = int(self.y + dist * math.sin(angle))
            crater_size = random.randint(2, 5)
            pygame.draw.circle(screen, (100, 100, 100), (crater_x, crater_y), crater_size)