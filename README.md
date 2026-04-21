# WikiHow Gender Analysis

Research project analyzing gender-based participation patterns in WikiHow article editing across different topical continuums.

## Project Structure

```
WikiHow Project/
├── wikihow/          # Core library for data processing
├── deepseek/         # AI bridge for semantic analysis
├── scripts/          # Operational scripts
├── data/             # Selected datasets
└── run_all.py        # Main execution entry
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the full analysis pipeline:
   ```bash
   python run_all.py --publication
   ```

## Key Metrics

The analysis tracks the following metrics across various continuums:
- Editor gender distribution
- Contribution volume (bytes added/removed)
- Temporal trends (2005-present)

## Data Usage

The project utilizes authentic data collected from the WikiHow platform. All analysis is performed using high-fidelity historical metadata to ensure research integrity.

---
*Research project repository.*
