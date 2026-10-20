# utils.py
import math
from asteroid import Asteroid
from settings import SHIP_RADIUS


def check_collision(ship, asteroid):
    dx = ship.x - asteroid.x
    dy = ship.y - asteroid.y
    distance = math.hypot(dx, dy)
    return distance < SHIP_RADIUS + asteroid.radius

def spawn_safe_asteroid(ship, min_distance=200):
    """Создаёт астероид, который не появляется слишком близко к кораблю."""
    for _ in range(20):          # максимум 20 попыток
        a = Asteroid()
        if math.hypot(a.x - ship.x, a.y - ship.y) >= min_distance:
            return a
    return Asteroid()

def ship_reached_exit(ship, level):
    """True, если корабль коснулся клетки выхода."""
    if not level:
        return False

    row, col = level["exit"]
    tile = level["tile_size"]

    # Центр клетки выхода в пикселях
    exit_x = col * tile + tile // 2
    exit_y = row * tile + tile // 2

    dist = math.hypot(ship.x - exit_x, ship.y - exit_y)
    return dist < tile // 2  # вошёл в клетку выхода