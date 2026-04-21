"""
Publication-quality visualization functions
- 100% stacked bar charts
- Grayscale-friendly color schemes
- Clean, professional styling suitable for academic publications
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter

# Publication-quality settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 300

# Color scheme: grayscale-friendly with patterns
# Using distinct colors that work in both color and grayscale
COLORS = {
    'male': '#2166ac',      # Blue (dark in grayscale)
    'female': '#b2182b',    # Red (medium in grayscale)
    'unknown': '#cccccc',   # Light gray
}

# Alternative: Full grayscale
COLORS_GRAYSCALE = {
    'male': '#404040',      # Dark gray
    'female': '#999999',    # Medium gray
    'unknown': '#d9d9d9',   # Light gray
}

def percentage_formatter(x, pos):
    """Format axis labels as percentages"""
    return f'{int(x)}%'

def generate_100percent_stacked_bar(df, title_str, output_path, total_arts, total_edits,
                                     use_grayscale=False, show_counts=True):
    """
    Generate 100% stacked horizontal bar chart

    Parameters:
    -----------
    df : DataFrame
        Must have columns: Category, Male_Edits, Female_Edits, Unknown_Edits,
                          Male_Editors, Female_Editors, Articles
    title_str : str
        Title for the chart
    output_path : str
        Where to save the PNG
    total_arts : int
        Total articles analyzed
    total_edits : int
        Total edits analyzed
    use_grayscale : bool
        If True, use grayscale colors only
    show_counts : bool
        If True, show absolute counts in annotations
    """

    colors = COLORS_GRAYSCALE if use_grayscale else COLORS

    # Calculate percentages
    df = df.copy()
    df['Total_Edits'] = df['Male_Edits'] + df['Female_Edits'] + df['Unknown_Edits']
    df['Male_Pct'] = 100 * df['Male_Edits'] / df['Total_Edits'].replace(0, 1)
    df['Female_Pct'] = 100 * df['Female_Edits'] / df['Total_Edits'].replace(0, 1)
    df['Unknown_Pct'] = 100 * df['Unknown_Edits'] / df['Total_Edits'].replace(0, 1)

    # Create figure
    fig_height = max(6, len(df) * 0.6 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    y_positions = np.arange(len(df))

    # Create 100% stacked bars
    bars_male = ax.barh(y_positions, df['Male_Pct'],
                        color=colors['male'],
                        label='Male',
                        edgecolor='white',
                        linewidth=0.5)

    bars_female = ax.barh(y_positions, df['Female_Pct'],
                          left=df['Male_Pct'],
                          color=colors['female'],
                          label='Female',
                          edgecolor='white',
                          linewidth=0.5)

    bars_unknown = ax.barh(y_positions, df['Unknown_Pct'],
                           left=df['Male_Pct'] + df['Female_Pct'],
                           color=colors['unknown'],
                           label='Unknown',
                           edgecolor='white',
                           linewidth=0.5,
                           alpha=0.5)

    # Set labels and title
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df['Category'])
    ax.invert_yaxis()

    ax.set_xlabel('Percentage of Edits by Gender (%)', fontweight='bold')
    ax.set_ylabel('Category', fontweight='bold')
    ax.set_title(f'{title_str}\n(N = {total_arts} articles, {total_edits} edits from identified genders)',
                 fontweight='bold', pad=15)

    # Format x-axis as percentages
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # Add percentage labels inside bars
    for i, row in df.iterrows():
        # Male percentage
        if row['Male_Pct'] > 5:  # Only show if segment is large enough
            label = f"{row['Male_Pct']:.0f}%"
            if show_counts:
                label += f"\n(n={row['Male_Edits']})"
            ax.text(row['Male_Pct']/2, i, label,
                   ha='center', va='center',
                   color='white', fontweight='bold', fontsize=8)

        # Female percentage
        if row['Female_Pct'] > 5:
            label = f"{row['Female_Pct']:.0f}%"
            if show_counts:
                label += f"\n(n={row['Female_Edits']})"
            ax.text(row['Male_Pct'] + row['Female_Pct']/2, i, label,
                   ha='center', va='center',
                   color='white', fontweight='bold', fontsize=8)

        # Add annotation on the right side with editor counts
        annotation = f"{row['Male_Editors']}M / {row['Female_Editors']}F editors"
        ax.text(102, i, annotation,
               va='center', ha='left', fontsize=8, style='italic')

    # Extend x-axis slightly for annotations
    ax.set_xlim(0, 125)

    # Add grid for readability
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, edgecolor='gray')

    # Clean up spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"[OK] Publication chart saved: {output_path}")
    plt.close()

def generate_publication_pivot_table(df_temporal, title_str, output_path,
                                      show_percentages=True):
    """
    Generate publication-quality pivot table as PNG

    Parameters:
    -----------
    df_temporal : DataFrame
        Must have columns: Category, Period, Male_Edits, Female_Edits
    title_str : str
        Title for the table
    output_path : str
        Where to save the PNG
    show_percentages : bool
        If True, show percentages alongside counts
    """

    if df_temporal.empty:
        print("No temporal data to generate pivot table")
        return

    # Create pivot
    pivot = df_temporal.pivot_table(
        values=['Male_Edits', 'Female_Edits'],
        index='Category',
        columns='Period',
        aggfunc='sum',
        fill_value=0
    )

    if pivot.empty:
        print("Pivot table is empty, skipping")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(12, max(6, len(pivot) * 0.5 + 1)))
    ax.axis('tight')
    ax.axis('off')

    # Prepare table data
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

                    if show_percentages:
                        cell_text = f"M: {male_pct}% (n={male_count})\nF: {female_pct}% (n={female_count})"
                    else:
                        cell_text = f"M: {male_count}\nF: {female_count}"
                else:
                    cell_text = "—"
            except:
                cell_text = "—"
            row.append(cell_text)
        table_data.append(row)

    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15] + [0.17] * len(periods))

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2.2)

    # Style header row
    for i in range(len(header_row)):
        cell = table[(0, i)]
        cell.set_facecolor('#404040')
        cell.set_text_props(weight='bold', color='white', fontsize=9)
        cell.set_edgecolor('white')

    # Style category column
    for i in range(1, len(table_data)):
        cell = table[(i, 0)]
        cell.set_facecolor('#e0e0e0')
        cell.set_text_props(weight='bold', fontsize=8)
        cell.set_edgecolor('white')

    # Style data cells
    for i in range(1, len(table_data)):
        for j in range(1, len(header_row)):
            cell = table[(i, j)]
            cell.set_edgecolor('#cccccc')

    plt.title(f'{title_str}\n(Edit distribution by gender across time periods)',
              fontweight='bold', fontsize=11, pad=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"[OK] Publication pivot table saved: {output_path}")
    plt.close()

def generate_contribution_breakdown_chart(df, title_str, output_path, total_arts, total_edits,
                                          use_grayscale=False):
    """
    Generate chart showing contribution breakdown (additions vs deletions)
    100% stacked bars showing proportion of additions

    Parameters:
    -----------
    df : DataFrame
        Must have: Category, Male_Additions, Male_Deletions, Female_Additions, Female_Deletions
    """

    colors = COLORS_GRAYSCALE if use_grayscale else COLORS

    # Calculate net contributions and percentages
    df = df.copy()
    df['Male_Total'] = df['Male_Additions'] + df['Male_Deletions']
    df['Female_Total'] = df['Female_Additions'] + df['Female_Deletions']
    df['Total_Contribution'] = df['Male_Total'] + df['Female_Total']

    df['Male_Add_Pct'] = 100 * df['Male_Additions'] / df['Total_Contribution'].replace(0, 1)
    df['Male_Del_Pct'] = 100 * df['Male_Deletions'] / df['Total_Contribution'].replace(0, 1)
    df['Female_Add_Pct'] = 100 * df['Female_Additions'] / df['Total_Contribution'].replace(0, 1)
    df['Female_Del_Pct'] = 100 * df['Female_Deletions'] / df['Total_Contribution'].replace(0, 1)

    # Create figure
    fig_height = max(6, len(df) * 0.6 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    y_positions = np.arange(len(df))

    # Stacked: Male additions, Male deletions, Female additions, Female deletions
    bar1 = ax.barh(y_positions, df['Male_Add_Pct'],
                   color=colors['male'], label='Male (additions)',
                   edgecolor='white', linewidth=0.5)

    bar2 = ax.barh(y_positions, df['Male_Del_Pct'],
                   left=df['Male_Add_Pct'],
                   color=colors['male'], label='Male (deletions)',
                   edgecolor='white', linewidth=0.5, alpha=0.5, hatch='//')

    bar3 = ax.barh(y_positions, df['Female_Add_Pct'],
                   left=df['Male_Add_Pct'] + df['Male_Del_Pct'],
                   color=colors['female'], label='Female (additions)',
                   edgecolor='white', linewidth=0.5)

    bar4 = ax.barh(y_positions, df['Female_Del_Pct'],
                   left=df['Male_Add_Pct'] + df['Male_Del_Pct'] + df['Female_Add_Pct'],
                   color=colors['female'], label='Female (deletions)',
                   edgecolor='white', linewidth=0.5, alpha=0.5, hatch='//')

    # Labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df['Category'])
    ax.invert_yaxis()

    ax.set_xlabel('Percentage of Total Contribution (%)', fontweight='bold')
    ax.set_ylabel('Category', fontweight='bold')
    ax.set_title(f'{title_str}\n(Contribution breakdown: additions vs. deletions by gender)',
                 fontweight='bold', pad=15)

    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # Add annotations
    for i, row in df.iterrows():
        # Summary annotation on right
        male_net = row['Male_Additions'] - row['Male_Deletions']
        female_net = row['Female_Additions'] - row['Female_Deletions']
        annotation = f"M: +{row['Male_Additions']}/−{row['Male_Deletions']} | F: +{row['Female_Additions']}/−{row['Female_Deletions']}"
        ax.text(102, i, annotation, va='center', ha='left', fontsize=7, family='monospace')

    ax.set_xlim(0, 160)

    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, edgecolor='gray', ncol=2)

    # Clean spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"[OK] Contribution breakdown chart saved: {output_path}")
    plt.close()
