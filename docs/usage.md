# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP client for API calls
- `matplotlib` - Visualization
- `pandas` - Data processing
- `numpy` - Numerical operations

### 2. Run Analysis

#### Option A: Single Continuum (Original Version)
```bash
python plot_spectrum.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Elder Abuse" "Interior Walls" "Baking" "Laundry" "Household Hair Colorants" "Gardening" "Home Appliances" "Plumbing"
```

**Outputs:**
- `data/processed/spectrum_domestic.csv` - Edit counts by gender
- `visualizations/domestic/spectrum_domestic.png` - Bar chart

#### Option B: Single Continuum (Enhanced Version)
```bash
python plot_spectrum_enhanced.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Elder Abuse" "Interior Walls" "Baking" "Laundry" "Household Hair Colorants" "Gardening" "Home Appliances" "Plumbing"
```

**Outputs:**
- `data/processed/domestic_enhanced.csv` - Full contribution data [+add/-remove]
- `data/processed/domestic_temporal.csv` - Year-wise breakdown
- `visualizations/domestic/domestic_contributions.png` - Contribution bar chart
- `visualizations/domestic/domestic_pivot_table.png` - Temporal pivot table

#### Option C: All Continuums (Original Version)
```bash
python run_all.py
```

#### Option D: All Continuums (Enhanced Version)
```bash
python run_all.py --enhanced
```

### 3. Check Results

All outputs are organized by type:

```
data/processed/          # CSV files
visualizations/          # PNG charts and tables
  ├── domestic/
  ├── occupational/
  ├── entertainment/
  └── policy/
```

## Understanding the Output

### CSV Files

#### `spectrum_{continuum}.csv` (Original)
| Column | Description |
|--------|-------------|
| Category | WikiHow category name |
| Articles | Number of articles analyzed |
| Male_Editors | Count of male editors |
| Female_Editors | Count of female editors |
| Unknown_Editors | Count of editors with unknown gender |
| Male_Edits | Total edits by male editors |
| Female_Edits | Total edits by female editors |
| Unknown_Edits | Total edits by unknown gender editors |

#### `{continuum}_enhanced.csv` (Enhanced)
All columns from original, plus:
| Column | Description |
|--------|-------------|
| Male_Additions | Bytes added by male editors |
| Male_Deletions | Bytes removed by male editors |
| Female_Additions | Bytes added by female editors |
| Female_Deletions | Bytes removed by female editors |
| Unknown_Additions | Bytes added by unknown gender editors |
| Unknown_Deletions | Bytes removed by unknown gender editors |

#### `{continuum}_temporal.csv` (Enhanced)
| Column | Description |
|--------|-------------|
| Continuum | Continuum name |
| Category | Category name |
| Period | 5-year period (e.g., "2005-2009") |
| Male_Edits | Male edits in this period |
| Female_Edits | Female edits in this period |

### Visualization Files

#### `spectrum_{continuum}.png` (Original)
- Horizontal stacked bar chart
- Shows edit counts by gender
- Categories ordered along spectrum (female-coded → male-coded)

#### `{continuum}_contributions.png` (Enhanced)
- Horizontal stacked bar chart
- Shows bytes added (contribution volume) by gender
- Annotations show [+add/-remove] breakdown
- Example annotation: `M: 5u, 22e [+3450/-120]`
  - 5 users
  - 22 edits
  - +3450 bytes added
  - -120 bytes removed

#### `{continuum}_pivot_table.png` (Enhanced)
- Temporal analysis table
- Rows = Categories
- Columns = 5-year periods (2005-2009, 2010-2014, etc.)
- Cells show: `M:count(%)` and `F:count(%)`
- Example: `M:15(68%)` means 15 male edits, 68% of total for that cell

## Advanced Usage

### Custom Category Lists

You can analyze any set of categories:

```bash
python plot_spectrum_enhanced.py custom_tech "Technology Continuum" "Social Media" "Programming" "Gaming" "Cybersecurity"
```

### Finding Categories

Use the category discovery tools:

```bash
# Find categories containing a keyword
python find_cats.py "cooking"

# Verify categories exist
python verify_cats.py
```

### Adjusting Sample Size

Edit the constants in the scripts:

```python
ARTICLE_LIMIT = 5      # Articles per category (default: 5)
REVISION_LIMIT = 30    # Revisions per article (default: 30)
```

**Trade-offs:**
- Higher limits = more data, longer runtime, higher API usage
- Lower limits = faster, but less representative sample

### Understanding 5-Year Periods

WikiHow launched in 2005, so periods are:
- **2005-2009**: Early years
- **2010-2014**: Growth phase
- **2015-2019**: Maturity
- **2020-2024**: Recent years
- **2025-2029**: Current period

Edits are categorized by their timestamp into these periods.

## Interpreting Results

### Gender Coding
- **Female-coded**: Categories traditionally associated with women (e.g., Baking, Nursing)
- **Male-coded**: Categories traditionally associated with men (e.g., Plumbing, Software)
- **Neutral**: Categories without strong gender stereotypes (e.g., Gardening, Business)

### What to Look For

1. **Stereotype Confirmation**: Do female-coded categories have more female participation?

2. **Outliers**: Categories that defy expected patterns
   - Example: A male-coded category with majority female editors

3. **Temporal Shifts**: Has gender balance changed over time?
   - Check pivot table for trends across periods

4. **Contribution Intensity**: Do minority-gender editors contribute differently?
   - Compare edit counts vs. byte contributions
   - Check [+add/-remove] ratios

5. **Deletion Patterns**: Do genders differ in content removal?
   - Higher deletions might indicate:
     - Quality control behavior
     - Vandalism reverting
     - Content refinement

## API Rate Limits

The WikiHow API has rate limits. The scripts implement:

- **5 second delay** between requests
- **Exponential backoff** on rate limit errors
- **10 second cooldown** between continuums (in run_all.py)

If you hit rate limits:
1. Reduce `ARTICLE_LIMIT` and `REVISION_LIMIT`
2. Run continuums separately instead of using run_all.py
3. Add longer delays in the code

## Gender Detection Methods

The system uses three methods in order:

1. **MediaWiki Profile Setting** (primary)
   - User's declared gender in WikiHow settings
   - Most reliable when set

2. **Profile Page Pronoun Analysis** (fallback #1)
   - Scans user profile for pronouns (she/her, he/him, they/them)
   - Uses regex patterns

3. **Genderize.io API** (fallback #2)
   - Name-based inference using first name
   - Requires ≥85% confidence threshold
   - Limited to 1000 requests/day (free tier)

**Note**: Gender detection is imperfect and limited to binary categories (due to MediaWiki constraints). Results should be interpreted with this limitation in mind.

## Troubleshooting

### Error: "No articles found for category"
- Category name might be incorrect
- Use `verify_cats.py` to check valid names
- Try variations (singular vs. plural, etc.)

### Error: "WikiHow API rate limit exceeded"
- Wait 5-10 minutes
- Reduce sample sizes
- Check internet connection

### Empty pivot table
- No edits in the analyzed time periods
- Increase `REVISION_LIMIT` to get more historical data
- Try different categories

### Missing genderize.io results
- Free tier limit reached (1000 requests/day)
- Not critical - system falls back to "unknown"

## Citation

If using this data for research, please note:

```
WikiHow Gender Stratification Analysis
Data source: WikiHow.com (via MediaWiki API)
Gender inference: User profiles + Genderize.io
Sample size: 5 articles × 30 revisions per category
Analysis period: 2005-2025
```

## Next Steps

See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for:
- Research hypotheses
- Detailed methodology
- Limitations and considerations
- Future research directions
