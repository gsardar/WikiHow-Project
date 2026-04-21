
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

json_path = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic\health\Lose-Weight.json"

with open(json_path, 'r', encoding='utf-8') as f:
    revisions = json.load(f).get('revisions', [])

# Explicit/genital content patterns (research/content moderation context)
EXPLICIT_PATTERNS = re.compile(
    r"\bpenis\b|\bvagina\b|\bdick\b|\bcock\b|\bpussy\b|\bboob|\bbreast|\bnipple|\banus\b|\bass\b|\bballs\b|\btesticle|\bgenitals?\b|\bsexual organ|\bnaked\b|\bnude\b|\bporn|\bxxx\b|\bsex tape|\berecti|\borgasm",
    re.IGNORECASE
)

results = []
for r in revisions:
    added   = r.get('exact_contribution', {}).get('added', [])
    removed = r.get('exact_contribution', {}).get('removed', [])
    
    for line in added:
        m = EXPLICIT_PATTERNS.search(line)
        if m:
            results.append({'direction': 'ADDED', 'match': m.group(0), 'rev': r, 'content': line[:300]})
    for line in removed:
        m = EXPLICIT_PATTERNS.search(line)
        if m:
            results.append({'direction': 'REMOVED', 'match': m.group(0), 'rev': r, 'content': line[:300]})

print(f"=== EXPLICIT/GENITAL CONTENT SCAN ===")
print(f"Total flagged instances: {len(results)}\n")

if not results:
    print("None found.")
else:
    for i, item in enumerate(results, 1):
        r = item['rev']
        tag = "[ADDED by editor]" if item['direction'] == 'ADDED' else "[REMOVED by revert]"
        print(f"--- #{i} {tag} ---")
        print(f"  ID        : {r.get('id')}")
        print(f"  User      : {r.get('user')}")
        print(f"  Timestamp : {r.get('timestamp')}")
        print(f"  Status    : {r.get('status')}")
        print(f"  Summary   : {r.get('summary', '')[:80]}")
        print(f"  MATCHED   : \"{item['match']}\"")
        print(f"  CONTENT   : {item['content']}")
        print()
