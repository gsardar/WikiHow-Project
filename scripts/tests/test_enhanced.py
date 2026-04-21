"""
Quick test of enhanced analysis using sample data
This avoids API calls for faster testing
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Simulate what the enhanced script would produce
def create_test_data():
    """Create sample data mimicking the enhanced analysis output"""

    data = {
        'Category': ['Baby Toys', 'Baking', 'Plumbing'],
        'Articles': [5, 5, 5],
        'Male_Editors': [15, 11, 8],
        'Female_Editors': [7, 10, 3],
        'Unknown_Editors': [20, 35, 20],
        'Male_Edits': [21, 23, 16],
        'Female_Edits': [14, 11, 5],
        'Unknown_Edits': [52, 78, 47],
        'Male_Additions': [3450, 4200, 5600],
        'Male_Deletions': [120, 340, 89],
        'Female_Additions': [2800, 3100, 890],
        'Female_Deletions': [95, 210, 45],
        'Unknown_Additions': [8900, 12000, 7800],
        'Unknown_Deletions': [450, 890, 320],
    }

    return pd.DataFrame(data)

def create_test_temporal_data():
    """Create sample temporal data"""

    data = []
    categories = ['Baby Toys', 'Baking', 'Plumbing']
    # All 5 periods to match the real analysis
    periods = ['2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2026']

    for cat in categories:
        for period in periods:
            # Simulate varying distributions
            male_base = hash(cat + period + 'male') % 20
            female_base = hash(cat + period + 'female') % 20
            data.append({
                'Continuum': 'Test Domestic',
                'Category': cat,
                'Period': period,
                'Male_Edits': male_base,
                'Female_Edits': female_base,
            })

    return pd.DataFrame(data)

def generate_test_contribution_chart(df, output_path):
    """Test the contribution chart generation"""

    print("Generating contribution chart...")

    fig, ax = plt.subplots(figsize=(14, 6))
    y_positions = np.arange(len(df))

    # Stacked bars
    ax.barh(y_positions, df["Male_Additions"], color="#4C72B0",
            label="Male Additions (+)", edgecolor="white")
    ax.barh(y_positions, df["Female_Additions"], left=df["Male_Additions"],
            color="#C44E52", label="Female Additions (+)", edgecolor="white")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(df["Category"])
    ax.invert_yaxis()

    ax.set_xlabel("Contribution Volume (bytes added)", fontsize=12)
    ax.set_ylabel("Continuum (Expected Female → Expected Male)", fontsize=12)
    ax.set_title("TEST: Gender Stratification - Contribution Volume", fontsize=14, pad=20)

    # Annotations
    for i, row in df.iterrows():
        total = row["Male_Additions"] + row["Female_Additions"]
        annotation = f"   {row['Articles']} arts | M: {row['Male_Editors']}u, {row['Male_Edits']}e [+{row['Male_Additions']}/-{row['Male_Deletions']}] | F: {row['Female_Editors']}u, {row['Female_Edits']}e [+{row['Female_Additions']}/-{row['Female_Deletions']}]"
        ax.text(total, i, annotation, va='center', ha='left', fontsize=9, color='#333333')

        # Bar labels
        if row["Male_Additions"] > 100:
            ax.text(row["Male_Additions"]/2, i, f"+{row['Male_Additions']}",
                   ha='center', va='center', color='white', fontweight='bold', fontsize=9)
        if row["Female_Additions"] > 100:
            ax.text(row["Male_Additions"] + row["Female_Additions"]/2, i, f"+{row['Female_Additions']}",
                   ha='center', va='center', color='white', fontweight='bold', fontsize=9)

    xmax = ax.get_xlim()[1]
    ax.set_xlim(right=xmax * 1.45)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white')
    print(f"[OK] Chart saved: {output_path}")
    plt.close()

def generate_test_pivot_table(df_temporal, output_path):
    """Test the pivot table generation"""

    print("Generating pivot table...")

    pivot = df_temporal.pivot_table(
        values=['Male_Edits', 'Female_Edits'],
        index='Category',
        columns='Period',
        aggfunc='sum',
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')

    categories = pivot.index.tolist()
    periods = df_temporal['Period'].unique().tolist()

    # Build table
    table_data = []
    header_row = ["Category"] + periods
    table_data.append(header_row)

    for cat in categories:
        row = [cat]
        for period in periods:
            try:
                male_count = int(pivot.loc[cat, ('Male_Edits', period)])
                female_count = int(pivot.loc[cat, ('Female_Edits', period)])
                total = male_count + female_count
                if total > 0:
                    male_pct = int(100 * male_count / total)
                    female_pct = int(100 * female_count / total)
                    cell_text = f"M:{male_count}({male_pct}%)\nF:{female_count}({female_pct}%)"
                else:
                    cell_text = "—"
            except:
                cell_text = "—"
            row.append(cell_text)
        table_data.append(row)

    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15] + [0.21] * len(periods))

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)

    # Style
    for i in range(len(header_row)):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')

    for i in range(1, len(table_data)):
        cell = table[(i, 0)]
        cell.set_facecolor('#E7E6E6')
        cell.set_text_props(weight='bold')

    plt.title("TEST: Temporal Analysis (5-year periods)", fontsize=14, pad=20, weight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"[OK] Pivot table saved: {output_path}")
    plt.close()

def main():
    print("\n" + "="*60)
    print("Testing Enhanced Analysis Visualization Functions")
    print("="*60)

    # Create output directory
    test_dir = "visualizations/test"
    os.makedirs(test_dir, exist_ok=True)

    # Generate test data
    print("\n1. Creating test data...")
    df = create_test_data()
    df_temporal = create_test_temporal_data()

    print(f"   [OK] Created data for {len(df)} categories")
    print(f"   [OK] Created temporal data for {len(df_temporal)} category-period combinations")

    # Save test CSVs
    csv_dir = "data/processed"
    os.makedirs(csv_dir, exist_ok=True)

    df.to_csv(f"{csv_dir}/test_enhanced.csv", index=False)
    df_temporal.to_csv(f"{csv_dir}/test_temporal.csv", index=False)
    print(f"   [OK] Saved test CSVs to {csv_dir}/")

    # Test visualizations
    print("\n2. Testing contribution chart generation...")
    generate_test_contribution_chart(df, f"{test_dir}/test_contributions.png")

    print("\n3. Testing pivot table generation...")
    generate_test_pivot_table(df_temporal, f"{test_dir}/test_pivot_table.png")

    print("\n" + "="*60)
    print("[SUCCESS] All tests passed!")
    print("="*60)
    print("\nGenerated files:")
    print(f"  - {csv_dir}/test_enhanced.csv")
    print(f"  - {csv_dir}/test_temporal.csv")
    print(f"  - {test_dir}/test_contributions.png")
    print(f"  - {test_dir}/test_pivot_table.png")
    print("\nYou can view the PNG files to verify the output format.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
