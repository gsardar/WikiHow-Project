import os
import json
import csv
from datetime import datetime

# Path Configuration
CONTRIBUTORS_PATH = r"f:\Users\Admin\Documents\WikiHow Project\data\contributors_final.csv"
DOMESTIC_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic"
OUTPUT_PATH = r"f:\Users\Admin\Documents\WikiHow Project\research_taxonomy\continuum_yearly_taxonomy.csv"

# Load Gender Map
gender_map = {}
with open(CONTRIBUTORS_PATH, encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        gender_map[row['username'].lower()] = row['gender']

def parse_year(ts):
    if not ts: return None
    ts = ts.strip()
    try: return datetime.strptime(ts, "%H:%M, %d %B %Y").year
    except:
        try: return int(ts[:4]) if ts[0].isdigit() else int(ts.split()[-1])
        except: return None

# Actual Data from Domestic
# { (sub, year): {gender: {edits: 0, words: 0}} }
actuals = {}

for sub in os.listdir(DOMESTIC_DIR):
    sub_path = os.path.join(DOMESTIC_DIR, sub)
    if os.path.isdir(sub_path):
        for fname in os.listdir(sub_path):
            if fname.endswith('.json'):
                try:
                    with open(os.path.join(sub_path, fname), encoding='utf-8') as jf:
                        data = json.load(jf)
                        for rev in data.get('revisions', []):
                            yr = parse_year(rev.get('timestamp'))
                            if not yr or yr < 2005 or yr > 2026: continue
                            
                            user = (rev.get('user') or "").lower()
                            gender = gender_map.get(user, 'unknown')
                            if gender == 'unknown': continue
                            
                            key = (sub, yr)
                            if key not in actuals:
                                actuals[key] = {g: {'edits': 0, 'words': 0} for g in ['male', 'female', 'non-binary']}
                            
                            actuals[key][gender]['edits'] += 1
                            added = rev.get('exact_contribution', {}).get('added', [])
                            words = sum(len(str(p)) for p in added) // 5
                            actuals[key][gender]['words'] += words
                except: pass

# Write Header
header = ["Continuum", "Rank", "Sub-Continuum", "Year", "Male_Edits", "Female_Edits", "NB_Edits", "Male_Words", "Female_Words", "NB_Words"]

with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    # Process Domestic Actuals
    # We output every year for every sub
    
    # Define the taxonomy for the script to iterate
    tax = [
        ("Domestic", 0, "Baby Care", "baby_care"),
        ("Domestic", 1, "Towel Origami", "towel_origami"),
        ("Domestic", 2, "Baking", "baking"),
        ("Domestic", 3, "Laundry", "laundry"),
        ("Domestic", 4, "Housekeeping", "housekeeping"),
        ("Domestic", 5, "Gardening", "gardening"),
        ("Domestic", 6, "Home-and-Garden", "home_and_garden"),
        ("Domestic", 7, "Washing/Dryers", "washing_machines"),
        ("Domestic", 8, "Plumbing", "plumbing"),
        ("Domestic", 9, "Electrical Wiring", "electrical_wiring"),
        ("Occupational", 0, "Nursing", "nursing"),
        ("Occupational", 9, "Software Engineering", "software_engineering"),
        ("Entertainment", 0, "Knitting", "knitting"),
        ("Entertainment", 3, "Hobbies & Crafts", "hobbies_crafts"),
        ("Entertainment", 9, "PC Gaming", "pc_gaming"),
        ("Policy", 0, "Maternal Health", "maternal_health"),
        ("Policy", 9, "Military", "military")
        # Adding a representative set of high-interest categories
    ]
    # For speed and output, I will generate a robust sample of years
    years = range(2005, 2027)
    
    for c_name, rank, sub_disp, sub_key in tax:
        for yr in years:
            data = actuals.get((sub_key, yr), {g: {'edits':0,'words':0} for g in ['male','female','non-binary']})
            writer.writerow([
                c_name, rank, sub_disp, yr,
                data['male']['edits'], data['female']['edits'], data['non-binary']['edits'],
                data['male']['words'], data['female']['words'], data['non-binary']['words']
            ])

print(f"Generated yearly taxonomy at {OUTPUT_PATH}")
