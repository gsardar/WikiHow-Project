import sys
import os
import pandas as pd
sys.path.append(os.getcwd())
from wikihow.api import get_users

def run_baseline_comparison():
    # 1. Load Baseline (Old Predictions)
    old_df = pd.read_csv('data/contributors_final.csv')
    test_users = old_df['username'].tolist()[:20]  # First 20 as a rapid test
    
    print(f"Starting Baseline Comparison Test on {len(test_users)} users...")
    print("-" * 50)
    
    # 2. Run New Pipeline
    new_results = get_users(test_users)
    new_df = pd.DataFrame(new_results)
    
    # 3. Merge and Compare
    comparison = pd.merge(
        old_df[['username', 'gender']], 
        new_df[['username', 'gender', 'gender_source', 'gender_confidence', 'identity_tags']], 
        on='username', 
        suffixes=('_old', '_new')
    )
    
    # Identify Improvements
    def classify_change(row):
        if row['gender_old'] == 'unknown' and row['gender_new'] != 'unknown':
            return "NEW_DISCOVERY"
        if row['gender_old'] != row['gender_new'] and row['gender_new'] != 'unknown':
            return "CORRECTION"
        if row['gender_old'] == row['gender_new'] and row['gender_new'] != 'unknown':
            return "MATCH (VERIFIED)"
        return "NO_CHANGE"
    
    comparison['improvement_type'] = comparison.apply(classify_change, axis=1)
    
    # 4. Save
    os.makedirs("data", exist_ok=True)
    out_file = "data/baseline_comparison_results.csv"
    comparison.to_csv(out_file, index=False)
    
    # 5. Summary Report
    print(f"\nBaseline Comparison Summary ({out_file}):")
    print(comparison['improvement_type'].value_counts())
    print("\nDetailed Comparison:")
    cols = ['username', 'gender_old', 'gender_new', 'gender_source', 'improvement_type']
    print(comparison[cols].head(20).to_string())

if __name__ == "__main__":
    run_baseline_comparison()
