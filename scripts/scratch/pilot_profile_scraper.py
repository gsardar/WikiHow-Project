import os
import csv
import json
import time
import logging
from seleniumbase import Driver

# --- CONFIG ---
WORKSPACE_DIR = r"f:\Users\Admin\Documents\WikiHow Project"
CSV_PATH = os.path.join(WORKSPACE_DIR, "data", "contributors_final.csv")
OUTPUT_JSON = os.path.join(WORKSPACE_DIR, "data", "pilot_research_data.json")
SCREENSHOT_DIR = os.path.join(WORKSPACE_DIR, "data", "screenshots", "pilot_research")
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "browser_session")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

def run_pilot_scrape(limit=50):
    logger.info(f"Starting pilot scrape of {limit} accounts...")
    
    # 1. Load Usernames
    users = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit: break
            users.append(row)
            
    # 2. Initialize Driver
    # We use uc=True to handle potential antibot and ensure we can see profiles clearly.
    driver = Driver(uc=True, headless=True, user_data_dir=USER_DATA_DIR)
    
    results = []
    
    try:
        for user in users:
            username = user["username"]
            url = user["profile_url"]
            logger.info(f"Processing: {username} -> {url}")
            
            try:
                driver.get(url)
                time.sleep(3) # Wait for renders
                
                # Capture Screenshot
                shot_name = f"{username.replace(' ', '_')}_profile.png"
                shot_path = os.path.join(SCREENSHOT_DIR, shot_name)
                driver.save_screenshot(shot_path)
                
                # Extract Text (Main areas for pattern research)
                # WikiHow user pages have bio in #bodyContent
                bio_text = driver.get_text("#bodyContent")
                header_text = driver.get_text(".user_info_card") if driver.find_elements(".user_info_card") else ""
                
                results.append({
                    "username": username,
                    "url": url,
                    "screenshot": shot_path,
                    "bio_snippet": bio_text[:1000], # First 1000 chars
                    "header": header_text,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logger.error(f"Failed to process {username}: {e}")
                
        # 3. Save results
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Scrape complete. Results saved to {OUTPUT_JSON}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_pilot_scrape(50)
