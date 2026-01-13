import sqlite3
from datetime import datetime

DB_NAME = "weather_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temp INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_to_history(city: str, temp: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute(
        "INSERT INTO history (city, temp, timestamp) VALUES (?, ?, ?)",
        (city.capitalize(), temp, dt_string)
    )
    conn.commit()
    conn.close()

def get_recent_history(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT city, temp, timestamp FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
