
"""
WikiHow Contribution Statistics Visualizer
===========================================
Reads all completed JSON files from the contributions directory
and generates a suite of analysis charts:
  1. Edit Type Distribution (pie chart)
  2. Vandalism vs Genuine vs Gatekeeping (stacked bar by year)
  3. Most Active Admins / Reverters (bar chart)
  4. Revert Timeline (line chart over years)
  5. Minor Edit Rate (is_minor over time)
  6. Expert vs Non-Expert Contribution Ratio

Usage:
    python scripts/visualize_contributions.py
    python scripts/visualize_contributions.py --article Lose-Weight
"""

import os
import sys
import json
import re
import argparse
import glob
from collections import defaultdict
from datetime import datetime

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("Installing matplotlib...")
    os.system(f"{sys.executable} -m pip install matplotlib numpy")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONT_DIR  = os.path.join(BASE_DIR, "data", "contributions", "continuum")
OUT_DIR   = os.path.join(BASE_DIR, "data", "visualizations", "stats")
os.makedirs(OUT_DIR, exist_ok=True)

GATEKEEPING_PAT = re.compile(r"RCP reverted|reverted edits by|undid revision|rollback|rv ", re.IGNORECASE)
VANDALISM_PAT   = re.compile(r"vand|spam|test|gibberish|profanity|offensive|blank|troll|lol|haha|fuck|shit|crap", re.IGNORECASE)
GENDER_PAT      = re.compile(r"npov|sexist|gender|woman|women|female|feminism|her\b|pronouns|gendered", re.IGNORECASE)

PALETTE = {
    "GENUINE":      "#4CAF50",
    "VANDALISM":    "#F44336",
    "GATEKEEPING":  "#FF9800",
    "GENDER":       "#9C27B0",
    "SPAM":         "#F44336",
    "OTHER":        "#9E9E9E",
}

def parse_year(ts: str) -> int | None:
    m = re.search(r"\b(200[5-9]|20[12]\d)\b", ts)
    return int(m.group(1)) if m else None

def classify(rev: dict) -> str:
    summary = rev.get("summary", "")
    if VANDALISM_PAT.search(summary): return "VANDALISM"
    if GENDER_PAT.search(summary) and GATEKEEPING_PAT.search(summary): return "GENDER"
    if GATEKEEPING_PAT.search(summary): return "GATEKEEPING"
    if rev.get("contribution_type") == "revert": return "GATEKEEPING"
    if rev.get("status") == "reverted": return "REJECTED"
    return "GENUINE"

def load_articles(article_filter=None):
    all_revisions = []
    files = glob.glob(os.path.join(CONT_DIR, "**", "*.json"), recursive=True)
    files = [f for f in files if not f.endswith(".bak")]
    for fpath in files:
        title = os.path.basename(fpath).replace(".json","")
        if article_filter and title.lower() != article_filter.lower():
            continue
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            for rev in data.get("revisions", []):
                rev["_article"] = title
                rev["_continuum"] = data.get("continuum", "unknown")
                rev["_subcategory"] = data.get("subcategory", "unknown")
                all_revisions.append(rev)
        except:
            pass
    return all_revisions

def chart1_edit_types(revisions, tag):
    counts = defaultdict(int)
    for r in revisions:
        counts[r.get("contribution_type", "unknown")] += 1
    labels = list(counts.keys())
    values = [counts[l] for l in labels]
    colors = plt.cm.Set3.colors[:len(labels)]

    fig, ax = plt.subplots(figsize=(9,7))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    ax.set_title(f"Edit Type Distribution\n({tag})", fontsize=15, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, f"{tag}_edit_types.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [SAVED] {path}")

def chart2_yearly_stacked(revisions, tag):
    yearly = defaultdict(lambda: defaultdict(int))
    for r in revisions:
        year = parse_year(r.get("timestamp",""))
        if not year or year < 2005 or year > 2026: continue
        cat = classify(r)
        yearly[year][cat] += 1

    years = sorted(yearly.keys())
    cats  = ["GENUINE", "REJECTED", "GATEKEEPING", "VANDALISM", "GENDER", "OTHER"]
    colors = [PALETTE.get(c, "#9E9E9E") for c in cats]

    bottom = np.zeros(len(years))
    fig, ax = plt.subplots(figsize=(14,6))
    for cat, color in zip(cats, colors):
        vals = [yearly[y].get(cat, 0) for y in years]
        ax.bar(years, vals, bottom=bottom, label=cat, color=color, alpha=0.85)
        bottom += np.array(vals)

    ax.set_title(f"Contribution Patterns by Year\n({tag})", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Edits")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, f"{tag}_yearly_stacked.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [SAVED] {path}")

def chart3_top_reverters(revisions, tag):
    counter = defaultdict(int)
    for r in revisions:
        if GATEKEEPING_PAT.search(r.get("summary", "")):
            counter[r.get("user", "Unknown")] += 1
    top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:15]
    if not top: return
    names, counts = zip(*top)

    fig, ax = plt.subplots(figsize=(10,6))
    bars = ax.barh(names[::-1], counts[::-1], color="#FF9800")
    ax.set_title(f"Top 15 Admin Reverters (RCP Gatekeepers)\n({tag})", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of Reverts")
    for bar, val in zip(bars, counts[::-1]):
        ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2, str(val), va="center", fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, f"{tag}_top_reverters.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [SAVED] {path}")

def chart4_minor_edit_rate(revisions, tag):
    yearly_minor  = defaultdict(int)
    yearly_total  = defaultdict(int)
    for r in revisions:
        year = parse_year(r.get("timestamp",""))
        if not year or year < 2005 or year > 2026: continue
        yearly_total[year] += 1
        if r.get("is_minor"): yearly_minor[year] += 1
    years = sorted(yearly_total.keys())
    rates = [yearly_minor[y]/yearly_total[y]*100 for y in years]

    fig, ax = plt.subplots(figsize=(12,5))
    ax.fill_between(years, rates, alpha=0.3, color="#2196F3")
    ax.plot(years, rates, color="#2196F3", linewidth=2, marker="o")
    ax.set_title(f"Minor Edit Rate by Year (is_minor)\n({tag})", fontsize=13, fontweight="bold")
    ax.set_ylabel("% Minor Edits")
    ax.set_xlabel("Year")
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, f"{tag}_minor_edit_rate.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [SAVED] {path}")

def chart5_genuine_vs_nongenuine(revisions, tag):
    genuine     = sum(1 for r in revisions if classify(r) == "GENUINE")
    gatekeeping = sum(1 for r in revisions if classify(r) in ("GATEKEEPING","GENDER"))
    vandalism   = sum(1 for r in revisions if classify(r) == "VANDALISM")
    rejected    = sum(1 for r in revisions if classify(r) == "REJECTED")
    other       = len(revisions) - genuine - gatekeeping - vandalism - rejected

    labels = ["Genuine", "Rejected\n(by admins)", "Gatekeeping\nReverts", "Vandalism", "Other"]
    values = [genuine, rejected, gatekeeping, vandalism, other]
    colors = ["#4CAF50", "#03A9F4", "#FF9800", "#F44336", "#9E9E9E"]

    fig, ax = plt.subplots(figsize=(10,7))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct=lambda p: f"{p:.1f}%\n({int(p/100*sum(values))})",
        colors=colors, startangle=140, pctdistance=0.75
    )
    for at in autotexts: at.set_fontsize(9)
    ax.set_title(f"Genuine vs. Non-Genuine Edit Composition\n({tag})", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, f"{tag}_composition.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [SAVED] {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", default=None, help="Focus on one article slug (e.g. Lose-Weight)")
    args = parser.parse_args()

    tag = args.article if args.article else "ALL_ARTICLES"
    print(f"\n{'='*55}")
    print(f"  WIKIHOW VISUALIZATION ENGINE")
    print(f"  Focus: {tag}")
    print(f"  Output: {OUT_DIR}")
    print(f"{'='*55}\n")

    revisions = load_articles(args.article)
    if not revisions:
        print("No revisions loaded. Check your data directory.")
        return

    print(f"  Loaded {len(revisions):,} revisions total.\n  Generating charts...\n")

    chart1_edit_types(revisions, tag)
    chart2_yearly_stacked(revisions, tag)
    chart3_top_reverters(revisions, tag)
    chart4_minor_edit_rate(revisions, tag)
    chart5_genuine_vs_nongenuine(revisions, tag)

    print(f"\n  All charts saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
