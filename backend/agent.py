from datetime import datetime, timedelta
import sqlite3
import os

# ---------------- DB CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dreambalance.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- FETCH LAST 7 DAYS ----------------
def fetch_last_week_entries(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dominant_emotion
        FROM dream_journal
        WHERE user_id = ?
          AND entry_date >= date('now','-7 day')
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- ANALYZE CALM vs STRESS ----------------
def analyze_emotions(entries):
    calm_emotions = {"Happy", "Peaceful", "Refreshed", "Energized"}
    stress_emotions = {"Sad", "Anxious", "Scared", "Confused", "Tired"}

    calm_count = 0
    stress_count = 0

    for row in entries:
        emotion = row["dominant_emotion"]
        if not emotion:
            continue

        if emotion in calm_emotions:
            calm_count += 1
        elif emotion in stress_emotions:
            stress_count += 1

    total = calm_count + stress_count

    if total == 0:
        return {
            "calm_percentage": 0,
            "stress_percentage": 0,
            "dominant_state": "Calm"
        }

    calm_pct = round((calm_count / total) * 100)
    stress_pct = round((stress_count / total) * 100)

    dominant_state = "Calm" if calm_pct >= stress_pct else "Stressed"

    return {
        "calm_percentage": calm_pct,
        "stress_percentage": stress_pct,
        "dominant_state": dominant_state
    }


# ---------------- GENERATE AI INSIGHT ----------------
def generate_insight(dominant_state):
    if dominant_state == "Stressed":
        return {
            "reasoning": "Your emotional patterns suggest elevated stress levels this week.",
            "recommendations": [
                "Practice relaxation before sleep",
                "Limit screen time at night",
                "Try breathing or meditation exercises"
            ]
        }

    return {
        "reasoning": "Your dreams reflect a generally calm and balanced emotional state.",
        "recommendations": [
            "Maintain your current routine",
            "Continue healthy sleep habits",
            "Practice gratitude before sleep"
        ]
    }


# ---------------- MAIN AGENT RESPONSE ----------------
def generate_ai_agent_response(user_id):
    entries = fetch_last_week_entries(user_id)
    analysis = analyze_emotions(entries)
    insight = generate_insight(analysis["dominant_state"])

    return {
        "state_distribution": {
            "Calm State": analysis["calm_percentage"],
            "Stress State": analysis["stress_percentage"]
        },
        "ai_insight": insight
    }
