import sys
import os
import time
import argparse
sys.path.append(os.getcwd())
from wikihow.api import get_users, get_screenshot, switch_to_tab, _get_driver
from wikihow.llm_engine import infer_gender

def test_unified_flow(no_tor=False):
    username = "AdrianaBaird" # Our test case
    print(f"DEBUG: Starting Unified Multi-Modal Test for {username}...")
    print(f"DEBUG: Tor Enabled: {not no_tor}")
    
    # 1. Initialize Driver
    _get_driver(no_tor=no_tor)
    
    # 2. Scrape Profile
    print(f"DEBUG: Navigating to wikiHow Profile: {username}...")
    results = get_users([username])
    user_info = results[0]
    
    # 3. Capture Screenshot
    screenshot_path = f"data/screenshots/{username}_multimodal.png"
    get_screenshot(screenshot_path)
    print(f"DEBUG: Screenshot captured: {screenshot_path}")
    
    # 4. Trigger Multi-Modal Inference
    print("DEBUG: Switching to DeepSeek tab and uploading screenshot...")
    gen_res = infer_gender(
        username=username,
        real_name=user_info["real_name"],
        location=user_info["location"],
        genderize_guess=user_info["gender"],
        genderize_confidence=user_info["gender_confidence"],
        image_ai_guess=user_info["image_ai_guess"],
        image_path=screenshot_path
    )
    
    print("-" * 50)
    print(f"FINAL RESULT FOR {username}:")
    print(f"Status: {gen_res.get('status')}")
    print(f"Source: {gen_res.get('source')}")
    print(f"Evidence: {gen_res.get('how_predicted')}")
    print("-" * 50)
    
    print("DEBUG: Test complete. Browser is staying open for your inspection.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tor", action="store_true", help="Disable Tor proxy for this run")
    args = parser.parse_args()
    test_unified_flow(no_tor=args.no_tor)
