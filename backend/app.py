from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import hash_password, check_password, create_token
import sqlite3
import os
from auth import bcrypt
from models import create_tables

app = Flask(__name__)

CORS(app)
bcrypt.init_app(app)
create_tables()

DB_PATH = os.path.join(os.path.dirname(__file__), "dreambalance.db")

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

        if not all([username, email, password]):
            return jsonify({"error": "Missing fields"}), 400

        db = get_db()
        cursor = db.cursor()

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered"}), 409

        hashed = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, email, password, gender) VALUES (?, ?, ?, ?)",
            (username, email, hashed, gender)
        )
        db.commit()

        user_id = cursor.lastrowid
        token = create_token(user_id)

        return jsonify({
            "token": token,
            "username": username
        }), 200

    except Exception as e:
        print("REGISTER ERROR:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        print("LOGIN DATA:", data)

        email = data.get("email")
        password = data.get("password")

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, username, password FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()

        if not user or not check_password(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_token(user["id"])

        return jsonify({
            "token": token,
            "username": user["username"]
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
