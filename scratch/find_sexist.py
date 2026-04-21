
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

json_path = r"f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum\domestic\health\Lose-Weight.json"

with open(json_path, 'r', encoding='utf-8') as f:
    revisions = json.load(f).get('revisions', [])

# Patterns targeting sexist/gendered stereotypes in the CONTENT of edits (not just summaries)
SEXIST_PATTERNS = re.compile(
    r"women (should|must|need to|have to|are supposed to)|"
    r"men (are better|don.t need|don.t have)|"
    r"girls? (should|need to|must)|"
    r"ladies? (should|need to|try)|"
    r"for (women|girls|females?|ladies) (only|especially)|"
    r"as a woman|being a woman|"
    r"your (husband|boyfriend|man) will|"
    r"look (good|attractive|sexy) for (him|men|your man)|"
    r"bikini body|beach body|"
    r"men prefer|men like (thin|slim|skinny)|"
    r"no man wants|"
    r"lose weight (to|so you can) (attract|impress|please)|"
    r"get a man|find a husband|"
    r"fat girls?|ugly (fat|overweight)|"
    r"real women|"
    r"don.t eat like a (pig|cow|animal)|"
    r"women.s (bodies|figure|shape) (should|must|are supposed)",
    re.IGNORECASE
)

BODY_SHAMING = re.compile(
    r"you.re fat|you are fat|stop being fat|why are you fat|"
    r"fat (loser|pig|slob|ass)|"
    r"disgusting (fat|body|weight)|"
    r"nobody likes fat|"
    r"too fat to|"
    r"you should be (ashamed|embarrassed) of your (body|weight|size)|"
    r"lazy (fat|overweight)|"
    r"land(whale|whale)",
    re.IGNORECASE
)

results = []

for r in revisions:
    added = r.get('exact_contribution', {}).get('added', [])
    removed = r.get('exact_contribution', {}).get('removed', [])
    all_content = added + removed
    
    for line in all_content:
        sexist_match = SEXIST_PATTERNS.search(line)
        body_shame_match = BODY_SHAMING.search(line)
        
        if sexist_match or body_shame_match:
            results.append({
                'id': r.get('id'),
                'user': r.get('user'),
                'timestamp': r.get('timestamp'),
                'status': r.get('status'),
                'summary': r.get('summary', ''),
                'match_type': 'SEXIST_STEREOTYPE' if sexist_match else 'BODY_SHAMING',
                'matched_pattern': (sexist_match or body_shame_match).group(0),
                'direction': 'ADDED' if line in added else 'REMOVED',
                'content_snippet': line[:300]
            })

print(f"=== SEXIST / BODY-SHAMING CONTENT SCAN ===")
print(f"Total matches found: {len(results)}\n")

if not results:
    print("No direct sexist stereotype or body-shaming language found in diffs.")
else:
    for i, r in enumerate(results, 1):
        direction_tag = "[ADDED by editor]" if r['direction'] == 'ADDED' else "[REMOVED by revert]"
        print(f"--- #{i} [{r['match_type']}] {direction_tag} ---")
        print(f"  ID        : {r['id']}")
        print(f"  User      : {r['user']}")
        print(f"  Timestamp : {r['timestamp']}")
        print(f"  Status    : {r['status']}")
        print(f"  Summary   : {r['summary'][:80]}")
        print(f"  MATCHED   : \"{r['matched_pattern']}\"")
        print(f"  CONTENT   : {r['content_snippet']}")
        print()
