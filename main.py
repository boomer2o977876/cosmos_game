# main.py
import time
import math
from venv import logger
import pygame
import logging
import os

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, RED, BLUE,
    DARK_BLUE, WHITE, YELLOW, LIGHT_GRAY, MAX_ASTEROIDS
)
from ship import Ship
from asteroid import Asteroid
from button import Button
from utils import check_collision, spawn_safe_asteroid
from ui import draw_menu, draw_game_over
from level_loader import load_level, get_default_level
from utils import check_collision, ship_reached_exit
from scores import save_score
from ui import ask_player_name

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/game.log", encoding="utf-8"),
        logging.StreamHandler(),   # опционально: вывод в консоль
    ],
)




def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Космическая Одиссея")
    clock = pygame.time.Clock()

    # Состояния игры
    MENU, PLAYING, GAME_OVER = 0, 1, 2
    game_state = MENU

    level = load_level("level.json")
    if level is None:
        level = get_default_level()

    final_score = 0

    # Сохраняем уровень в game_state / в объект игры
    # game.level = level

    

    # Кнопки
    start_button = Button(SCREEN_WIDTH // 2 - 100, 450, 200, 60,
                          "START", GREEN, (0, 200, 0))
    quit_button = Button(SCREEN_WIDTH // 2 - 100, 530, 200, 60,
                         "QUIT", RED, (200, 0, 0))
    restart_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 60,
                            "RESTART", BLUE, DARK_BLUE)

    # Игровые объекты
    ship = None
    asteroids = []

    # Счет
    score = 0
    score_start_time = 0
    final_score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == MENU:
                if start_button.handle_event(event):
                    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    asteroids = [spawn_safe_asteroid(ship) for _ in range(MAX_ASTEROIDS)]
                    score = 0
                    score_start_time = time.time()
                    game_state = PLAYING
                if quit_button.handle_event(event):
                    running = False

            elif game_state == GAME_OVER:
                if restart_button.handle_event(event):
                    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    asteroids = [Asteroid() for _ in range(MAX_ASTEROIDS)]
                    score = 0
                    score_start_time = time.time()
                    game_state = PLAYING
                if quit_button.handle_event(event):
                    running = False

        # Логика
        if game_state == PLAYING:
            score = int(time.time() - score_start_time)

            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_w]:
                ship.apply_thrust()
                logger.debug("Шаг игрока: тяга (vx=%.2f, vy=%.2f)", ship.vx, ship.vy)

            
            if keys[pygame.K_a]: ship.alpha -= 0.05
            if keys[pygame.K_d]: ship.alpha += 0.05
            if keys[pygame.K_w]: ship.apply_thrust()
            if keys[pygame.K_s]: ship.apply_brake()

            ship.update()
            for asteroid in asteroids:
                asteroid.update()

            if check_collision(ship, asteroid):
                logger.info("Поражение. Счёт: %d", score)

            player = ask_player_name(screen, clock)
            save_score(player, score, result="lose")

            final_score = score
            game_state = GAME_OVER
            break

            for asteroid in asteroids:
                for asteroid in asteroids:
                    dx = ship.x - asteroid.x
                    dy = ship.y - asteroid.y
                    dist = math.hypot(dx, dy)
                    print(f"ship=({ship.x:.0f},{ship.y:.0f}) ast=({asteroid.x:.0f},{asteroid.y:.0f}) "
                    f"r={asteroid.radius} dist={dist:.0f}")
                if check_collision(ship, asteroid):
                    logger.info("Поражение. Финальный счёт: %d", score)
                    final_score = score
                    game_state = GAME_OVER
                    break

            if game_state == PLAYING and ship_reached_exit(ship, level):
                logger.info("Победа! Счёт: %d", score)
                final_score = score
                game_state = GAME_OVER

            while len(asteroids) < MAX_ASTEROIDS:
                asteroids.append(spawn_safe_asteroid(ship))

            # Отрисовка
            screen.fill((0, 0, 0))
            for asteroid in asteroids:
                asteroid.draw(screen)
            ship.draw(screen)

            # Счет и скорость
            font_info = pygame.font.Font(None, 24)
            speed = math.hypot(ship.vx, ship.vy)
            screen.blit(font_info.render(f"Скорость: {speed:.2f}", True, WHITE), (10, 10))
            score_font = pygame.font.Font(None, 36)
            screen.blit(score_font.render(f"Счет: {score}", True, YELLOW), (10, 40))

            hint_font = pygame.font.Font(None, 20)
            hint = hint_font.render("W - газ | S - тормоз | A/D - поворот", True, LIGHT_GRAY)
            screen.blit(hint, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 30))

        elif game_state == MENU:
            draw_menu(screen, start_button, quit_button)

        elif game_state == GAME_OVER:
            draw_game_over(screen, ship, asteroids, restart_button, quit_button, final_score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()