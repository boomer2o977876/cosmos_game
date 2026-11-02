# utils.py
import math
from settings import SHIP_RADIUS


def check_collision(ship, asteroid):
    dx = ship.x - asteroid.x
    dy = ship.y - asteroid.y
    distance = math.hypot(dx, dy)
    return distance < SHIP_RADIUS + asteroid.radius