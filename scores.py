# scores.py
import csv
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SCORES_FILE = "scores.csv"
HEADERS = ["timestamp", "player", "score", "result"]


def save_score(player_name, score, result):
    """
    Дописывает строку в CSV-файл рекордов.
    Если файла нет — создаёт его с заголовками.
    """
    file_exists = os.path.isfile(SCORES_FILE)

    try:
        with open(SCORES_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(HEADERS)
                logger.info("Создан файл рекордов '%s'", SCORES_FILE)

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                player_name,
                score,
                result,   # "win" / "lose"
            ])
            logger.info("Рекорд сохранён: %s, %d, %s", player_name, score, result)

    except OSError as e:
        logger.error("Не удалось записать рекорд: %s", e)
        print(f"[ОШИБКА] Не удалось сохранить рекорд: {e}")