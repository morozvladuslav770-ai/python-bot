from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
 
# Головне меню
def get_main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🗓 Записатись на стрижку")],
        [KeyboardButton(text="📍 Де ми знаходимось?"), KeyboardButton(text="📞 Контакти")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
 
# Вибір категорії
def get_categories_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👨 Чоловічий зал", callback_data="category_male")
    builder.button(text="👩 Жіночий зал", callback_data="category_female")
    builder.adjust(2)
    return builder.as_markup()
 
# Чоловічі послуги
def get_male_services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Класична під насадку — 250 грн", callback_data="srv_m_classic")
    builder.button(text="Фейд (Low/Mid/High) — 300 грн", callback_data="srv_m_fade")
    builder.button(text="Дитяча (до 12 років) — 200 грн", callback_data="srv_m_child")
    builder.button(text="Стрижка + миття + укладка — 350 грн", callback_data="srv_m_complex_hair")
    builder.button(text="Оформлення бороди — 100 грн", callback_data="srv_m_beard")
    builder.button(text="Фарбування бороди — 100 грн", callback_data="srv_m_color_beard")
    builder.button(text="Комплекс (Насадка+Борода) — 350 грн", callback_data="srv_m_comp_beard")
    builder.button(text="Комплекс (Фейд+Борода+Віск) — 400 грн", callback_data="srv_m_full")
    builder.button(text="Камуфляж сивини — від 100 грн", callback_data="srv_m_camouflage")
    builder.button(text="Миття голови окремо — 50 грн", callback_data="srv_m_wash")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    return builder.as_markup()
 
# Жіночі послуги
def get_female_services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Жіноча стрижка — 250 грн", callback_data="srv_f_haircut")
    builder.button(text="Фарбування волосся — від 400 грн", callback_data="srv_f_coloring")
    builder.button(text="Укладка волосся — 200 грн", callback_data="srv_f_styling")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    return builder.as_markup()
 
# Динамічні кнопки для вибору ДАТИ (найближчі 5 днів)
def get_dates_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    now = datetime.now()
    
    # 📥 Імпортуємо базу локально всередині функції
    import database
    
    weekdays = ["Пн", "Вв", "Ср", "Чт", "Пт", "Сб", "Нд"]
    
    for i in range(5):
        date_obj = now + timedelta(days=i)
        date_str = date_obj.strftime("%d.%m")
        
        # 🔥 ЯКЩО ДАТА БЛОКОВАНА МАЙСТРОМ — ПРОПУСКАЄМО ЇЇ, КЛІЄНТ ЇЇ НЕ ПОБАЧИТЬ
        if database.is_date_blocked(date_str):
            continue
            
        day_name = weekdays[date_obj.weekday()]
        display_text = f"{day_name}, {date_str}"
        if i == 0:
            display_text = f"🍏 Сьогодні ({date_str})"
        elif i == 1:
            display_text = f"🍋 Завтра ({date_str})"
            
        builder.button(text=display_text, callback_data=f"date_{date_str}")
        
    builder.adjust(1)
    return builder.as_markup()
 
# Кнопки для вибору ЧАСУ (Слоти роботи салону), з урахуванням вже зайнятих
def get_time_slots_kb(date_str: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Припустимо, салон працює з 09:00 до 17:00 щогодини
    slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
 
    import database
    booked = set(database.get_booked_times(date_str))
 
    for slot in slots:
        if slot in booked:
            continue  # Зайнятий слот клієнту не показуємо
        builder.button(text=slot, callback_data=f"time_{slot}")
 
    builder.adjust(3) # Кнопки по 3 в ряд, щоб виглядало як сітка
    return builder.as_markup()
 
# Кнопка для швидкої відправки телефону
def get_phone_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📱 Надіслати свій номер телефону", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)