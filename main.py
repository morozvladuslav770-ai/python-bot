# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher

# Імпортуємо модулі повністю, а не окремі змінні (це захищає від зациклення)
import config
import database
from handlers import common, booking, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Ініціалізація бази даних
    database.init_db()
    
    # Створюємо бота, звертаючись до config
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Підключаємо роутери
    dp.include_router(common.router)
    dp.include_router(booking.router)
    dp.include_router(admin.router)

    print("🚀 Бот успішно запустився з адмін-панеллю!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())