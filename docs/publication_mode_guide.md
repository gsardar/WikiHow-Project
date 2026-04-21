# Publication-Quality Visualization Guide

## Overview

The publication mode generates **academic-quality visualizations** suitable for journal articles, conferences, and formal reports.

### Key Features

✅ **100% stacked bar charts** - Shows proportions, not absolute counts
✅ **Professional typography** - Times New Roman, proper font sizes
✅ **Grayscale-friendly** - Works in both color and black & white
✅ **Clean styling** - Minimal clutter, maximum clarity
✅ **High resolution** - 300 DPI for print quality

---

## Quick Start

### Single Continuum (Publication Mode)

```bash
python plot_spectrum_publication.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing"
```

### All Continuums (Publication Mode - Fastest)

```bash
python run_all.py --publication
```

### Grayscale Version (for print)

```bash
python run_all.py --publication --grayscale
```

---

## Visualization Types

### 1. 100% Stacked Bar Chart

**Purpose**: Show gender distribution as percentages

**Features**:
- Each bar totals 100%
- Shows Male/Female/Unknown proportions
- Percentages labeled inside bars
- Absolute counts shown as (n=X)
- Editor counts on right side

**Use for**: Main gender distribution analysis

### 2. Temporal Pivot Table

**Purpose**: Show how gender participation changed over time

**Features**:
- Professional table layout
- Dark header row
- Shows both percentages and counts
- 5 time periods (2005-2009 through 2025-2026)

**Use for**: Temporal trends analysis

### 3. Contribution Breakdown Chart

**Purpose**: Show additions vs. deletions by gender

**Features**:
- 100% stacked bars
- Solid colors = additions
- Hatched patterns = deletions
- Shows complete contribution profile

**Use for**: Understanding contribution behavior beyond edit counts

---

## Output Files

For each continuum (e.g., "domestic"), generates:

### Data Files (`data/processed/`)
- `domestic_publication.csv` - Full dataset
- `domestic_temporal_pub.csv` - Temporal breakdown

### Visualizations (`visualizations/domestic/`)
- `domestic_100pct_stacked.png` - Main chart (color or grayscale)
- `domestic_temporal_table.png` - Temporal analysis table
- `domestic_contribution_breakdown.png` - Additions vs. deletions

All images: **300 DPI, publication-ready**

---

## Color Schemes

### Color Mode (Default)
- **Male**: Blue (#2166ac) - Dark in grayscale
- **Female**: Red (#b2182b) - Medium in grayscale
- **Unknown**: Light gray (#cccccc)

### Grayscale Mode
- **Male**: Dark gray (#404040)
- **Female**: Medium gray (#999999)
- **Unknown**: Light gray (#d9d9d9)

Both modes work well when printed in black & white!

---

## Usage Examples

### Example 1: Color version for presentation

```bash
python plot_spectrum_publication.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Elder Abuse" "Interior Walls" "Baking" "Laundry" "Household Hair Colorants" "Gardening" "Home Appliances" "Plumbing"
```

**Output**: Color charts at 300 DPI

### Example 2: Grayscale for journal submission

```bash
python plot_spectrum_publication.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Elder Abuse" "Interior Walls" "Baking" "Laundry" "Household Hair Colorants" "Gardening" "Home Appliances" "Plumbing" --grayscale
```

**Output**: Grayscale charts (print-safe)

### Example 3: All continuums, grayscale, 3 workers

```bash
python run_all.py --publication --grayscale --workers 3
```

**Output**: All 4 continuums in grayscale, ~10-15 minutes

---

## Typography & Styling

### Fonts
- **Family**: Serif (Times New Roman preferred)
- **Title**: 12pt, bold
- **Axes labels**: 11pt, bold
- **Tick labels**: 9pt
- **Legend**: 9pt
- **Annotations**: 8-9pt

### Chart Elements
- **DPI**: 300 (high quality for print)
- **Grid**: Light, dashed, horizontal only
- **Spines**: Top and right hidden (clean look)
- **Legend**: Bottom right, white background

---

## Comparison: Publication vs. Standard Mode

| Feature | Standard Mode | Publication Mode |
|---------|--------------|------------------|
| Bar type | Absolute counts | 100% stacked (proportions) |
| Typography | Default sans-serif | Times New Roman serif |
| DPI | 300 | 300 |
| Colors | Bright | Professional, grayscale-safe |
| Annotations | Counts only | Counts + percentages |
| Grid | Basic | Professional |
| Print-ready | Yes | Optimized |

---

## Tips for Academic Publications

### For Journal Articles

1. **Use grayscale mode** if journal doesn't guarantee color printing:
   ```bash
   python run_all.py --publication --grayscale
   ```

2. **Include sample size** in caption:
   > "Figure 1. Gender distribution across domestic task categories (N = 20 articles, 87 edits from identified genders)."

3. **Explain percentages** in text:
   > "Plumbing showed 35% male participation versus 6% female (n=28 and n=5 edits respectively)."

### For Conference Presentations

1. **Use color mode** for slides:
   ```bash
   python run_all.py --publication
   ```

2. **Enlarge charts** - 300 DPI allows scaling without quality loss

3. **Highlight key findings** in presentation text

### For Posters

1. **Color mode recommended** for visual impact
2. **300 DPI** ensures clarity even at poster size
3. **Include all three chart types** for comprehensive story

---

## Interpreting the Charts

### 100% Stacked Bar Chart

**Reading the chart**:
- Each bar = 100% of edits (excluding unknown gender)
- Blue segment = % male contribution
- Red segment = % female contribution
- Gray segment = % unknown gender

**What to look for**:
- Imbalanced bars → stereotype confirmation
- Balanced bars (50/50) → gender-neutral topic
- Trend across categories → continuum gradient

**Example interpretation**:
> "Plumbing (35% male, 6% female) shows strong male participation, while Baby Toys (24% male, 16% female) is more balanced, consistent with gender stereotypes."

### Temporal Pivot Table

**Reading the table**:
- Rows = Categories
- Columns = Time periods
- Cells = M: X% (n=Y) / F: Z% (n=W)

**What to look for**:
- Percentage shifts over time
- Increasing/decreasing gender gaps
- Period-specific patterns

**Example interpretation**:
> "Baking shifted from 79% male (2005-2009) to 58% male (2025-2026), suggesting decreasing male dominance over time."

### Contribution Breakdown

**Reading the chart**:
- Solid = Additions (new content)
- Hatched = Deletions (content removal)
- Each bar = 100% of contribution volume

**What to look for**:
- Deletion patterns by gender
- Additive vs. subtractive behavior
- Quality control indicators

**Example interpretation**:
> "Males contributed 60% of additions but only 40% of deletions in Plumbing, suggesting more constructive editing behavior."

---

## Command Reference

### Basic Commands

```bash
# Single continuum (color)
python plot_spectrum_publication.py CONTINUUM_ID "Title" "Cat1" "Cat2" ...

# Single continuum (grayscale)
python plot_spectrum_publication.py CONTINUUM_ID "Title" "Cat1" "Cat2" ... --grayscale

# All continuums (color)
python run_all.py --publication

# All continuums (grayscale)
python run_all.py --publication --grayscale

# Custom workers
python run_all.py --publication --workers 3
```

### Testing (No API Calls)

```bash
# Test publication visualizations
python test_publication.py

# View outputs in: visualizations/test_publication/
```

---

## Performance

| Mode | Time (1 continuum) | Time (4 continuums) |
|------|-------------------|---------------------|
| Sequential | 8-10 min | 32-40 min |
| Publication (parallel) | 2-3 min | 8-12 min |

**Publication mode uses parallel processing by default** (3-5x faster)

---

## Troubleshooting

### Charts don't look right

**Check**: Font availability
- Windows: Times New Roman should be available
- Linux: Install `sudo apt-get install msttcorefonts`
- Mac: Times New Roman included

### Low resolution output

**Check**: DPI setting
- Default: 300 DPI (publication quality)
- If needed: Edit `viz_publication.py` line 20: `'figure.dpi': 300`

### Colors too bright/dark

**Try**: Grayscale mode
```bash
python plot_spectrum_publication.py CONTINUUM "..." --grayscale
```

---

## Citation Format

If using in research:

```
Visualizations generated using WikiHow Gender Stratification Analysis toolkit.
Publication-quality mode with 100% stacked bar charts.
Sample: N articles, M edits from identified genders.
Time periods: 2005-2026 (five periods).
```

---

## Next Steps

1. **Generate test outputs**:
   ```bash
   python test_publication.py
   ```

2. **Run one continuum**:
   ```bash
   python plot_spectrum_publication.py domestic "Domestic Continuum" "Baby Toys" "Baking" "Plumbing"
   ```

3. **Run all continuums**:
   ```bash
   python run_all.py --publication
   ```

4. **Check results** in `visualizations/{continuum}/`

---

**Publication mode is the recommended way to generate figures for academic papers, theses, and formal reports.**

---

**Last Updated**: March 18, 2026
