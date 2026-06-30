# handlers/admin.py
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from datetime import datetime, timedelta

import config
import database

router = Router()

# Кнопки для підтвердження/скасування конкретного запису клієнта
def get_admin_booking_kb(booking_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Підтвердити", callback_data=f"adm_confirm_{booking_id}")
    builder.button(text="❌ Скасувати запис", callback_data=f"adm_cancel_{booking_id}")
    builder.adjust(2)
    return builder.as_markup()

# Постійне адмін-меню (клавіатура внизу екрана)
def get_admin_main_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🔒 Керувати вихідними")],
        [KeyboardButton(text="🏠 Клієнтське меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Кнопки для вибору дати, яку треба заблокувати/розблокувати
def get_admin_dates_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    now = datetime.now()
    
    for i in range(7): # Показуємо майстру 7 днів для керування графіком
        date_obj = now + timedelta(days=i)
        date_str = date_obj.strftime("%d.%m")
        
        # Перевіряємо в базі, чи цей день уже є вихідним
        if database.is_date_blocked(date_str):
            status_text = f"🔴 {date_str} (Вихідний)"
        else:
            status_text = f"🟢 {date_str} (Робочий)"
            
        builder.button(text=status_text, callback_data=f"adm_toggle_date_{date_str}")
        
    builder.adjust(1)
    return builder.as_markup()

# --- ОБРОБКА ЗАПИСІВ КЛІЄНТІВ ---

@router.callback_query(F.data.startswith("adm_confirm_"))
async def confirm_booking(callback: types.CallbackQuery):
    await callback.answer()
    booking_id = int(callback.data.split("_")[2])
    
    # ✅ ВИПРАВЛЕНО: додано database.
    database.update_booking_status(booking_id, "підтверджено")
    
    await callback.message.edit_text(
        text=callback.message.text + "\n\n🟢 **СТАТУС: ПІДТВЕРДЖЕНО**"
    )

@router.callback_query(F.data.startswith("adm_cancel_"))
async def cancel_booking(callback: types.CallbackQuery):
    await callback.answer()
    booking_id = int(callback.data.split("_")[2])
    
    # ✅ ВИПРАВЛЕНО: додано database.
    database.delete_booking(booking_id)
    
    await callback.message.edit_text(
        text=callback.message.text + "\n\n🔴 **СТАТУС: СКАСОВАНО**"
    )

# --- КЕРУВАННЯ ГРАФІКОМ (АДМІН-ПАНЕЛЬ) ---

# Вхід в адмінку по команді /admin (тільки для ADMIN_ID)
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return # Звичайних людей ігноруємо
        
    await message.answer(
        "👋 Вітаємо в панелі керування салончиком, Олено!\n"
        "Оберіть потрібну дію в меню нижче:",
        reply_markup=get_admin_main_kb()
    )

# Натиснули кнопку "Керувати вихідними"
@router.message(F.text == "🔒 Керувати вихідними")
async def manage_days(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return
        
    await message.answer(
        "📅 **Налаштування робочих днів**\n\n"
        "Натисніть на день, щоб змінити його статус (Робочий 🔄 Вихідний):",
        reply_markup=get_admin_dates_kb()
    )

# Перемикання статусу дня (Робочий <-> Вихідний) при кліку на дату
@router.callback_query(F.data.startswith("adm_toggle_date_"))
async def toggle_date(callback: types.CallbackQuery):
    await callback.answer()
    date_str = callback.data.split("_")[3]
    
    if database.is_date_blocked(date_str):
        database.unblock_date(date_str) # Робимо знову робочим
    else:
        database.block_date(date_str) # Ставимо вихідний
        
    # Миттєво оновлюємо клавіатуру, щоб Олена бачила зміни кольору кнопок
    await callback.message.edit_reply_markup(reply_markup=get_admin_dates_kb())

# Повернення в клієнтське меню
@router.message(F.text == "🏠 Клієнтське меню")
async def back_to_client(message: types.Message):
    from keyboards.inline import get_main_menu_kb
    await message.answer("Перемкнулися на режим клієнта.", reply_markup=get_main_menu_kb())