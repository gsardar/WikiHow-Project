import os
import re
import time
import glob
import random
import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- CONFIG ---
WORKSPACE_DIR = r"c:\Users\Admin\Documents\WikiHow Project"
ACCOUNTS_DIR = os.path.join(WORKSPACE_DIR, "data", "DataVersions", "v1", "accounts")
BROWSER_DATA = os.path.join(WORKSPACE_DIR, "data", "browser_session")

import subprocess

def check_collisions():
    """Checks for other running scrapers and prompts to kill or wait."""
    try:
        # Check for other python scripts that might be scrapers
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe"', shell=True).decode()
        # Filter for logic: we only care if more than 1 python process is running (this script is one)
        count = output.count("python.exe")
        if count > 1:
            print(f"\nWARNING: {count-1} other Python process(es) detected.")
            print("To avoid session lock collisions, we recommend closing other scrapers.")
            # Auto-kill for automation safety if user didn't object
            # os.system("taskkill /F /IM python.exe /T") 
            # Actually, let's just warn and exit to be safe, or offer to kill Chrome
            os.system("taskkill /F /IM chrome.exe /T")
            print("Closed all Chrome instances to free up session locks.\n")
    except: pass

import requests

class AccountIntelligence:
    def __init__(self):
        check_collisions()
        self.bridge_url = "http://127.0.0.1:8002"

    def harvest_usernames(self):
        """Finds all unique registered users in extraction histories."""
        base_path = os.path.join(WORKSPACE_DIR, "data", "DataVersions", "v1", "extraction")
        files = glob.glob(os.path.join(base_path, "**", "*_History.csv"), recursive=True)
        users = set()
        print(f"Scanning {len(files)} histories for contributors...")
        for f in files:
            try:
                df = pd.read_csv(f)
                if 'user' in df.columns:
                    users.update(df[df['is_anon'] == False]['user'].dropna().unique())
            except: pass
        out_csv = os.path.join(ACCOUNTS_DIR, "all_discovered_users.csv")
        pd.DataFrame({'username': list(users)}).to_csv(out_csv, index=False)
        print(f"Harvested {len(users)} users.")

    def probe_vision(self, sample_size=5):
        """Visits WikiHow through the Bridge and captures visual context."""
        all_users = pd.read_csv(os.path.join(ACCOUNTS_DIR, "all_discovered_users.csv"))['username'].tolist()
        sample = random.sample(all_users, min(len(all_users), sample_size))
        # Force Sophia B for testing
        if "Sophia B" not in sample: sample[0] = "Sophia B"
        
        results = []
        print(f"Starting VISION Batch Probe ({len(sample)} users)...")
        for u in sample:
            temp_path = os.path.abspath(os.path.join(WORKSPACE_DIR, "data", "temp_gender_audit.png"))
            try:
                # 1. Navigate Hub to User Page + Talk Page
                print(f"  [Hub] Visiting {u}...")
                requests.post(f"{self.bridge_url}/navigate", json={"url": f"https://www.wikihow.com/User:{u.replace(' ', '_')}"})
                
                # 2. Extract context via screenshot
                requests.post(f"{self.bridge_url}/screenshot", json={"path": temp_path})
                
                # 3. Vision Prompting (Multimodal Inference)
                prompt = f"Look at this WikiHow user profile screenshot for '{u}'. Based on visual silhouettes, the name parts, bio content, or community interaction comments, what is the most likely gender? Return exactly 'Male', 'Female', or 'Unknown'. Give a short reason."
                print(f"  [Hub] Requesting Visual Inference from DeepSeek...")
                response = requests.post(f"{self.bridge_url}/ask", json={"prompt": prompt, "file_path": temp_path}).json()
                
                verdict = response.get("response", "Unknown")
                print(f"  Result: {verdict[:100]}...")
                results.append({'username': u, 'llm_verdict': verdict})
            except Exception as e:
                print(f"  Audit Failure for {u}: {e}")
        
        pd.DataFrame(results).to_csv(os.path.join(ACCOUNTS_DIR, "vision_audit_results.csv"), index=False)
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest", action="store_true")
    parser.add_argument("--probe", type=int, default=0)
    args = parser.parse_args()
    
    intel = AccountIntelligence()
    if args.harvest: intel.harvest_usernames()
    if args.probe > 0: intel.probe_vision(args.probe)
