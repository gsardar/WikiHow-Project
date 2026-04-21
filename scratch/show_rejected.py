import os, json, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

base = r'f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum'
files = glob.glob(os.path.join(base, '**', '*.json'), recursive=True)

examples = []
for fpath in files:
    try:
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        for rev in data.get('revisions', []):
            status = rev.get('status', '')
            summary = rev.get('summary', '')
            user = rev.get('user', '')
            added = rev.get('exact_contribution', {}).get('added', [])
            removed = rev.get('exact_contribution', {}).get('removed', [])
            if status in ('reverted', 'rejected', 'undone'):
                added = rev.get('exact_contribution', {}).get('added', [])
                removed = rev.get('exact_contribution', {}).get('removed', [])
                examples.append({
                    'article': os.path.basename(fpath).replace('.json', ''),
                    'user': rev.get('user', 'Unknown'),
                    'status': status,
                    'summary': rev.get('summary', ''),
                    'gender': rev.get('inferred_gender', 'Unknown'),
                    'added_snippet': str(added[0])[:220] if added else '',
                    'removed_snippet': str(removed[0])[:220] if removed else ''
                })
    except Exception:
        pass

print(f'Total rejected/reverted revisions: {len(examples)}')
print()

seen = set()
shown = 0
for e in examples:
    key = e['summary'][:40]
    if key and key not in seen and shown < 15:
        seen.add(key)
        print(f"Article : {e['article']}")
        print(f"User    : {e['user']}  |  Gender: {e['gender']}")
        print(f"Status  : {e['status']}")
        print(f"Summary : {e['summary']}")
        if e['added_snippet']:
            print(f"Added   : {e['added_snippet']}")
        if e['removed_snippet']:
            print(f"Removed : {e['removed_snippet']}")
        print()
        shown += 1
