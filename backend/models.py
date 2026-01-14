# models.py

import sqlite3
from database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        gender TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DreamJournal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        sleep_type TEXT,
        sleep_duration_minutes INTEGER,
        had_dream BOOLEAN,
        dream_text TEXT,
        auto_title TEXT,
        user_title TEXT,
        mood_before_sleep TEXT,
        feeling_after_waking TEXT,
        dominant_emotion TEXT,

        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DreamEmotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        emotion TEXT NOT NULL,
        confidence REAL,
        FOREIGN KEY (entry_id) REFERENCES DreamJournal (id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database tables created successfully.")
