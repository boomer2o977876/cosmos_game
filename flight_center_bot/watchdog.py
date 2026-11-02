import asyncio
import logging
from aiogram import Bot
from analytics import get_best_session
from session_store import _read_all # Импортируем функцию чтения всех сессий

logger = logging.getLogger(__name__)

async def record_watcher(bot: Bot, interval: int = 15):
    """
    Фоновый цикл, который проверяет появление новых рекордов.
    """
    logger.info("Фоновый воркер /watch запущен.")
    last_best_time = None

    # Инициализируем последний рекорд при старте, чтобы не спамить старыми данными
    initial_best = get_best_session()
    if initial_best:
        last_best_time = initial_best["start_time"]

    while True:
        await asyncio.sleep(interval)
        
        current_best = get_best_session()
        if not current_best:
            continue

        # Если появился новый рекорд (время начала сессии изменилось)
        if current_best["start_time"] != last_best_time:
            # Если мы знали старый рекорд и новый больше него, или это вообще первый рекорд
            logger.info(f"Обнаружен новый рекорд: {current_best['distance']} м")
            
            # Получаем всех, у кого включены уведомления
            all_sessions = await _read_all()
            for user_id_str, sess in all_sessions.items():
                if sess.get("watch"):
                    try:
                        text = (
                            "<b>🚨 Новый рекорд полёта!</b>\n\n"
                            f"Дистанция: <b>{current_best['distance']:.0f}</b> м\n"
                            f"Максимальный уровень: <b>{current_best['max_level']}</b>\n"
                            f"Дата полёта: {current_best['start_time']}"
                        )
                        await bot.send_message(chat_id=int(user_id_str), text=text, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Не удалось отправить уведомление {user_id_str}: {e}")
            
            # Запоминаем новый рекорд
            last_best_time = current_best["start_time"]