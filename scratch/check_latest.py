import json, os, glob

base = r'data\contributions\continuum\domestic'
files = glob.glob(os.path.join(base, '**', '*.json'), recursive=True)
files.sort(key=os.path.getmtime, reverse=True)

if files:
    latest = files[0]
    print(f'Latest file: {latest}')
    with open(latest, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    revs = data.get('revisions', [])
    print(f'Total Revisions extracted: {len(revs)}')
    banned = sum(1 for r in revs if r.get('likely_banned') or 'vandal' in r.get('comment', '').lower())
    print(f'Potential Vandalism/Banned: {banned}')
    
    talk = data.get('talk_page_text', '')
    print(f'Talk Page Character Count: {len(talk)}')
else:
    print('No json files found.')
