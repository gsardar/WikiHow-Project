# WikiHow Gender Stratification Analysis Project

## Project Overview

This research project analyzes gender-based participation patterns in WikiHow article editing across different topical continuums. The study examines whether certain topics exhibit gender-stereotypical participation patterns, both in terms of editor demographics and contribution volume.

## Research Objectives

### Primary Objectives
1. **Quantify gender participation across stereotype-aligned topics**: Measure male and female editor participation across topic categories traditionally associated with different genders
2. **Analyze contribution volume by gender**: Move beyond simple editor counts to examine the actual volume of content contributed (measured in bytes added/removed)
3. **Temporal analysis**: Track how gender participation patterns evolve over time (2005-2010 vs 2011-2015)
4. **Cross-continuum comparison**: Compare participation patterns across four distinct continuums (domestic, occupational, entertainment, policy)

### Secondary Objectives
1. **Distinguish between additive and subtractive contributions**: Track whether contributions add or remove content
2. **Identify participation outliers**: Find categories that defy expected gender stereotypes
3. **Visualize patterns effectively**: Create clear, informative visualizations for academic and public audiences

## Continuums Under Study

### 1. Domestic & Household Management Continuum
Expected gradient from female-stereotyped → male-stereotyped tasks:
- **Female-coded**: Baby Toys, Elder Abuse, Baking, Laundry, Household Hair Colorants
- **Neutral/Mixed**: Interior Walls, Gardening, Home Appliances
- **Male-coded**: Plumbing

### 2. Occupational & Professional Fields Continuum
Expected gradient from female-stereotyped → male-stereotyped careers:
- **Female-coded**: Nursing Careers, Human Resources Careers
- **Neutral/Mixed**: Waking Up Early, Business, Darts
- **Male-coded**: Physics, Software, Mechanical Puzzles, Construction Toys, Industrial Machinery and Tools

### 3. Entertainment & Leisure Continuum
Expected gradient:
- **Female-coded**: Knitting, Dancing, Poetry, Social Media
- **Neutral/Mixed**: Photography, Board Games, Games
- **Male-coded**: Protection Against Hacking, DIY, OLPC

### 4. Public Policy & Governance Continuum
Expected gradient:
- **Female-coded**: User Education, Animal Welfare Activism
- **Neutral/Mixed**: Foreign Exchange Market, Policy
- **Male-coded**: Law Enforcement, Military Clothing, Turbans

## Research Hypotheses

### H1: Gender Stereotype Alignment
**Hypothesis**: Categories traditionally associated with a particular gender will show higher participation (both editor count and contribution volume) from that gender.

**Prediction**:
- Female-coded categories (e.g., Baking, Nursing) will show higher female participation
- Male-coded categories (e.g., Plumbing, Software) will show higher male participation

### H2: Contribution Volume vs. Editor Count Divergence
**Hypothesis**: Gender distribution by contribution volume may differ from distribution by editor count, suggesting differential engagement intensity.

**Prediction**:
- Some categories may have balanced editor counts but imbalanced contribution volumes
- Minority-gender editors in stereotype-aligned categories may make smaller or larger average contributions

### H3: Temporal Shift in Gender Participation
**Hypothesis**: Gender participation patterns have shifted between 2005-2010 and 2011-2015 time periods.

**Prediction**:
- Later period (2011-2015) will show more balanced gender participation across categories
- Female participation in male-coded categories increases over time
- Male participation in female-coded categories shows less change

### H4: Additive vs. Subtractive Contribution Patterns
**Hypothesis**: Gender groups may differ in whether they primarily add or remove content.

**Prediction**:
- Both genders primarily contribute additive edits
- Potential differences in deletion/refinement behavior across gender groups
- Gender-minority editors may show different add/remove patterns (e.g., more conservative edits)

### H5: Cross-Continuum Consistency
**Hypothesis**: Gender stereotyping strength varies across different continuums (domestic vs. occupational vs. entertainment vs. policy).

**Prediction**:
- Domestic continuum shows strongest gender stereotyping effects
- Occupational continuum shows moderate stereotyping
- Entertainment and policy continuums show weaker or more variable patterns

### H6: Neutral Category Behavior
**Hypothesis**: Gender-neutral categories (e.g., Gardening, Business) will show balanced participation.

**Prediction**:
- Categories without strong gender associations show approximately 50/50 participation
- Neutral categories may vary more widely, showing no predictable pattern

### H7: Outlier Categories
**Hypothesis**: Some categories will show counter-stereotypical patterns (e.g., male-coded topics with female majority).

**Prediction**:
- Identify specific categories that defy stereotypes
- These outliers may reveal important nuances about gender and knowledge domains

## Methodology

### Data Collection
- **Source**: WikiHow API (MediaWiki-based)
- **Sample Size**: 5 articles per category, 30 most recent revisions per article
- **Gender Inference**:
  1. Primary: MediaWiki user profile settings
  2. Fallback 1: User profile page pronoun analysis
  3. Fallback 2: Genderize.io first-name analysis (≥85% confidence threshold)

### Metrics Tracked

#### Editor-Level Metrics
- Male editor count
- Female editor count
- Unknown/unidentified gender editor count

#### Contribution-Level Metrics (NEW)
- **Male contributions**: [+bytes added, -bytes removed]
- **Female contributions**: [+bytes added, -bytes removed]
- **Unknown contributions**: [+bytes added, -bytes removed]
- Total edit count by gender
- Net contribution volume by gender

#### Temporal Metrics
- Year-wise breakdown (2005-2010 vs 2011-2015)
- Edit distribution over time
- Gender participation shifts between periods

### Visualization Outputs

1. **Stacked Horizontal Bar Charts**: Show gender distribution across continuum categories
2. **Pivot Tables**: Year × Continuum × Gender matrices showing participation patterns
3. **Contribution Breakdown Charts**: Visualize [+add, -remove] patterns by gender
4. **Temporal Comparison Graphs**: Side-by-side comparison of time periods

## Expected Outcomes

### Academic Contributions
- Empirical evidence of gender stereotyping in online knowledge production
- Understanding of how gender affects contribution patterns in peer-production systems
- Insights into temporal evolution of gender participation gaps

### Practical Applications
- Identify categories needing targeted recruitment of underrepresented genders
- Inform WikiHow community outreach and diversity initiatives
- Provide baseline for tracking progress in gender equity

## Limitations & Considerations

### Methodological Limitations
1. **Gender Binary**: Analysis limited to male/female categories (MediaWiki limitation + genderize.io constraints)
2. **Inference Accuracy**: Gender detection relies on self-reporting and name-based inference (potential misclassification)
3. **Sample Size**: Limited to 5 articles × 30 revisions per category (resource constraints)
4. **Selection Bias**: Categories chosen based on perceived stereotyping (confirmation bias risk)

### Ethical Considerations
1. **Privacy**: Uses only publicly available data (usernames, public profiles)
2. **Essentialism Risk**: Analysis does not imply gender determines interests or capabilities
3. **Intersectionality**: Cannot account for race, age, geography, or other demographic factors

### Technical Limitations
1. **API Rate Limits**: WikiHow API throttling affects data collection speed
2. **Byte Changes**: Byte deltas approximate but don't perfectly represent content quality
3. **Bot Edits**: Analysis excludes anonymous edits but may include bot accounts with usernames

## Future Research Directions

1. **Expanded Temporal Analysis**: Extend to 2016-2025 data
2. **Content Quality Metrics**: Analyze edit quality, not just quantity
3. **User Journey Tracking**: Follow individual editor trajectories across categories
4. **Comparative Platform Analysis**: Compare WikiHow patterns to Wikipedia, other wikis
5. **Non-Binary Gender Analysis**: Incorporate they/them pronoun detection if data becomes available
6. **Multilingual Analysis**: Examine gender patterns across WikiHow language editions

## Project Structure

```
WikiHow Project/
├── wikihow/                    # Core API and utilities
│   ├── api.py                 # WikiHow API client
│   ├── cli.py                 # Command-line interface
│   └── ...
├── continuums/                # Output data and visualizations
│   ├── domestic/              # Domestic continuum outputs
│   ├── occupational/          # Occupational continuum outputs
│   ├── entertainment/         # Entertainment continuum outputs
│   └── policy/                # Policy continuum outputs
├── plot_spectrum.py           # Main analysis script
├── run_all.py                 # Batch runner for all continuums
├── mapped_spaces.json         # Continuum definitions
└── PROJECT_OVERVIEW.md        # This document
```

## Running the Analysis

### Single Continuum
```bash
python plot_spectrum.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Elder Abuse" "Baking" ...
```

### All Continuums
```bash
python run_all.py
```

## Contributors

This project analyzes collaborative knowledge production. The analysis itself reflects ongoing research into gender, technology, and peer production systems.

## License & Data Availability

- **Code**: Available in project repository
- **Data**: Raw CSV files exported for transparency and reproducibility
- **Visualizations**: PNG charts generated for publication and presentation

---

**Last Updated**: March 2026
**Status**: Active Development - Enhanced Contribution Analysis Phase
