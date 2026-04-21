import sys
import os
import json
sys.path.append(os.getcwd())
from wikihow.api import get_users

def test_new_logic():
    test_users = ["Whimaway", "Joseph_S", "Varun Gera"]
    print(f"Testing new logic for users: {test_users}")
    print("-" * 40)
    
    results = get_users(test_users)
    
    for user in results:
        print(f"User: {user['username']}")
        print(f"  Real Name: {user['real_name']}")
        print(f"  Location:  {user['location']}")
        print(f"  Year:      {user['year']}")
        print(f"  Gender:    {user['gender']} ({user['gender_confidence']})")
        print(f"  Source:    {user['gender_source']}")
        print(f"  Badges:    {user['badges']}")
        print("-" * 20)

if __name__ == "__main__":
    test_new_logic()
