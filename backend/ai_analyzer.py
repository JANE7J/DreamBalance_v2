from transformers import pipeline
import re

# Load the pre-trained emotion-classification model from Hugging Face.
# This model will be downloaded automatically the first time this code is run.
# It's specifically fine-tuned to detect a range of emotions in text.
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

def analyze_dream_text(dream_text: str):
    """
    Analyzes the dream text using a pre-trained AI model to extract emotions,
    and then generates a title.
    """
    if not dream_text or not dream_text.strip():
        return {
            "auto_title": "A Quiet Rest",
            "emotions": [{"label": "neutral", "score": 1.0}],
            "dominant_emotion": "Neutral"
        }

    # --- AI Emotion Analysis ---
    # The model returns a list of dictionaries, one for each emotion.
    processed_emotions = emotion_classifier(dream_text)[0]
    
    # Sort emotions by score to find the dominant one
    sorted_emotions = sorted(processed_emotions, key=lambda x: x['score'], reverse=True)
    dominant_emotion = sorted_emotions[0]['label'].capitalize()

    # --- Auto-Title Generation (Rule-Based) ---
    # A simple but effective method to generate a title.
    # We'll find the first noun phrase in the dream.
    words = re.findall(r'\b\w+\b', dream_text)
    title_words = []
    for i, word in enumerate(words):
        # A simple heuristic: find an interesting start (verb, adj) followed by nouns.
        if len(title_words) == 0 and word.lower() not in ["i", "a", "the", "and", "it"]:
            title_words.append(word.capitalize())
        elif len(title_words) > 0:
            title_words.append(word)
        
        if len(title_words) >= 4:
            break
    
    auto_title = " ".join(title_words) if title_words else "A Vivid Dream"

    return {
        "auto_title": auto_title,
        "emotions": sorted_emotions,
        "dominant_emotion": dominant_emotion
    }
