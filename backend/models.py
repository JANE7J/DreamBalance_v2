import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dreambalance.db")

def create_tables():
    """Creates all required tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ USERS TABLE (matches app.py queries exactly)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        gender TEXT
    )
    """)

    # Dream journal entries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dream_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry_date TEXT,
        sleep_type TEXT,
        sleep_duration_minutes INTEGER,
        had_dream INTEGER,
        dream_text TEXT,
        mood_before_sleep TEXT,
        feeling_after_waking TEXT,
        dominant_emotion TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Emotion detection table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dream_emotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        emotion TEXT NOT NULL,
        confidence REAL,
        FOREIGN KEY (entry_id) REFERENCES dream_journal(id)
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database tables created successfully")
