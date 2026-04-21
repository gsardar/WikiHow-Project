import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from datetime import datetime
from wikihow import api
import argparse

ARTICLE_LIMIT = 5
REVISION_LIMIT = 30

# WikiHow was founded in 2005, so we'll create 5-year periods from 2005
YEAR_PERIODS = [
    ("2005-2009", 2005, 2009),
    ("2010-2014", 2010, 2014),
    ("2015-2019", 2015, 2019),
    ("2020-2024", 2020, 2024),
    ("2025-2026", 2025, 2026),
]

def get_year_period(timestamp_str: str) -> str:
    """Convert timestamp to 5-year period label"""
    try:
        year = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).year
        for period_label, start_year, end_year in YEAR_PERIODS:
            if start_year <= year <= end_year:
                return period_label
        return "Unknown"
    except:
        return "Unknown"

def process_continuum_enhanced(output_name: str, title_str: str, categories: list[str]):
    """
    Enhanced processing that tracks:
    - Byte additions vs deletions by gender
    - Temporal distribution across 5-year periods
    - Per-category and per-period breakdowns
    """

    print(f"\n=============================================")
    print(f"Starting Enhanced Analysis: {title_str}")
    print(f"=============================================")

    results = []
    temporal_data = []  # For year-wise analysis

    total_arts = 0
    total_edits = 0

    valid_categories = []

    for cat in categories:
        print(f"\n--- Processing Category: {cat} ---")
        try:
            articles = api.get_category_members(cat, limit=ARTICLE_LIMIT)
        except Exception as e:
            print(f"Error fetching articles for {cat}: {e}")
            continue

        if not articles:
            print(f"No articles found for {cat}.")
            continue

        valid_categories.append(cat)
        total_arts += len(articles)

        # Initialize tracking dictionaries
        unique_users = set()
        user_edit_counts = {}
        user_additions = {}  # Track positive byte changes
        user_deletions = {}  # Track negative byte changes (absolute value)
        user_temporal = {}   # Track edits by time period

        for art in articles:
            title = art["title"]
            try:
                revs = api.get_revisions(title, limit=REVISION_LIMIT)
                for r in revs:
                    if not r.get("anon", False):
                        user = r["user"]
                        unique_users.add(user)
                        user_edit_counts[user] = user_edit_counts.get(user, 0) + 1

                        # Track size delta
                        size_delta = r.get("size_delta", 0)
                        if size_delta > 0:
                            user_additions[user] = user_additions.get(user, 0) + size_delta
                        elif size_delta < 0:
                            user_deletions[user] = user_deletions.get(user, 0) + abs(size_delta)

                        # Track temporal period
                        period = get_year_period(r.get("timestamp", ""))
                        if user not in user_temporal:
                            user_temporal[user] = {}
                        user_temporal[user][period] = user_temporal[user].get(period, 0) + 1

            except Exception as e:
                print(f"Error fetching revs for {title}: {e}")

        # Resolve genders
        users_list = list(unique_users)
        user_info = {}
        print(f"Resolving {len(users_list)} users for {cat}...")

        for i in range(0, len(users_list), 50):
            batch = users_list[i:i+50]
            try:
                info = api.get_users(batch, fallback_to_profile=True)
                user_info.update(info)
            except Exception as e:
                print(f"Error fetching user specs: {e}")

        # Aggregate by gender
        male_users = 0
        female_users = 0
        unknown_users = 0

        male_edits = 0
        female_edits = 0
        unknown_edits = 0

        male_additions = 0
        male_deletions = 0
        female_additions = 0
        female_deletions = 0
        unknown_additions = 0
        unknown_deletions = 0

        # Temporal breakdown by gender
        male_temporal = {p[0]: 0 for p in YEAR_PERIODS}
        female_temporal = {p[0]: 0 for p in YEAR_PERIODS}

        for u in users_list:
            g = user_info.get(u, {}).get("gender", "unknown")
            edits = user_edit_counts.get(u, 0)
            additions = user_additions.get(u, 0)
            deletions = user_deletions.get(u, 0)

            if g == "male":
                male_users += 1
                male_edits += edits
                male_additions += additions
                male_deletions += deletions
                for period, count in user_temporal.get(u, {}).items():
                    if period in male_temporal:
                        male_temporal[period] += count
            elif g == "female":
                female_users += 1
                female_edits += edits
                female_additions += additions
                female_deletions += deletions
                for period, count in user_temporal.get(u, {}).items():
                    if period in female_temporal:
                        female_temporal[period] += count
            else:
                unknown_users += 1
                unknown_edits += edits
                unknown_additions += additions
                unknown_deletions += deletions

        print(f"Result: M: {male_users} users ({male_edits} edits, +{male_additions}/-{male_deletions} bytes) | F: {female_users} users ({female_edits} edits, +{female_additions}/-{female_deletions} bytes)")

        cat_total_edits = male_edits + female_edits + unknown_edits
        total_edits += cat_total_edits

        results.append({
            "Category": cat,
            "Articles": len(articles),
            "Male_Editors": male_users,
            "Female_Editors": female_users,
            "Unknown_Editors": unknown_users,
            "Male_Edits": male_edits,
            "Female_Edits": female_edits,
            "Unknown_Edits": unknown_edits,
            "Male_Additions": male_additions,
            "Male_Deletions": male_deletions,
            "Female_Additions": female_additions,
            "Female_Deletions": female_deletions,
            "Unknown_Additions": unknown_additions,
            "Unknown_Deletions": unknown_deletions,
        })

        # Store temporal data for pivot table
        for period in YEAR_PERIODS:
            period_label = period[0]
            temporal_data.append({
                "Continuum": title_str,
                "Category": cat,
                "Period": period_label,
                "Male_Edits": male_temporal.get(period_label, 0),
                "Female_Edits": female_temporal.get(period_label, 0),
            })

    if not results:
        print(f"No data gathered for {output_name}, skipping chart.")
        return

    # Generate outputs
    df = pd.DataFrame(results)
    df_temporal = pd.DataFrame(temporal_data)

    # Ensure categories are in the original order
    df["Category"] = pd.Categorical(df["Category"], categories=valid_categories, ordered=True)
    df = df.sort_values("Category")

    out_dir_data = "data/processed"
    out_dir_viz = f"visualizations/{output_name}"
    os.makedirs(out_dir_data, exist_ok=True)
    os.makedirs(out_dir_viz, exist_ok=True)

    # Save raw data to CSV
    csv_filename = os.path.join(out_dir_data, f"{output_name}_enhanced.csv")
    df.to_csv(csv_filename, index=False)
    print(f"Enhanced data exported to {csv_filename}")

    # Save temporal data
    temporal_csv = os.path.join(out_dir_data, f"{output_name}_temporal.csv")
    df_temporal.to_csv(temporal_csv, index=False)
    print(f"Temporal data exported to {temporal_csv}")

    # Generate visualizations
    generate_contribution_chart(df, title_str, output_name, out_dir_viz, total_arts, total_edits)
    generate_pivot_table_image(df_temporal, title_str, output_name, out_dir_viz)

def generate_contribution_chart(df, title_str, output_name, out_dir, total_arts, total_edits):
    """Generate horizontal bar chart with [+add/-remove] breakdown"""

    fig_height = max(8, len(df) * 1.0 + 2)
    fig, ax = plt.subplots(figsize=(16, fig_height))

    y_positions = np.arange(len(df))

    # Create stacked bars showing additions
    # Male additions (blue)
    ax.barh(y_positions, df["Male_Additions"], color="#4C72B0", label="Male Additions (+)", edgecolor="white")

    # Female contributions (start after male)
    ax.barh(y_positions, df["Female_Additions"], left=df["Male_Additions"],
            color="#C44E52", label="Female Additions (+)", edgecolor="white")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(df["Category"])
    ax.invert_yaxis()

    ax.set_xlabel(f"Contribution Volume (bytes added)\n(Total Articles: {total_arts} | Total Edits: {total_edits})", fontsize=12)
    ax.set_ylabel("Continuum (Expected Female → Expected Male)", fontsize=12)
    ax.set_title(f"Gender Stratification: {title_str}\n(Contribution volume by known genders)", fontsize=14, pad=20)

    # Add annotations with detailed stats
    for i, row in df.iterrows():
        cat = row["Category"]
        m_add = row["Male_Additions"]
        m_del = row["Male_Deletions"]
        f_add = row["Female_Additions"]
        f_del = row["Female_Deletions"]
        m_users = row["Male_Editors"]
        f_users = row["Female_Editors"]
        m_edits = row["Male_Edits"]
        f_edits = row["Female_Edits"]
        arts = row["Articles"]

        total_contribution = m_add + f_add

        # Right-side annotation
        annotation = f"   {arts} arts | M: {m_users}u, {m_edits}e [+{m_add}/-{m_del}] | F: {f_users}u, {f_edits}e [+{f_add}/-{f_del}]"
        ax.text(total_contribution, i, annotation, va='center', ha='left', fontsize=9, color='#333333')

        # Inside bars - show addition counts
        if m_add > 100:
            ax.text(m_add/2, i, f"+{m_add}", ha='center', va='center', color='white', fontweight='bold', fontsize=9)
        if f_add > 100:
            ax.text(m_add + f_add/2, i, f"+{f_add}", ha='center', va='center', color='white', fontweight='bold', fontsize=9)

    # Extend x-axis for annotations
    xmax = ax.get_xlim()[1]
    ax.set_xlim(right=xmax * 1.45)

    ax.legend(loc="upper right")

    plt.tight_layout()
    filename = os.path.join(out_dir, f"{output_name}_contributions.png")
    plt.savefig(filename, dpi=300, facecolor='white')
    print(f"Contribution chart saved as {filename}")
    plt.close()

def generate_pivot_table_image(df_temporal, title_str, output_name, out_dir):
    """Generate a pivot table as PNG showing year-wise gender distribution"""

    if df_temporal.empty:
        print("No temporal data to generate pivot table")
        return

    # Create pivot: rows = categories, columns = periods, cells = M/F split
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
    fig, ax = plt.subplots(figsize=(14, max(8, len(pivot) * 0.6)))
    ax.axis('tight')
    ax.axis('off')

    # Prepare table data
    categories = pivot.index.tolist()
    periods = [p[0] for p in YEAR_PERIODS if p[0] in pivot.columns.get_level_values(1)]

    # Build table cell data
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

    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15] + [0.17] * len(periods))

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)

    # Style header row
    for i in range(len(header_row)):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')

    # Style category column
    for i in range(1, len(table_data)):
        cell = table[(i, 0)]
        cell.set_facecolor('#E7E6E6')
        cell.set_text_props(weight='bold')

    plt.title(f"Temporal Analysis: {title_str}\n(Edit counts by gender across 5-year periods)",
              fontsize=14, pad=20, weight='bold')

    plt.tight_layout()
    filename = os.path.join(out_dir, f"{output_name}_pivot_table.png")
    plt.savefig(filename, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"Pivot table saved as {filename}")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Enhanced gender spectrum analysis for WikiHow categories.")
    parser.add_argument("output_name", help="Prefix for output files (e.g., 'domestic')")
    parser.add_argument("title", help="Title for the charts")
    parser.add_argument("categories", nargs="+", help="Ordered list of WikiHow categories")

    args = parser.parse_args()
    process_continuum_enhanced(args.output_name, args.title, args.categories)

if __name__ == "__main__":
    main()
