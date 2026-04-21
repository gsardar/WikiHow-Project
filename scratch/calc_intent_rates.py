import os
import json
import glob
import re
import pandas as pd
from collections import defaultdict
from datetime import datetime

CONT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions"
OUTPUT_DIR = r"f:\Users\Admin\Documents\WikiHow Project\research_taxonomy"

def detect_tags(comment):
    comment = str(comment).lower()
    tags = []
    if re.search(r'\bvand\b|\bvandalism\b', comment): tags.append("VANDALISM")
    elif re.search(r'\bspam\b|\bpromo\b|\bpromotional\b', comment): tags.append("SPAM_PROMOTIONAL")
    elif re.search(r'\bsarcasm\b|\bjoke\b|\bnonsense\b', comment): tags.append("NON_GENUINE_SARCASM")
    
    # Gatekeeping & Maintenance
    if re.search(r'\brcp\b', comment): tags.append("RCP")
    if re.search(r'\bce\b|\bcopyedit\b', comment): tags.append("COPYEDIT")
    if re.search(r'\bnpov\b', comment): tags.append("NPOV")
    if re.search(r'\btoc\b|\bhtoc\b|\bformat\b', comment): tags.append("FORMAT_GATEKEEPING")
    
    return tags

def run_analysis():
    files = glob.glob(os.path.join(CONT_DIR, "**", "*.json"), recursive=True)
    files = [f for f in files if not f.endswith(".bak")]
    
    tag_stats = defaultdict(lambda: {"total": 0, "reverted": 0, "accepted": 0})
    
    for fpath in files:
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            
            revisions = data.get("revisions", [])
            for rev in revisions:
                comment = rev.get("comment", "")
                is_revert = bool(re.search(r'(revert|undo|rollback|undid|RCP)', comment, re.IGNORECASE))
                
                tags = detect_tags(comment)
                # If this edit *is* a revert of vandalism, the vandalism was rejected.
                # Since we don't have diff alignment here, we'll map the tags found in comments to proxy the intent.
                for t in tags:
                    tag_stats[t]["total"] += 1
                    # If an edit is marked with a tag but it's ALSO a revert, it means it's an administrative revert.
                    # This means the *original* edit was rejected.
                    if is_revert:
                        tag_stats[t]["reverted"] += 1
                    else:
                        tag_stats[t]["accepted"] += 1
                        
        except Exception as e:
            pass
            
    # Process Results
    rows = []
    for tag, stats in tag_stats.items():
        total = stats["total"]
        if total > 0:
            rej_rate = (stats["reverted"] / total) * 100
            acc_rate = (stats["accepted"] / total) * 100
            rows.append({
                "Contribution_Intent_Tag": tag,
                "Total_Count": total,
                "Accepted_Rate_%": round(acc_rate, 2),
                "Rejected_Rate_%": round(rej_rate, 2),
                "Accepted_Count": stats["accepted"],
                "Rejected_Count": stats["reverted"]
            })
            
    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, "contribution_intent_rates.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    run_analysis()
