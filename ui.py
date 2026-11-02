# ui.py
import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, BLUE,
    LIGHT_GRAY, RED, YELLOW, WHITE
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

def draw_highscores(screen, records, back_button):
    """
    Экран таблицы рекордов.
    records — список dict от HighScores.top().
    """
    screen.fill(BLACK)

    # звездный фон
    for _ in range(80):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        b = random.randint(80, 200)
        pygame.draw.circle(screen, (b, b, b), (x, y), size)

    # заголовок
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("ТАБЛИЦА РЕКОРДОВ", True, YELLOW)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))

    # заголовки столбцов
    head_font = pygame.font.Font(None, 28)
    row_font  = pygame.font.Font(None, 26)

    left = 60
    col_x = [left, left + 60, left + 130, left + 400, left + 620]
    headers = ["#", "Счёт", "Уровень", "Название уровня", "Дата"]
    for x, h in zip(col_x, headers):
        screen.blit(head_font.render(h, True, LIGHT_GRAY), (x, 130))

    pygame.draw.line(screen, (80, 80, 80), (left, 160),
                     (SCREEN_WIDTH - 40, 160), 2)

    # строки
    y = 175
    if not records:
        msg = row_font.render("Пока нет рекордов. Сыграйте первую игру!",
                              True, LIGHT_GRAY)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 300)))
    else:
        for i, r in enumerate(records[:10], start=1):
            color = YELLOW if i == 1 else WHITE if i <= 3 else LIGHT_GRAY
            screen.blit(row_font.render(f"{i}", True, color), (col_x[0], y))
            screen.blit(row_font.render(f"{r['score']}", True, color), (col_x[1], y))
            screen.blit(row_font.render(f"{r['level']}", True, color), (col_x[2], y))
            screen.blit(row_font.render(f"{r['level_name']}", True, color), (col_x[3], y))
            screen.blit(row_font.render(f"{r['date']}", True, color), (col_x[4], y))
            y += 32

    back_button.draw(screen)