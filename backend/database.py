import sqlite3
import os

# Build the path to the database file relative to the backend folder
DB_FOLDER = os.path.join(os.path.dirname(__file__), "..", "database")
DB_PATH = os.path.join(DB_FOLDER, "dreambalance_v2.db")

# Ensure the database directory exists
os.makedirs(DB_FOLDER, exist_ok=True)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
