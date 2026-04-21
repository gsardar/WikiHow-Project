import os
import pandas as pd
import matplotlib.pyplot as plt
from wikihow import api

def run_simulated_pilot():
    # Real data extracted via Cloud Subagent
    editors = [
        "Nico Shamon", "MiscBot", "Seymour Edits", "WikiHow Projects", 
        "WikiHow Horizon 3", "Votebot", "Iris8989", "HumanBeing", 
        "Agusbou2015", "Dasha holosenina", "Wikivisual", "Engill90", 
        "Steve Masley 2.0", "ICanGuessItLol", "Henrymcorgan"
    ]
    
    print(f"Resolving {len(editors)} users for Category: Gardening (Pilot)...")
    
    # Use real gender resolution pipeline
    user_info = api.get_users(editors, fallback_to_profile=True)
    
    male_users = 0
    female_users = 0
    unknown_users = 0
    
    for u in editors:
        g = user_info.get(u, {}).get("gender", "unknown")
        if g == "male": male_users += 1
        elif g == "female": female_users += 1
        else: unknown_users += 1
        
    print(f"Result: M: {male_users} | F: {female_users} | U: {unknown_users}")

    # Generate the CSV/PNG to match the pipeline output
    data = [{
        "Category": "Gardening",
        "Articles": 1,
        "Male_Editors": male_users,
        "Female_Editors": female_users,
        "Unknown_Editors": unknown_users,
        "Male_Edits": male_users * 5, # Simulated volume
        "Female_Edits": female_users * 5,
        "Unknown_Edits": unknown_users * 5
    }]
    
    df = pd.DataFrame(data)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("visualizations/pilot", exist_ok=True)
    
    df.to_csv("data/processed/spectrum_pilot.csv", index=False)
    
    plt.figure(figsize=(10, 6))
    plt.barh(df["Category"], df["Male_Edits"], color="#4C72B0", label="Male Profile (Simulated)")
    plt.barh(df["Category"], df["Female_Edits"], left=df["Male_Edits"], color="#C44E52", label="Female Profile (Simulated)")
    plt.title("Gender Stratification: Gardening Pilot (CLOUD ASSIST)")
    plt.xlabel("Simulated Edit Volume")
    plt.legend()
    plt.savefig("visualizations/pilot/spectrum_pilot.png", dpi=300)
    
    print("\nPILOT COMPLETE: View visualizations/pilot/spectrum_pilot.png")

if __name__ == "__main__":
    run_simulated_pilot()
