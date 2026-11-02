# flight_recorder.py
import os
import time

DEFAULT_LOG_PATH = os.path.join(os.path.dirname(__file__), "flight_data.log")


class FlightRecorder:
    """
    Каждую секунду записывает в лог:
      timestamp | x | y | vx | vy | speed | level
    """
    def __init__(self, log_path: str = DEFAULT_LOG_PATH, interval: float = 1.0):
        self.log_path = log_path
        self.interval = interval
        self._accum = 0.0
        self._file = None
        self._session_started = False

    # ---------- lifecycle ----------
    def start(self):
        """Открывает лог-файл (в режиме append) и пишет заголовок сессии."""
        self._close()
        self._file = open(self.log_path, "a", encoding="utf-8")
        self._file.write(
            f"\n# === SESSION START {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
        )
        self._file.write("# timestamp | x | y | vx | vy | speed | level\n")
        self._file.flush()
        self._accum = 0.0
        self._session_started = True

    def stop(self):
        """Закрывает файл и пишет маркер завершения сессии."""
        if self._file is not None:
            try:
                self._file.write(
                    f"# === SESSION END {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                )
                self._file.flush()
            finally:
                self._file.close()
                self._file = None
        self._session_started = False

    def _close(self):
        if self._file is not None:
            try:
                self._file.close()
            finally:
                self._file = None

    # ---------- запись ----------
    def update(self, dt: float, ship, level: int = 1):
        """Вызывать каждый кадр. Внутри — таймер на self.interval секунд."""
        if not self._session_started or self._file is None:
            return

        self._accum += dt
        if self._accum < self.interval:
            return
        self._accum -= self.interval

        speed = (ship.vx ** 2 + ship.vy ** 2) ** 0.5
        ts = time.strftime("%H:%M:%S")
        line = (
            f"{ts} | {ship.x:8.2f} | {ship.y:8.2f} | "
            f"{ship.vx:7.3f} | {ship.vy:7.3f} | "
            f"{speed:7.3f} | {level}\n"
        )
        self._file.write(line)
        self._file.flush()

    def __del__(self):
        self._close()