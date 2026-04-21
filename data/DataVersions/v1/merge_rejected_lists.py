import os
import pandas as pd
import csv

base_path = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery"
output_file = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\cleanup.csv"

all_rejections = []

for root, dirs, files in os.walk(base_path):
    if "rejected_list.csv" in files:
        file_path = os.path.join(root, "rejected_list.csv")
        try:
            # Using engine='python' or error_bad_lines (deprecated) / on_bad_lines='skip'
            # But better to just try and fix the read if possible.
            df = pd.read_csv(file_path, on_bad_lines='warn', engine='python')
            
            # Ensure Category and Continuum are captured
            category = os.path.basename(root)
            continuum = os.path.basename(os.path.dirname(root))
            
            if 'Category' not in df.columns:
                df['Category'] = category
            if 'Continuum' not in df.columns:
                df['Continuum'] = continuum
                
            all_rejections.append(df)
            print(f"Successfully processed {file_path}")
        except Exception as e:
            print(f"FAILED to read {file_path}: {e}")

if all_rejections:
    master_df = pd.concat(all_rejections, ignore_index=True)
    cols = ['Continuum', 'Category', 'Query', 'Google Title', 'Real WikiHow Title', 'URL', 'Rejection_Reason']
    available_cols = [c for c in cols if c in master_df.columns]
    master_df[available_cols].to_csv(output_file, index=False)
    print(f"\nFinal master cleanup report saved at {output_file}")
    print(f"Total rejected records logged: {len(master_df)}")
else:
    print("No rejected_list.csv files found.")
