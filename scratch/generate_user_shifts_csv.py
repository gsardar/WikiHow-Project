import os
import json
import glob
import pandas as pd
from collections import defaultdict
from datetime import datetime

CONT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions"
OUTPUT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\research_taxonomy"

def parse_wikihow_ts(ts_str):
    try:
        ts_str = ts_str.strip()
        return datetime.strptime(ts_str, "%H:%M, %d %B %Y")
    except:
        try:
             return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except:
             return None

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

def generate_shift_csv():
    histories = load_all_user_histories()
    
    # Filter active human users with at least 15 edits
    active_users = []
    for user, history in histories.items():
        if len(history) < 15: continue
        active_users.append((user, len(history), history))
        
    rows = []
    
    for user, count, history in active_users:
        history = sorted(history, key=lambda x: x["date"])
        years = sorted(list(set(h["year"] for h in history)))
        year_range = f"{years[0]} - {years[-1]}"
        
        yearly_cat = defaultdict(lambda: defaultdict(int))
        for h in history:
            yearly_cat[h["year"]][h["continuum"] + "::" + h["subcategory"]] += 1
            
        # Compile yearwise distribution
        distribution_str = []
        for yr in years:
            top_cat = max(yearly_cat[yr].items(), key=lambda x: x[1])[0]
            distribution_str.append(f"{yr}: {top_cat} ({yearly_cat[yr][top_cat]} edits)")
            
        # Compile overall top articles
        art_stats = defaultdict(int)
        for h in history:
            art_stats[h['article']] += 1
        top_arts = sorted(art_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        top_arts_str = ", ".join([f"{a} ({c})" for a, c in top_arts])
        
        # Check if there is a shift (multiple different top categories over years)
        top_cats_over_years = [max(yearly_cat[yr].items(), key=lambda x: x[1])[0] for yr in years]
        has_shift = len(set(top_cats_over_years)) > 1
        
        rows.append({
            "Username": user,
            "Total_Edits": count,
            "Year_Range": year_range,
            "Has_Topical_Shift": has_shift,
            "Yearwise_Distribution": " | ".join(distribution_str),
            "Top_Articles": top_arts_str
        })
        
    df = pd.DataFrame(rows)
    # Sort by total edits
    df = df.sort_values(by="Total_Edits", ascending=False)
    
    out_path = os.path.join(OUTPUT_DIR, "user_shifts_distribution.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    generate_shift_csv()
