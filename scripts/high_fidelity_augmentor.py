import os
import time
import csv
import re
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

# Base Paths
EXTRACTION_DIR = r"f:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\extraction"
MAIN_BROWSER_PROFILE = r"f:\Users\Admin\Documents\WikiHow Project\data\browser_session"

# Setup Driver
def get_driver():
    proxy = tor.get_selenium_proxy()
    # UC mode to avoid blocks, headless False to see what's happening if needed
    driver = Driver(uc=True, headless=True, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
    return driver

def extract_diff_content(driver, diff_url):
    try:
        driver.get(diff_url)
        time.sleep(2) # Stabilize
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        added_lines = soup.find_all('td', class_='diff-addedline')
        deleted_lines = soup.find_all('td', class_='diff-deletedline')
        
        added_text = "\n".join([line.get_text() for line in added_lines])
        deleted_text = "\n".join([line.get_text() for line in deleted_lines])
        
        return added_text.strip(), deleted_text.strip()
    except Exception as e:
        print(f"      [ERR] Diff extraction failed: {e}")
        return "", ""

def process_file(file_path):
    print(f"\n>>> Augmenting: {os.path.basename(file_path)}")
    
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Check if already augmented
    if 'added_text' in fieldnames:
        print("    [SKIP] Already contains content columns.")
        return

    # Prepare Title from filename
    title_match = re.search(r'^(.*)_history\.csv$', os.path.basename(file_path))
    if not title_match: return
    title = title_match.group(1).replace('_', ' ')

    driver = get_driver()
    
    updated_rows = []
    for i, row in enumerate(rows):
        rev_id = row['revision_id']
        parent_id = "" # In basic extractor we didn't save parent_id, we'll infer it
        if i + 1 < len(rows):
            parent_id = rows[i+1]['revision_id']
            
        print(f"    [{i+1}/{len(rows)}] Processing Rev: {rev_id}...")
        
        diff_url = f"https://www.wikihow.com/index.php?title={title.replace(' ', '_')}&diff={rev_id}&oldid={parent_id}" if parent_id else ""
        
        added_text, deleted_text = "", ""
        if diff_url:
            added_text, deleted_text = extract_diff_content(driver, diff_url)
            
        is_revert = bool(re.search(r'(revert|undo|rollback|undid|RCP)', row.get('comment', ''), re.IGNORECASE))
        
        row.update({
            'diff_url': diff_url,
            'added_text': added_text,
            'deleted_text': deleted_text,
            'is_revert': is_revert
        })
        updated_rows.append(row)
        
        # IP Rotation every 10 diffs to be safe
        if (i + 1) % 10 == 0:
            print("      [SYSTEM] Proxy rotation...")
            tor.rotate_ip()
            time.sleep(2)

    driver.quit()

    # Save augmented file
    new_fieldnames = fieldnames + ['diff_url', 'added_text', 'deleted_text', 'is_revert']
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    print("    [DONE] File updated.")

def main():
    target_continuum = "domestic"
    base_path = os.path.join(EXTRACTION_DIR, target_continuum)
    
    # Just process the top 2 for now as a deep-fidelity test
    count = 0
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith('_history.csv'):
                process_file(os.path.join(root, f))
                count += 1
                if count >= 3: return # Safety limit for pilot

if __name__ == "__main__":
    main()
