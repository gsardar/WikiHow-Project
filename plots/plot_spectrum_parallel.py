"""
Enhanced parallel version of plot_spectrum_enhanced.py
Uses concurrent requests to speed up data collection significantly
"""

import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from wikihow import api
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

ARTICLE_LIMIT = 5
REVISION_LIMIT = 30
MAX_WORKERS = 5  # Number of parallel requests (be careful with rate limits!)

# WikiHow was founded in 2005
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
    """Fetch revisions for a single article (used in parallel)"""
    try:
        revs = api.get_revisions(article_title, limit=REVISION_LIMIT)
        return {'success': True, 'title': article_title, 'revisions': revs}
    except Exception as e:
        return {'success': False, 'title': article_title, 'error': str(e)}

def fetch_user_batch(users_batch: list):
    """Fetch user info for a batch (used in parallel)"""
    try:
        info = api.get_users(users_batch, fallback_to_profile=True)
        return {'success': True, 'users': info}
    except Exception as e:
        return {'success': False, 'error': str(e), 'users': {}}

def process_category_parallel(cat: str, articles: list):
    """Process a single category with parallel revision fetching"""

    print(f"\n--- Processing Category: {cat} (parallel mode) ---")

    unique_users = set()
    user_edit_counts = {}
    user_additions = {}
    user_deletions = {}
    user_temporal = {}

    # Fetch revisions for all articles in parallel
    print(f"Fetching revisions for {len(articles)} articles in parallel...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all article fetches
        future_to_article = {
            executor.submit(fetch_article_revisions, art["title"]): art
            for art in articles
        }

        # Process results as they complete
        completed = 0
        for future in as_completed(future_to_article):
            result = future.result()
            completed += 1

            if result['success']:
                revs = result['revisions']
                print(f"  [{completed}/{len(articles)}] {result['title']}: {len(revs)} revisions")

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
            else:
                print(f"  [{completed}/{len(articles)}] ERROR: {result['title']}: {result['error']}")

    elapsed = time.time() - start_time
    print(f"Fetched revisions in {elapsed:.1f}s")

    # Resolve genders in parallel batches
    users_list = list(unique_users)
    print(f"Resolving {len(users_list)} users in parallel batches...")

    user_info = {}
    batches = [users_list[i:i+50] for i in range(0, len(users_list), 50)]

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {
            executor.submit(fetch_user_batch, batch): batch
            for batch in batches
        }

        completed = 0
        for future in as_completed(future_to_batch):
            result = future.result()
            completed += 1
            if result['success']:
                user_info.update(result['users'])
                print(f"  [{completed}/{len(batches)}] Batch resolved: {len(result['users'])} users")
            else:
                print(f"  [{completed}/{len(batches)}] ERROR: {result['error']}")

    elapsed = time.time() - start_time
    print(f"Resolved genders in {elapsed:.1f}s")

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

    print(f"Result: M: {male_users} users ({male_edits} edits, +{male_additions}/-{male_deletions} bytes) | F: {female_users} users ({female_edits} edits, +{female_additions}/-{female_deletions} bytes)")

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

def process_continuum_parallel(output_name: str, title_str: str, categories: list[str]):
    """
    Parallel version - uses ThreadPoolExecutor for concurrent API requests
    MUCH faster than sequential version, but be mindful of rate limits
    """

    print(f"\n=============================================")
    print(f"Starting PARALLEL Enhanced Analysis: {title_str}")
    print(f"Max parallel workers: {MAX_WORKERS}")
    print(f"=============================================")

    overall_start = time.time()
    results = []
    temporal_data = []

    total_arts = 0
    total_edits = 0
    valid_categories = []

    for cat in categories:
        try:
            print(f"\nFetching articles for category: {cat}")
            articles = api.get_category_members(cat, limit=ARTICLE_LIMIT)

            if not articles:
                print(f"No articles found for {cat}.")
                continue

            valid_categories.append(cat)
            total_arts += len(articles)

            # Process this category with parallelism
            cat_result, male_temporal, female_temporal = process_category_parallel(cat, articles)
            results.append(cat_result)

            # Store temporal data
            for period in YEAR_PERIODS:
                period_label = period[0]
                temporal_data.append({
                    'Continuum': title_str,
                    'Category': cat,
                    'Period': period_label,
                    'Male_Edits': male_temporal.get(period_label, 0),
                    'Female_Edits': female_temporal.get(period_label, 0),
                })

            total_edits += cat_result['Male_Edits'] + cat_result['Female_Edits'] + cat_result['Unknown_Edits']

        except Exception as e:
            print(f"Error processing category {cat}: {e}")
            continue

    overall_elapsed = time.time() - overall_start
    print(f"\n{'='*60}")
    print(f"Total processing time: {overall_elapsed:.1f}s ({overall_elapsed/60:.1f} minutes)")
    print(f"{'='*60}")

    if not results:
        print(f"No data gathered for {output_name}, skipping outputs.")
        return

    # Generate outputs (same as enhanced version)
    df = pd.DataFrame(results)
    df_temporal = pd.DataFrame(temporal_data)

    df["Category"] = pd.Categorical(df["Category"], categories=valid_categories, ordered=True)
    df = df.sort_values("Category")

    out_dir_data = "data/processed"
    out_dir_viz = f"visualizations/{output_name}"
    os.makedirs(out_dir_data, exist_ok=True)
    os.makedirs(out_dir_viz, exist_ok=True)

    # Save CSVs
    csv_filename = os.path.join(out_dir_data, f"{output_name}_enhanced_parallel.csv")
    df.to_csv(csv_filename, index=False)
    print(f"Enhanced data exported to {csv_filename}")

    temporal_csv = os.path.join(out_dir_data, f"{output_name}_temporal_parallel.csv")
    df_temporal.to_csv(temporal_csv, index=False)
    print(f"Temporal data exported to {temporal_csv}")

    # Generate visualizations (reuse functions from enhanced version)
    from plot_spectrum_enhanced import generate_contribution_chart, generate_pivot_table_image

    generate_contribution_chart(df, title_str, output_name + "_parallel", out_dir_viz, total_arts, total_edits)
    generate_pivot_table_image(df_temporal, title_str, output_name + "_parallel", out_dir_viz)

def main():
    parser = argparse.ArgumentParser(description="PARALLEL enhanced gender spectrum analysis for WikiHow categories.")
    parser.add_argument("output_name", help="Prefix for output files (e.g., 'domestic')")
    parser.add_argument("title", help="Title for the charts")
    parser.add_argument("categories", nargs="+", help="Ordered list of WikiHow categories")
    parser.add_argument("--workers", type=int, default=5, help="Max parallel workers (default: 5)")

    args = parser.parse_args()

    global MAX_WORKERS
    MAX_WORKERS = args.workers

    process_continuum_parallel(args.output_name, args.title, args.categories)

if __name__ == "__main__":
    main()
