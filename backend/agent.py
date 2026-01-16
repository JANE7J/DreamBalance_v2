import sqlite3
import os

# ---------------- DB CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dreambalance.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- FETCH LAST 7 DAYS (ORDERED) ----------------
def fetch_last_week_entries(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dominant_emotion, entry_date
        FROM dream_journal
        WHERE user_id = ?
          AND entry_date >= date('now','-7 day')
        ORDER BY entry_date DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- ANALYZE CALM vs STRESS ----------------
def analyze_emotions(entries):
    calm_emotions = {"happy", "peaceful", "refreshed", "energized"}
    stress_emotions = {"sad", "anxious", "scared", "confused", "tired", "fear"}

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
            "dominant_state": "Calm State",
            "tie_breaker": "none"
        }

    calm_pct = round((calm_count / total) * 100)
    stress_pct = round((stress_count / total) * 100)

    # Normal weekly dominance
    if calm_pct > stress_pct:
        return {
            "calm_percentage": calm_pct,
            "stress_percentage": stress_pct,
            "dominant_state": "Calm State",
            "tie_breaker": "weekly"
        }

    if stress_pct > calm_pct:
        return {
            "calm_percentage": calm_pct,
            "stress_percentage": stress_pct,
            "dominant_state": "Stress State",
            "tie_breaker": "weekly"
        }

    # 🔥 TIE → USE MOST RECENT DREAM
    latest_emotion = entries[0]["dominant_emotion"].strip().lower()

    dominant_state = (
        "Calm State"
        if latest_emotion in calm_emotions
        else "Stress State"
    )

    return {
        "calm_percentage": calm_pct,
        "stress_percentage": stress_pct,
        "dominant_state": dominant_state,
        "tie_breaker": "recent"
    }


# ---------------- GENERATE AI INSIGHT ----------------
def generate_insight(dominant_state, tie_breaker):
    if dominant_state == "Stress State":
        reasoning = (
            "Overall, your dreams this week indicate elevated stress levels."
            if tie_breaker == "weekly"
            else "Your overall emotions were balanced this week, but your most recent dream reflects stress."
        )

        return {
            "reasoning": reasoning,
            "recommendations": [
                "Practice relaxation before sleep",
                "Reduce screen time at night",
                "Try breathing or meditation exercises"
            ]
        }

    reasoning = (
        "Overall, your dreams this week suggest a calm and balanced mental state."
        if tie_breaker == "weekly"
        else "Your overall emotions were balanced this week, but your most recent dream reflects calmness."
    )

    return {
        "reasoning": reasoning,
        "recommendations": [
            "Maintain your current sleep routine",
            "Continue positive daily habits",
            "Practice gratitude before sleep"
        ]
    }


# ---------------- MAIN AGENT RESPONSE ----------------
def generate_ai_agent_response(user_id):
    entries = fetch_last_week_entries(user_id)
    analysis = analyze_emotions(entries)

    insight = generate_insight(
        analysis["dominant_state"],
        analysis["tie_breaker"]
    )

    return {
        "state_distribution": {
            "Calm State": analysis["calm_percentage"],
            "Stress State": analysis["stress_percentage"]
        },
        "dominant_state": analysis["dominant_state"],
        "ai_insight": insight
    }
