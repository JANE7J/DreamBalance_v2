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

# ---------------- ANALYZE EMOTIONS ----------------
def analyze_emotions(entries):
    emotion_count = {}

    for row in entries:
        emotion = row["dominant_emotion"]
        if emotion:
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1

    if not emotion_count:
        return {
            "dominant_emotion": "Neutral",
            "emotion_summary": {}
        }

    dominant_emotion = max(emotion_count, key=emotion_count.get)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_summary": emotion_count
    }

# ---------------- GENERATE AI INSIGHT ----------------
def generate_insight(dominant_emotion):
    emotion = dominant_emotion.lower()

    if emotion in ["fear", "anxious", "scared"]:
        return {
            "reasoning": (
                "Your recent dreams show fear-related emotions. "
                "This may indicate stress or anxiety during waking hours."
            ),
            "recommendations": [
                "Practice relaxation before sleep",
                "Reduce screen time at night",
                "Try breathing or meditation exercises"
            ]
        }

    elif emotion in ["sad", "sadness"]:
        return {
            "reasoning": (
                "Your dreams reflect sadness, which may suggest emotional fatigue."
            ),
            "recommendations": [
                "Talk to someone you trust",
                "Engage in light physical activity",
                "Maintain a consistent sleep schedule"
            ]
        }

    elif emotion in ["joy", "happy", "peaceful", "refreshed"]:
        return {
            "reasoning": (
                "Your dreams show positive emotional patterns, indicating balance and recovery."
            ),
            "recommendations": [
                "Maintain your current sleep routine",
                "Continue positive daily habits",
                "Practice gratitude before sleep"
            ]
        }

    else:
        return {
            "reasoning": (
                "Your emotional patterns are mixed this week."
            ),
            "recommendations": [
                "Maintain a balanced routine",
                "Monitor emotional changes",
                "Ensure regular sleep hours"
            ]
        }

# ---------------- MAIN AGENT RESPONSE ----------------
def generate_ai_agent_response(user_id):
    entries = fetch_last_week_entries(user_id)

    emotion_data = analyze_emotions(entries)
    insight = generate_insight(emotion_data["dominant_emotion"])

    return {
        "week_summary": {
            "total_entries": len(entries),
            "dominant_emotion": emotion_data["dominant_emotion"],
            "emotion_summary": emotion_data["emotion_summary"]
        },
        "ai_insight": insight
    }
