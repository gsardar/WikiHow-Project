import os
import csv
import re

def sync_category(category_path, extraction_path):
    rejected_list_path = os.path.join(category_path, 'rejected_list.csv')
    if not os.path.exists(rejected_list_path):
        print(f"No rejected_list.csv found at {rejected_list_path}")
        return

    rejected_titles = []
    with open(rejected_list_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rejected_titles.append(row['Real WikiHow Title'])

    if not os.path.exists(extraction_path):
        print(f"Extraction directory not found: {extraction_path}")
        return

    files = os.listdir(extraction_path)
    deleted_count = 0
    
    for title in rejected_titles:
        # Normalize title for matching
        # WikiHow titles in filenames replace spaces with _ and often remove special chars
        clean_title = re.sub(r'[^\w\s]', '', title).replace(' ', '_')
        
        found = False
        for f in files:
            # Check if the filename starts with the normalized title
            # Filenames are like 'Title_history.csv'
            fname_normalized = re.sub(r'[^\w]', '_', f.replace('_history.csv', ''))
            title_normalized = re.sub(r'[^\w]', '_', clean_title)
            
            if fname_normalized.lower().startswith(title_normalized.lower()) or title_normalized.lower() in fname_normalized.lower():
                full_path = os.path.join(extraction_path, f)
                print(f"Deleting: {f} (Matched: {title})")
                try:
                    os.remove(full_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {f}: {e}")
                found = True
                break
        
    print(f"Done syncing {extraction_path}. Deleted {deleted_count} files.")

if __name__ == "__main__":
    base_discovery_path = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery\domestic"
    base_extraction_path = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\extraction\domestic"
    
    if os.path.exists(base_discovery_path):
        for category in os.listdir(base_discovery_path):
            cat_path = os.path.join(base_discovery_path, category)
            ext_path = os.path.join(base_extraction_path, category)
            if os.path.isdir(cat_path):
                print(f"\n--- Syncing Category: {category} ---")
                sync_category(cat_path, ext_path)
