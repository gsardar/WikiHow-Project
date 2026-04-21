import os, json, glob, sys

sys.stdout.reconfigure(encoding='utf-8')

base = r'f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum'
files = glob.glob(os.path.join(base, '**', '*.json'), recursive=True)

expressive_examples = []

# Keywords that might indicate non-standard, interesting, or "lightly cursed" content
interesting_keywords = ['stop', 'messing', 'hell', 'crap', 'damn', 'dumb', 'stupid', 'incorrect', 'bad', 'why', 'wrong', 'gatekeeping']

for fpath in files:
    try:
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        article = os.path.basename(fpath).replace('.json', '')
        for rev in data.get('revisions', []):
            status = rev.get('status', '')
            if status in ('reverted', 'rejected', 'undone'):
                summary = rev.get('summary', '').strip()
                added = rev.get('exact_contribution', {}).get('added', [])
                removed = rev.get('exact_contribution', {}).get('removed', [])
                
                added_text = str(added[0]).strip() if added else ''
                removed_text = str(removed[0]).strip() if removed else ''
                
                full_text = (summary + ' ' + added_text + ' ' + removed_text).lower()
                
                # Look for "expressive" or interesting edits
                if any(word in full_text for word in interesting_keywords):
                    # Filter out the really bad stuff (strictly no hate speech or extreme violence)
                    if not any(bad in full_text for bad in ['raped', 'strangle', 'nazi']):
                        expressive_examples.append({
                            'article': article,
                            'user': rev.get('user', 'Unknown'),
                            'summary': summary,
                            'added': added_text[:250],
                            'removed': removed_text[:250]
                        })
    except:
        pass

print("# EXPRESSIVE & INTERESTING REVERTED EXAMPLES")
# Pick 15 variety examples
seen = set()
count = 0
for e in expressive_examples:
    if count >= 15: break
    key = e['summary'][:50] + e['article']
    if key in seen: continue
    seen.add(key)
    
    print(f"\n--- Article: {e['article']} ---")
    print(f"User    : {e['user']}")
    print(f"Summary : {e['summary'] if e['summary'] else '[No Summary]'}")
    if e['added']: print(f"Added   : \"{e['added']}...\"")
    if e['removed']: print(f"Removed : \"{e['removed']}...\"")
    count += 1
