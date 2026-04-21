"""
Test publication-quality visualizations
"""

import pandas as pd
import os
from viz_publication import (
    generate_100percent_stacked_bar,
    generate_publication_pivot_table,
    generate_contribution_breakdown_chart
)

def create_test_data():
    """Create sample data"""
    data = {
        'Category': ['Baby Toys', 'Baking', 'Gardening', 'Plumbing'],
        'Articles': [5, 5, 5, 5],
        'Male_Editors': [15, 11, 8, 16],
        'Female_Editors': [7, 10, 6, 3],
        'Unknown_Editors': [20, 35, 18, 20],
        'Male_Edits': [21, 23, 18, 28],
        'Female_Edits': [14, 11, 12, 5],
        'Unknown_Edits': [52, 78, 45, 47],
        'Male_Additions': [3450, 4200, 2800, 5600],
        'Male_Deletions': [120, 340, 150, 89],
        'Female_Additions': [2800, 3100, 2100, 890],
        'Female_Deletions': [95, 210, 80, 45],
        'Unknown_Additions': [8900, 12000, 7200, 7800],
        'Unknown_Deletions': [450, 890, 380, 320],
    }
    return pd.DataFrame(data)

def create_test_temporal_data():
    """Create sample temporal data"""
    data = []
    categories = ['Baby Toys', 'Baking', 'Gardening', 'Plumbing']
    periods = ['2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2026']

    for cat in categories:
        for period in periods:
            male_base = hash(cat + period + 'male') % 25 + 5
            female_base = hash(cat + period + 'female') % 25 + 5
            data.append({
                'Continuum': 'Test Domestic',
                'Category': cat,
                'Period': period,
                'Male_Edits': male_base,
                'Female_Edits': female_base,
            })

    return pd.DataFrame(data)

def main():
    print("\n" + "="*70)
    print("Testing Publication-Quality Visualizations")
    print("="*70)

    # Create output directory
    test_dir = "visualizations/test_publication"
    os.makedirs(test_dir, exist_ok=True)

    # Generate test data
    print("\n1. Creating test data...")
    df = create_test_data()
    df_temporal = create_test_temporal_data()
    print(f"   [OK] Created data for {len(df)} categories")

    # Test 100% stacked bar (color)
    print("\n2. Generating 100% stacked bar chart (color)...")
    generate_100percent_stacked_bar(
        df=df,
        title_str="Gender Distribution Across Domestic Task Categories",
        output_path=f"{test_dir}/test_100pct_stacked_color.png",
        total_arts=20,
        total_edits=87,
        use_grayscale=False,
        show_counts=True
    )

    # Test 100% stacked bar (grayscale)
    print("\n3. Generating 100% stacked bar chart (grayscale)...")
    generate_100percent_stacked_bar(
        df=df,
        title_str="Gender Distribution Across Domestic Task Categories",
        output_path=f"{test_dir}/test_100pct_stacked_grayscale.png",
        total_arts=20,
        total_edits=87,
        use_grayscale=True,
        show_counts=True
    )

    # Test pivot table
    print("\n4. Generating publication pivot table...")
    generate_publication_pivot_table(
        df_temporal=df_temporal,
        title_str="Temporal Analysis: Gender Participation Over Time",
        output_path=f"{test_dir}/test_pivot_publication.png",
        show_percentages=True
    )

    # Test contribution breakdown
    print("\n5. Generating contribution breakdown chart...")
    generate_contribution_breakdown_chart(
        df=df,
        title_str="Contribution Breakdown by Gender",
        output_path=f"{test_dir}/test_contribution_breakdown.png",
        total_arts=20,
        total_edits=87,
        use_grayscale=False
    )

    print("\n" + "="*70)
    print("[SUCCESS] All publication visualizations generated!")
    print("="*70)
    print("\nGenerated files:")
    print(f"  - {test_dir}/test_100pct_stacked_color.png")
    print(f"  - {test_dir}/test_100pct_stacked_grayscale.png")
    print(f"  - {test_dir}/test_pivot_publication.png")
    print(f"  - {test_dir}/test_contribution_breakdown.png")
    print("\nView these files to see publication-quality output.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
