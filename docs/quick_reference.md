# Quick Reference Card

## 🚀 Common Commands

### Testing (No API calls)
```bash
python test_enhanced.py
```

### Single Continuum Analysis
```bash
# Original (edit counts only)
python plot_spectrum.py domestic "Domestic Continuum" "Baby Toys" "Baking" "Plumbing"

# Enhanced (contributions + temporal)
python plot_spectrum_enhanced.py domestic "Domestic Continuum" "Baby Toys" "Baking" "Plumbing"
```

### All Continuums
```bash
# Original version
python run_all.py

# Enhanced version
python run_all.py --enhanced
```

## 📊 Understanding Output Files

### CSV Files (in `data/processed/`)

**Original**: `spectrum_{continuum}.csv`
- Basic edit counts by gender

**Enhanced**: `{continuum}_enhanced.csv`
- Includes: Male/Female_Additions, Male/Female_Deletions

**Temporal**: `{continuum}_temporal.csv`
- Category × Period × Gender breakdown

### Charts (in `visualizations/{continuum}/`)

**Original**: `spectrum_{continuum}.png`
- Stacked bars showing edit counts

**Enhanced**: `{continuum}_contributions.png`
- Stacked bars showing bytes added
- Annotations: `M: 8u, 16e [+5600/-89]`

**Pivot Table**: `{continuum}_pivot_table.png`
- Time periods × Categories
- Cells show M/F counts and percentages

## 📖 Documentation Map

| Question | Document |
|----------|----------|
| How do I start? | [README.md](README.md) |
| How do I use it? | [docs/USAGE.md](docs/USAGE.md) |
| What's the research goal? | [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) |
| What changed? | [docs/CHANGES.md](docs/CHANGES.md) |
| Quick overview? | [SUMMARY.md](SUMMARY.md) |
| Quick reference? | This file |

## 🔧 Configuration

### Adjust Sample Size
Edit in `plot_spectrum_enhanced.py`:
```python
ARTICLE_LIMIT = 5      # Articles per category
REVISION_LIMIT = 30    # Revisions per article
```

### Add/Edit Continuums
Edit `data/mapped_spaces.json`:
```json
{
  "continuum_id": {
    "title": "Continuum Name",
    "cats": ["Category1", "Category2", ...]
  }
}
```

### 5-Year Periods
Defined in `plot_spectrum_enhanced.py`:
```python
YEAR_PERIODS = [
    ("2005-2009", 2005, 2009),
    ("2010-2014", 2010, 2014),
    ("2015-2019", 2015, 2019),
    ("2020-2024", 2020, 2024),
    ("2025-2029", 2025, 2029),
]
```

## 🎯 Four Continuums

### 1. Domestic & Household Management
**Spectrum**: Female-coded → Male-coded
- Baby Toys, Elder Abuse, Interior Walls, Baking, Laundry, Household Hair Colorants, Gardening, Home Appliances, Plumbing

### 2. Occupational & Professional Fields
**Spectrum**: Female-coded → Male-coded
- Waking Up Early, Nursing Careers, Human Resources Careers, Darts, Business, Physics, Software, Mechanical Puzzles, Construction Toys, Industrial Machinery and Tools

### 3. Entertainment & Leisure
**Spectrum**: Female-coded → Male-coded
- Knitting, Dancing, Poetry, Social Media, Photography, Passports, Board Games, OLPC, Games, Protection Against Hacking, DIY

### 4. Public Policy & Governance
**Spectrum**: Female-coded → Male-coded
- User Education, Animal Welfare Activism, Turbans, Foreign Exchange Market, Law Enforcement, Military Clothing, Policy

## 📈 Reading the Charts

### Contribution Bar Chart
```
Baby Toys  [████ Male ████][███ Female ███]  5 arts | M: 15u, 21e [+3450/-120] | F: 7u, 14e [+2800/-95]
```

**Means**:
- 5 articles analyzed
- Male: 15 users, 21 edits, added 3450 bytes, removed 120 bytes
- Female: 7 users, 14 edits, added 2800 bytes, removed 95 bytes

### Pivot Table
```
| Category   | 2005-2009      | 2010-2014      |
|------------|----------------|----------------|
| Baking     | M:18(90%)      | M:5(22%)       |
|            | F:2(10%)       | F:17(77%)      |
```

**Means**:
- 2005-2009: 90% male editors (18 edits), 10% female (2 edits)
- 2010-2014: 22% male editors (5 edits), 77% female (17 edits)
- Shows shift toward female participation over time

## 🔍 Interpreting Results

### Look For:

1. **Stereotype Confirmation**
   - Female-coded categories (Baking) → More female participation?
   - Male-coded categories (Plumbing) → More male participation?

2. **Outliers**
   - Male-coded categories with female majority
   - Female-coded categories with male majority

3. **Temporal Shifts**
   - Are later periods (2015-2019, 2020-2024) more balanced?
   - Which categories changed most?

4. **Contribution Intensity**
   - Do minority-gender editors contribute more/less per edit?
   - Compare edit counts vs. byte contributions

5. **Deletion Patterns**
   - Higher deletions → quality control, vandalism reverting, or refinement?
   - Do genders differ in [-remove] behavior?

## ⚡ Performance Tips

### Speed Up Testing
1. Use `test_enhanced.py` instead of real API calls
2. Reduce `ARTICLE_LIMIT` and `REVISION_LIMIT`
3. Test on one category first

### Avoid Rate Limits
1. Don't run multiple instances simultaneously
2. Use `run_all.py` (includes automatic delays)
3. Spread analysis across multiple days

### Storage Space
- Each continuum: ~2-3 MB (CSVs + PNGs)
- All 4 continuums: ~10-12 MB total

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No articles found" | Check category name in `verify_cats.py` |
| Rate limit error | Wait 5-10 minutes, reduce sample sizes |
| Empty pivot table | Increase `REVISION_LIMIT` for more history |
| Unicode error | Using Windows? Test scripts now use `[OK]` instead of ✓ |

## 📞 Getting Help

1. Check [docs/USAGE.md](docs/USAGE.md) troubleshooting section
2. Review error messages carefully
3. Test with `test_enhanced.py` to isolate API issues
4. Check `data/*.log` files for detailed logs

## ✅ Verification Checklist

Before running full analysis:

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Tested with `python test_enhanced.py`
- [ ] Verified categories exist (`python verify_cats.py`)
- [ ] Checked `data/mapped_spaces.json` is correct
- [ ] Understand API rate limits (5 sec between requests)
- [ ] Have ~1 hour for full `run_all.py --enhanced`

## 🎓 Academic Use

If citing this project:

```
WikiHow Gender Stratification Analysis
Method: Gender inference via MediaWiki API + Genderize.io
Sample: 5 articles × 30 revisions per category
Periods: 5-year intervals (2005-2029)
Metrics: Edit counts, byte contributions [+add/-remove]
Source code: [Your repository URL]
```

---

**Last Updated**: March 18, 2026
