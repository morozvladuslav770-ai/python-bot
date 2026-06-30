# database.py
import sqlite3

DB_NAME = "barber.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Таблиця записів клієнтів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            phone TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'очікує'  -- 'очікує', 'підтверджено'
        )
    ''')
    
    # 2. Таблиця заблокованих дат (повністю вихідні дні)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_dates (
            date TEXT PRIMARY KEY
        )
    ''')
    
    # 3. Таблиця індивідуальних робочих слотів для конкретних дат
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_schedule (
            date TEXT,
            time TEXT,
            PRIMARY KEY (date, time)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- ФУНКЦІЇ ДЛЯ РОБОТИ З ЗАПИСАМИ ---

def add_booking(user_id, full_name, phone, service, date, time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (user_id, full_name, phone, service, date, time) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, full_name, phone, service, date, time)
    )
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def update_booking_status(booking_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    conn.commit()
    conn.close()

def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

# --- ФУНКЦІЇ ДЛЯ АДМІНІСТРУВАННЯ ГРАФІКУ ---

def block_date(date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO blocked_dates (date) VALUES (?)", (date,))
    conn.commit()
    conn.close()

def unblock_date(date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_dates WHERE date = ?", (date,))
    conn.commit()
    conn.close()

def is_date_blocked(date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blocked_dates WHERE date = ?", (date,))
    result = cursor.fetchone()
    conn.close()
    return result is not None