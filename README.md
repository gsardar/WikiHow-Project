# WikiHow Gender Stratification Analysis

Research project analyzing gender-based participation patterns in WikiHow article editing across different topical continuums.

## 📁 Project Structure

```
WikiHow Project/
├── wikihow/                    # Core library
│   ├── api.py                 # WikiHow API client (with gender detection)
│   ├── cli.py                 # Command-line interface
│   ├── cache.py               # Caching utilities
│   ├── exporter.py            # Data export functions
│   └── renderer.py            # Rendering utilities
│
├── data/                       # All data files
│   ├── mapped_spaces.json     # Continuum definitions (4 continuums)
│   ├── raw/                   # Raw API responses (if cached)
│   ├── processed/             # Processed CSV files
│   │   ├── spectrum_domestic.csv
│   │   ├── spectrum_occupational.csv
│   │   ├── domestic_enhanced.csv
│   │   ├── domestic_temporal.csv
│   │   └── ...
│
│   └── *.log                  # Processing logs
│
├── visualizations/             # All generated charts and tables
│   ├── domestic/              # Domestic continuum visuals
│   │   ├── spectrum_domestic.png
│   │   ├── domestic_contributions.png
│   │   └── domestic_pivot_table.png
│   ├── occupational/          # Occupational continuum visuals
│   ├── entertainment/         # Entertainment continuum visuals
│   ├── policy/                # Policy continuum visuals
│   └── gender_spectrum_chart.png
│
├── docs/                       # Documentation
│   ├── PROJECT_OVERVIEW.md    # Detailed project description & hypotheses
│   └── ...
│
├── plot_spectrum.py            # Original analysis script (edit count only)
├── plot_spectrum_enhanced.py   # NEW: Enhanced analysis (contributions + temporal)
├── run_all.py                  # Batch runner for all continuums
├── find_cats.py                # Category discovery utility
├── map_categories.py           # Category mapping utility
├── verify_cats.py              # Category verification utility
├── open_history_in_browser.py  # Debugging utility
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Analysis for Single Continuum
```bash
# Original version (edit counts only)
python plot_spectrum.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing" ...

# Enhanced version (contributions + temporal analysis)
python plot_spectrum_enhanced.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing" ...

# Parallel version (FAST - 3-5x speed improvement)
python plot_spectrum_parallel.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing" ...

# Publication version (RECOMMENDED - 100% stacked bars, publication-quality)
python plot_spectrum_publication.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing" ...
```

### Run All Continuums
```bash
# Sequential mode (~35-40 minutes)
python run_all.py

# Enhanced mode with temporal analysis (~35-40 minutes)
python run_all.py --enhanced

# Parallel mode (fast: ~10-15 minutes)
python run_all.py --parallel

# Publication mode - RECOMMENDED (fast + publication-quality charts: ~10-15 minutes)
python run_all.py --publication

# Publication mode with grayscale (for print journals)
python run_all.py --publication --grayscale
```

## 📊 Output Files

For each continuum (e.g., "domestic"), the analysis generates:

### Data Files (in `data/processed/`)
1. **`domestic_enhanced.csv`** - Full dataset with columns:
   - Category, Articles, Male/Female/Unknown Editors
   - Male/Female/Unknown Edits
   - Male/Female Additions/Deletions (bytes)

2. **`domestic_temporal.csv`** - Year-wise breakdown:
   - Continuum, Category, Period (5-year), Male/Female Edits

### Visualizations (in `visualizations/domestic/`)
1. **`domestic_contributions.png`** - Horizontal bar chart showing:
   - Gender distribution of contributions (bytes added)
   - Annotations with [+add/-remove] breakdowns

2. **`domestic_pivot_table.png`** - Temporal pivot table showing:
   - Categories × Year Periods (2005-2009, 2010-2014, etc.)
   - Male/Female edit counts and percentages per period

## 🔬 Research Continuums

### 1. Domestic & Household Management
Expected gradient: female-coded → male-coded
- Baby Toys, Baking, Laundry → Gardening, Plumbing

### 2. Occupational & Professional Fields
Expected gradient: female-coded → male-coded
- Nursing, HR → Physics, Software, Industrial Machinery

### 3. Entertainment & Leisure
Expected gradient: female-coded → male-coded
- Knitting, Dancing → DIY, Hacking, OLPC

### 4. Public Policy & Governance
Expected gradient: female-coded → male-coded
- User Education, Animal Welfare → Law Enforcement, Military

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for detailed hypotheses and methodology.

## 🔧 Configuration

Edit `data/mapped_spaces.json` to:
- Add/remove continuums
- Modify category lists
- Change category ordering

## 📈 Key Metrics Tracked

### Editor-Level
- Count of male/female/unknown editors per category
- Total edits per gender group

### Contribution-Level (NEW)
- **Bytes added** by each gender (positive contributions)
- **Bytes removed** by each gender (deletions/refinements)
- Net contribution volume

### Temporal (NEW)
- 5-year period breakdowns (2005-2009, 2010-2014, etc.)
- Edit distribution over time by gender




```bash


```

### Verify Categories Exist
```bash
python verify_cats.py
```

### Find Related Categories
```bash
python find_cats.py "keyword"
```

## 🛡️ Stability & Performance: The "Tank" Engine

The project has been upgraded to an **Ultra-Stable "Tank" Architecture** to handle high-volume scraping without system crashes:
- **Zero-Browser Engine**: Gender resolution (Real Name & Bio) is performed via static requests, bypassing the need for a crash-prone browser driver.
- **Session Sync**: The system synchronizes your active **Gourav 4** session cookies for authenticated, high-rate access to WikiHow profiles.
- **Static History Scraper**: Article histories are fetched via optimized static requests, ensuring 100% stability.

## 🔐 Security & Version Control

> [!CAUTION]
> **IMPORTANT**: The `data/` directory is excluded from version control via `.gitignore`.
> This directory contains **sensitive session data (cookies, credentials)** for the "Gourav 4" account.
> **DO NOT** manually upload the `data/` folder to GitHub to prevent account takeover.

## 🤝 Contributing

When adding new analysis scripts:
1. Keep scripts in project root
2. Save data outputs to `data/processed/`
3. Save visualizations to `visualizations/{continuum_name}/`
4. Update this README with new output descriptions

## 📄 License

Research project - see project documentation for data usage guidelines.

## 📧 Contact

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for research context and contact information.
