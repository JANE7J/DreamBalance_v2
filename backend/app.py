from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import hash_password, check_password, create_token, bcrypt, token_required
from models import create_tables
import sqlite3
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
CORS(app)
bcrypt.init_app(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dreambalance.db")

# Create tables ONCE at startup
create_tables()

# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HEALTH CHECK ----------------
@app.route("/")
def home():
    return "DreamBalance v2 Backend is Running"

# ---------------- REGISTER ----------------
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        gender = data.get("gender")

        if not username or not email or not password:
            return jsonify({"error": "Missing fields"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            db.close()
            return jsonify({"error": "Email already registered"}), 409

        hashed_password = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, email, password, gender) VALUES (?, ?, ?, ?)",
            (username, email, hashed_password, gender)
        )
        db.commit()

        user_id = cursor.lastrowid
        db.close()

        token = create_token(user_id)

        return jsonify({
            "token": token,
            "username": username
        }), 200

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500

# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing fields"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, username, password FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        db.close()

        if not user or not check_password(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_token(user["id"])

        return jsonify({
            "token": token,
            "username": user["username"]
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500

# ---------------- CALENDAR FETCH ----------------
@app.route("/api/entries/calendar", methods=["GET"])
@token_required
def get_calendar_entries(user_id):
    year = request.args.get("year")
    month = request.args.get("month")

    if not year or not month:
        return jsonify([])

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id,
               entry_date,
               dream_text,
               feeling_after_waking,
               dominant_emotion
        FROM dream_journal
        WHERE user_id = ?
          AND strftime('%Y', entry_date) = ?
          AND strftime('%m', entry_date) = ?
    """, (user_id, year, month.zfill(2)))

    rows = cursor.fetchall()
    db.close()

    return jsonify([dict(row) for row in rows])

@app.route("/api/analytics", methods=["GET"])
@token_required
def analytics(user_id):
    db = get_db()
    cursor = db.cursor()

    # Total dreams
    cursor.execute(
        "SELECT COUNT(*) as total FROM dream_journal WHERE user_id = ?",
        (user_id,)
    )
    total = cursor.fetchone()["total"]

    # Mood distribution
    cursor.execute("""
        SELECT dominant_emotion, COUNT(*) as count
        FROM dream_journal
        WHERE user_id = ?
        GROUP BY dominant_emotion
    """, (user_id,))
    moods = [dict(row) for row in cursor.fetchall()]

    db.close()

    return jsonify({
        "total_dreams": total,
        "mood_distribution": moods
    })


# ---------------- CREATE ENTRY ----------------
@app.route("/api/entries", methods=["POST"])
@token_required
def create_entry(user_id):
    data = request.get_json()

    entry_date = data.get("entry_date")
    description = data.get("description")
    mood = data.get("mood")

    if not entry_date or not mood:
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO dream_journal
        (user_id, entry_date, dream_text, feeling_after_waking, dominant_emotion)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, entry_date, description, mood, mood))

    db.commit()
    db.close()

    return jsonify({"message": "Entry saved"}), 201

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
