"""
Publication-quality analysis script
Uses 100% stacked bars and professional styling
"""

import os
import sys
from datetime import datetime
from wikihow import api
import argparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from viz_publication import (
    generate_100percent_stacked_bar,
    generate_publication_pivot_table,
    generate_contribution_breakdown_chart
)

ARTICLE_LIMIT = 5
REVISION_LIMIT = 30
MAX_WORKERS = 5

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

def fetch_article_revisions(article_title: str):
    """Fetch revisions for a single article"""
    try:
        revs = api.get_revisions(article_title, limit=REVISION_LIMIT)
        return {'success': True, 'title': article_title, 'revisions': revs}
    except Exception as e:
        return {'success': False, 'title': article_title, 'error': str(e)}

def fetch_user_batch(users_batch: list):
    """Fetch user info for a batch"""
    try:
        info = api.get_users(users_batch, fallback_to_profile=True)
        return {'success': True, 'users': info}
    except Exception as e:
        return {'success': False, 'error': str(e), 'users': {}}

def process_category_parallel(cat: str, articles: list):
    """Process a category with parallel requests"""

    print(f"\n--- Processing: {cat} ---")

    unique_users = set()
    user_edit_counts = {}
    user_additions = {}
    user_deletions = {}
    user_temporal = {}

    # Fetch revisions in parallel
    print(f"Fetching {len(articles)} articles...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_article = {
            executor.submit(fetch_article_revisions, art["title"]): art
            for art in articles
        }

        completed = 0
        for future in as_completed(future_to_article):
            result = future.result()
            completed += 1

            if result['success']:
                for r in result['revisions']:
                    if not r.get("anon", False):
                        user = r["user"]
                        unique_users.add(user)
                        user_edit_counts[user] = user_edit_counts.get(user, 0) + 1

                        size_delta = r.get("size_delta", 0)
                        if size_delta > 0:
                            user_additions[user] = user_additions.get(user, 0) + size_delta
                        elif size_delta < 0:
                            user_deletions[user] = user_deletions.get(user, 0) + abs(size_delta)

                        period = get_year_period(r.get("timestamp", ""))
                        if user not in user_temporal:
                            user_temporal[user] = {}
                        user_temporal[user][period] = user_temporal[user].get(period, 0) + 1

    elapsed = time.time() - start_time
    print(f"  Fetched in {elapsed:.1f}s")

    # Resolve genders in parallel
    users_list = list(unique_users)
    print(f"Resolving {len(users_list)} users...")

    user_info = {}
    batches = [users_list[i:i+50] for i in range(0, len(users_list), 50)]

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {
            executor.submit(fetch_user_batch, batch): batch
            for batch in batches
        }

        for future in as_completed(future_to_batch):
            result = future.result()
            if result['success']:
                user_info.update(result['users'])

    elapsed = time.time() - start_time
    print(f"  Resolved in {elapsed:.1f}s")

    # Aggregate by gender
    male_users = female_users = unknown_users = 0
    male_edits = female_edits = unknown_edits = 0
    male_additions = male_deletions = 0
    female_additions = female_deletions = 0
    unknown_additions = unknown_deletions = 0

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

    print(f"  M: {male_users}u, {male_edits}e | F: {female_users}u, {female_edits}e")

    return {
        'Category': cat,
        'Articles': len(articles),
        'Male_Editors': male_users,
        'Female_Editors': female_users,
        'Unknown_Editors': unknown_users,
        'Male_Edits': male_edits,
        'Female_Edits': female_edits,
        'Unknown_Edits': unknown_edits,
        'Male_Additions': male_additions,
        'Male_Deletions': male_deletions,
        'Female_Additions': female_additions,
        'Female_Deletions': female_deletions,
        'Unknown_Additions': unknown_additions,
        'Unknown_Deletions': unknown_deletions,
    }, male_temporal, female_temporal

def process_continuum_publication(output_name: str, title_str: str, categories: list[str],
                                  use_grayscale: bool = False):
    """Process continuum with publication-quality outputs"""

    print(f"\n{'='*70}")
    print(f"Publication-Quality Analysis: {title_str}")
    print(f"{'='*70}")

    overall_start = time.time()
    results = []
    temporal_data = []

    total_arts = 0
    total_edits = 0
    valid_categories = []

    for cat in categories:
        try:
            articles = api.get_category_members(cat, limit=ARTICLE_LIMIT)

            if not articles:
                print(f"No articles found for {cat}")
                continue

            valid_categories.append(cat)
            total_arts += len(articles)

            cat_result, male_temporal, female_temporal = process_category_parallel(cat, articles)
            results.append(cat_result)

            for period in YEAR_PERIODS:
                period_label = period[0]
                temporal_data.append({
                    'Continuum': title_str,
                    'Category': cat,
                    'Period': period_label,
                    'Male_Edits': male_temporal.get(period_label, 0),
                    'Female_Edits': female_temporal.get(period_label, 0),
                })

            total_edits += cat_result['Male_Edits'] + cat_result['Female_Edits']

        except Exception as e:
            print(f"Error processing {cat}: {e}")
            continue

    overall_elapsed = time.time() - overall_start
    print(f"\n{'='*70}")
    print(f"Processing completed in {overall_elapsed:.1f}s ({overall_elapsed/60:.1f} min)")
    print(f"{'='*70}")

    if not results:
        print("No data gathered, skipping outputs.")
        return

    # Create DataFrames
    df = pd.DataFrame(results)
    df_temporal = pd.DataFrame(temporal_data)

    df["Category"] = pd.Categorical(df["Category"], categories=valid_categories, ordered=True)
    df = df.sort_values("Category")

    # Create output directories
    out_dir_data = "data/processed"
    out_dir_viz = f"visualizations/{output_name}"
    os.makedirs(out_dir_data, exist_ok=True)
    os.makedirs(out_dir_viz, exist_ok=True)

    # Save CSV files
    csv_file = os.path.join(out_dir_data, f"{output_name}_publication.csv")
    df.to_csv(csv_file, index=False)
    print(f"\n[OK] Data saved: {csv_file}")

    temporal_csv = os.path.join(out_dir_data, f"{output_name}_temporal_pub.csv")
    df_temporal.to_csv(temporal_csv, index=False)
    print(f"[OK] Temporal data saved: {temporal_csv}")

    # Generate publication visualizations
    print(f"\nGenerating publication-quality visualizations...")

    # 1. 100% stacked bar chart
    generate_100percent_stacked_bar(
        df=df,
        title_str=title_str,
        output_path=os.path.join(out_dir_viz, f"{output_name}_100pct_stacked.png"),
        total_arts=total_arts,
        total_edits=total_edits,
        use_grayscale=use_grayscale,
        show_counts=True
    )

    # 2. Pivot table
    generate_publication_pivot_table(
        df_temporal=df_temporal,
        title_str=title_str,
        output_path=os.path.join(out_dir_viz, f"{output_name}_temporal_table.png"),
        show_percentages=True
    )

    # 3. Contribution breakdown
    generate_contribution_breakdown_chart(
        df=df,
        title_str=title_str,
        output_path=os.path.join(out_dir_viz, f"{output_name}_contribution_breakdown.png"),
        total_arts=total_arts,
        total_edits=total_edits,
        use_grayscale=use_grayscale
    )

    print(f"\n{'='*70}")
    print(f"[SUCCESS] Analysis complete!")
    print(f"{'='*70}")
    print(f"\nOutputs saved to:")
    print(f"  Data: {out_dir_data}/")
    print(f"  Visualizations: {out_dir_viz}/")

def main():
    parser = argparse.ArgumentParser(description="Publication-quality gender analysis")
    parser.add_argument("output_name", help="Output name (e.g., 'domestic')")
    parser.add_argument("title", help="Chart title")
    parser.add_argument("categories", nargs="+", help="Category list")
    parser.add_argument("--grayscale", action="store_true", help="Use grayscale colors")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers")

    args = parser.parse_args()

    global MAX_WORKERS
    MAX_WORKERS = args.workers

    process_continuum_publication(args.output_name, args.title, args.categories, args.grayscale)

if __name__ == "__main__":
    main()
