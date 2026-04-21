"""
WikiHow Diachronic Gender Study — Module 4: ML Toxicity & Tone Scanner
Runs Transformer-based Machine Learning models over reverted edits to classify
vandalism, sexism, body-shaming, and patronizing tone policing.

Note for Colab: Run `!pip install transformers detoxify pandas torch` before executing.
"""

import pandas as pd
import time
from transformers import pipeline
from detoxify import Detoxify

# ── 1. Configuration & Setup ──────────────────────────────────────────────────
DRIVE_BASE = "/content/drive/MyDrive/wikiHow_Diachronic"
REVISIONS_CSV = f"{DRIVE_BASE}/revisions.csv"
ML_OUTPUT_CSV = f"{DRIVE_BASE}/vandalism_ml_analysis.csv"

# Define the labels for our Zero-Shot Tone Classifier
TONE_LABELS = [
    "unsolicited lifestyle advice",
    "patronizing and condescending",
    "body shaming or appearance critique",
    "objective instruction",
    "spam or nonsense"
]

print("Loading Machine Learning Models (This may take a minute...)")
# Load Model 1: Detoxify (RoBERTa) for Hate Speech & Sexism
# Trained on the massive Google Jigsaw dataset
tox_model = Detoxify('original')

# Load Model 2: Zero-Shot Classifier (BART-Large-MNLI) for Tone Policing
# Understands semantic context without needing explicit training on our exact words
tone_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0) 
# Note: device=0 uses the Colab GPU. Change to device=-1 if running on a standard CPU.

print("Models loaded successfully!\n")

# ── 2. Classification Functions ───────────────────────────────────────────────

def analyze_toxicity(text):
    """Uses Detoxify to check for explicit toxicity and identity attacks (sexism)."""
    if not isinstance(text, str) or not text.strip():
        return {"is_toxic": False, "is_identity_attack": False}
    
    results = tox_model.predict(text)
    
    # We set a confidence threshold of 0.6 (60%)
    return {
        "is_toxic": bool(results['toxicity'] > 0.6),
        "is_identity_attack": bool(results['identity_attack'] > 0.6), # Captures sexism/slurs
        "toxicity_score": round(float(results['toxicity']), 3)
    }

def analyze_tone(text):
    """Uses BART Zero-Shot to classify the nuanced tone of the edit."""
    if not isinstance(text, str) or not text.strip():
        return "unknown"
    
    # We ask the model: "Which of these labels best describes this text?"
    result = tone_model(text, TONE_LABELS)
    
    # Get the highest scoring label
    top_label = result['labels'][0]
    top_score = result['scores'][0]
    
    # Only assign the label if the model is relatively confident (> 40%)
    if top_score > 0.40:
        return top_label
    else:
        return "objective instruction" # Default fallback


# ── 3. Execution on the Dataset ───────────────────────────────────────────────

def run_ml_scanner():
    print(f"Reading {REVISIONS_CSV}...")
    try:
        df = pd.read_csv(REVISIONS_CSV)
    except FileNotFoundError:
        print("Error: revisions.csv not found. Please run Module 1 first.")
        return

    # Filter: We only want to spend ML compute time on edits that were REVERTED
    # (Checking if the comment contains 'revert', 'undo', 'vandalism', etc.)
    revert_mask = df['comment'].str.contains(r'(?i)\b(revert|undo|undid|rvv|vandalism)\b', na=False)
    reverted_edits = df[revert_mask].copy()
    
    print(f"Found {len(reverted_edits)} reverted edits to analyze.")
    
    if len(reverted_edits) == 0:
        print("No reverted edits found. Exiting.")
        return

    results_list = []
    
    print("Starting ML classification loop...")
    start_time = time.time()
    
    for index, row in reverted_edits.iterrows():
        # In a full pipeline, we would fetch the 'diff' text from the MediaWiki API here.
        # For this module, we will analyze the comment metadata as a proxy if diff is missing.
        text_to_analyze = str(row.get('comment', ''))
        
        # 1. Run Toxicity Model
        tox_results = analyze_toxicity(text_to_analyze)
        
        # 2. Run Tone Policing Model
        tone_result = analyze_tone(text_to_analyze)
        
        # 3. Categorize into your Research Buckets
        final_category = "Generic/Nonsense"
        if tox_results['is_identity_attack']:
            final_category = "Sexist / Identity Slur"
        elif tone_result == "body shaming or appearance critique":
            final_category = "Body-Shaming"
        elif tone_result in ["unsolicited lifestyle advice", "patronizing and condescending"]:
            final_category = "Moralizing / Tone Policing"
        elif tone_result == "objective instruction" and not tox_results['is_toxic']:
            final_category = "Ideological Gatekeeping" # A revert of a normal, non-toxic instruction
            
        # Save the row data
        results_list.append({
            "revision_id": row['revision_id'],
            "article_title": row['article_title'],
            "continuum": row['continuum'],
            "category": row['category'],
            "analyzed_text": text_to_analyze,
            "is_toxic": tox_results['is_toxic'],
            "tone_label": tone_result,
            "final_classification": final_category
        })
        
        # Print a progress update every 50 rows
        if len(results_list) % 50 == 0:
            print(f"  Processed {len(results_list)} rows...")

    # Save results to a new CSV
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(ML_OUTPUT_CSV, index=False)
    
    elapsed = round(time.time() - start_time, 2)
    print(f"\nModule 4 Complete in {elapsed} seconds!")
    print(f"Saved highly-contextual ML classifications to: {ML_OUTPUT_CSV}")
    
    # Print a quick summary map
    print("\n--- Summary of Revert Types ---")
    print(results_df['final_classification'].value_counts())

if __name__ == "__main__":
    run_ml_scanner()