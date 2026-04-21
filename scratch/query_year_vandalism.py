
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

json_path = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic\health\Lose-Weight.json"

with open(json_path, 'r', encoding='utf-8') as f:
    revisions = json.load(f).get('revisions', [])

VANDALISM_PAT = re.compile(
    r"vand|spam|test|gibberish|profanity|offensive|troll|fuck|shit|crap|lol|haha|idiot|stupid|blank|delete all|junk",
    re.IGNORECASE
)

def parse_year(ts):
    m = re.search(r"\b(20\d{2})\b", ts)
    return int(m.group(1)) if m else None

target_years = {2014, 2015}

print("=== VANDALISM EVENTS — 2014 & 2015 ===\n")

for r in revisions:
    year = parse_year(r.get('timestamp', ''))
    if year not in target_years:
        continue

    summary = r.get('summary', '')
    added   = r.get('exact_contribution', {}).get('added', [])
    removed = r.get('exact_contribution', {}).get('removed', [])
    all_text = ' '.join(added + removed)

    is_vandalism = VANDALISM_PAT.search(summary) or VANDALISM_PAT.search(all_text)
    if not is_vandalism:
        continue

    print(f"--- [{year}] Revision {r.get('id')} ---")
    print(f"  User      : {r.get('user')}  (anon={r.get('anon')})")
    print(f"  Timestamp : {r.get('timestamp')}")
    print(f"  Status    : {r.get('status')} | Type: {r.get('contribution_type')}")
    print(f"  Summary   : {summary[:100]}")
    if added:
        print(f"  ADDED     : {added[0][:250]}")
    if removed:
        print(f"  REMOVED   : {removed[0][:250]}")
    print()
