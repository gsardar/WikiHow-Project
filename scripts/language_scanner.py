"""
language_scanner.py (Module 4)
==============================
Reads the historical revisions of WikiHow articles and runs a lexical analysis
against a defined static gender dictionary (tier 1, 2, and 3). 
Computes the "Delta Analysis" (shift in neutrality over time) for both
articles and users, identifying where the biggest linguistic shifts occur.
"""

import os, json, re
import pandas as pd
from collections import Counter
import requests
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(base_dir, "..", "data")
DRIVE_DIR = "/content/drive/MyDrive/wikiHow_Diachronic"

# If running locally for testing, map DRIVE_DIR to local test folder
if not os.path.exists(DRIVE_DIR):
    DRIVE_DIR = os.path.join(base_dir, "..", "data", "test_drive")
    os.makedirs(DRIVE_DIR, exist_ok=True)

OUT_CSV = os.path.join(DRIVE_DIR, "language_evolution.csv")
OUT_DELTA_CSV = os.path.join(DRIVE_DIR, "language_delta_analysis.csv")

# ── 1. The Standard Gender Lexicon ────────────────────────────────────────────
# We start with the Bolukbasi (2016) list if available, but for our strict
# Diachronic study, we use the 3-tier structure defined in the methodology.

STANDARD_GENDER_LEXICON = {
    # Tier 1: Core Pronouns (Highest Frequency)
    "pronouns": {
        "masculine": ["he", "him", "his", "himself"],
        "feminine": ["she", "her", "hers", "herself"],
        "neutral": ["they", "them", "their", "theirs", "themselves"]
    },
    
    # Tier 2: Core Nouns & Kinship
    "nouns": {
        "masculine": ["man", "men", "boy", "boys", "guy", "guys", "gentleman", "gentlemen", 
                      "father", "dad", "brother", "son", "husband", "uncle", "nephew"],
        "feminine": ["woman", "women", "girl", "girls", "lady", "ladies", 
                     "mother", "mom", "sister", "daughter", "wife", "aunt", "niece"],
        "neutral": ["person", "people", "individual", "folks", "child", "children", 
                    "parent", "sibling", "spouse", "partner"]
    },
    
    # Tier 3: Gendered Occupations & Roles
    "occupations": {
        "masculine": ["policeman", "fireman", "businessman", "salesman", "chairman", 
                      "repairman", "handyman", "craftsman", "actor", "waiter", "host"],
        "feminine": ["policewoman", "firewoman", "businesswoman", "saleswoman", "chairwoman", 
                     "actress", "waitress", "hostess", "maid", "cleaning lady", "stewardess"],
        "neutral": ["police officer", "firefighter", "businessperson", "salesperson", "chairperson", 
                    "technician", "repairer", "cleaner", "flight attendant", "server"]
    }
}

# Compile into flat sets for O(1) checking
MASC_WORDS = set(
    STANDARD_GENDER_LEXICON["pronouns"]["masculine"] +
    STANDARD_GENDER_LEXICON["nouns"]["masculine"] +
    STANDARD_GENDER_LEXICON["occupations"]["masculine"]
)

FEM_WORDS = set(
    STANDARD_GENDER_LEXICON["pronouns"]["feminine"] +
    STANDARD_GENDER_LEXICON["nouns"]["feminine"] +
    STANDARD_GENDER_LEXICON["occupations"]["feminine"]
)

NEUT_WORDS = set(
    STANDARD_GENDER_LEXICON["pronouns"]["neutral"] +
    STANDARD_GENDER_LEXICON["nouns"]["neutral"] +
    STANDARD_GENDER_LEXICON["occupations"]["neutral"]
)

def analyze_text(text):
    """
    Cleans text and counts occurrences of masculine, feminine, and neutral tokens.
    Uses regex word boundaries to avoid partial matches (e.g. 'mechanic' triggering 'he').
    """
    if not text:
        return 0, 0, 0
    
    # Fast regex tokenization (lowercase, words only)
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    m_count = sum(1 for w in words if w in MASC_WORDS)
    f_count = sum(1 for w in words if w in FEM_WORDS)
    n_count = sum(1 for w in words if w in NEUT_WORDS)
    
    return m_count, f_count, n_count

# ── 2. Data Fetching ──────────────────────────────────────────────────────────

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (TextScanner)"

def get_revision_text(revid, retries=3):
    """Fetches the actual text content of a specific revision."""
    params = {
        "action": "query",
        "prop": "revisions",
        "revids": revid,
        "rvprop": "content",
        "rvslots": "main",
        "format": "json"
    }
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                if pid == "-1": return ""
                revs = page.get("revisions", [])
                if revs:
                    return revs[0].get("slots", {}).get("main", {}).get("*", "")
            return ""
        except Exception:
            if attempt == retries:
                return ""
            time.sleep(2**attempt)
    return ""

def score_article_year(title, rev_id):
    """Fetches text and returns the NLP scores for a specific revision."""
    print(f"  Fetching rev {rev_id} ...", end="", flush=True)
    text = get_revision_text(rev_id)
    m, f, n = analyze_text(text)
    total = m + f + n
    pct_m = (m / total) if total > 0 else 0
    pct_f = (f / total) if total > 0 else 0
    pct_n = (n / total) if total > 0 else 0
    print(f"  [M:{m} F:{f} N:{n} | Words:{len(text.split())}]")
    return {"m_count": m, "f_count": f, "n_count": n, "total_gendered": total,
            "pct_masc": pct_m, "pct_fem": pct_f, "pct_neut": pct_n}

# ── 3. Delta Analysis (Change over Time) ──────────────────────────────────────
# Note: In a full run, this script reads `articles.csv` generated by Module 1-3.
# It then picks a "baseline" revision (e.g. 2010 or first edit) and a 
# "current" revision (e.g. 2024 or last edit), runs the text scanner on both,
# and calculates the Delta (shift in neutrality).

def run_delta_analysis(articles_df, revisions_df):
    """
    Main routine: for every article, find its earliest and latest revisions.
    Calculate text gender scores for both.
    """
    results = []
    
    for idx, row in articles_df.iterrows():
        title = row["article_title"]
        print(f"\nScanning: {title}")
        
        # Find all revisions for this article, chronologically
        art_revs = revisions_df[revisions_df["article_title"] == title].sort_values("timestamp")
        
        if len(art_revs) < 2:
            print("  Skipping: not enough revisions.")
            continue
            
        first_rev = art_revs.iloc[0]["revision_id"]
        last_rev  = art_revs.iloc[-1]["revision_id"]
        
        start_scores = score_article_year(title, first_rev)
        end_scores   = score_article_year(title, last_rev)
        
        # Calculate Delta: Positive delta means it became MORE neutral
        delta_neutrality = end_scores["pct_neut"] - start_scores["pct_neut"]
        
        results.append({
            "article_title": title,
            "continuum": row.get("continuum", ""),
            "category": row.get("category", ""),
            "start_year": art_revs.iloc[0].get("year", ""),
            "end_year": art_revs.iloc[-1].get("year", ""),
            
            "start_masc": start_scores["pct_masc"],
            "start_fem": start_scores["pct_fem"],
            "start_neut": start_scores["pct_neut"],
            
            "end_masc": end_scores["pct_masc"],
            "end_fem": end_scores["pct_fem"],
            "end_neut": end_scores["pct_neut"],
            
            "delta_neutrality": delta_neutrality
        })
        time.sleep(1) # API politeness
        
    delta_df = pd.DataFrame(results)
    
    if not delta_df.empty:
        delta_df = delta_df.sort_values("delta_neutrality", ascending=False)
        delta_df.to_csv(OUT_DELTA_CSV, index=False)
        print(f"\n=> Saved delta analysis to {OUT_DELTA_CSV}")
        
        print("\nTOP 5 MOST EXTREME NEUTRALITY SHIFTS (Gender Flips):")
        print(delta_df[["article_title", "start_year", "end_year", "delta_neutrality"]].head(5).to_string())

if __name__ == "__main__":
    print("=" * 60)
    print("WikiHow Diachronic Study - Module 4 (Linguistic Scanner)")
    print("=" * 60)
    
    arts_csv = os.path.join(DRIVE_DIR, "articles.csv")
    revs_csv = os.path.join(DRIVE_DIR, "revisions_part_000.csv")
    
    if os.path.exists(arts_csv) and os.path.exists(revs_csv):
        print("Dataset found. Commencing scanner...")
        a_df = pd.read_csv(arts_csv).head(10) # process first 10 for safety
        r_df = pd.read_csv(revs_csv)
        run_delta_analysis(a_df, r_df)
    else:
        print(f"Waiting for Module 1-3 to collect data into:\n  {DRIVE_DIR}")
        print("\nTest Run: Scanning a dummy sentence...")
        test_txt = "The repairman said he would fix the sink. Later, the technician said they resolved the plumbing issue."
        print(f"Text: '{test_txt}'")
        m,f,n = analyze_text(test_txt)
        print(f"Result: Masculine={m}, Feminine={f}, Neutral={n}")
