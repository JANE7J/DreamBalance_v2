from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from agent import generate_ai_agent_response

from models import create_tables
from database import get_db_connection
from auth import hash_password, check_password, create_token, token_required, bcrypt

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"])
bcrypt.init_app(app)

@app.route("/")
def home():
    return "DreamBalance v2 Backend is Running"

# ---------------- AUTH ---------------- #

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO User (username, email, password_hash, gender) VALUES (?, ?, ?, ?)",
            (
                data["username"],
                data["email"],
                hash_password(data["password"]),
                data.get("gender")
            )
        )
        conn.commit()
    except conn.IntegrityError:
        return jsonify({"error": "User already exists"}), 409
    finally:
        conn.close()

    token = create_token(cursor.lastrowid)
    return jsonify({"token": token, "username": data["username"]}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM User WHERE email = ?", (data["email"],))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password(user["password_hash"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "token": create_token(user["id"]),
        "username": user["username"]
    })


# ---------------- ENTRIES ---------------- #

@app.route("/api/entries", methods=["POST"])
@token_required
def add_entry(current_user_id):
    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    mood = data.get("mood", "").strip()
    entry_date = data.get("entry_date")

    if not title or not description or not mood or not entry_date:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO DreamJournal (
            user_id,
            entry_date,
            user_title,
            dream_text,
            feeling_after_waking,
            dominant_emotion,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        current_user_id,
        entry_date,
        title,
        description,
        mood,
        mood
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Entry added"}), 201


@app.route("/api/entries/calendar", methods=["GET"])
@token_required
def get_calendar_entries(current_user_id):
    year = request.args.get("year")
    month = request.args.get("month").zfill(2)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            entry_date,
            user_title,
            COALESCE(dream_text, '') AS dream_text,
            COALESCE(feeling_after_waking, 'Unknown') AS feeling_after_waking,
            COALESCE(dominant_emotion, 'Unknown') AS dominant_emotion
        FROM DreamJournal
        WHERE user_id = ?
          AND strftime('%Y', entry_date) = ?
          AND strftime('%m', entry_date) = ?
        ORDER BY entry_date DESC, id DESC
    """, (current_user_id, year, month))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/entries/<int:entry_id>", methods=["PUT"])
@token_required
def update_entry(current_user_id, entry_id):
    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    mood = data.get("mood", "").strip()

    if not title or not description or not mood:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE DreamJournal
        SET
            user_title = ?,
            dream_text = ?,
            feeling_after_waking = ?,
            dominant_emotion = ?
        WHERE id = ? AND user_id = ?
    """, (
        title,
        description,
        mood,
        mood,
        entry_id,
        current_user_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Entry updated"})


# ---------------- ANALYTICS ---------------- #

@app.route("/api/analytics", methods=["GET"])
@token_required
def analytics(current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dominant_emotion, COUNT(*) as count
        FROM DreamJournal
        WHERE user_id = ?
        GROUP BY dominant_emotion
    """, (current_user_id,))

    rows = cursor.fetchall()
    conn.close()

    calm = {"Happy","Peaceful","Energized","Relaxed","Refreshed","Content","Neutral"}
    state = {"Calm State": 0, "Stress State": 0}

    for r in rows:
        if r["dominant_emotion"] in calm:
            state["Calm State"] += r["count"]
        else:
            state["Stress State"] += r["count"]

    total = sum(state.values()) or 1
    for k in state:
        state[k] = round(state[k] * 100 / total)

    return jsonify({
        "state_distribution": state,
        "ai_agent": generate_ai_agent_response(current_user_id)
    })


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5001)
