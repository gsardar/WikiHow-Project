import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import csv
from wikihow import api
import argparse

ARTICLE_LIMIT = 5 # Default
REVISION_LIMIT = 30

def process_continuum(output_name: str, title_str: str, categories: list[str], limit: int = None):
    article_limit = limit if limit is not None else ARTICLE_LIMIT
    
    print(f"\n=============================================")
    print(f"Starting Analysis: {title_str} (Limit: {article_limit})")
    print(f"=============================================")
    
    results = []
    
    total_arts = 0
    total_edits = 0

    valid_categories = []

    for cat in categories:
        print(f"\n--- Processing Category: {cat} ---")
        try:
            articles = api.get_category_members(cat, limit=article_limit)
        except Exception as e:
            print(f"Error fetching articles for {cat}: {e}")
            continue

        if not articles:
            print(f"No articles found for {cat}.")
            continue
            
        valid_categories.append(cat)
        total_arts += len(articles)

        unique_users = set()
        user_edit_counts = {}
        
        for art in articles:
            title = art["title"]
            try:
                revs = api.get_revisions(title, limit=REVISION_LIMIT)
                for r in revs:
                    if not r.get("anon", False):
                        user = r["user"]
                        unique_users.add(user)
                        user_edit_counts[user] = user_edit_counts.get(user, 0) + 1
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

        male_users = 0
        female_users = 0
        unknown_users = 0
        
        male_edits = 0
        female_edits = 0
        unknown_edits = 0
        
        for u in users_list:
            g = user_info.get(u, {}).get("gender", "unknown")
            edits = user_edit_counts.get(u, 0)
            
            if g == "male":
                male_users += 1
                male_edits += edits
            elif g == "female":
                female_users += 1
                female_edits += edits
            else:
                unknown_users += 1
                unknown_edits += edits

        print(f"Result: M: {male_users} users ({male_edits} edits) | F: {female_users} users ({female_edits} edits) | U: {unknown_users} users")

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
            "Unknown_Edits": unknown_edits
        })

    if not results:
        print(f"No data gathered for {output_name}, skipping chart.")
        return

    # Generate Chart
    df = pd.DataFrame(results)
    
    # Ensure categories are in the original order but only include those we actually found data for
    df["Category"] = pd.Categorical(df["Category"], categories=valid_categories, ordered=True)
    df = df.sort_values("Category")

    out_dir_data = "data/processed"
    out_dir_viz = f"visualizations/{output_name}"
    os.makedirs(out_dir_data, exist_ok=True)
    os.makedirs(out_dir_viz, exist_ok=True)

    # Save raw data to CSV for further research
    csv_filename = os.path.join(out_dir_data, f"spectrum_{output_name}.csv")
    df.to_csv(csv_filename, index=False)
    print(f"Raw data exported to {csv_filename}")

    # Use adaptive height depending on the number of categories
    fig_height = max(6, len(df) * 0.8 + 2)
    plt.figure(figsize=(14, fig_height))
    
    # Horizontal bars
    bars_male = plt.barh(df["Category"], df["Male_Edits"], color="#4C72B0", label="Male Edits", edgecolor="white")
    bars_female = plt.barh(df["Category"], df["Female_Edits"], left=df["Male_Edits"], color="#C44E52", label="Female Edits", edgecolor="white")

    plt.title(f"Gender Stratification: {title_str}\n(Total edit volume from known genders in sample)", fontsize=14, pad=20)
    plt.xlabel(f"Number of Edits\n(Total Articles Analyzed: {total_arts} | Total Edits Analyzed: {total_edits})", fontsize=12)
    plt.ylabel("Continuum (Expected Female → Expected Male)", fontsize=12)
    
    # Invert Y-axis so the first category is at the top
    plt.gca().invert_yaxis()
    
    # Add count labels on bars
    for i, (cat_name, m_edits, f_edits, m_users, f_users, arts_count) in enumerate(zip(df["Category"], df["Male_Edits"], df["Female_Edits"], df["Male_Editors"], df["Female_Editors"], df["Articles"])):
        total_labeled_edits = m_edits + f_edits
        
        # Tail annotation
        annotation = f"   {arts_count} arts | M: {m_users} users, F: {f_users} users | {total_labeled_edits} labeled edits"
        plt.text(total_labeled_edits, i, annotation, va='center', ha='left', fontsize=10, color='#333333')
        
        # Inside the bars
        if m_edits > 0:
            plt.text(m_edits/2, i, f"{m_edits}", ha='center', va='center', color='white', fontweight='bold')
        if f_edits > 0:
            plt.text(m_edits + f_edits/2, i, f"{f_edits}", ha='center', va='center', color='white', fontweight='bold')

    # Add padding to the right so annotations don't cut off
    xmax = plt.gca().get_xlim()[1]
    plt.gca().set_xlim(right=xmax * 1.35)

    plt.legend(loc="upper right")

    plt.tight_layout()
    filename = os.path.join(out_dir_viz, f"spectrum_{output_name}.png")
    plt.savefig(filename, dpi=300, facecolor='white')
    print(f"Graph saved as {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate a gender spectrum bar chart for WikiHow categories.")
    parser.add_argument("output_name", help="Prefix for the output PNG file (e.g., 'domestic' becomes 'spectrum_domestic.png')")
    parser.add_argument("title", help="Title for the chart")
    parser.add_argument("categories", nargs="+", help="Ordered list of WikiHow categories to plot on the X-axis (from female-coded to male-coded, or vice versa)")
    parser.add_argument("--limit", type=int, default=None, help="Overide article limit per category")

    args = parser.parse_args()
    process_continuum(args.output_name, args.title, args.categories, limit=args.limit)

if __name__ == "__main__":
    main()
