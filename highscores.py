# highscores.py
import csv
import os
import time

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), "highscores.csv")
FIELDNAMES = ["date", "score", "level", "level_name", "sector"]


class HighScores:
    """
    Простая таблица рекордов на CSV.
    Файл создаётся автоматически при первом сохранении.
    """
    def __init__(self, csv_path: str = DEFAULT_CSV_PATH, max_records: int = 50):
        self.csv_path = csv_path
        self.max_records = max_records
        

    # ---------- IO ----------
    def _ensure_header(self):
        """Создаёт файл с заголовком, если его нет."""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def load(self) -> list[dict]:
        """Возвращает список записей, отсортированный по счёту (по убыванию)."""
        if not os.path.exists(self.csv_path):
            return []
        records = []
        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        records.append({
                            "date":       row.get("date", ""),
                            "score":      int(row.get("score", 0)),
                            "level":      int(row.get("level", 1)),
                            "level_name": row.get("level_name", ""),
                            "sector":     row.get("sector", ""),
                        })
                    except (ValueError, TypeError):
                        # битая строка — пропускаем
                        continue
        except (OSError, csv.Error):
            return []
        records.sort(key=lambda r: r["score"], reverse=True)
        return records

    def add(self, score: int, level: int, level_name: str, sector: str) -> bool:
        """
        Добавляет запись. Возвращает True, если она попала в топ-max_records.
        """
        try:
            self._ensure_header()
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerow({
                    "date":       time.strftime("%Y-%m-%d %H:%M:%S"),
                    "score":      int(score),
                    "level":      int(level),
                    "level_name": level_name,
                    "sector":     sector,
                })
        except OSError as e:
            print(f"[HighScores] Не удалось записать рекорд: {e}")
            return False

        # если записей стало больше max_records — обрезаем
        records = self.load()
        if len(records) > self.max_records:
            self._rewrite(records[: self.max_records])

        return any(
            r["score"] == score and r["level"] == level
            for r in self.load()[: self.max_records]
        )

    def _rewrite(self, records: list[dict]):
        """Перезаписывает CSV только топ-N записями."""
        try:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                for r in records:
                    writer.writerow(r)
        except OSError as e:
            print(f"[HighScores] Не удалось перезаписать CSV: {e}")

    def top(self, n: int = 10) -> list[dict]:
        return self.load()[:n]