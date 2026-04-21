import os
import json
import csv
import glob

DATA_DIR = r"C:\Users\Admin\Documents\WikiHow Project\data\discovery\domestic"
MAPPED_SPACES = r"C:\Users\Admin\Documents\WikiHow Project\data\mapped_spaces.json"
OUTPUT_PATH = os.path.join(DATA_DIR, "cleaned_domestic_master.csv")

# Noise keywords (Animals/Pets) that often pollute the "Domestic" continuum
NOISE_KEYWORDS = [
    "bird", "parakeet", "budgie", "finch", "pigeon", "sparrow", 
    "rabbit", "squirrel", "kitten", "puppy", "puppies", "goat", 
    "mouse", "mice", "hamster", "guinea pig", "tortoise", "squirrel"
]

META_KEYWORDS = [
    "how to articles from wikihow", 
    "not found", 
    "error resolving"
]

def load_scores():
    with open(MAPPED_SPACES, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['domestic']['cats']

def is_clean(title):
    t_lower = title.lower()
    # Filter out Meta/Error pages
    for meta in META_KEYWORDS:
        if meta in t_lower:
            return False
    # Filter out Animals (The Pet/Animal care continuum is separate)
    for noise in NOISE_KEYWORDS:
        if noise in t_lower:
            # edge case: "How to Cook a Whole Bird" is domestic (Cooking), 
            # but "How to Care for a Baby Bird" is Pets.
            # We'll stick to a broad filter for now to be safe.
            return False
    return True

def main():
    scores = load_scores()
    all_rows = []
    seen_urls = set()
    
    # Iterate through each subcategory folder in domestic
    csv_files = glob.glob(os.path.join(DATA_DIR, "*", "discovery_report.csv"))
    
    print(f"Found {len(csv_files)} category reports for cleaning.")
    
    for csv_file in csv_files:
        cat_folder = os.path.basename(os.path.dirname(csv_file))
        # Find the original category name to get the score
        # Note: slug was category.replace(" ", "_").lower()
        original_cat = "Unknown"
        score = -1
        for cat_name, cat_score in scores.items():
            if cat_name.replace(" ", "_").lower() == cat_folder:
                original_cat = cat_name
                score = cat_score
                break
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count_removed = 0
            
            # Robust header detection
            title_key = None
            for row in reader:
                if title_key is None:
                    # Detect which title key exists in this specific CSV
                    for potential_key in ['Real WikiHow Title', 'WikiHow Real Title']:
                        if potential_key in row:
                            title_key = potential_key
                            break
                
                url = row['URL']
                title = row.get(title_key, "Unknown") if title_key else "Unknown"
                
                # Deduplication and Cleaning
                if url not in seen_urls and is_clean(title):
                    row['Category'] = original_cat
                    row['Spectrum Score'] = score
                    all_rows.append(row)
                    seen_urls.add(url)
                else:
                    count_removed += 1
            
            print(f"  Processed {cat_folder}: Kept {len(seen_urls)} total items. Removed {count_removed} noise/dupes.")

    # Export Master CSV
    if all_rows:
        headers = ["Category", "Spectrum Score", "Google Title", "Real WikiHow Title", "URL"]
        with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\n[SUCCESS] Master Cleaned Dataset saved to: {OUTPUT_PATH}")
        print(f"Total Unique High-Quality Articles: {len(all_rows)}")
    else:
        print("[ERROR] No data found to clean.")

if __name__ == "__main__":
    main()
