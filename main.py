# main.py
import time
import math
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, RED, BLUE,
    DARK_BLUE, WHITE, YELLOW, LIGHT_GRAY, MAX_ASTEROIDS
)
from ship import Ship
from asteroid import Asteroid
from button import Button
from utils import check_collision
from ui import draw_menu, draw_game_over


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Космическая Одиссея")
    clock = pygame.time.Clock()

    # Состояния игры
    MENU, PLAYING, GAME_OVER = 0, 1, 2
    game_state = MENU

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
                    asteroids = [Asteroid() for _ in range(MAX_ASTEROIDS)]
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
            if keys[pygame.K_a]: ship.alpha -= 0.05
            if keys[pygame.K_d]: ship.alpha += 0.05
            if keys[pygame.K_w]: ship.apply_thrust()
            if keys[pygame.K_s]: ship.apply_brake()

            ship.update()
            for asteroid in asteroids:
                asteroid.update()

            for asteroid in asteroids:
                if check_collision(ship, asteroid):
                    final_score = score
                    game_state = GAME_OVER
                    break

            while len(asteroids) < MAX_ASTEROIDS:
                asteroids.append(Asteroid())

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