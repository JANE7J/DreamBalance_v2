import sqlite3
from database import get_db_connection

def create_tables():
    """Creates all necessary database tables if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # User table for authentication
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        gender TEXT
    )
    """)

    # Main table for all sleep/dream entries
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
        
        FOREIGN KEY (user_id) REFERENCES User (id)
    )
    """)
    
    # Table for multiple emotions detected in a single dream
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
    print("Database tables (with User table) created successfully.")
