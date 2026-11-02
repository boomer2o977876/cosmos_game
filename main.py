# main.py
import time
import math
import random
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, RED, BLUE,
    DARK_BLUE, WHITE, YELLOW, LIGHT_GRAY
)
from ship import Ship
from asteroid import Asteroid
from button import Button
from utils import check_collision
from ui import draw_menu, draw_game_over, draw_highscores
from level_manager import LevelManager
from flight_recorder import FlightRecorder
from highscores import HighScores


def _spawn_asteroid(cfg):
    speed = random.uniform(cfg.speed_min, cfg.speed_max)
    radius = random.randint(cfg.radius_min, cfg.radius_max)
    return Asteroid(speed=speed, radius=radius)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Космическая Одиссея")
    clock = pygame.time.Clock()

    MENU, PLAYING, GAME_OVER, HIGHSCORES = 0, 1, 2, 3
    game_state = MENU

    # --- конфиг уровней, лог, рекорды ---
    try:
        level_manager = LevelManager()
    except RuntimeError as e:
        print("[FATAL] Не удалось загрузить space_sectors.json:")
        print(e)
        pygame.quit()
        return

    recorder   = FlightRecorder()
    highscores = HighScores()

    # --- кнопки (меню: START / SCORES / QUIT) ---
    start_button   = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 60,
                            "START",  GREEN, (0, 200, 0))
    scores_button  = Button(SCREEN_WIDTH // 2 - 100, 475, 200, 60,
                            "SCORES", BLUE, DARK_BLUE)
    quit_button    = Button(SCREEN_WIDTH // 2 - 100, 550, 200, 60,
                            "QUIT",   RED,  (200, 0, 0))
    restart_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 60,
                            "RESTART", BLUE, DARK_BLUE)
    back_button    = Button(SCREEN_WIDTH // 2 - 100, 520, 200, 60,
                            "BACK", GREEN, (0, 200, 0))

    ship = None
    asteroids = []
    score = 0
    score_start_time = 0
    final_score = 0
    spawn_accum = 0.0

    def reset_session():
        nonlocal ship, asteroids, score, score_start_time, spawn_accum
        ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        asteroids = []
        score = 0
        score_start_time = time.time()
        spawn_accum = 0.0
        level_manager.reset()
        cfg = level_manager.current_level
        for _ in range(max(1, cfg.max_asteroids // 2)):
            asteroids.append(_spawn_asteroid(cfg))
        recorder.start()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt > 0.1:
            dt = 0.1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == MENU:
                if start_button.handle_event(event):
                    reset_session()
                    game_state = PLAYING
                if scores_button.handle_event(event):
                    game_state = HIGHSCORES
                if quit_button.handle_event(event):
                    running = False

            elif game_state == PLAYING:
                pass  # управление через get_pressed()

            elif game_state == GAME_OVER:
                if restart_button.handle_event(event):
                    reset_session()
                    game_state = PLAYING
                if quit_button.handle_event(event):
                    running = False

            elif game_state == HIGHSCORES:
                if back_button.handle_event(event):
                    game_state = MENU
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = MENU

        # ---------------- Логика ----------------
        if game_state == PLAYING:
            score = int(time.time() - score_start_time)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]: ship.alpha -= 0.05
            if keys[pygame.K_d]: ship.alpha += 0.05
            if keys[pygame.K_w]: ship.apply_thrust()
            if keys[pygame.K_s]: ship.apply_brake()

            ship.update()
            for a in asteroids:
                a.update()

            changed = level_manager.update(dt)
            cfg = level_manager.current_level
            if changed:
                asteroids.clear()
                spawn_accum = 0.0
                for _ in range(max(1, cfg.max_asteroids // 2)):
                    asteroids.append(_spawn_asteroid(cfg))

            spawn_accum += dt
            while (len(asteroids) < cfg.max_asteroids
                   and spawn_accum >= cfg.spawn_interval):
                spawn_accum -= cfg.spawn_interval
                asteroids.append(_spawn_asteroid(cfg))

            for a in asteroids:
                if check_collision(ship, a):
                    final_score = score
                    game_state = GAME_OVER
                    recorder.stop()
                    highscores.add(
                        score=final_score,
                        level=cfg.level,
                        level_name=cfg.name,
                        sector=level_manager.sector_name,
                    )
                    break

            recorder.update(dt, ship, level=cfg.level)

            # --------- Отрисовка ---------
            screen.fill((0, 0, 0))
            for a in asteroids:
                a.draw(screen)
            ship.draw(screen)

            f = pygame.font.Font(None, 24)
            speed = math.hypot(ship.vx, ship.vy)
            screen.blit(f.render(f"Скорость: {speed:.2f}", True, WHITE), (10, 10))
            sf = pygame.font.Font(None, 36)
            screen.blit(sf.render(f"Счет: {score}", True, YELLOW), (10, 40))
            screen.blit(f.render(f"Сектор: {level_manager.sector_name}", True, LIGHT_GRAY), (10, 80))
            screen.blit(f.render(f"Уровень {cfg.level}: {cfg.name}", True, YELLOW), (10, 105))
            bx, by, bw, bh = 10, 130, 200, 10
            pygame.draw.rect(screen, (60, 60, 60), (bx, by, bw, bh))
            pygame.draw.rect(screen, GREEN,
                             (bx, by, int(bw * level_manager.level_progress()), bh))
            hf = pygame.font.Font(None, 20)
            screen.blit(hf.render("W - газ | S - тормоз | A/D - поворот",
                                  True, LIGHT_GRAY),
                        (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 30))

        elif game_state == MENU:
            draw_menu(screen, start_button, quit_button)
            # SCORES-кнопку рисуем поверх, т.к. draw_menu знает только про две
            scores_button.draw(screen)

        elif game_state == GAME_OVER:
            draw_game_over(screen, ship, asteroids, restart_button,
                           quit_button, final_score)
            f = pygame.font.Font(None, 30)
            lvl_t = f.render(
                f"Уровень: {level_manager.current_level.level} "
                f"({level_manager.current_level.name})",
                True, LIGHT_GRAY,
            )
            screen.blit(lvl_t, lvl_t.get_rect(center=(SCREEN_WIDTH // 2, 500)))

            best = highscores.top(1)
            if best:
                best_t = f.render(f"Рекорд: {best[0]['score']}", True, YELLOW)
                screen.blit(best_t, best_t.get_rect(center=(SCREEN_WIDTH // 2, 540)))

        elif game_state == HIGHSCORES:
            draw_highscores(screen, highscores.top(10), back_button)

        pygame.display.flip()

    recorder.stop()
    pygame.quit()


if __name__ == "__main__":
    main()