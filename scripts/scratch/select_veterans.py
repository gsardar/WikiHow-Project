import csv
import os

input_path = "f:/Users/Admin/Documents/WikiHow Project/data/contributors_final.csv"
output_path = "f:/Users/Admin/Documents/WikiHow Project/data/target_50_veterans_v2.csv"

def get_tenure_years(tenure_str):
    if not tenure_str or "unknown" in tenure_str.lower():
        return 0
    # format: "over X years!"
    parts = tenure_str.split(' ')
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    return 0

with open(input_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Sort by tenure years descending, then by username to be stable
sorted_rows = sorted(rows, key=lambda x: (get_tenure_years(x['tenure']), x['username']), reverse=True)

with open(output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(sorted_rows[:50])

print(f"Saved 50 veterans to {output_path}")
print("Top 5:")
for row in sorted_rows[:50]:
    print(f" - {row['username']} ({row['tenure']})")
