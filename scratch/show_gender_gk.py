
import json
import re

json_path = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic\health\Lose-Weight.json"

with open(json_path, 'r', encoding='utf-8') as f:
    revisions = json.load(f).get('revisions', [])

GATEKEEPING_PATTERNS = re.compile(
    r"RCP reverted|reverted edits by|undid revision|undo revision|rollback|rv ", re.IGNORECASE
)
GENDER_NPOV_PATTERNS = re.compile(
    r"npov|sexist|gender|woman|women|female|feminism|sexism|bias|neutral|she|her\b|patriarchy|misogyn|pronouns|gendered", re.IGNORECASE
)

cases = [r for r in revisions if GENDER_NPOV_PATTERNS.search(r.get('summary', '')) and GATEKEEPING_PATTERNS.search(r.get('summary', ''))]

print(f"=== CONFIRMED GENDER GATEKEEPING EVENTS ({len(cases)}) ===\n")
for i, r in enumerate(cases, 1):
    added   = r.get('exact_contribution', {}).get('added', [])
    removed = r.get('exact_contribution', {}).get('removed', [])
    print(f"--- CASE {i} ---")
    print(f"  Revision ID  : {r.get('id')}")
    print(f"  Timestamp    : {r.get('timestamp')}")
    print(f"  Actor        : {r.get('user')}  (is_expert={r.get('is_expert')})")
    print(f"  Is Minor     : {r.get('is_minor')}")
    print(f"  Byte Change  : {r.get('change')}")
    print(f"  Summary      : {r.get('summary')}")
    print(f"  Status       : {r.get('status')} | Type: {r.get('contribution_type')}")
    if added:
        print(f"  ADDED        : {added[0][:200]}")
    if removed:
        print(f"  REMOVED      : {removed[0][:200]}")
    print()
