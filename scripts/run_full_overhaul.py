import sys
import os
import pandas as pd
import time
sys.path.append(os.getcwd())
from wikihow.api import get_users

def run_full_overhaul():
    # 1. Load Baseline (Old Predictions)
    baseline_file = 'data/contributors_final.csv'
    if not os.path.exists(baseline_file):
        print(f"Error: {baseline_file} not found.")
        return
    
    df_old = pd.read_csv(baseline_file)
    usernames = df_old['username'].tolist()
    
    print(f"Starting Full Overhaul Extraction for {len(usernames)} users...")
    print("Browser visibility: ENABLED (headless=False)")
    print("-" * 60)
    
    # 2. Process in batches to prevent memory leaks and save progress
    batch_size = 20
    results_all = []
    out_file = 'data/contributors_overhauled.csv'
    
    for i in range(0, len(usernames), batch_size):
        batch = usernames[i:i + batch_size]
        print(f"\nProcessing Batch {i//batch_size + 1}/{len(usernames)//batch_size + 1}...")
        
        batch_results = get_users(batch)
        results_all.extend(batch_results)
        
        # Periodic Save
        df_new = pd.DataFrame(results_all)
        df_new.to_csv(out_file, index=False)
        print(f"Progress Saved: {len(results_all)} / {len(usernames)} users completed.")
    
    print("-" * 60)
    print(f"OVERHAUL COMPLETE: Final results saved to {out_file}.")

if __name__ == "__main__":
    run_full_overhaul()
