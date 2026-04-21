import os
import csv
import pandas as pd
from wikihow import api

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
REVISIONS_CSV = os.path.join(DATA_DIR, "revisions.csv")
CONTRIBUTORS_CSV = os.path.join(DATA_DIR, "contributors_final.csv")
HEADERS = ["username", "profile_url", "editcount", "gender", "gender_source", "gender_confidence", "gender_evidence", "pronoun", "location", "tenure", "badges"]

def initialize_csv(path, headers):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

def main():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    initialize_csv(CONTRIBUTORS_CSV, HEADERS)
    
    unique_usernames = set()
    if os.path.exists(REVISIONS_CSV):
        df_revs = pd.read_csv(REVISIONS_CSV)
        unique_usernames.update(df_revs[df_revs['anon'] == False]['user'].unique())

    if os.path.exists(CONTRIBUTORS_CSV) and os.path.getsize(CONTRIBUTORS_CSV) > 100:
        df_done = pd.read_csv(CONTRIBUTORS_CSV)
        unique_usernames = unique_usernames - set(df_done['username'].tolist())

    users_list = sorted(list(unique_usernames))
    print(f"Batching {len(users_list)} contributors...")
    
    with open(CONTRIBUTORS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction='ignore')
        for i in range(0, len(users_list), 50):
            batch = users_list[i:i+50]
            print(f"  > Batch {i//50 + 1}")
            for username, user_info in api.get_users(batch):
                writer.writerow(user_info)
                f.flush()

if __name__ == "__main__":
    main()
