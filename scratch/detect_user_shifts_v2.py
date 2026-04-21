import os
import json
import glob
from collections import defaultdict
from datetime import datetime

CONT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions"

def load_all_user_histories():
    user_histories = defaultdict(list)
    files = glob.glob(os.path.join(CONT_DIR, "**", "*.json"), recursive=True)
    files = [f for f in files if not f.endswith(".bak")]
    
    for fpath in files:
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            
            continuum = data.get("continuum", "unknown")
            subcategory = data.get("subcategory", "unknown")
            article = os.path.basename(fpath).replace(".json", "")
            
            for rev in data.get("revisions", []):
                user = rev.get("user")
                if not user or user.lower() == "generic" or "bot" in user.lower():
                    continue
                
                timestamp_str = rev.get("timestamp")
                if not timestamp_str:
                    continue
                
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except:
                    continue
                
                user_histories[user].append({
                    "date": dt,
                    "year": dt.year,
                    "article": article,
                    "subcategory": subcategory
                })
        except:
            pass
            
    return user_histories

histories = load_all_user_histories()

# Find users who have edited in multiple subcategories
multi_cat_users = []
for user, history in histories.items():
    cats = set(h["subcategory"] for h in history)
    if len(cats) >= 2:
        multi_cat_users.append((user, len(history), cats))

# Sort by activity
multi_cat_users.sort(key=lambda x: x[1], reverse=True)

print(f"Top 10 users with multi-category contributions:")
for user, count, cats in multi_cat_users[:10]:
    print(f"\nUser: {user} ({count} edits)")
    
    # Breakdown by year and category
    year_map = defaultdict(lambda: defaultdict(int))
    for h in histories[user]:
        year_map[h["year"]][h["subcategory"]] += 1
        
    for yr in sorted(year_map.keys()):
        parts = []
        for cat, val in year_map[yr].items():
            parts.append(f"{cat}: {val}")
        print(f"  {yr}: {', '.join(parts)}")
    
    # Top articles
    art_map = defaultdict(int)
    for h in histories[user]:
        art_map[f"{h['subcategory']} | {h['article']}"] += 1
    sorted_arts = sorted(art_map.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Top Articles: {sorted_arts}")

