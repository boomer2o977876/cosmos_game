import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("FLIGHT_CENTER_BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("Установи FLIGHT_CENTER_BOT_TOKEN в файле .env или окружении")