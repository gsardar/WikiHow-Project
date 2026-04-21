import csv
import os
import sys

def compare_csvs(old_path, new_path):
    if not os.path.exists(old_path) or not os.path.exists(new_path):
        print(f"Error: One or both files not found. ({old_path}, {new_path})")
        return

    old_data = {}
    with open(old_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_data[row["username"]] = row

    new_data = {}
    with open(new_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            new_data[row["username"]] = row

    # Comparison metrics
    total = len(new_data)
    old_unknown = sum(1 for r in old_data.values() if r.get("gender") == "unknown")
    new_unknown = sum(1 for r in new_data.values() if r.get("gender") == "unknown")
    
    conversions = []
    for username, new_row in new_data.items():
        old_row = old_data.get(username, {})
        if old_row.get("gender") == "unknown" and new_row.get("gender") != "unknown":
            conversions.append({
                "username": username,
                "old": "unknown",
                "new": new_row["gender"],
                "confidence": new_row.get("gender_confidence", 0)
            })

    # Output Report
    print("\n" + "="*40)
    print(" GENDER OVERHAUL COMPARISON REPORT ")
    print("="*40)
    print(f"Total contributors processed: {total}")
    print(f"Old 'unknown' count:        {old_unknown}")
    print(f"New 'unknown' count:        {new_unknown}")
    print(f"Users identified:           {len(conversions)}")
    print(f"Conversion Rate:           {(len(conversions)/old_unknown)*100:.1f}%" if old_unknown > 0 else "0%")
    print("="*40)
    
    if conversions:
        print("\nTOP CONVERSIONS (First 10):")
        print(f"{'Username':<25} | {'Old':<10} | {'New':<10} | {'Conf':<6}")
        print("-" * 60)
        for c in conversions[:10]:
            print(f"{c['username']:<25} | {c['old']:<10} | {c['new']:<10} | {c['confidence']:<6}")
    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    OLD_CSV = "data/contributors_final.csv"
    NEW_CSV = "data/contributors_overhauled.csv"
    compare_csvs(OLD_CSV, NEW_CSV)
