import pandas as pd
import json

df = pd.read_csv('f:/Users/Admin/Documents/WikiHow Project/research_taxonomy/continuum_yearly_taxonomy.csv')

out_strs = []
for cont in df['Continuum'].unique():
    out_strs.append(f'// {cont} Data')
    subset = df[df['Continuum'] == cont]
    short_c = cont.lower()[:3]
    out_strs.append(f"const {short_c}TemporalData = {{")
    
    subs = subset['Sub-Continuum'].unique()
    for sub in subs:
        sub_df = subset[subset['Sub-Continuum'] == sub].sort_values('Year')
        y = list(sub_df['Year'])
        m = list(sub_df['Male_Words'])
        f = list(sub_df['Female_Words'])
        nb = list(sub_df['NB_Words'])
        out_strs.append(f"  '{sub}': {{")
        out_strs.append(f"    labels: {y},")
        out_strs.append(f"    m: {m},")
        out_strs.append(f"    f: {f},")
        out_strs.append(f"    nb: {nb}")
        out_strs.append("  },")
    out_strs.append("};")
    subs_list_str = json.dumps(list(subs))
    out_strs.append(f"const {short_c}L = {subs_list_str};\n")

with open('f:/Users/Admin/Documents/WikiHow Project/scratch/js_builder.txt', 'w') as f:
    f.write('\n'.join(out_strs))
