import csv
from collections import defaultdict

yearly_edits = defaultdict(lambda: {'Male': 0, 'Female': 0, 'NB': 0})

with open(r'c:\Users\Admin\Documents\WikiHow Project\research_taxonomy\continuum_yearly_taxonomy.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        year = int(row['Year'])
        yearly_edits[year]['Male'] += int(row['Male_Edits'])
        yearly_edits[year]['Female'] += int(row['Female_Edits'])
        yearly_edits[year]['NB'] += int(row['NB_Edits'])

for year in sorted(yearly_edits.keys()):
    m = yearly_edits[year]['Male']
    f = yearly_edits[year]['Female']
    n = yearly_edits[year]['NB']
    print(f"{year}, {m+f+n}, {f}, {m}, {n}")
