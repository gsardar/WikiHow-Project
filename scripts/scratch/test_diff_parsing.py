import requests
from bs4 import BeautifulSoup

url = 'https://www.wikihow.com/api.php?action=query&prop=revisions&titles=Apply-Makeup&rvlimit=5&rvprop=ids|comment|user&format=json'
req = requests.get(url)
data = req.json()
pages = data.get('query', {}).get('pages', {})
page_id = list(pages.keys())[0]
revs = pages[page_id].get('revisions', [])

if len(revs) >= 2:
    rev1 = revs[0]['revid']
    rev2 = revs[1]['revid']
    
    print(f'Comparing rev {rev1} to {rev2}')
    print(f'Top rev comment: {revs[0].get("comment", "")}')
    
    diff_url = f'https://www.wikihow.com/index.php?title=Apply-Makeup&diff={rev1}&oldid={rev2}'
    print(f'Fetching: {diff_url}')
    diff_req = requests.get(diff_url)
    soup = BeautifulSoup(diff_req.text, 'html.parser')
    
    added_lines = soup.find_all('td', class_='diff-addedline')
    deleted_lines = soup.find_all('td', class_='diff-deletedline')
    
    print('\n--- ADDED CONTENT ---')
    for line in added_lines:
        print(line.get_text()[:100].strip())
        
    print('\n--- DELETED CONTENT ---')
    for line in deleted_lines:
        print(line.get_text()[:100].strip())
