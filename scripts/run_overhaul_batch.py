import os
import csv
import sys
import time
import logging

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

from wikihow.api import _get_driver, get_screenshot
from wikihow.llm_engine import infer_gender

# Configuration
INPUT_CSV = "data/contributors_final.csv"
OUTPUT_CSV = "data/contributors_overhauled.csv"
SCREENSHOT_DIR = "data/temp_screenshots"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_batch(limit=None):
    if not os.path.exists(INPUT_CSV):
        logger.error(f"Input file {INPUT_CSV} not found!")
        return

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # Read existing data
    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Filter for unknowns
    targets = [r for r in rows if r.get("gender") == "unknown" or float(r.get("gender_confidence", 0)) < 0.9]
    logger.info(f"Found {len(targets)} targets for overhaul.")

    if limit:
        targets = targets[:limit]
        logger.info(f"Limiting to first {limit} targets.")

    # Process
    try:
        BRIDGE_URL = "http://127.0.0.1:8002"
        import requests
        
        for i, row in enumerate(targets):
            username = row["username"]
            profile_url = f"https://www.wikihow.com/User:{username.replace(' ', '-')}"
            logger.info(f"[{i+1}/{len(targets)}] Processing {username}...")
            
            try:
                # 1. Visit Profile via Bridge
                requests.post(f"{BRIDGE_URL}/navigate", json={"url": profile_url})
                time.sleep(3)
                
                # 2. Capture Full Screenshot via Bridge
                shot_path = os.path.abspath(os.path.join(SCREENSHOT_DIR, f"{username.replace(' ', '_')}.png"))
                requests.post(f"{BRIDGE_URL}/screenshot", json={"path": shot_path})
                
                # 3. Perform Multi-modal Inference via Bridge
                gen_res = infer_gender(
                    username=username,
                    real_name=row.get("real_name", ""),
                    location=row.get("location", ""),
                    image_path=shot_path
                )
                
                # 4. Update Row
                if gen_res and gen_res.get("status") in ("female", "male", "non-binary"):
                    row["gender"] = gen_res["status"]
                    row["gender_confidence"] = gen_res.get("confidence", 0.0)
                    row["gender_source"] = "DeepSeek-Multimodal"
                    logger.info(f"  Result: {gen_res['status']} ({gen_res.get('confidence')})")
                else:
                    logger.warning(f"  DeepSeek could not determine gender for {username}.")

            except Exception as e:
                logger.error(f"  Error processing {username}: {e}")
            
            # Save progress incrementally
            save_progress(rows, fieldnames)

    except KeyboardInterrupt:
        logger.info("Interrupted by user (SIGINT). Progress saved.")
    except Exception as e:
        import traceback
        logger.error(f"CRITICAL ERROR in batch runner: {e}")
        traceback.print_exc()
    finally:
        save_progress(rows, fieldnames)
        logger.info(f"Batch complete. Results saved to {OUTPUT_CSV}")

def save_progress(rows, fieldnames):
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of users to process")
    args = parser.parse_args()
    
    run_batch(limit=args.limit)
