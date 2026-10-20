# ui.py
import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, BLUE,
    LIGHT_GRAY, RED, WHITE, YELLOW
)
from ship import Ship


def draw_menu(screen, start_button, quit_button):
    """Отрисовка главного меню"""
    screen.fill(BLACK)
    
    # Звездный фон
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
    
    # Заголовок
    title_font = pygame.font.Font(None, 80)
    title = title_font.render("КОСМИЧЕСКАЯ", True, BLUE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title, title_rect)
    
    title2 = title_font.render("ОДИССЕЯ", True, BLUE)
    title2_rect = title2.get_rect(center=(SCREEN_WIDTH // 2, 230))
    screen.blit(title2, title2_rect)
    
    # Подзаголовок
    sub_font = pygame.font.Font(None, 30)
    sub = sub_font.render("Управление: W - газ | S - тормоз | A/D - поворот", True, LIGHT_GRAY)
    sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 290))
    screen.blit(sub, sub_rect)
    
    # Рисуем маленький кораблик для красоты
    demo_ship = Ship(SCREEN_WIDTH // 2, 380)
    demo_ship.alpha = -math.pi / 2  # Смотрит вверх
    demo_ship.draw(screen)
    
    # Кнопки
    start_button.draw(screen)
    quit_button.draw(screen)
pass

def ask_player_name(screen, clock):
    """
    Простой ввод имени в стиле аркады.
    Возвращает строку (может быть пустой).
    """
    font = pygame.font.Font(None, 48)
    hint_font = pygame.font.Font(None, 28)

    name = ""
    input_active = True

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15:
                    name += event.unicode

        screen.fill(BLACK)

        title = font.render("Введите имя:", True, YELLOW)
        screen.blit(title, title.get_rect(center=(400, 200)))

        name_surf = font.render(name + "_", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(center=(400, 300)))

        hint = hint_font.render("Enter — подтвердить", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(400, 400)))

        pygame.display.flip()
        clock.tick(30)

    return name.strip() or "Игрок"

def draw_game_over(screen, ship, asteroids, restart_button, quit_button, final_score=0):
    """Отрисовка экрана Game Over"""
    screen.fill(BLACK)
    
    # Продолжаем рисовать астероиды (они не движутся)
    for asteroid in asteroids:
        asteroid.draw(screen)
    
    # Рисуем корабль (но с красным оттенком)
    ship.draw(screen)
    
    # Затемнение
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Заголовок GAME OVER
    font = pygame.font.Font(None, 100)
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(text, text_rect)
    
    # Кнопки
    restart_button.draw(screen)
    quit_button.draw(screen)
    pass