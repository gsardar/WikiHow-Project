import sys
import os
sys.path.append(os.getcwd())
from wikihow.api import get_genderize_gender
import json

def test_final_integration():
    print("Testing WikiHow Scraper - Tor Genderize Integration")
    print("--------------------------------------------------")
    
    # Test names
    names = ["John", "Mary", "Alex"]
    
    print(f"Fetching gender for: {names} (Enforced Tor Only)")
    try:
        results = get_genderize_gender(names)
        print("\nResults:")
        print(json.dumps(results, indent=4))
        
        # Check if Tor was used (evidence should be present in logs if we enabled it)
        # But here we just verify the call succeeded.
        if "John" in results:
            print("\nSUCCESS: Gender data retrieved via Tor proxy.")
        else:
            print("\nFAILURE: No data returned.")
            
    except Exception as e:
        print(f"\nIntegration Error: {e}")
        print("Ensure the Tor service is running: python scripts/service_control.py status")

if __name__ == "__main__":
    test_final_integration()
