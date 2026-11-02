import json
from dataclasses import dataclass, field
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECTORS_PATH = os.path.join(BASE_DIR, "data", "space_sectors.json")

LOG_PATH = os.path.join(BASE_DIR, "..", "flight_data.log")

def load_sectors() -> dict:
    with open(SECTORS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@dataclass
class FlightRow:
    ts: str
    x: float
    y: float
    vx: float
    vy: float
    speed: float
    level: int

@dataclass
class FlightSession:
    start_time: str
    rows: list[FlightRow] = field(default_factory=list)
    
    @property
    def distance(self) -> float:
        # Лог пишется раз в секунду, поэтому дистанция = сумма скоростей
        return sum(row.speed for row in self.rows)
    
    @property
    def max_level(self) -> int:
        return max((row.level for row in self.rows), default=1)
    
    @property
    def avg_speed(self) -> float:
        if not self.rows:
            return 0.0
        return sum(row.speed for row in self.rows) / len(self.rows)

def parse_sessions() -> list[FlightSession]:
    """Читает лог и разбивает его на сессии."""
    sessions = []
    current_session = None

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Обработка маркеров сессии
            if line.startswith("# === SESSION START"):
                # Извлекаем время начала (опционально, для красоты)
                start_time = line.split("SESSION START ")[-1].replace(" ===", "")
                current_session = FlightSession(start_time=start_time)
                continue
                
            if line.startswith("# === SESSION END"):
                if current_session and current_session.rows:
                    sessions.append(current_session)
                current_session = None
                continue

            # Пропускаем заголовки и прочие комментарии
            if line.startswith("#"):
                continue

            # Парсим строки с данными
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 7:
                continue
            try:
                row = FlightRow(
                    ts=parts[0],
                    x=float(parts[1]), y=float(parts[2]),
                    vx=float(parts[3]), vy=float(parts[4]),
                    speed=float(parts[5]),
                    level=int(parts[6]),
                )
                if current_session is not None:
                    current_session.rows.append(row)
            except ValueError:
                continue

    # Если файл закончился без маркера END, но данные были
    if current_session and current_session.rows:
        sessions.append(current_session)

    return sessions

def top_by_distance(sectors: dict, limit: int = 5) -> list[dict]:
    """Возвращает топ сессий по пройденной дистанции."""
    sessions = parse_sessions()
    # Сортируем по убыванию дистанции
    sessions.sort(key=lambda s: s.distance, reverse=True)
    
    names = {lvl["level"]: lvl["name"] for lvl in sectors["levels"]}
    
    result = []
    for s in sessions[:limit]:
        result.append({
            "time": s.start_time,
            "distance": s.distance,
            "level": s.max_level,
            "level_name": names.get(s.max_level, f"Уровень {s.max_level}"),
            "avg_speed": s.avg_speed
        })
    return result

def flight_summary() -> dict:
    """Сводка по всем сессиям (для /flight)."""
    sessions = parse_sessions()
    if not sessions:
        return {"sessions": 0, "total_distance": 0, "max_speed": 0, "total_time": 0}
    
    all_rows = [row for s in sessions for row in s.rows]
    speeds = [r.speed for r in all_rows]
    
    return {
        "sessions": len(sessions),
        "total_distance": sum(s.distance for s in sessions),
        "max_speed": max(speeds) if speeds else 0,
        "total_time": len(all_rows), # секунды
    }

def player_stats(user_id: int) -> dict:
    """Собирает глобальную статистику по логу (так как в игре нет привязки к игроку)."""
    sessions = parse_sessions()
    if not sessions:
        return {"flights": 0, "total_distance": 0.0, "best_level": 1, "achievements": []}
    
    total_distance = sum(s.distance for s in sessions)
    best_level = max((s.max_level for s in sessions), default=1)
    
    # --- Логика ачивок ---
    achievements = []
    
    # 1. За количество полетов
    if len(sessions) >= 20:
        achievements.append("Ветеран космоса (20+ полетов)")
    elif len(sessions) >= 5:
        achievements.append("Опытный пилот (5+ полетов)")

    # 2. За дистанцию
    if total_distance >= 10000:
        achievements.append("Покоритель галактики (10 000+ м)")
    elif total_distance >= 3000:
        achievements.append("Дальний рейс (3 000+ м)")

    # 3. За уровень
    if best_level >= 4:
        achievements.append("Выживший в Осколках кометы (Ур. 4+)")
    elif best_level >= 2:
        achievements.append("Прошел пояс астероидов (Ур. 2+)")

    # 4. За скорость (ищем самую быструю сессию)
    max_avg_speed = max((s.avg_speed for s in sessions), default=0)
    if max_avg_speed >= 4.0:
        achievements.append("Сверхзвуковой (Ср. скорость 4.0+)")

    return {
        "flights": len(sessions),
        "total_distance": total_distance,
        "best_level": best_level,
        "achievements": achievements
    }

def get_best_session() -> dict | None:
    """Возвращает данные лучшей сессии (для отслеживания рекордов)."""
    sessions = parse_sessions()
    if not sessions:
        return None
    
    # Ищем сессию с максимальной дистанцией
    best = max(sessions, key=lambda s: s.distance)
    return {
        "start_time": best.start_time,
        "distance": best.distance,
        "max_level": best.max_level
    }