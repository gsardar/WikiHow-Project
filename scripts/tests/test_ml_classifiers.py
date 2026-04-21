# -*- coding: utf-8 -*-
"""
test_ml_classifiers.py
======================
This script tests the proposed ML architectures (RoBERTa for Toxicity and
BART for Zero-Shot Tone Classification) against real-world examples of
WikiHow vandalism and tone-policing.

Note: This requires `transformers`, `torch`, and `detoxify` to run locally.
"""

import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def test_classifiers():
    print("Loading ML Classifiers... (This may take a moment to download weights)")
    
    try:
        from detoxify import Detoxify
        from transformers import pipeline
    except ImportError:
        print("\n[ERROR] Missing required libraries. Please run:")
        print("pip install detoxify transformers torch")
        return

    # Load Models
    try:
        # 1. Detoxify (RoBERTa trained on Jigsaw)
        toxicity_model = Detoxify('original')
        
        # 2. Zero-Shot Classifier (BART Large MNLI)
        # Using a smaller model here for faster local testing (distilbart or similar if needed)
        # but facebook/bart-large-mnli is the standard for accuracy. 
        # For speed in testing, we use 'valhalla/distilbart-mnli-12-3'
        print("Models downloading/loading...")
        tone_classifier = pipeline(
            "zero-shot-classification",
            model="valhalla/distilbart-mnli-12-3",
            device=-1 # CPU
        )
    except Exception as e:
        print(f"\n[ERROR] Failed to load models: {e}")
        return

    # ── Test Scenarios ────────────────────────────────────────────────────────

    test_examples = [
        # Image 1 (Gross Troll/Vandalism)
        "Poop all over your face. You might say, \"What? That's impossible. How could i ever curve my body around to poop on my face?\" To you I say, I have no idea. Stretch a little I guess. Once you have the feces covering your face (and yes I do mean the inside of your mouth too) urinate into a cup and place it on the counter next to your beauty supplies (you'll need this to clean the feces off later). After letting the human waste sit on your face for about 15 minutes, rinse it thoroughly with the urine from earlier.",
        
        # Image 2 (Tone Policing / Unsolicited Advice)
        "BIG SMILE! smiling will help you look so much prettier but make sure you've brushed your teeth!",
        
        # Image 3 (Subtle Sabotage)
        "Wash your face with a harsh acid",
        
        # 4. Normal, helpful edit comment (Control)
        "Corrected a minor spelling mistake in step 3."
    ]

    TONE_LABELS = [
        "objective instruction", 
        "unsolicited advice", 
        "body shaming", 
        "patronizing or condescending",
        "encouraging natural beauty"
    ]

    print("\n" + "="*80)
    print("ML CLASSIFIER TEST RESULTS")
    print("="*80)

    for i, text in enumerate(test_examples, 1):
        print(f"\n[{i}] TEXT: \"{text}\"")
        
        # Run Toxicity
        tox_results = toxicity_model.predict(text)
        # Format toxic results > 10%
        tox_flags = {k: f"{v*100:.1f}%" for k, v in tox_results.items() if v > 0.10}
        
        # Run Tone Zero-Shot
        tone_results = tone_classifier(text, TONE_LABELS, multi_label=True)
        # Format tone results > 40% confidence
        tone_flags = {label: f"{score*100:.1f}%" 
                      for label, score in zip(tone_results['labels'], tone_results['scores']) 
                      if score > 0.40}

        print("  -- Toxicity (RoBERTa):", tox_flags if tox_flags else "Clean (<10%)")
        print("  -- Tone (Zero-Shot)  :", tone_flags if tone_flags else "No dominant tone")

if __name__ == "__main__":
    test_classifiers()
