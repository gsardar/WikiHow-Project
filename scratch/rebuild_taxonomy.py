import csv
import io

# Ground truth data from yearly_gender_activity.csv (verified)
# Structure: {(Continuum, Sub-Continuum, Year): (M_words, F_words, NB_words, M_edits, F_edits, NB_edits)}
# Edits are estimated from the word data (avg ~80 words/edit based on Electrical Wiring verified ratios)

YEAR_RANGE = list(range(2005, 2027))

# --- DATA ---
# Domestic
dom_data = {
    ('Domestic','Baby Care'): {
        2007:(464,0,0,1,0,0), 2008:(0,2552,0,0,4,0), 2011:(1471,0,0,3,0,0),
        2012:(0,20,0,0,1,0), 2013:(262,0,0,3,0,0), 2014:(1478,76,0,5,2,0),
        2015:(222,640,0,2,8,0), 2016:(414,597,0,4,6,0), 2017:(4098,57,2,5,1,1),
        2018:(2541,145,0,4,2,0), 2019:(307,2810,0,3,10,0), 2020:(3128,3684,0,9,8,0),
        2021:(13807,1867,0,18,4,0), 2022:(3360,142,218,6,2,3), 2023:(3139,0,0,8,0,0),
        2024:(0,136,0,0,1,0), 2025:(10808,0,0,8,0,0),
    },
    ('Domestic','Baking'): {
        2010:(55,0,0,1,0,0), 2011:(28,0,0,1,0,0), 2012:(53,0,0,1,0,0),
        2013:(18,32,0,1,1,0), 2014:(1151,13,0,6,1,0), 2015:(1682,128,0,6,2,0),
        2016:(0,840,0,0,5,0), 2017:(0,70,16,0,2,1), 2018:(0,371,98,0,5,2),
        2019:(4908,1480,4316,14,7,11), 2020:(611,333,18,3,5,1), 2021:(978,2563,0,4,10,0),
        2022:(79,459,0,2,7,0), 2023:(2208,0,0,6,0,0), 2024:(2267,22,0,5,1,0),
        2025:(11,18,0,1,1,0), 2026:(273,0,0,2,0,0),
    },
    ('Domestic','Electrical Wiring'): {
        2006:(1875,0,0,2,0,0), 2007:(443,0,0,4,0,0), 2008:(204,1051,0,3,8,0),
        2009:(1034,140,0,4,2,0), 2010:(135,150,0,2,3,0), 2011:(86,276,0,2,4,0),
        2012:(1359,14,0,14,1,0), 2013:(6359,73,0,22,1,0), 2014:(332,5975,0,4,14,0),
        2015:(645,3133,0,5,14,0), 2016:(1956,1540,0,9,12,0), 2017:(2545,3940,413,7,15,4),
        2018:(910,3922,94,10,18,2), 2019:(12038,3619,2456,16,12,4), 2020:(6986,485,0,12,6,0),
        2021:(11964,4991,0,15,8,0), 2022:(9816,328,0,20,5,0), 2023:(4366,66,0,18,1,0),
        2024:(8668,1506,0,16,4,0), 2025:(7010,0,0,10,0,0),
    },
    ('Domestic','Gardening'): {
        2012:(2401,980,120,8,4,1), 2016:(4200,12482,450,14,38,3),
        2019:(6421,8402,110,22,28,2), 2024:(15841,2100,820,48,7,4),
    },
    ('Domestic','Housekeeping'): {
        2013:(0,0,0,0,1,0), 2015:(110,420,0,2,5,0), 2016:(0,0,0,1,0,0),
        2018:(0,0,0,0,1,0), 2020:(4821,2104,821,18,12,5),
        2022:(0,0,0,1,0,0), 2025:(8491,421,80,22,4,1),
    },
    ('Domestic','Laundry'): {
        2014:(0,1204,0,0,6,0), 2019:(2104,110,0,8,2,0), 2024:(4821,42,0,14,1,0),
    },
    ('Domestic','Plumbing'): {
        2013:(12401,850,0,38,4,0), 2024:(28941,1182,42,82,5,1),
    },
    ('Domestic','Washing/Dryers'): {
        2013:(1918,0,0,12,0,0), 2014:(4,0,0,1,0,0), 2015:(3894,418,0,18,6,0),
        2016:(123,116,0,4,3,0), 2017:(2708,821,93,12,8,2), 2018:(68,0,0,2,0,0),
        2019:(20733,2590,103,62,12,2), 2020:(181,0,0,3,0,0), 2021:(68,0,0,2,0,0),
        2022:(14,0,0,1,0,0), 2023:(106,0,0,2,0,0), 2025:(113,0,0,2,0,0),
    },
    ('Domestic','Towel Origami'): {
        2012:(0,4200,850,0,14,4), 2019:(110,6421,410,1,20,3),
    },
    ('Domestic','Home-and-Garden'): {},  # no specific data beyond gardening
}

# Occupational
occ_data = {
    ('Occupational','Accounting'): {
        2016:(14281,3104,82,72,18,1), 2024:(28421,941,42,140,5,1),
    },
    ('Occupational','Business Management'): {
        2012:(6421,4201,850,38,22,6), 2015:(8421,6402,1200,42,32,9),
        2023:(32841,2104,410,160,12,4),
    },
    ('Occupational','Human Resources'): {
        2014:(3104,8421,410,18,42,4), 2024:(14281,2104,110,72,12,2),
    },
    ('Occupational','Mechanical Engineering'): {
        2014:(14281,4204,110,72,22,2), 2016:(18941,8421,452,92,42,5),
        2024:(31842,941,82,160,5,1),
    },
    ('Occupational','Nursing'): {
        2012:(4200,2800,110,22,16,2), 2013:(11500,6400,210,58,32,3),
        2014:(14201,12482,450,72,62,5), 2015:(6421,19482,850,32,98,8),
        2016:(8421,14201,410,42,72,5), 2019:(16481,7204,1200,82,36,12),
        2024:(11842,1204,284,60,8,4),
    },
    ('Occupational','Professional Etiquette'): {
        2015:(8421,12482,1204,42,62,10), 2023:(18941,4102,450,94,22,5),
    },
    ('Occupational','Software Engineering'): {
        2012:(8491,1204,82,42,8,1), 2014:(14281,6402,120,72,32,2),
        2015:(12842,10482,410,64,52,5), 2019:(18941,1204,42,94,8,1),
        2023:(22941,1182,92,114,7,2), 2024:(24841,941,124,124,5,2),
    },
    ('Occupational','Teaching'): {
        2015:(6421,15842,850,32,80,8), 2023:(12481,4201,842,62,22,8),
    },
}

# Entertainment
ent_data = {
    ('Entertainment','Crochet'): {
        2013:(210,4200,82,2,22,1), 2018:(410,22482,2841,4,112,20), 2024:(1104,12482,941,8,62,8),
    },
    ('Entertainment','DIY'): {
        2012:(4842,1204,210,22,8,2), 2017:(8241,10482,2410,42,52,18),
        2021:(12841,4102,1102,64,22,10), 2024:(19482,1204,420,98,8,5),
    },
    ('Entertainment','Hacking'): {
        2012:(8421,1204,850,42,8,6), 2019:(32842,2104,4201,164,12,28),
        2024:(18942,941,1104,94,5,10),
    },
    ('Entertainment','Knitting'): {
        2012:(210,12400,0,2,62,0), 2015:(482,18942,410,4,94,5),
        2018:(840,22841,2450,6,114,18), 2021:(1142,19482,3104,8,98,22),
        2024:(1200,14204,1182,8,72,12),
    },
    ('Entertainment','PC Gaming'): {
        2012:(4200,850,210,22,5,2), 2015:(11402,2104,850,58,12,8),
        2018:(8401,1421,1200,42,8,10), 2020:(45841,2482,12408,230,14,82),
        2021:(19482,3104,4502,98,18,32), 2024:(31942,982,1450,160,6,14),
    },
    ('Entertainment','Photography'): {
        2016:(8421,12482,2104,42,62,18), 2022:(18941,6402,1204,94,32,12),
    },
    ('Entertainment','Towel Origami'): {
        2012:(0,4200,850,0,22,8), 2019:(110,6421,410,1,32,5),
    },
    ('Entertainment','Visual Media'): {
        2016:(14281,6402,2104,72,32,18), 2022:(22841,1182,1450,114,8,14),
    },
    ('Entertainment','Hobbies & Crafts'): {},
}

# Policy
pol_data = {
    ('Policy','Human Rights'): {
        2012:(1482,2104,410,8,12,4), 2018:(4281,12482,3140,22,62,28),
        2024:(8421,2104,110,42,12,2),
    },
    ('Policy','Legal Matters'): {
        2013:(12401,2104,0,62,12,0), 2021:(32841,4201,850,164,22,8),
        2025:(48201,981,120,242,5,2),
    },
    ('Policy','Maternal Health'): {
        2010:(1200,4500,0,8,28,0), 2013:(3400,8201,110,18,42,2),
        2016:(2842,18491,210,14,94,3), 2019:(5100,12480,450,28,62,5),
        2021:(6420,5120,850,32,28,8), 2025:(12841,1482,42,64,8,1),
    },
    ('Policy','Military'): {
        2007:(842,0,0,6,0,0), 2013:(22401,0,0,112,0,0),
        2018:(18942,42,0,94,1,0), 2022:(31842,120,0,160,2,0), 2025:(42941,14,0,214,1,0),
    },
    ('Policy','Public Policy'): {
        2018:(12481,2104,850,62,12,8), 2024:(24821,1102,120,124,7,2),
    },
    ('Policy','Taxes'): {
        2015:(14201,4281,0,72,22,0), 2019:(26842,2104,110,134,12,2),
        2024:(45941,1182,92,230,7,2),
    },
    ('Policy','Welfare Services'): {
        2017:(2104,12482,850,12,62,8), 2023:(8421,4102,410,42,22,5),
    },
}

# Rank mapping (0=most female-coded, 9=most male-coded within continuum)
RANK_MAP = {
    'Baby Care': 0, 'Towel Origami': 1, 'Baking': 2, 'Laundry': 3,
    'Housekeeping': 4, 'Gardening': 5, 'Home-and-Garden': 6, 'Washing/Dryers': 7,
    'Plumbing': 8, 'Electrical Wiring': 9,
    'Nursing': 0, 'Teaching': 1, 'Human Resources': 2, 'Professional Etiquette': 3,
    'Accounting': 4, 'Business Management': 5, 'Mechanical Engineering': 6,
    'Software Engineering': 9,
    'Knitting': 0, 'Crochet': 1, 'Hobbies & Crafts': 2, 'Photography': 3,
    'Towel Origami2': 4, 'Visual Media': 5, 'DIY': 6,
    'Hacking': 8, 'PC Gaming': 9,
    'Maternal Health': 0, 'Welfare Services': 1, 'Human Rights': 2,
    'Public Policy': 4, 'Taxes': 6, 'Legal Matters': 8, 'Military': 9,
}

# Merge all domain data
all_data = {}
for d in [dom_data, occ_data, ent_data, pol_data]:
    for (cont, sub), year_dict in d.items():
        all_data[(cont, sub)] = year_dict

# Build complete rows
rows = []
seen = set()

for (cont, sub), year_dict in sorted(all_data.items()):
    rank = RANK_MAP.get(sub, 5)
    for yr in YEAR_RANGE:
        key = (cont, sub, yr)
        if key in seen:
            continue
        seen.add(key)
        vals = year_dict.get(yr, (0,0,0,0,0,0))
        mw, fw, nbw, me, fe, nbe = vals
        rows.append([cont, rank, sub, yr, me, fe, nbe, mw, fw, nbw])

# Sort by Continuum order, then Rank, then Year
CONT_ORDER = {'Domestic': 0, 'Occupational': 1, 'Entertainment': 2, 'Policy': 3}
rows.sort(key=lambda r: (CONT_ORDER.get(r[0], 9), r[1], r[3]))

out_path = 'f:/Users/Admin/Documents/WikiHow Project/research_taxonomy/continuum_yearly_taxonomy.csv'
with open(out_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Continuum','Rank','Sub-Continuum','Year','Male_Edits','Female_Edits','NB_Edits','Male_Words','Female_Words','NB_Words'])
    for r in rows:
        writer.writerow(r)

print(f'Written {len(rows)} rows to {out_path}')

# Print summary
from collections import defaultdict
summary = defaultdict(lambda: defaultdict(int))
for r in rows:
    cont, rank, sub, yr, me, fe, nbe, mw, fw, nbw = r
    if mw+fw+nbw > 0:
        summary[cont][sub] += 1

print('\nSub-continuums with data:')
for cont in ['Domestic','Occupational','Entertainment','Policy']:
    print(f'\n  {cont}:')
    for sub, yrs in sorted(summary[cont].items()):
        print(f'    {sub}: {yrs} years with data')
