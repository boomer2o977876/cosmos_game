import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from watchdog import record_watcher # Импортируем воркер

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    # Запускаем фоновый воркер
    asyncio.create_task(record_watcher(bot))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())