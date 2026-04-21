"""
WikiHow Contributor Database Manager

Handles:
- Yearly folder structure under data/db/YYYY/
- Auto-creates year folders on demand (handles unknown/future years gracefully)
- Migrates legacy contributors_v1.csv into the new structure
- Consolidation helpers for cross-year queries (e.g., for visualization)

Folder layout:
    data/
      db/
        YYYY/
          contributors.csv
          articles.csv
          revisions.csv
        Unknown/
          contributors.csv    <- entries where join year could not be determined
"""

import os
import re
import pandas as pd
from datetime import datetime

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_FILE_V1  = os.path.join("data", "contributors_v1.csv")
DB_ROOT       = os.path.join("data", "db")      # yearly activity (articles, revisions)
AUTHORS_DIR   = os.path.join("data", "authors") # flat master author registry
AUTHORS_FILE  = os.path.join(AUTHORS_DIR, "contributors.csv")
CURRENT_YEAR  = datetime.now().year             # auto-updates each run

# ─── SCHEMA: expected columns for each table ──────────────────────────────────
CONTRIBUTOR_COLS = [
    "username", "profile_url", "real_name", "location", "year", "tenure",
    "edit_count", "pronoun", "gender", "identity_tags", "gender_source",
    "gender_confidence", "badges", "image_ai_guess", "genai_raw_json",
]

ARTICLE_COLS = [
    "article_id", "title", "category", "continuum", "starter_username",
    "starter_gender", "total_revisions", "female_editors", "male_editors",
    "unknown_editors", "female_bytes_added", "male_bytes_added",
    "female_bytes_removed", "male_bytes_removed",
]

REVISION_COLS = [
    "rev_id", "article_id", "username", "gender", "timestamp",
    "bytes_delta", "diff_text", "change_type", "change_confidence",
]


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_year_from_tenure(tenure_str) -> str:
    """
    Derive approximate join year from a tenure string.
    Examples: 'over 5 years!' → 2021,  'over 18 years!' → 2008
    Falls back to 'Unknown' if not parseable.
    """
    if pd.isna(tenure_str) or not isinstance(tenure_str, str):
        return "Unknown"

    # 'over N years' or 'N years'
    m = re.search(r"(\d+)\s+years?", tenure_str, re.I)
    if m:
        return str(CURRENT_YEAR - int(m.group(1)))

    # Explicit 4-digit year anywhere in string
    m = re.search(r"20\d{2}", tenure_str)
    if m:
        return m.group(0)

    return "Unknown"


def year_dir(year) -> str:
    """Return the path for a given year folder, creating it if needed."""
    folder = os.path.join(DB_ROOT, str(year))
    os.makedirs(folder, exist_ok=True)
    return folder


def year_file(year, table: str = "contributors") -> str:
    """Return full path to a CSV file inside a year folder. Creates folder if needed."""
    return os.path.join(year_dir(year), f"{table}.csv")


def upsert_records(df: pd.DataFrame, year, table: str = "contributors",
                   pk: str = "username") -> None:
    """
    Write a DataFrame into the correct year folder CSV.
    If the file already exists, merges on primary key (newest record wins).
    Auto-creates the year folder if it does not exist.
    """
    path = year_file(year, table)
    if os.path.exists(path):
        existing = pd.read_csv(path, dtype=str)
        merged = (pd.concat([existing, df.astype(str)])
                    .drop_duplicates(subset=[pk], keep="last")
                    .reset_index(drop=True))
    else:
        merged = df.astype(str)

    merged.to_csv(path, index=False)


# ─── MIGRATION FROM V1 ────────────────────────────────────────────────────────

def migrate_v1():
    """
    One-time migration: read contributors_v1.csv → data/authors/contributors.csv
    ALL authors go into a single flat master registry (not split by year).
    Year folders (data/db/YYYY/) are reserved for articles and revisions only.
    Safe to re-run (uses upsert, not overwrite).
    """
    if not os.path.exists(DATA_FILE_V1):
        print(f"[db_manager] {DATA_FILE_V1} not found — skipping migration.")
        return

    os.makedirs(AUTHORS_DIR, exist_ok=True)
    df = pd.read_csv(DATA_FILE_V1, dtype=str)

    # Ensure all schema columns exist
    for col in CONTRIBUTOR_COLS:
        if col not in df.columns:
            df[col] = ""

    # Derive year from tenure where year is missing (kept as a column, not as a folder key)
    df["year"] = df.apply(
        lambda r: get_year_from_tenure(r.get("tenure", ""))
                  if str(r.get("year", "")).strip() in ("", "nan", "Unknown")
                  else str(r["year"]),
        axis=1,
    )

    # Write the full flat master file
    if os.path.exists(AUTHORS_FILE):
        existing = pd.read_csv(AUTHORS_FILE, dtype=str)
        merged = (pd.concat([existing, df[CONTRIBUTOR_COLS].astype(str)])
                    .drop_duplicates(subset=["username"], keep="last")
                    .reset_index(drop=True))
    else:
        merged = df[CONTRIBUTOR_COLS].astype(str)

    merged.to_csv(AUTHORS_FILE, index=False)
    print(f"[db_manager] ✅  {len(merged)} total authors → {AUTHORS_FILE}")
    print(f"[db_manager] Migration complete. Authors file: {os.path.abspath(AUTHORS_FILE)}")
    print(f"[db_manager] Note: data/db/YYYY/ folders are for articles & revisions only.")


# ─── CONSOLIDATE (cross-year queries) ─────────────────────────────────────────

def load_authors() -> pd.DataFrame:
    """Load the flat master author registry."""
    if os.path.exists(AUTHORS_FILE):
        return pd.read_csv(AUTHORS_FILE, dtype=str)
    return pd.DataFrame(columns=CONTRIBUTOR_COLS)


def load_activity(table: str = "articles") -> pd.DataFrame:
    """
    Load and concatenate all year CSVs for articles or revisions across every year folder.
    Use: load_activity('articles') or load_activity('revisions')
    """
    os.makedirs(DB_ROOT, exist_ok=True)
    frames = []
    for entry in sorted(os.scandir(DB_ROOT), key=lambda e: e.name):
        if entry.is_dir():
            path = os.path.join(entry.path, f"{table}.csv")
            if os.path.exists(path):
                frames.append(pd.read_csv(path, dtype=str))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def upsert_author(record: dict) -> None:
    """
    Upsert a single author record into the master authors file.
    Call this after each profile scan.
    """
    os.makedirs(AUTHORS_DIR, exist_ok=True)
    df_new = pd.DataFrame([record]).astype(str)
    if os.path.exists(AUTHORS_FILE):
        existing = pd.read_csv(AUTHORS_FILE, dtype=str)
        merged = (pd.concat([existing, df_new])
                    .drop_duplicates(subset=["username"], keep="last")
                    .reset_index(drop=True))
    else:
        merged = df_new
    merged.to_csv(AUTHORS_FILE, index=False)


def ensure_year_folders(years: list) -> None:
    """
    Pre-create year folders for a list of years.
    Call this before writing articles from any scrape run.
    """
    for y in years:
        folder = year_dir(y)
        print(f"[db_manager] Ensured folder: {folder}")


def init_table_if_missing(year, table: str, columns: list) -> None:
    """
    Write an empty CSV with the correct headers for a table/year if it doesn't exist.
    """
    path = year_file(year, table)
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)
        print(f"[db_manager] Created empty {table}.csv for {year}")


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "migrate"

    if cmd == "migrate":
        migrate_v1()
    elif cmd == "load":
        table = sys.argv[2] if len(sys.argv) > 2 else "contributors"
        df = load_all(table)
        print(df.describe())
        print(df.head())
    elif cmd == "ensure":
        # e.g. python db_manager.py ensure 2005 2006 2007
        years = sys.argv[2:] if len(sys.argv) > 2 else [str(y) for y in range(2005, CURRENT_YEAR + 1)]
        ensure_year_folders(years)
    else:
        print(f"Unknown command: {cmd}. Use: migrate | load | ensure")
