
import json
import re
from collections import defaultdict

json_path = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic\health\Lose-Weight.json"

with open(json_path, 'r', encoding='utf-8') as f:
    revisions = json.load(f).get('revisions', [])

# --- HEURISTIC CLASSIFIERS ---

VANDALISM_PATTERNS = re.compile(
    r"vand|spam|test|gibberish|nonsense|profanity|offensive|blank|delete all|junk|troll|lol|haha|fuck|shit|ass|crap|idiot|stupid", 
    re.IGNORECASE
)

GATEKEEPING_PATTERNS = re.compile(
    r"RCP reverted|reverted edits by|undid revision|undo revision|rollback|rv ", 
    re.IGNORECASE
)

GENDER_NPOV_PATTERNS = re.compile(
    r"npov|sexist|gender|woman|women|female|feminism|sexism|bias|neutral|she|her\b|patriarchy|misogyn|pronouns|gendered", 
    re.IGNORECASE
)

SPAM_PROMO_PATTERNS = re.compile(
    r"http|www\.|\.com|\.net|\.org|buy|click|visit|promo|advertis|affiliate|sponsor", 
    re.IGNORECASE
)

EXPERT_BLOCK_PATTERNS = re.compile(
    r"expert|medical|doctor|physician|professional|credentials|cite|citation|source|reference|evidence|study|research|clinical", 
    re.IGNORECASE
)

STYLE_BLOCK_PATTERNS = re.compile(
    r"format|style|htoc|toc|template|wikihow style|typo|spelling|grammar|whitespace|capitali|punctuation|ce\b|copyedit", 
    re.IGNORECASE
)

IDENTITY_CONTENT = re.compile(
    r"woman|women|girl|female|mother|she |her |diet|weight loss|body|fat|slim|beauty|appearance|size|look", 
    re.IGNORECASE
)

results = defaultdict(list)

for r in revisions:
    summary = r.get('summary', '')
    added = ' '.join(r.get('exact_contribution', {}).get('added', []))
    removed = ' '.join(r.get('exact_contribution', {}).get('removed', []))
    combined_text = summary + ' ' + added + ' ' + removed

    ctype = r.get('contribution_type', '')
    status = r.get('status', '')

    # Only looking at non-genuine candidates
    if ctype != 'revert' and status != 'reverted':
        results['GENUINE'].append(r)
        continue

    # --- Sub-classify ---
    if VANDALISM_PATTERNS.search(summary) or VANDALISM_PATTERNS.search(added):
        results['VANDALISM'].append(r)
    elif SPAM_PROMO_PATTERNS.search(added):
        results['SPAM_PROMOTIONAL'].append(r)
    elif GENDER_NPOV_PATTERNS.search(summary) and GATEKEEPING_PATTERNS.search(summary):
        results['GENDER_GATEKEEPING'].append(r)
    elif GENDER_NPOV_PATTERNS.search(summary) or (IDENTITY_CONTENT.search(removed) and GATEKEEPING_PATTERNS.search(summary)):
        results['GENDER_ADJACENT_REVERT'].append(r)
    elif EXPERT_BLOCK_PATTERNS.search(summary) and GATEKEEPING_PATTERNS.search(summary):
        results['EXPERT_AUTHORITY_BLOCK'].append(r)
    elif STYLE_BLOCK_PATTERNS.search(summary) and GATEKEEPING_PATTERNS.search(summary):
        results['STYLE_MAINTENANCE_BLOCK'].append(r)
    elif GATEKEEPING_PATTERNS.search(summary):
        results['GENERAL_RCP_ROLLBACK'].append(r)
    elif status == 'reverted' and ctype in ('addition', 'major_addition', 'sourcing'):
        results['REJECTED_GENUINE_CONTRIBUTION'].append(r)
    else:
        results['OTHER_NON_GENUINE'].append(r)

total = len(revisions)
print(f"\n{'='*55}")
print(f"  NON-GENUINE CLASSIFICATION REPORT")
print(f"  Total Revisions: {total}")
print(f"{'='*55}\n")

category_order = [
    'GENUINE',
    'VANDALISM',
    'SPAM_PROMOTIONAL',
    'GENDER_GATEKEEPING',
    'GENDER_ADJACENT_REVERT',
    'EXPERT_AUTHORITY_BLOCK',
    'STYLE_MAINTENANCE_BLOCK',
    'GENERAL_RCP_ROLLBACK',
    'REJECTED_GENUINE_CONTRIBUTION',
    'OTHER_NON_GENUINE',
]

for cat in category_order:
    items = results.get(cat, [])
    pct = len(items) / total * 100
    flag = "[OK]  " if cat == 'GENUINE' else "[!!!] " if 'GENDER' in cat else "[x]   "
    print(f"{flag} {cat:<35}: {len(items):4} ({pct:5.1f}%)")
    if items and cat not in ('GENUINE', 'OTHER_NON_GENUINE', 'REJECTED_GENUINE_CONTRIBUTION'):
        example = items[0].get('summary', '')[:80]
        print(f"     +-- Example: \"{example}\"")

print(f"\n{'='*55}")
ungrouped = sum(len(v) for v in results.values())
print(f"  Total accounted for: {ungrouped}")
