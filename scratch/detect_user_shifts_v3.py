import os
import json
import glob
from collections import defaultdict
from datetime import datetime
import re

CONT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions"

def parse_wikihow_ts(ts_str):
    # Format: "10:02, 26 February 2026"
    try:
        # Remove any extra spaces
        ts_str = ts_str.strip()
        # Use strptime
        return datetime.strptime(ts_str, "%H:%M, %d %B %Y")
    except:
        try:
             # ISO format fallback
             return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except:
             return None

def load_all_user_histories():
    user_histories = defaultdict(list)
    files = glob.glob(os.path.join(CONT_DIR, "**", "*.json"), recursive=True)
    files = [f for f in files if not f.endswith(".bak")]
    
    print(f"Loading {len(files)} files...")
    
    for fpath in files:
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            
            continuum = data.get("continuum", "unknown")
            subcategory = data.get("subcategory", "unknown")
            article = data.get("title", os.path.basename(fpath).replace(".json", ""))
            
            for rev in data.get("revisions", []):
                user = rev.get("user")
                if not user or user.lower() == "generic" or "bot" in user.lower():
                    continue
                
                dt = parse_wikihow_ts(rev.get("timestamp", ""))
                if not dt:
                    continue
                
                user_histories[user].append({
                    "date": dt,
                    "year": dt.year,
                    "article": article,
                    "continuum": continuum,
                    "subcategory": subcategory
                })
        except:
            pass
            
    return user_histories

histories = load_all_user_histories()

# Filter active human users
active_users = []
for user, history in histories.items():
    if len(history) < 30: continue
    cats = sorted(list(set(h["subcategory"] for h in history)))
    active_users.append((user, len(history), cats))

active_users.sort(key=lambda x: x[1], reverse=True)

print(f"\n--- Top 10 Active Users and their Shifts ---")
for user, count, cats in active_users[:15]:
    history = sorted(histories[user], key=lambda x: x["date"])
    years = sorted(list(set(h["year"] for h in history)))
    
    # Check for shift in subcategory
    yearly_cat = defaultdict(lambda: defaultdict(int))
    for h in history:
        yearly_cat[h["year"]][h["subcategory"]] += 1
        
    print(f"\nUser: {user} ({count} edits, {years[0]}-{years[-1]})")
    for yr in years:
        top_cat = max(yearly_cat[yr].items(), key=lambda x: x[1])[0]
        print(f"  {yr}: {top_cat} ({yearly_cat[yr][top_cat]} edits)")
        
    # Article shift evidence
    art_stats = defaultdict(int)
    for h in history:
        art_stats[f"[{h['subcategory']}] {h['article']}"] += 1
    top_arts = sorted(art_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Top Articles: {top_arts}")

