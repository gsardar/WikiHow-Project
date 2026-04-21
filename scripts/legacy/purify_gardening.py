import os
import pandas as pd

# Paths
DISCOVERY_CSV = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery\domestic\gardening\discovery_report.csv"
REJECTED_CSV = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery\domestic\gardening\rejected_list.csv"
EXTRACTION_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\extraction\domestic\gardening"

def purify():
    if not os.path.exists(DISCOVERY_CSV):
        print("Discovery file not found.")
        return

    df = pd.read_csv(DISCOVERY_CSV)
    
    # Define exclusion keywords (Noise detection)
    noise_keywords = [
        "Phone Number", "Numbers to Call", "Aura", "Blessed Week", "Tapple", 
        "Emoji", "Sex", "Percy Jackson", "Mental Age", "Truth or Dare", 
        "Facebook", "Screenshot", "Safe Search", "Subnet", "Linux", "Study Group", 
        "Instagram", "Mutual Friends", "Blue Lock", "Classroom", "Presentation", 
        "Hobby", "School Hot Takes", "Candlestick", "Invitation", "Friday Wishes", 
        "Anniversary", "Group Chat", "Flirty", "Message", "Quotes", "Name", 
        "American History", "Banking", "Finance", "Error Resolving", "Pass Notes", 
        "Pass Time", "Cinemas", "Villager Jobs", "Diet and Diabetes", "Sleep in Class",
        "Domain Expansion"
    ]
    
    rejection_mask = df['Real WikiHow Title'].str.contains('|'.join(noise_keywords), case=False, na=False)
    
    # Also reject the "Special:CategoryListing" and "Main-Page" and "Top Categories"
    misc_mask = df['URL'].str.contains('Special:|Main-Page', case=False, na=False)
    
    total_rejection_mask = rejection_mask | misc_mask
    
    rejected_df = df[total_rejection_mask].copy()
    rejected_df['Rejection_Reason'] = "Irrelevant (Discovery Noise)"
    
    # Save/Append to rejected_list
    if os.path.exists(REJECTED_CSV):
        existing_rejected = pd.read_csv(REJECTED_CSV)
        final_rejected = pd.concat([existing_rejected, rejected_df]).drop_duplicates(subset=['URL'])
    else:
        final_rejected = rejected_df
        
    final_rejected.to_csv(REJECTED_CSV, index=False)
    print(f"Added {len(rejected_df)} noise rows to rejected_list.csv")
    
    # Update discovery_report
    purified_df = df[~total_rejection_mask]
    purified_df.to_csv(DISCOVERY_CSV, index=False)
    print(f"Purified Discovery Report now has {len(purified_df)} rows.")

    # SYNC EXTRACTION FOLDER (Cleanup physical files)
    print("\nSyncing extraction folder...")
    valid_titles = set()
    for title in purified_df['Real WikiHow Title']:
        safe_title = "".join([c if c.isalnum() else "_" for c in title])[:50]
        valid_titles.add(f"{safe_title}_history.csv")

    deleted_count = 0
    if os.path.exists(EXTRACTION_DIR):
        for f in os.listdir(EXTRACTION_DIR):
            if f not in valid_titles:
                os.remove(os.path.join(EXTRACTION_DIR, f))
                deleted_count += 1
    
    print(f"Deleted {deleted_count} unrelated files from extraction folder.")

if __name__ == "__main__":
    purify()
