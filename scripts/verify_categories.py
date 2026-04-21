import sys
from wikihow import api

continuums = [
    {
        "output": "domestic",
        "title": "Domestic & Household Management Continuum",
        "cats": [
            "Baby Care", "Senior Care", "Home Decor", "Baking", 
            "Laundry", "Personal Finance", "Gardening", 
            "Furniture", "Appliance Repair", "Plumbing"
        ]
    },
    {
        "output": "occupational",
        "title": "Occupational & Professional Continuum",
        "cats": [
            "Early Childhood Education", "Nursing", "Social Work", "Human Resources", 
            "Arts and Entertainment", "Business Management", "Physics", 
            "Programming", "Engineering", "Construction"
        ]
    },
    {
        "output": "entertainment",
        "title": "Entertainment & Leisure Continuum",
        "cats": [
            "Knitting", "Dancing", "Reading", "Social Media", 
            "Photography", "Team Sports", "Board Games", 
            "Video Gaming", "Video Game Development", "Hacking"
        ]
    },
    {
        "output": "policy",
        "title": "Public Policy & Governance Continuum",
        "cats": [
            "Maternal Health", "Education and Communications", "Welfare", "Health", 
            "Community", "Taxes", "Politics", 
            "Police and Law Enforcement", "Military", "Politics and Government"
        ]
    }
]

def main():
    print("Verifying categories...")
    
    for c in continuums:
        print(f"\n[{c['title']}]")
        valid_cats = []
        for cat in c["cats"]:
            try:
                # Just fetch 1 to see if the category exists and has content
                articles = api.get_category_members(cat, limit=1)
                if articles:
                    print(f"  [OK] {cat}")
                    valid_cats.append(cat)
                else:
                    print(f"  [MISSING] {cat}")
            except Exception as e:
                print(f"  [ERROR] {cat}: {e}")
                
if __name__ == "__main__":
    main()
