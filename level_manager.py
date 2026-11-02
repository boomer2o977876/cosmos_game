# level_manager.py
import json
import os

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "space_sectors.json")


class LevelConfig:
    """Один уровень (волна) с параметрами астероидов."""
    def __init__(self, data: dict):
        self.level            = int(data["level"])
        self.name             = str(data["name"])
        self.max_asteroids    = int(data["max_asteroids"])
        self.speed_min        = float(data["asteroid_speed_min"])
        self.speed_max        = float(data["asteroid_speed_max"])
        self.radius_min       = int(data["asteroid_radius_min"])
        self.radius_max       = int(data["asteroid_radius_max"])
        self.spawn_interval   = float(data["spawn_interval_seconds"])

    def __repr__(self):
        return f"<Level {self.level} '{self.name}' max={self.max_asteroids}>"


class LevelManager:
    """
    Читает space_sectors.json, инициализирует сектор
    и переключает уровни каждые level_duration_seconds.
    """
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self.sector_name = "Unknown Sector"
        self.level_duration = 30.0
        self.levels: list[LevelConfig] = []

        self.current_index = 0
        self.elapsed_in_level = 0.0
        self.total_elapsed = 0.0

        self._load()

    # ---------- загрузка ----------
    def _load(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Файл конфигурации сектора не найден: {self.config_path}"
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Ошибка парсинга JSON в {self.config_path}: {e}"
            )

        self.sector_name    = data.get("sector_name", "Unknown Sector")
        self.level_duration = float(data.get("level_duration_seconds", 30))

        raw_levels = data.get("levels", [])
        if not raw_levels:
            raise RuntimeError("В space_sectors.json нет ни одного уровня (levels пуст).")

        try:
            self.levels = [LevelConfig(lvl) for lvl in raw_levels]
        except KeyError as e:
            raise RuntimeError(f"В конфигурации уровня отсутствует поле: {e}")

        # гарантируем сортировку по номеру
        self.levels.sort(key=lambda lv: lv.level)

    # ---------- состояние ----------
    @property
    def current_level(self) -> LevelConfig:
        return self.levels[self.current_index]

    def is_last_level(self) -> bool:
        return self.current_index >= len(self.levels) - 1

    # ---------- обновление ----------
    def update(self, dt: float) -> bool:
        """
        Возвращает True, если уровень только что сменился
        (удобно для сброса/переспавна астероидов).
        """
        self.elapsed_in_level += dt
        self.total_elapsed += dt

        if self.elapsed_in_level >= self.level_duration:
            self.elapsed_in_level -= self.level_duration
            if not self.is_last_level():
                self.current_index += 1
            # если последний — остаёмся на нём (бесконечный «финальный» сектор)
            return True
        return False

    def reset(self):
        self.current_index = 0
        self.elapsed_in_level = 0.0
        self.total_elapsed = 0.0

    def level_progress(self) -> float:
        """0.0 .. 1.0 — прогресс внутри текущего уровня."""
        if self.level_duration <= 0:
            return 1.0
        return min(1.0, self.elapsed_in_level / self.level_duration)