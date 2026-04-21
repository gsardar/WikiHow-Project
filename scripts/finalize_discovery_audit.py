import pandas as pd
import os
import re

# Configuration
BASE_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\discovery"
LOG_FILE = "audit_log.txt"

# Keywords for Rejection Logic
POP_CULTURE = [
    "harry potter", "percy jackson", "jujutsu kaisen", "anime", "k-pop", "p1harmony", 
    "omegaverse", "top or bottom", "fictional", "crush", "dating", "boyfriend", "girlfriend",
    "kiss", "makeup", "outfit", "elegant woman", "sexy", "guy looks", "crush thinks",
    "prank", "mischief", "fake sick", "skip class", "get someone fired", "kill time",
    "auras", "astrology", "sagittarius", "leo man", "taurus", "chiron", "grabovoi",
    "minecraft", "roblox", "fortnite", "ghosts", "haunted", "urban legend", "slang", "cba meaning"
]

LIFESTYLE_NOISE = [
    "moisturizer", "eyelash", "legs", "laundry", "stain", "cleaning", "hair", "bath",
    "gift ideas", "birthday wishes", "instagram bio", "pickup lines", "jokes", "trivia",
    "kahoot", "whiteboard games", "minute to win it", "party games"
]

# Exceptions to KEEP (Strong Technical/Professional/Educational)
TECH_EXCEPTIONS = [
    "career", "certification", "program", "policy", "handbook", "accounting", "nurse", 
    "nursing", "diagnosis", "surgery", "catheter", "iv", "software", "engineer", "mechanical",
    "economic", "federal", "civic", "government", "law", "citizen", "student council",
    "homework", "ideal student", "study group", "exam", "nclex", "asvab", "interview"
]

def audit_file(file_path):
    print(f"Processing: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    if df.empty:
        return

    cleaned_rows = []
    rejected_rows = []

    for index, row in df.iterrows():
        title = str(row['Google Title']).lower()
        real_title = str(row['Real WikiHow Title']).lower()
        combined_text = title + " " + real_title
        
        is_target = False
        rejection_reason = "Unclassified"

        # Check for technical exceptions first (Keep)
        if any(keyword in combined_text for keyword in TECH_EXCEPTIONS):
            is_target = True

        # Enforcement of Rejection Rules
        if any(keyword in combined_text for keyword in POP_CULTURE):
            is_target = False
            rejection_reason = "Pop Culture / Social Noise"
            
        elif any(keyword in combined_text for keyword in LIFESTYLE_NOISE):
            # Only reject if it's NOT in a technical context (like "Dress for Banking Job")
            if not any(keyword in combined_text for keyword in TECH_EXCEPTIONS):
                is_target = False
                rejection_reason = "Lifestyle / Social Noise"

        # Special Rule: Student Mischief vs Success
        if "skip" in combined_text or "fake sick" in combined_text or "get out of" in combined_text:
            is_target = False
            rejection_reason = "Mischief Noise"

        if is_target:
            cleaned_rows.append(row)
        else:
            row_dict = row.to_dict()
            row_dict['Rejection_Reason'] = rejection_reason
            rejected_rows.append(row_dict)

    # Write Cleaned File
    df_cleaned = pd.DataFrame(cleaned_rows)
    df_cleaned.to_csv(file_path, index=False)

    # Write Rejected File
    rejected_path = os.path.join(os.path.dirname(file_path), "rejected_list.csv")
    df_rejected = pd.DataFrame(rejected_rows)
    df_rejected.to_csv(rejected_path, index=False)
    
    print(f"  -> Cleaned: {len(cleaned_rows)} | Rejected: {len(rejected_rows)}")

def main():
    for root, dirs, files in os.walk(BASE_DIR):
        if "discovery_report.csv" in files:
            audit_file(os.path.join(root, "discovery_report.csv"))

if __name__ == "__main__":
    main()
