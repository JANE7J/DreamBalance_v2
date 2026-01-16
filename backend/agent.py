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
    calm_emotions = {
        "happy", "peaceful", "refreshed", "energized"
    }
    stress_emotions = {
        "sad", "anxious", "scared", "confused", "tired", "fear"
    }

    calm_count = 0
    stress_count = 0

    for row in entries:
        emotion = row["dominant_emotion"]
        if not emotion:
            continue

        emotion = emotion.strip().lower()

        if emotion in calm_emotions:
            calm_count += 1
        elif emotion in stress_emotions:
            stress_count += 1

    total = calm_count + stress_count

    if total == 0:
        return {
            "calm_percentage": 0,
            "stress_percentage": 0,
            "dominant_state": "Calm State"
        }

    calm_pct = round((calm_count / total) * 100)
    stress_pct = round((stress_count / total) * 100)

    dominant_state = (
        "Calm State" if calm_pct >= stress_pct else "Stress State"
    )

    return {
        "calm_percentage": calm_pct,
        "stress_percentage": stress_pct,
        "dominant_state": dominant_state
    }


# ---------------- GENERATE AI INSIGHT ----------------
def generate_insight(dominant_state):
    if dominant_state == "Stress State":
        return {
            "reasoning": "Your emotional patterns indicate elevated stress levels this week.",
            "recommendations": [
                "Practice relaxation before sleep",
                "Reduce screen time at night",
                "Try breathing or meditation exercises"
            ]
        }

    return {
        "reasoning": "Your dreams suggest a calm and balanced mental state.",
        "recommendations": [
            "Maintain your current sleep routine",
            "Continue positive daily habits",
            "Practice gratitude before sleep"
        ]
    }


# ---------------- MAIN AGENT RESPONSE ----------------
def generate_ai_agent_response(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch last 7 days ordered by most recent
    cursor.execute("""
        SELECT dominant_emotion, entry_date
        FROM dream_journal
        WHERE user_id = ?
          AND entry_date >= date('now','-7 day')
        ORDER BY entry_date DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    calm_emotions = {"happy", "peaceful", "refreshed", "energized"}
    stress_emotions = {"sad", "anxious", "scared", "confused", "tired", "fear"}

    calm_count = 0
    stress_count = 0

    for row in rows:
        emotion = row["dominant_emotion"]
        if not emotion:
            continue

        emotion = emotion.lower().strip()
        if emotion in calm_emotions:
            calm_count += 1
        elif emotion in stress_emotions:
            stress_count += 1

    # Most recent emotion (tie-breaker)
    recent_emotion = rows[0]["dominant_emotion"].lower().strip() if rows else None

    # Decide dominant state
    if calm_count > stress_count:
        dominant_state = "Calm State"
        reason = "Overall weekly pattern shows more calm dreams."
    elif stress_count > calm_count:
        dominant_state = "Stress State"
        reason = "Overall weekly pattern shows more stress-related dreams."
    else:
        # 🔥 Tie breaker using most recent dream
        if recent_emotion in calm_emotions:
            dominant_state = "Calm State"
            reason = (
                "Overall weekly emotions are balanced, "
                "but your most recent dream reflects calmness."
            )
        else:
            dominant_state = "Stress State"
            reason = (
                "Overall weekly emotions are balanced, "
                "but your most recent dream reflects stress."
            )

    insight = generate_insight(dominant_state)

    return {
        "state_distribution": {
            "Calm State": round((calm_count / max(calm_count + stress_count, 1)) * 100),
            "Stress State": round((stress_count / max(calm_count + stress_count, 1)) * 100)
        },
        "dominant_state": dominant_state,
        "ai_insight": {
            "reasoning": reason,
            "recommendations": insight["recommendations"]
        }
    }

