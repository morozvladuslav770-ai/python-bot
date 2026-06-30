from aiogram import Router, F, types
from aiogram.filters import CommandStart
from keyboards.inline import get_main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\n"
        "Вітаємо у нашому салоні краси ✨\n"
        "Оберіть потрібний пункт у меню нижче 👇",
        reply_markup=get_main_menu_kb()
    )

# Обробка кнопки Локації
@router.message(F.text == "📍 Де ми знаходимось?")
async def show_location(message: types.Message):
    await message.answer("📍 Наша адреса: с. Попельник, вул. Шевченка, 12 ")
    
    # Відправляємо справжню точку на карті. 
    # Вставте сюди реальні широту (latitude) та довготу (longitude) вашого салону
    await message.answer_location(latitude=48.381645, longitude=25.332614)

# Обробка кнопки Контактів
@router.message(F.text == "📞 Контакти")
async def show_contacts(message: types.Message):
    await message.answer(
        "📞 **Наші контакти:**\n\n"
        "👩 Майстер: Олена\n"
        "📱 Телефон: +380 97 123 45 67\n"
        "🕒 Графік роботи: Пн-Сб з 09:00 до 18:00 (Нд — вихідний)"
    )