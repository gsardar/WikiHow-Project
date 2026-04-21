import os, json, glob, sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'f:\Users\Admin\Documents\WikiHow Project\data\contributions\continuum'
all_files = glob.glob(os.path.join(base_dir, '**', '*.json'), recursive=True)

results = []

interesting_words = ['wrong', 'bad', 'stupid', 'idiot', 'stop', 'damn', 'hell', 'messing', 'incorrect', 'bias', 'opinion', 'sexist', 'safety']

for fpath in all_files:
    try:
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        
        article_title = data.get('title', 'Unknown')
        article_url = f"https://www.wikihow.com/{article_title.replace(' ', '-')}"
        continuum = data.get('continuum', 'unknown')
        subcategory = data.get('subcategory', 'unknown')
        
        for rev in data.get('revisions', []):
            if rev.get('status') in ('reverted', 'undone', 'rejected'):
                summary = rev.get('summary', '')
                added = rev.get('exact_contribution', {}).get('added', [])
                removed = rev.get('exact_contribution', {}).get('removed', [])
                rev_id = rev.get('id', '')
                
                added_text = str(added[0]) if added else ""
                removed_text = str(removed[0]) if removed else ""
                
                content_for_check = (summary + " " + added_text + " " + removed_text).lower()
                
                if any(word in content_for_check for word in interesting_words):
                    # Filter out highly toxic stuff
                    if not any(toxic in content_for_check for toxic in ['raped', 'nazi']):
                        results.append({
                            'title': article_title,
                            'url': article_url,
                            'diff_url': f"https://www.wikihow.com/index.php?diff={rev_id}" if rev_id else "N/A",
                            'continuum': f"{continuum}/{subcategory}",
                            'user': rev.get('user', 'Unknown'),
                            'summary': summary,
                            'added': added_text[:150],
                            'removed': removed_text[:150]
                        })
    except:
        pass

# Sort by sub-continuum to provide variety
results.sort(key=lambda x: x['continuum'])

# Pick top 20 varied examples
final_selection = []
seen_subcats = {}
for r in results:
    subcat = r['continuum']
    if seen_subcats.get(subcat, 0) < 3: # Max 3 per subcategory for variety
        final_selection.append(r)
        seen_subcats[subcat] = seen_subcats.get(subcat, 0) + 1
    if len(final_selection) >= 20:
        break

print("# DIVERSE CROSS-CONTINUUM REVERTED EXAMPLES")
for e in final_selection:
    print(f"\n--- Article: {e['title']} [{e['continuum']}] ---")
    print(f"URL     : {e['url']}")
    print(f"Diff    : {e['diff_url']}")
    print(f"User    : {e['user']}")
    print(f"Summary : {e['summary'] if e['summary'] else '[No Summary]'}")
    if e['added']: print(f"Added   : \"{e['added']}...\"")
    if e['removed']: print(f"Removed : \"{e['removed']}...\"")
