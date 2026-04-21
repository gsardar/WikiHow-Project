
import json
import os
import csv

MANIFEST_PATH = "data/extraction_manifest.json"
MASTER_CSV = "data/DataVersions/v1/backup1/discovery/domestic/cleaned_domestic_master.csv"

def check_progress():
    print("====================================================")
    print("   WIKIHOW EXTRACTION PROGRESS DASHBOARD")
    print("====================================================")
    
    # 1. Load Manifest
    if not os.path.exists(MANIFEST_PATH):
        print("Manifest not found. Start extraction first.")
        return
        
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error reading manifest: {e}")
        return
    
    completed_count = len(manifest.get("completed", {}))
    failed_count = len(manifest.get("failed", {}))
    
    # 2. Load Master List
    total_articles = 0
    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_articles = sum(1 for row in reader)
    
    # 3. Calculate Stats
    progress_pct = (completed_count / total_articles * 100) if total_articles > 0 else 0
    
    print(f"Total Master List: {total_articles} articles")
    print(f"Successfully Saved: {completed_count}")
    print(f"Failed/Retriable:  {failed_count}")
    print(f"Total Progress:    [{'#' * int(progress_pct/5)}{'.' * (20 - int(progress_pct/5))}] {progress_pct:.1f}%")
    print("-" * 52)
    
    # Show last 5 completed
    print("\nRecently Completed:")
    recent = list(manifest.get("completed", {}).items())[-5:]
    for path, info in reversed(recent):
        print(f" [+] {path.split('/')[-1]} ({info.get('completed_at', '').split('T')[1].split('.')[0]})")

if __name__ == "__main__":
    check_progress()
