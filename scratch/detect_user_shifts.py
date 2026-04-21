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
    
    print(f"Loading {len(files)} files...")
    
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
                
                # timestamps look like "2024-03-21T18:14:14Z" or similar
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                except:
                    continue
                
                user_histories[user].append({
                    "date": dt,
                    "year": dt.year,
                    "article": article,
                    "continuum": continuum,
                    "subcategory": subcategory
                })
        except Exception as e:
            # print(f"Error loading {fpath}: {e}")
            pass
            
    return user_histories

def analyze_shifts(user_histories):
    shifts = []
    
    for user, history in user_histories.items():
        if len(history) < 20: # skip low activity users
            continue
            
        history.sort(key=lambda x: x["date"])
        
        # Group by year
        years = sorted(list(set(h["year"] for h in history)))
        if len(years) < 3: # skip users with short tenure
            continue
            
        # Analyze first 3 years vs last 3 years
        early_records = [h for h in history if h["year"] <= years[0] + 2]
        late_records = [h for h in history if h["year"] >= years[-1] - 2]
        
        if not early_records or not late_records:
            continue
            
        early_cat = defaultdict(int)
        for h in early_records:
            early_cat[h["subcategory"]] += 1
            
        late_cat = defaultdict(int)
        for h in late_records:
            late_cat[h["subcategory"]] += 1
            
        # Find dominant category
        def get_top(cats):
            if not cats: return "none", 0
            sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)
            return sorted_cats[0]
            
        top_early, count_early = get_top(early_cat)
        top_late, count_late = get_top(late_cat)
        
        if top_early != top_late and count_early > 5 and count_late > 5:
            # Check if it's a "significant" shift
            # If the early cat is 90% and late is 10%, that's a shift.
            early_ratio = count_early / len(early_records)
            late_ratio = late_cat.get(top_early, 0) / len(late_records)
            
            if early_ratio > 0.6 and late_ratio < 0.2:
                shifts.append({
                    "user": user,
                    "early_period": (years[0], years[0]+2),
                    "late_period": (years[-1]-2, years[-1]),
                    "from": top_early,
                    "to": top_late,
                    "history": history
                })
                
    return shifts

histories = load_all_user_histories()
detected_shifts = analyze_shifts(histories)

print(f"Detected {len(detected_shifts)} users with significant shifts.")

# Display top candidates
for i, s in enumerate(detected_shifts[:5]):
    print(f"\nCandidate {i+1}: {s['user']}")
    print(f"Shift: {s['from']} -> {s['to']}")
    print(f"Timeline: {s['early_period'][0]} to {s['late_period'][1]}")
    
    # Table of top articles
    early_articles = defaultdict(int)
    for h in s['history']:
        if h['year'] <= s['early_period'][1]:
            early_articles[h['article']] += 1
            
    late_articles = defaultdict(int)
    for h in s['history']:
        if h['year'] >= s['late_period'][0]:
            late_articles[h['article']] += 1
            
    sorted_early = sorted(early_articles.items(), key=lambda x: x[1], reverse=True)[:3]
    sorted_late = sorted(late_articles.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print("Early Top Articles:", sorted_early)
    print("Late Top Articles:", sorted_late)

