import os
import json
import csv
from datetime import datetime

# Path Configuration
CONTRIBUTORS_PATH = r"f:\Users\Admin\Documents\WikiHow Project\data\contributors_final.csv"
DOMESTIC_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic"

# Load Gender Map
gender_map = {}
with open(CONTRIBUTORS_PATH, encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        gender_map[row['username'].lower()] = row['gender']

def parse_year(ts):
    if not ts: return None
    ts = ts.strip()
    # Format: "10:02, 26 February 2026"
    try:
        return datetime.strptime(ts, "%H:%M, %d %B %Y").year
    except:
        # Fallback for ISO or other formats
        try:
            return int(ts[:4]) if ts[0].isdigit() else int(ts.split()[-1])
        except:
            return None

yearly_data = {} # {year: {gender: count}}

# Process Revisions
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
                            
                            if yr not in yearly_data:
                                yearly_data[yr] = {'male': 0, 'female': 0, 'non-binary': 0}
                            yearly_data[yr][gender] += 1
                except:
                    pass

# Output CSV for Analysis
print("Year,Male_Edits,Female_Edits,NB_Edits,Total_Verified")
for yr in sorted(yearly_data.keys()):
    d = yearly_data[yr]
    total = sum(d.values())
    print(f"{yr},{d['male']},{d['female']},{d['non-binary']},{total}")
