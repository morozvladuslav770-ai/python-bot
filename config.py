import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не знайдено. Створи файл .env у корені проєкту "
        "(дивись .env.example) і встав туди новий токен з BotFather."
    )