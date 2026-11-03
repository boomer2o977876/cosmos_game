# ship.py
import math
import pygame
from settings import (
    SHIP_RADIUS, THRUST, BRAKE_THRUST,
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
)


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 0
        self.vx = 0.0
        self.vy = 0.0
        self.is_braking = False


    def draw(self, screen):
        # Корпус корабля
        points = [
            (self.x + SHIP_RADIUS * math.cos(self.alpha),
             self.y + SHIP_RADIUS * math.sin(self.alpha)),
            (self.x + SHIP_RADIUS * 0.6 * math.cos(self.alpha + 2.5),
             self.y + SHIP_RADIUS * 0.6 * math.sin(self.alpha + 2.5)),
            (self.x + SHIP_RADIUS * 0.6 * math.cos(self.alpha - 2.5),
             self.y + SHIP_RADIUS * 0.6 * math.sin(self.alpha - 2.5))
        ]
        pygame.draw.polygon(screen, WHITE, points)

        # Пламя торможения
        if self.is_braking:
            speed = math.hypot(self.vx, self.vy)
            if speed > 0.5:
                flame_length = 15
                flame_points = [
                    (self.x + SHIP_RADIUS * 1.1 * math.cos(self.alpha + math.pi),
                     self.y + SHIP_RADIUS * 1.1 * math.sin(self.alpha + math.pi)),
                    (self.x + (SHIP_RADIUS + flame_length) * math.cos(self.alpha + math.pi + 0.5),
                     self.y + (SHIP_RADIUS + flame_length) * math.sin(self.alpha + math.pi + 0.5)),
                    (self.x + (SHIP_RADIUS + flame_length) * math.cos(self.alpha + math.pi - 0.5),
                     self.y + (SHIP_RADIUS + flame_length) * math.sin(self.alpha + math.pi - 0.5))
                ]
                pygame.draw.polygon(screen, (255, 100, 0), flame_points)

                flame_points_inner = [
                    (self.x + SHIP_RADIUS * 1.1 * math.cos(self.alpha + math.pi),
                     self.y + SHIP_RADIUS * 1.1 * math.sin(self.alpha + math.pi)),
                    (self.x + (SHIP_RADIUS + flame_length * 0.5) * math.cos(self.alpha + math.pi + 0.3),
                     self.y + (SHIP_RADIUS + flame_length * 0.5) * math.sin(self.alpha + math.pi + 0.3)),
                    (self.x + (SHIP_RADIUS + flame_length * 0.5) * math.cos(self.alpha + math.pi - 0.3),
                     self.y + (SHIP_RADIUS + flame_length * 0.5) * math.sin(self.alpha + math.pi - 0.3))
                ]
                pygame.draw.polygon(screen, (255, 255, 100), flame_points_inner)