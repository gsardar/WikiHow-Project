import sys
import os
import pandas as pd
sys.path.append(os.getcwd())
from wikihow.api import get_users

def run_performance_test():
    # 1. New Test Set (Random Article Contributors + Varun Gera + Whimaway)
    test_users = [
        'Teresa', 'Julia_S', 'Saurav_P', 'Lois_S', 'Joseph_S', 
        'Sora_L', 'Lizzie_M', 'Bebop', 'Heli_G', 'Kari_M',
        'Varun Gera', 'Whimaway'
    ]
    
    print(f"Starting Full Performance Test on {len(test_users)} users...")
    print("-" * 50)
    
    results = get_users(test_users)
    
    # 2. Build the new test CSV
    df = pd.DataFrame(results)
    
    # Organize columns
    cols = [
        'username', 'real_name', 'location', 'year', 'editcount', 
        'gender', 'gender_confidence', 'gender_source', 'badges'
    ]
    df = df[cols]
    
    # 3. Accuracy Heuristic (Consensus)
    # We define 'Accurate' if it matches a deterministic source (Pronoun)
    # or a high-confidence Name match (>0.95).
    def check_accuracy(row):
        if row['gender_source'] == "Pronoun":
            return "High (Deterministic)"
        if row['gender_confidence'] >= 0.95:
            return "High (Confident Name)"
        return "Medium (GenAI/Algorithm Fallback)"
    
    df['accuracy_level'] = df.apply(check_accuracy, axis=1)
    
    # 4. Save
    os.makedirs("data", exist_ok=True)
    out_file = "data/new_test_results.csv"
    df.to_csv(out_file, index=False)
    
    # 5. Summary Report
    print(f"\nFinal Report Summary ({out_file}):")
    print(df['gender_source'].value_counts())
    print("\nSample Results:")
    print(df[['username', 'gender', 'gender_source', 'accuracy_level']].head(10))
    print(f"\nTotal Processed: {len(df)}")

if __name__ == "__main__":
    run_performance_test()
