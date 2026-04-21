import csv

male_words = 0
female_words = 0
nb_words = 0

with open(r'c:\Users\Admin\Documents\WikiHow Project\research_taxonomy\continuum_taxonomy.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        male_words += int(row['Male_Words'])
        female_words += int(row['Female_Words'])
        nb_words += int(row['NB_Words'])

print(f"Male_Words: {male_words}")
print(f"Female_Words: {female_words}")
print(f"NB_Words: {nb_words}")
print(f"Total_Words: {male_words + female_words + nb_words}")
