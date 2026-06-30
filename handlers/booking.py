from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Імпортуємо ТІЛЬКИ клієнтські кнопки
from keyboards.inline import (
    get_categories_kb, get_male_services_kb, get_female_services_kb,
    get_dates_kb, get_time_slots_kb, get_phone_kb, get_main_menu_kb
)

router = Router()

class BookingStates(StatesGroup):
    choosing_category = State()
    choosing_service = State()
    choosing_date = State()       # Новий стан
    choosing_time = State()       # Новий стан
    entering_full_name = State()   # Змінено: Прізвище та Ім'я
    entering_phone = State()       # Новий стан

SERVICES_DICT = {
    "m_classic": "Класична під насадку (250 грн)",
    "m_fade": "Фейд (Low/Mid/High) (300 грн)",
    "m_child": "Дитяча (до 12 років) (200 грн)",
    "m_complex_hair": "Стрижка + миття + укладка (350 грн)",
    "m_beard": "Оформлення бороди (100 грн)",
    "m_color_beard": "Фарбування бороди (100 грн)",
    "m_comp_beard": "Комплекс (Насадка+Борода) (350 грн)",
    "m_full": "Комплекс (Фейд+Борода+Віск) (400 грн)",
    "m_camouflage": "Камуфляж сивини (від 100 грн)",
    "m_wash": "Миття голови окремо (50 грн)",
    
    "f_haircut": "Жіноча стрижка (250 грн)",
    "f_coloring": "Фарбування волосся (від 400 грн)",
    "f_styling": "Укладка волосся (200 грн)"
}

# 1. Старт
@router.message(F.text == "🗓 Записатись на стрижку")
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.choosing_category)
    await message.answer("Оберіть зал:", reply_markup=get_categories_kb())

# 2. Вибір залу
@router.callback_query(F.data.startswith("category_"))
async def category_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split("_")[1]
    await state.update_data(chosen_service=None)
    await state.set_state(BookingStates.choosing_service)
    
    if category == "male":
        await callback.message.edit_text("Оберіть чоловічу послугу:", reply_markup=get_male_services_kb())
    else:
        await callback.message.edit_text("Оберіть жіночу послугу:", reply_markup=get_female_services_kb())

# Назад до залів
@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BookingStates.choosing_category)
    await state.update_data(chosen_service=None)
    await callback.message.edit_text("Оберіть зал:", reply_markup=get_categories_kb())

# 3. Вибір конкретної послуги ➡️ Перехід до Дати
@router.callback_query(BookingStates.choosing_service, F.data.startswith("srv_"))
async def service_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    service_key = callback.data.replace("srv_", "")
    service_name = SERVICES_DICT.get(service_key, "Обрана послуга")
    
    await state.update_data(chosen_service=service_name)
    
    # Перемикаємо на вибір дати
    await state.set_state(BookingStates.choosing_date)
    await callback.message.edit_text("Оберіть зручну дату для запису: 👇", reply_markup=get_dates_kb())

# 4. Вибір ДАТИ ➡️ Перехід до Часу
@router.callback_query(BookingStates.choosing_date, F.data.startswith("date_"))
async def date_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    chosen_date = callback.data.split("_")[1]
    
    await state.update_data(booking_date=chosen_date)
    
    # Перемикаємо на вибір часу
    await state.set_state(BookingStates.choosing_time)
    await callback.message.edit_text(f"Ви обрали дату {chosen_date}.\nТепер оберіть час: 👇", reply_markup=get_time_slots_kb())

# 5. Вибір ЧАСУ ➡️ Запит Прізвища та Імені
@router.callback_query(BookingStates.choosing_time, F.data.startswith("time_"))
async def time_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    chosen_time = callback.data.split("_")[1]
    
    await state.update_data(booking_time=chosen_time)
    
    # Переходимо до текстового введення ПІБ
    await state.set_state(BookingStates.entering_full_name)
    # Використовуємо answer, бо інлайн-меню закінчилось, переходимо в режим діалогу
    await callback.message.answer("Будь ласка, введіть ваше *Прізвище та Ім'я* (наприклад: Майкл Джексон):")

# 6. Обробка ПІБ (Перевірка, щоб було хоча б два слова)
@router.message(BookingStates.entering_full_name)
async def full_name_entered(message: types.Message, state: FSMContext):
    text = message.text.strip()
    
    # Проста валідація: перевіряємо, чи є в тексті пробіл (тобто мінімум два слова)
    if " " not in text or len(text) < 5:
        await message.answer("❌ Помилка! Введіть, будь ласка, і Прізвище, і Ім'я разом через пробіл:")
        return

    await state.update_data(full_name=text)
    
    # Переходимо до запиту телефону
    await state.set_state(BookingStates.entering_phone)
    await message.answer(
        "Залишився останній крок! Надішліть ваш номер телефону за допомогою кнопки нижче або введіть його вручну:",
        reply_markup=get_phone_kb()
    )

# 7. Фінал: Обробка телефону (якщо надіслали кнопкою або написали текстом)

# Оновлений фінальний хендлер:
@router.message(BookingStates.entering_phone)
async def phone_entered(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
        if len(phone) < 9:
            await message.answer("❌ Номер телефону занадто короткий. Спробуйте ще раз:")
            return

    user_data = await state.get_data()
    await state.clear() 
    
    full_name = user_data.get('full_name')
    service = user_data.get('chosen_service')
    b_date = user_data.get('booking_date')
    b_time = user_data.get('booking_time')

    import config
    import database
    from handlers.admin import get_admin_booking_kb

    # 1. ЗБЕРІГАЄМО В БАЗУ ДАНИХ і отримуємо унікальний ID запису
    booking_id = database.add_booking(
        user_id=message.from_user.id,
        full_name=full_name,
        phone=phone,
        service=service,
        date=b_date,
        time=b_time
    )
    
    # 2. ВІДПРАВЛЯЄМО ПОВІДОМЛЕННЯ КЛІЄНТУ
    await message.answer(
        f"🎉 **Запис успішно сформовано!**\n\n"
        f"👤 Клієнт: {full_name}\n"
        f"✂️ Послуга: {service}\n"
        f"📅 Дата: {b_date}\n"
        f"🕒 Час: {b_time}\n\n"
        f"Очікуйте на підтвердження від майстра Олени! ⏳",
        reply_markup=get_main_menu_kb()
    )
    
    # 3. СПОВІЩАЄМО МАЙСТРА (АДМІНА)
    admin_text = (
        f"🔔 **НОВИЙ ЗАПИС НА СТРИЖКУ!** (ID: {booking_id})\n\n"
        f"👤 **Клієнт:** {full_name}\n"
        f"📱 **Телефон:** {phone}\n"
        f"✂️ **Послуга:** {service}\n"
        f"📅 **Дата:** {b_date}\n"
        f"🕒 **Час:** {b_time}"
    )
    
    # Імпортуємо функцію кнопок з admin.py для надсилання майстру
    from handlers.admin import get_admin_booking_kb
    
    # Надсилаємо повідомлення безпосередньо Олені
    await message.bot.send_message(
        chat_id=config.ADMIN_ID, 
        text=admin_text, 
        reply_markup=get_admin_booking_kb(booking_id)
    )