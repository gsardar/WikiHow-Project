import os, json, glob, sys
import re

sys.stdout.reconfigure(encoding='utf-8')

base = r'f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum'
files = glob.glob(os.path.join(base, '**', '*.json'), recursive=True)

presentation_examples = []

def is_safe(text):
    # Filter out profanity or sensitive keywords for presentation safety
    unsafe_keywords = ['raped', 'strangle', 'choke', 'sex', 'porn', 'fuck', 'shit', 'nazi']
    text_lower = text.lower()
    return not any(word in text_lower for word in unsafe_keywords)

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
                
                if is_safe(summary) and is_safe(added_text) and is_safe(removed_text):
                    presentation_examples.append({
                        'article': article,
                        'user': rev.get('user', 'Unknown'),
                        'summary': summary,
                        'added': added_text[:200],
                        'removed': removed_text[:200]
                    })
    except:
        pass

# Select specific archetypes for the presentation
categories = {
    'Good Faith Content Expansion': [],
    'Technical/Formatting Conflict': [],
    'Community Moderation Paradox (Patrol Approved but Reverted)': [],
    'Grammar/Style Rigidness': []
}

for e in presentation_examples:
    s = e['summary'].lower()
    a = e['added'].lower()
    
    # Category 1: Good Faith Content Expansion
    if len(e['added']) > 50 and not s and len(categories['Good Faith Content Expansion']) < 3:
        categories['Good Faith Content Expansion'].append(e)
        
    # Category 2: Technical/Formatting
    if ('category' in s or 'image' in s or 'link' in s) and len(categories['Technical/Formatting Conflict']) < 3:
        categories['Technical/Formatting Conflict'].append(e)
        
    # Category 3: Patrol Approved
    if ('patrol' in s or 'approved' in s) and len(categories['Community Moderation Paradox (Patrol Approved but Reverted)']) < 3:
        categories['Community Moderation Paradox (Patrol Approved but Reverted)'].append(e)
        
    # Category 4: Grammar
    if ('spell' in s or 'grammar' in s or 'typo' in s) and len(categories['Grammar/Style Rigidness']) < 3:
        categories['Grammar/Style Rigidness'].append(e)

print("# SAFE EXAMPLES FOR PRESENTATION")
for cat, items in categories.items():
    print(f"\n## {cat}")
    for i, e in enumerate(items):
        print(f"\nExample {i+1}: {e['article']}")
        print(f"- User: {e['user']}")
        print(f"- Reason: {e['summary'] if e['summary'] else 'None provided'}")
        if e['added']: print(f"- Added Content: \"{e['added']}...\"")
        if e['removed']: print(f"- Removed Content: \"{e['removed']}...\"")
