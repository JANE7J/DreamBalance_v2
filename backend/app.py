from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import hash_password, check_password, create_token, bcrypt
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
        print("REGISTER DATA:", data)

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
        print("LOGIN DATA:", data)

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

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
