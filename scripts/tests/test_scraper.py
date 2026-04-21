import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wikihow import api

def test_scraper():
    title = "Build-a-Computer"
    print(f"Testing scraper for: {title}")
    
    try:
        # 1. Test Revisions
        print("\n--- Testing get_revisions ---")
        revs = api.get_revisions(title, limit=5)
        print(f"Fetched {len(revs)} revisions.")
        for r in revs:
            print(f"  ID: {r.get('revid')}, User: {r.get('user')}, TS: {r.get('timestamp')}, Size: {r.get('size')}")
        
        if revs:
            # 2. Test Users
            print("\n--- Testing get_users ---")
            users = [revs[0]['user']]
            user_data = api.get_users(users)
            print(f"User data for {users[0]}:")
            print(json.dumps(user_data, indent=2))
            
            # 3. Test Diff
            if len(revs) > 1:
                print("\n--- Testing get_revision_diff ---")
                diff = api.get_revision_diff(revs[1]['revid'], revs[0]['revid'])
                print(f"Diff fetched for {revs[1]['revid']} -> {revs[0]['revid']}")
                print(f"Diff HTML Length: {len(diff['diff_html'])}")
                
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
