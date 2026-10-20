# level_loader.py
import json
import logging

logger = logging.getLogger(__name__)


def load_level(path="level.json"):
    """
    Загружает конфигурацию уровня из JSON.
    Возвращает словарь или None при ошибке.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Уровень '%s' успешно загружен", data.get("name", "?"))
        return data

    except FileNotFoundError:
        logger.error("Файл уровня '%s' не найден", path)
        print(f"[ОШИБКА] Файл уровня '{path}' не найден. Использую уровень по умолчанию.")
        return None

    except json.JSONDecodeError as e:
        logger.error("Ошибка парсинга JSON в '%s': %s", path, e)
        print(f"[ОШИБКА] Файл уровня повреждён: {e}. Использую уровень по умолчанию.")
        return None


def get_default_level():
    """Уровень по умолчанию — пустое поле 10×10 с выходом в углу."""
    return {
        "name": "Уровень по умолчанию",
        "matrix": [[0] * 10 for _ in range(10)],
        "tile_size": 60,
        "walls": [],
        "exit": [9, 9],
        "enemy_routes": [],
    }