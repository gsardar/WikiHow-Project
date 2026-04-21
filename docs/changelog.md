# Project Improvements - March 2026

## Summary of Changes

This document outlines the major improvements made to the WikiHow Gender Stratification Analysis project.

## 1. File Organization

### Before
```
WikiHow Project/
├── *.csv (mixed test and output files in root)
├── continuums/
│   ├── spectrum_domestic.csv
│   └── spectrum_domestic.png
├── plot_spectrum.py
└── wikihow/
```

### After
```
WikiHow Project/
├── data/
│   ├── mapped_spaces.json        # Configuration
│   ├── processed/                # Analysis outputs (CSV)
│   ├── test_samples/             # Test data
│   └── *.log                     # Logs
├── visualizations/
│   ├── domestic/                 # Domestic continuum charts
│   ├── occupational/             # Occupational continuum charts
│   ├── entertainment/            # Entertainment continuum charts
│   └── policy/                   # Policy continuum charts
├── docs/
│   ├── PROJECT_OVERVIEW.md       # Research documentation
│   ├── USAGE.md                  # Usage guide
│   └── CHANGES.md                # This file
├── plot_spectrum.py              # Original analysis
├── plot_spectrum_enhanced.py     # NEW: Enhanced analysis
├── run_all.py                    # Updated batch runner
└── wikihow/                      # Core library
```

**Benefits:**
- Clear separation of data, code, and outputs
- Easier to find specific continuum results
- Test data separated from production data
- Documentation centralized in docs/

## 2. Enhanced Analysis Features

### New Metrics Tracked

#### Contribution Volume (Bytes)
- **Before**: Only counted number of edits
- **After**: Tracks actual bytes added/removed
  - Male: [+additions, -deletions]
  - Female: [+additions, -deletions]

**Why this matters:**
- 10 small typo fixes ≠ 10 major content additions
- Reveals contribution *intensity*, not just participation
- Can identify if minority-gender editors contribute more/less per edit

#### Temporal Analysis (5-Year Periods)
- **Before**: No time-based analysis
- **After**: Breaks down edits by period:
  - 2005-2009
  - 2010-2014
  - 2015-2019
  - 2020-2024
  - 2025-2029

**Why this matters:**
- Track evolution of gender participation over time
- Test hypothesis: "Gender gaps are closing"
- Identify when categories became more/less balanced

### New Visualizations

#### 1. Contribution Bar Chart
- Shows bytes added (instead of just edit count)
- Annotations include [+add/-remove] breakdown
- Example: `M: 5u, 22e [+3450/-120]` means:
  - 5 male users
  - 22 edits
  - Added 3,450 bytes
  - Removed 120 bytes

#### 2. Pivot Table (PNG)
- Matrix view: Categories × Time Periods
- Each cell shows M/F edit distribution
- Enables temporal pattern analysis
- Publication-ready format

### New Data Files

For each continuum, now generates:

1. **`{continuum}_enhanced.csv`**
   - All original metrics plus:
   - Addition/deletion bytes by gender
   - More detailed breakdown

2. **`{continuum}_temporal.csv`**
   - Category × Period × Gender matrix
   - Enables time-series analysis
   - Can import into statistical software

## 3. API Improvements

### Enhanced `get_revisions()` Function
- **Before**: Returned user, timestamp, size, comment
- **After**: Also computes `size_delta` for each revision
  - Positive delta = bytes added
  - Negative delta = bytes removed
  - First revision delta = initial article size

**Implementation:**
```python
# Compute size deltas (newest to oldest, so we go backwards)
for i in range(len(all_revs)):
    current_size = all_revs[i].get("size", 0)
    if i < len(all_revs) - 1:
        previous_size = all_revs[i + 1].get("size", 0)
        all_revs[i]["size_delta"] = current_size - previous_size
    else:
        all_revs[i]["size_delta"] = current_size  # First revision
```

## 4. Documentation

### New Documentation Files

1. **`README.md`** (root)
   - Quick start guide
   - Project structure overview
   - Installation and basic usage

2. **`docs/PROJECT_OVERVIEW.md`**
   - Research objectives
   - 7 research hypotheses
   - Methodology details
   - Continuum definitions
   - Limitations and ethical considerations

3. **`docs/USAGE.md`**
   - Detailed usage instructions
   - Command examples
   - Output file explanations
   - Troubleshooting guide
   - API rate limit info

4. **`docs/CHANGES.md`** (this file)
   - Summary of improvements

## 5. Script Improvements

### `plot_spectrum_enhanced.py` (NEW)
- Tracks contribution volume (bytes)
- Tracks temporal distribution (5-year periods)
- Generates pivot tables
- Improved annotations with [+add/-remove] format

### `run_all.py` (UPDATED)
- Now supports `--enhanced` flag
- Updated paths for new folder structure
- Better progress reporting
- Can override script with `--script` parameter

**Usage:**
```bash
# Original version (all continuums)
python run_all.py

# Enhanced version (all continuums)
python run_all.py --enhanced
```

### `plot_spectrum.py` (UPDATED)
- Updated to use new folder structure
- Output paths now:
  - Data: `data/processed/`
  - Visualizations: `visualizations/{continuum}/`

## 6. Research Hypotheses Defined

Seven formal hypotheses now documented:

1. **H1: Gender Stereotype Alignment**
   - Female-coded categories → more female participation

2. **H2: Contribution Volume vs. Editor Count Divergence**
   - Editor counts may differ from contribution volume

3. **H3: Temporal Shift in Gender Participation**
   - Gender balance improving over time

4. **H4: Additive vs. Subtractive Contribution Patterns**
   - Gender differences in add/remove behavior

5. **H5: Cross-Continuum Consistency**
   - Stereotype strength varies by continuum type

6. **H6: Neutral Category Behavior**
   - Gender-neutral categories show balanced participation

7. **H7: Outlier Categories**
   - Some categories defy stereotypes

See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for full details.

## 7. Backward Compatibility

All original functionality preserved:

- `plot_spectrum.py` still works with same command-line interface
- Existing CSV structure unchanged (for original script)
- Can run both original and enhanced analyses

## Migration Guide

### For Existing Users

If you have old data in the root directory:

```bash
# Move old CSVs to test_samples
mv *.csv data/test_samples/

# Move mapped_spaces.json to data/
mv mapped_spaces.json data/

# Re-run analysis to generate in new structure
python run_all.py --enhanced
```

### For New Users

Just follow the Quick Start in [README.md](../README.md).

## Future Enhancements

Potential additions (not yet implemented):

1. **Multi-year trend lines**: Plot gender ratios over time
2. **Statistical significance testing**: Chi-square tests for gender distributions
3. **User journey tracking**: Follow individual editors across categories
4. **Quality metrics**: Beyond bytes, analyze edit acceptance/reversion rates
5. **Comparative analysis**: Compare WikiHow to Wikipedia patterns
6. **Interactive visualizations**: HTML/JavaScript charts for exploration

## Performance Considerations

### API Rate Limiting
- 5-second delay between requests (unchanged)
- 10-second cooldown between continuums (unchanged)
- Enhanced analysis takes ~same time as original (same API calls)

### Computation
- Size delta calculation: negligible overhead
- Temporal aggregation: minimal overhead
- Pivot table generation: <1 second per continuum

### Storage
- Enhanced CSV: ~2x size of original (more columns)
- Pivot table PNG: ~500KB per continuum
- Total additional storage: ~10MB for all 4 continuums

## Credits

**Original Project:**
- Basic gender analysis across continuums
- Edit count tracking
- Gender inference via MediaWiki + Genderize.io

**March 2026 Enhancements:**
- Contribution volume tracking ([+add/-remove])
- Temporal analysis (5-year periods)
- Pivot table visualizations
- Comprehensive documentation
- File organization

---

**Last Updated**: March 18, 2026
