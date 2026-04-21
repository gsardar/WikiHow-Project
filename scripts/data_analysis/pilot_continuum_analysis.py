import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import re

def parse_tenure(tenure_str):
    if pd.isna(tenure_str): return 0
    # Find digits in strings like "over 19 years!" or "5+ years"
    match = re.search(r'(\d+)', str(tenure_str))
    return int(match.group(1)) if match else 0

def categorize_authority(row):
    tenure = parse_tenure(row['ai_tenure'])
    badges = str(row['ai_badge_list']).lower()
    
    # 1. Authority (Admin)
    if 'admin' in badges or 'administrator' in badges:
        return 'Authority\n(Admin)'
    
    # 2. Specialist (Non-admin badges)
    if len(badges) > 5: # Not empty or "none"
        return 'Specialist\n(Badged)'
    
    # 3. Veteran (High tenure, no badges)
    if tenure >= 5:
        return 'Veteran\n(5+ yr)'
    
    # 4. Novice (Low tenure, no badges)
    return 'Novice\n(<5 yr)'

def run_analysis():
    # 1. Load latest snapshot
    snapshots = glob.glob('f:/Users/Admin/Documents/WikiHow Project/data/analysis_snapshots/*.csv')
    if not snapshots:
        print("No snapshots found.")
        return
    
    latest_file = sorted(snapshots)[-1]
    print(f"Analyzing {latest_file}...")
    df = pd.read_csv(latest_file)
    
    # 2. Preprocess
    df['gender_clean'] = df['ai_inferred_gender'].str.capitalize().fillna('Unknown')
    df['gender_clean'] = df['gender_clean'].replace({'Unknown': 'Unknown'}) # Redundant but safe
    
    df['authority_level'] = df.apply(categorize_authority, axis=1)
    
    # 3. Plotting Setup
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12})
    
    # Create the Authority Continuum Plot
    plt.figure(figsize=(14, 8))
    
    # Calculate percentages for stacked bar
    ct = pd.crosstab(df['authority_level'], df['gender_clean'], normalize='index') * 100
    
    # Ensure correct order
    order = ['Novice\n(<5 yr)', 'Veteran\n(5+ yr)', 'Specialist\n(Badged)', 'Authority\n(Admin)']
    ct = ct.reindex(order)
    colors = {'Female': '#e74c3c', 'Male': '#3498db', 'Unknown': '#95a5a6'}
    available_genders = [g for g in ['Female', 'Male', 'Unknown'] if g in ct.columns]
    
    ax = ct[available_genders].plot(kind='bar', stacked=True, color=[colors[g] for g in available_genders], width=0.8)
    
    # Aesthetics
    plt.title('Gender Distribution across the Authority Continuum\n(Normalized % of Known vs Unknown Genders)', pad=20, fontsize=16)
    plt.xlabel('Authority Level (Based on Tenure & Badges)', fontsize=14)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.xticks(rotation=0) # Professional horizontal labels
    plt.legend(title='Inferred Gender', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0, 100)
    
    # Add labels inside bars
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if height > 5: # Only label if big enough
            x, y = p.get_xy() 
            ax.text(x+width/2, y+height/2, f'{height:.0f}%', ha='center', va='center', color='white', weight='bold')

    plt.tight_layout()
    
    # 4. Output
    out_dir = 'f:/Users/Admin/Documents/WikiHow Project/visualizations/pilot'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'authority_continuum_gender.png')
    plt.savefig(out_path, dpi=300)
    print(f"Chart saved to {out_path}")

if __name__ == "__main__":
    run_analysis()
