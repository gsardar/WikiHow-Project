import pandas as pd
import numpy as np
from scipy import stats

# Path
CSV_PATH = r"f:\Users\Admin\Documents\WikiHow Project\research_taxonomy\continuum_taxonomy.csv"

# Load data
df = pd.read_csv(CSV_PATH)

# Test 1: Correlation between Rank and Male Word Volume Share
# Share = Male_Words / (Male_Words + Female_Words + NB_Words)
df['Male_Share'] = df['Male_Words'] / (df['Male_Words'] + df['Female_Words'] + df['NB_Words'])
df = df.dropna(subset=['Male_Share', 'Rank'])

rho, p_val_corr = stats.spearmanr(df['Rank'], df['Male_Share'])

# Test 2: Chi-Squared for extreme categories (Baby Care Rank 0 vs Wiring Rank 9)
# Comparing the observed Male/Female/NB word counts
obs = np.array([
    [45499, 12726, 220], # baby_care (Rank 0)
    [78731, 31209, 2963] # wiring (Rank 9)
])
chi2, p_val_chi2, dof, ex = stats.chi2_contingency(obs)

# Print results for md report
print(f"--- VOLUMETRIC CORRELATION (RANK VS MALE SHARE) ---")
print(f"Spearman rho: {rho:.4f}")
print(f"P-Value: {p_val_corr:e}")

print(f"\n--- DISTRIBUTION SIGNIFICANCE (DOMESTIC ENDPOINTS) ---")
print(f"Chi2 Statistic: {chi2:.4f}")
print(f"P-Value: {p_val_chi2:e}")

# Results summary
if p_val_corr < 0.05:
    print("\nCONCLUSION: The increase in Male dominance as technical rank increases is STATISTICALLY SIGNIFICANT (p < 0.05).")
else:
    print("\nCONCLUSION: The trend is observed but not statistically significant at current sample size.")
