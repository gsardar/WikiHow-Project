"""Generates wikihow_data_collection.ipynb. Run with: py build_notebook.py"""
import json, os

try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_dir = os.path.abspath(os.getcwd())

OUT = os.path.join(base_dir, "wikihow_data_collection.ipynb")

def md_cell(cid, src):
    lines = src.strip().split("\n")
    return {"id": cid, "cell_type": "markdown", "metadata": {},
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}

def code_cell(cid, src):
    lines = src.split("\n")
    return {"id": cid, "cell_type": "code", "metadata": {},
            "outputs": [], "execution_count": None,
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}

CELLS = []

# ── Title & How-To ────────────────────────────────────────────────────────────
CELLS.append(md_cell("title", '''\
# WikiHow Diachronic Gender Study — Continuous Data Collector

> **Design goal:** run indefinitely, survive Colab timeouts, and stop cleanly *only* when the
> free genderize.io daily quota is exhausted.

---

## How this notebook works — step by step

### Step 1 — `[Config]`
Set every tunable constant in one place: output paths, rate limits, continuum definitions,
shard sizes. **You only ever need to touch this cell.**

### Step 2 — `[Setup]`
- Mounts Google Drive
- Imports all libraries (matplotlib, pandas, requests …)
- Defines the **shard helper functions** — instead of one giant `revisions.csv` that must be
  fully rewritten every time (→ slow Drive uploads), revisions are stored in numbered shard
  files (`revisions_part_000.csv`, `revisions_part_001.csv`, …). Each shard is sealed once it
  reaches `SHARD_ROWS` rows and is **never touched again**. Only the current open shard is
  ever appended to.
- Loads the fault-tolerance tracker (`_progress.json`) so already-processed articles are skipped.

### Step 3 — `[Gender Engine]`
Defines the three-tier gender resolution pipeline:
| Tier | Method | `gender_source` |
|---|---|---|
| 1 | MediaWiki account gender setting | `mediawiki` |
| 2 | Pronoun scan on user profile page | `profile_pronouns` |
| 3 | genderize.io first-name lookup | `genderize.io` |

Tier 3 raises `GenderizeLimitReached` the moment the API returns HTTP 429.
That exception bubbles up and stops **only** the main loop — nothing else.

### Step 4 — `[Chart Renderer]`
Defines `render_charts()`:
- Reads **all** revision shards into one DataFrame
- Joins gender from the contributor cache
- Produces one horizontal 100%-stacked bar chart per continuum (male / female / unknown share of
  edits per category, ordered female→male-coded)
- Saves PNGs to `charts/` on Drive

### Step 5 — `[▶ Main Loop]` ← **the cell you run**
A single `while True` loop that:
1. Iterates every `(continuum, category, article)` triple in order
2. Fetches complete revision history from the WikiHow API (with retry/backoff)
3. Streams rows into the current shard — rolling to a new shard when full
4. Every `GENDER_BATCH` newly-seen named users → runs the 3-tier pipeline
5. Every `CHART_INTERVAL` articles → calls `render_charts()`
6. Catches `GenderizeLimitReached` → flushes caches, prints a clear stop message, exits

All other errors (network blip, WikiHow rate-limit) are retried with exponential back-off and
**never** stop the loop.

### Step 6 — `[Verify]`
On-demand summary cell — run any time (even while the loop is paused) to see counts, gender
distribution, top articles, and shard inventory.

---

| File on Drive | Contents |
|---|---|
| `revisions_part_NNN.csv` | Sharded revision rows — core data |
| `contributors.csv` | One row per unique contributor + resolved gender |
| `articles.csv` | One row per article, aggregated stats |
| `_progress.json` | Fault-tolerance set (auto-managed) |
| `_contributor_cache.json` | Gender resolution cache (auto-managed) |
| `charts/*.png` | Auto-updated visualisations |'''))

# ── Config ────────────────────────────────────────────────────────────────────
CELLS.append(code_cell("config", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║                    CONFIGURATION                             ║
# ║   Edit this cell only — everything else reads from here      ║
# ╚══════════════════════════════════════════════════════════════╝

# ── Paths ─────────────────────────────────────────────────────────────────────
DRIVE_BASE       = "/content/drive/MyDrive/wikiHow_Diachronic"
CHARTS_DIR       = f"{DRIVE_BASE}/charts"
CONTRIBUTORS_CSV = f"{DRIVE_BASE}/contributors.csv"
ARTICLES_CSV     = f"{DRIVE_BASE}/articles.csv"
PROGRESS_FILE    = f"{DRIVE_BASE}/_progress.json"
CONTRIB_CACHE    = f"{DRIVE_BASE}/_contributor_cache.json"
SHARD_PREFIX     = f"{DRIVE_BASE}/revisions_part_"   # + 000.csv, 001.csv …

# ── Storage ───────────────────────────────────────────────────────────────────
SHARD_ROWS       = 50_000   # max rows before opening a new shard file

# ── Loop cadence ──────────────────────────────────────────────────────────────
GENDER_BATCH     = 200      # resolve gender every N newly-seen named users
CHART_INTERVAL   = 50       # rebuild charts every N articles processed

# ── API ───────────────────────────────────────────────────────────────────────
BASE_URL           = "https://www.wikihow.com/api.php"
USER_AGENT         = "WikiHowGenderResearch/1.0 (research@university.edu)"
RATE_LIMIT         = 1.0    # min seconds between WikiHow API calls
GENDERIZE_MIN_PROB = 0.85   # minimum confidence threshold for genderize.io

# ── Continuums ────────────────────────────────────────────────────────────────
# Each list is ordered: female-coded (pos 0) → male-coded (pos 9)
CONTINUUMS = {
        "domestic": {
        "title": "Domestic & Household Management",
        "categories": [
            ("Babies and Infants", 0, ["baby", "babies", "infant", "newborn", "diaper", "nursery", "bottle", "crawl", "stroller", "toddler", "crib", "child", "kid", "parent", "pregnancy", "prenatal", "breastfeeding", "birth", "pacifier", "teething"]),
            ("Baking", 1, ["bake", "baking", "cake", "bread", "cookie", "oven", "flour", "dough", "yeast", "pastry", "muffin", "pie", "knead", "whisk", "sugar", "chocolate", "frosting", "cupcake", "brownie", "doughnut"]),
            ("Home Decorating", 2, ["decorate", "decoration", "furniture", "room", "wallpaper", "curtain", "rug", "interior", "pillow", "shelf", "paint", "accent", "lighting", "frame", "hanging", "art", "carpet", "mirror", "vase", "blind"]),
            ("Laundry", 3, ["laundry", "wash", "dry", "clothes", "stain", "detergent", "fabric", "iron", "bleach", "fold", "hamper", "machine", "linen", "silk", "wool", "wrinkle", "dryer", "washer", "sock", "lint"]),
            ("Gardening", 4, ["garden", "gardening", "plant", "soil", "grow", "flower", "vegetable", "seed", "weed", "lawn", "prune", "sprinkler", "mulch", "fertilizer", "tree", "shrub", "herb", "grass", "mow", "rose"]),
            ("Finance and Business", 5, ["money", "budget", "save", "invest", "debt", "credit", "bank", "tax", "retirement", "expense", "loan", "mortgage", "cash", "income", "wallet", "card", "billing", "check", "stock", "interest"]),
            ("Home Improvements", 6, ["repair", "install", "renovate", "renovation", "build", "wall", "floor", "door", "window", "roof", "tile", "siding", "gutter", "deck", "patio", "fence", "attic", "stairs", "drywall", "insulation"]),
            ("Home Appliances", 7, ["repair", "fix", "washer", "dryer", "fridge", "refrigerator", "microwave", "oven", "dishwasher", "stove", "vacuum", "freezer", "toaster", "blender", "kettle", "heater", "cool", "appliance"]),
            ("Plumbing", 8, ["pipe", "leak", "faucet", "drain", "toilet", "clog", "plumb", "plumbing", "sink", "shower", "water", "hose", "septic", "heater", "valve", "trap", "sump", "p-trap", "tank"]),
            ("Electrical Wiring and Safety Switches", 9, ["wire", "wiring", "outlet", "switch", "circuit", "light", "electrical", "breaker", "cord", "voltage", "fuse", "bulb", "terminal", "cable", "fixture", "ground", "panel", "spark"]),
        ],
    },
    "occupational": {
        "title": "Occupational & Professional Fields",
        "categories": [
            ("Nursing Careers", 0, []), ("Early Childhood Education", 1, []),
            ("Social Work", 2, []), ("Human Resources Careers", 3, []),
            ("Arts and Entertainment", 4, []), ("Business", 5, []),
            ("Physics", 6, []), ("Software", 7, []),
            ("Engineering", 8, []), ("Construction", 9, []),
        ],
    },
    "entertainment": {
        "title": "Entertainment & Leisure",
        "categories": [
            ("Knitting", 0, []), ("Dancing", 1, []), ("Reading", 2, []),
            ("Social Media", 3, []), ("Photography", 4, []), ("Board Games", 5, []),
            ("Team Sports", 6, []), ("Video Gaming", 7, []),
            ("DIY", 8, []), ("Hacking", 9, []),
        ],
    },
    "policy": {
        "title": "Public Policy & Governance",
        "categories": [
            ("Maternal Health", 0, []), ("Education and Communications", 1, []),
            ("Welfare", 2, []), ("Health", 3, []),
            ("Community", 4, []), ("Taxes", 5, []),
            ("Politics", 6, []), ("Law Enforcement", 7, []),
            ("Military", 8, []), ("Politics and Government", 9, []),
        ],
    },
}

# ── Column schemas ────────────────────────────────────────────────────────────
REVISIONS_COLS = [
    "article_title", "pageid", "continuum", "category", "continuum_position",
    "revision_id", "parent_id", "timestamp", "year", "year_period",
    "username", "is_anon", "edit_size_bytes", "size_delta_bytes",
    "comment", "is_revert", "gender", "gender_source",
]
CONTRIBUTORS_COLS = [
    "username", "global_editcount", "registration_date",
    "gender", "gender_source",
    "revisions_in_dataset", "articles_in_dataset", "continuums_in_dataset",
]
ARTICLES_COLS = [
    "article_title", "pageid", "continuum", "category", "continuum_position",
    "total_revisions", "first_edit_ts", "first_editor", "last_edit_ts", "last_editor",
]

total_cats = sum(len(v["categories"]) for v in CONTINUUMS.values())
print(f"✓ Config loaded — {len(CONTINUUMS)} continuums, {total_cats} categories")
print(f"  Drive path : {DRIVE_BASE}")
print(f"  Shard size : {SHARD_ROWS:,} rows/file   |  Gender every {GENDER_BATCH} users   |  Charts every {CHART_INTERVAL} articles")'''))

# ── Setup ─────────────────────────────────────────────────────────────────────
CELLS.append(code_cell("setup", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║                        SETUP                                 ║
# ║  Mount Drive · imports · shard helpers · load progress       ║
# ╚══════════════════════════════════════════════════════════════╝

from google.colab import drive
drive.mount("/content/drive")

import os, re, json, csv, time, glob
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for Colab
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from collections import Counter

os.makedirs(DRIVE_BASE,   exist_ok=True)
os.makedirs(CHARTS_DIR,   exist_ok=True)

# ── Shard helpers ─────────────────────────────────────────────────────────────
def _all_shard_paths():
    """Return sorted list of all existing shard file paths."""
    return sorted(glob.glob(f"{SHARD_PREFIX}???.csv"))

def _current_shard_state():
    """
    Return (path, current_row_count) for the active (open) shard.
    Creates revisions_part_000.csv if nothing exists yet.
    """
    existing = _all_shard_paths()
    if not existing:
        path = f"{SHARD_PREFIX}000.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=REVISIONS_COLS).writeheader()
        print(f"  Created shard: {Path(path).name}")
        return path, 0
    path = existing[-1]
    with open(path, encoding="utf-8") as f:
        # count rows without loading into RAM
        row_count = sum(1 for _ in f) - 1   # subtract header
    return path, max(row_count, 0)

def _open_new_shard(current_path):
    """Seal current shard and open the next one, returning its path."""
    idx = int(Path(current_path).stem.split("_")[-1]) + 1
    path = f"{SHARD_PREFIX}{idx:03d}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=REVISIONS_COLS).writeheader()
    print(f"  ↳ Rolled to new shard: {Path(path).name}")
    return path, 0

def _append_to_shard(rows, shard_path, shard_rows):
    """
    Append rows to the current shard, rolling to a new shard when full.
    Returns (new_shard_path, new_shard_row_count).
    """
    for chunk_start in range(0, len(rows), SHARD_ROWS):
        chunk = rows[chunk_start : chunk_start + SHARD_ROWS]
        space = SHARD_ROWS - shard_rows
        fitting, overflow = chunk[:space], chunk[space:]
        if fitting:
            with open(shard_path, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=REVISIONS_COLS,
                               extrasaction="ignore").writerows(fitting)
            shard_rows += len(fitting)
        if overflow:
            shard_path, shard_rows = _open_new_shard(shard_path)
            with open(shard_path, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=REVISIONS_COLS,
                               extrasaction="ignore").writerows(overflow)
            shard_rows += len(overflow)
    return shard_path, shard_rows

def _read_all_revisions(dtype=None):
    """Concatenate all shards into one DataFrame (for charts / verify only)."""
    paths = _all_shard_paths()
    if not paths:
        return pd.DataFrame(columns=REVISIONS_COLS)
    return pd.concat([pd.read_csv(p, dtype=dtype) for p in paths], ignore_index=True)

# ── Progress tracker ──────────────────────────────────────────────────────────
def _load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def _save_progress(done_set):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(done_set), f)

# ── Misc helpers ──────────────────────────────────────────────────────────────
def _is_anon(username):
    return bool(re.match(
        r"^(\d{1,3}\.){3}\d{1,3}$"   # IPv4
        r"|^[0-9a-fA-F:]{7,}$",       # IPv6
        str(username)
    ))

def _year_period(ts):
    try:
        y = datetime.fromisoformat(ts.replace("Z", "+00:00")).year
    except Exception:
        return 0, "Unknown"
    for label, s, e in [
        ("2005-2009", 2005, 2009), ("2010-2014", 2010, 2014),
        ("2015-2019", 2015, 2019), ("2020-2024", 2020, 2024),
        ("2025-2026", 2025, 2026),
    ]:
        if s <= y <= e:
            return y, label
    return y, "Unknown"

def _passes_filter(title, keywords):
    """Lexical Bounding Filter: returns True if title contains any keyword.
    If keywords list is empty, always returns True (filter disabled)."""
    if not keywords:
        return True
    t = title.lower()
    return any(kw.lower() in t for kw in keywords)

# ── Init ──────────────────────────────────────────────────────────────────────
completed_articles = _load_progress()
shard_path, shard_rows = _current_shard_state()
print(f"\\n✓ Setup complete")
print(f"  Active shard : {Path(shard_path).name}  ({shard_rows:,} rows so far)")
print(f"  Articles done: {len(completed_articles):,}")'''))

# ── Gender Engine ─────────────────────────────────────────────────────────────
CELLS.append(code_cell("gender-engine", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║                    GENDER ENGINE                             ║
# ║  3-tier pipeline:  MediaWiki → Profile → genderize.io        ║
# ╚══════════════════════════════════════════════════════════════╝

class GenderizeLimitReached(Exception):
    """Raised when genderize.io returns HTTP 429 (daily quota exhausted)."""
    pass

_last_req = 0.0

def _wiki_request(params, retries=8):
    """Rate-limited GET to the WikiHow MediaWiki API with exponential back-off.
    Retries on network errors and rate-limit responses — never raises for these."""
    global _last_req
    params.setdefault("format", "json")
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(1, retries + 1):
        gap = time.time() - _last_req
        if gap < RATE_LIMIT:
            time.sleep(RATE_LIMIT - gap)
        try:
            r = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
            _last_req = time.time()
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                code = data["error"].get("code", "")
                if "ratelimit" in code.lower():
                    wait = min(2 ** attempt + 5, 120)
                    print(f"    [WikiHow rate-limit] waiting {wait}s …")
                    time.sleep(wait)
                    continue
                raise ConnectionError(f"API error: {data[\\'error\\'].get(\\'info\\', code)}")
            return data
        except (requests.RequestException, ValueError) as exc:
            if attempt == retries:
                raise ConnectionError(f"WikiHow unreachable after {retries} attempts: {exc}")
            time.sleep(min(2 ** attempt, 60))
    raise ConnectionError("Max retries exceeded")


def _get_all_category_articles(category):
    """Fetch ALL {pageid, title} dicts from a category via cmcontinue pagination."""
    cat = f"Category:{category}" if not category.startswith("Category:") else category
    results, params = [], {
        "action": "query", "list": "categorymembers",
        "cmtitle": cat, "cmlimit": 500, "cmtype": "page",
    }
    while True:
        data = _wiki_request(params)
        results.extend(data.get("query", {}).get("categorymembers", []))
        cont = data.get("continue", {})
        if "cmcontinue" not in cont:
            break
        params["cmcontinue"] = cont["cmcontinue"]
    return results


def _get_all_revisions(title):
    """Fetch ALL revisions for one article (newest-first) via rvcontinue pagination.
    Computes size_delta_bytes inline. Returns [] if article not found."""
    results, params = [], {
        "action": "query", "prop": "revisions", "titles": title,
        "rvprop": "ids|user|timestamp|size|parsedcomment",
        "rvlimit": 500,
    }
    while True:
        data = _wiki_request(params)
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return []
            for rev in page.get("revisions", []):
                rev["_anon"] = "anon" in rev
                results.append(rev)
        cont = data.get("continue", {})
        if "rvcontinue" not in cont:
            break
        params["rvcontinue"] = cont["rvcontinue"]
    # Compute size deltas (newest = index 0)
    for i, rev in enumerate(results):
        prev = results[i + 1].get("size", 0) if i + 1 < len(results) else 0
        rev["_delta"] = rev.get("size", 0) - prev
    return results


# ── Tier 1: MediaWiki ─────────────────────────────────────────────────────────
def _tier1_mediawiki(usernames):
    result = {}
    for i in range(0, len(usernames), 50):
        chunk = usernames[i:i + 50]
        try:
            data = _wiki_request({
                "action": "query", "list": "users",
                "ususers": "|".join(chunk),
                "usprop": "gender|editcount|registration",
            })
            for u in data.get("query", {}).get("users", []):
                name = u.get("name", "")
                result[name] = {
                    "gender"           : u.get("gender", "unknown"),
                    "gender_source"    : "mediawiki",
                    "global_editcount" : u.get("editcount", 0),
                    "registration_date": u.get("registration", ""),
                }
        except Exception as exc:
            print(f"    [T1 chunk {i//50}] error: {exc}")
    return result


# ── Tier 2: Profile pronoun scan ──────────────────────────────────────────────
_pronoun_cache = {}

def _tier2_profile(username):
    if username in _pronoun_cache:
        return _pronoun_cache[username]
    try:
        data = _wiki_request({
            "action": "query", "titles": f"User:{username}",
            "prop": "revisions", "rvprop": "content", "rvslots": "main",
        })
        text = ""
        for page in data.get("query", {}).get("pages", {}).values():
            revs = page.get("revisions", [])
            if revs:
                text = revs[0].get("slots", {}).get("main", {}).get("*", "")
        t = text.lower()
        if re.search(r"\\b(she/her|pronouns?\\s*[:\\-]?\\s*she|i(?:\\'m| am) a (?:girl|woman|female))\\b", t):
            g = "female"
        elif re.search(r"\\b(he/him|pronouns?\\s*[:\\-]?\\s*he|i(?:\\'m| am) a (?:guy|man|male))\\b", t):
            g = "male"
        elif re.search(r"\\b(they/them|pronouns?\\s*[:\\-]?\\s*they)\\b", t):
            g = "neutral"
        else:
            g = "unknown"
    except Exception:
        g = "unknown"
    _pronoun_cache[username] = g
    return g


# ── Tier 3: genderize.io ──────────────────────────────────────────────────────
def _tier3_genderize(names_map):
    """
    names_map: {first_name: [username, …]}
    Returns {username: gender}.
    Raises GenderizeLimitReached on HTTP 429.
    """
    result = {}
    for i in range(0, len(names_map), 10):
        batch  = list(names_map.keys())[i:i + 10]
        params = [("name[]", n) for n in batch]
        try:
            resp = requests.get("https://api.genderize.io", params=params, timeout=10)
            if resp.status_code == 429:
                raise GenderizeLimitReached(
                    "genderize.io daily quota exhausted (HTTP 429). "
                    "Resume tomorrow — all progress is saved."
                )
            if resp.ok:
                for item in resp.json():
                    name = item.get("name", "")
                    g    = item.get("gender", "")
                    prob = item.get("probability", 0)
                    out  = (g if g in ("male", "female") and prob >= GENDERIZE_MIN_PROB
                            else "unknown")
                    for uname in names_map.get(name, []):
                        result[uname] = out
            else:
                for n in batch:
                    for uname in names_map.get(n, []):
                        result[uname] = "unknown"
        except GenderizeLimitReached:
            raise   # let it propagate — this is the intentional stop condition
        except Exception as exc:
            print(f"    [T3 batch {i//10}] error: {exc}")
            for n in batch:
                for uname in names_map.get(n, []):
                    result[uname] = "unknown"
        time.sleep(0.5)
    return result


# ── Full pipeline ─────────────────────────────────────────────────────────────
def resolve_genders(usernames, cache):
    """
    Run the 3-tier pipeline for a list of new usernames.
    Mutates `cache` in-place. May raise GenderizeLimitReached.
    """
    # Tier 1
    t1 = _tier1_mediawiki(usernames)
    cache.update(t1)

    # Tier 2
    t2_cands = [u for u in usernames if cache.get(u, {}).get("gender", "unknown") == "unknown"]
    for uname in t2_cands:
        g = _tier2_profile(uname)
        if g != "unknown":
            cache[uname]["gender"]        = g
            cache[uname]["gender_source"] = "profile_pronouns"

    # Tier 3  ← may raise GenderizeLimitReached
    t3_cands = [u for u in t2_cands if cache.get(u, {}).get("gender", "unknown") == "unknown"]
    names_map = {}
    for uname in t3_cands:
        spaced = re.sub(r"([a-z])([A-Z])", r"\\1 \\2", uname)   # split CamelCase
        first  = re.split(r"[^a-zA-Z]", spaced)[0]
        if len(first) > 2:
            names_map.setdefault(first, []).append(uname)
    if names_map:
        gz = _tier3_genderize(names_map)    # ← raises if limit hit
        for uname, g in gz.items():
            if g != "unknown":
                cache[uname]["gender"]        = g
                cache[uname]["gender_source"] = "genderize.io"

    # Ensure every user has a complete record
    for uname in usernames:
        if uname not in cache:
            cache[uname] = {"gender": "unknown", "gender_source": "none",
                            "global_editcount": 0, "registration_date": ""}
        elif cache[uname].get("gender", "unknown") == "unknown":
            cache[uname]["gender_source"] = "none"

print("✓ Gender engine loaded (GenderizeLimitReached sentinel armed)")'''))

# ── Chart Renderer ────────────────────────────────────────────────────────────
CELLS.append(code_cell("charts", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║                   CHART RENDERER                             ║
# ║  Reads all shards → draws 4 continuum bar charts             ║
# ╚══════════════════════════════════════════════════════════════╝

def render_charts(contrib_cache):
    """
    Read all revision shards, join gender from contrib_cache, and produce
    one 100%-stacked horizontal bar chart per continuum saved to CHARTS_DIR.
    Safe to call repeatedly — always overwrites the previous PNG.
    """
    revdf = _read_all_revisions(dtype=str)
    if revdf.empty:
        print("  [charts] no revision data yet — skipping")
        return

    # Join gender from cache (vectorised)
    user_gender = {u: info.get("gender", "unknown") for u, info in contrib_cache.items()}
    anon_mask   = revdf["is_anon"].str.lower() == "true"
    revdf["gender"] = (revdf["username"].map(user_gender)
                       .where(~anon_mask, other="anon")
                       .fillna("unknown"))

    COLORS = {"female": "#E05A8A", "male": "#4B8FCC", "unknown": "#AAAAAA", "anon": "#DDDDDD"}

    for cont_key, cont_info in CONTINUUMS.items():
        cdf = revdf[revdf["continuum"] == cont_key].copy()
        if cdf.empty:
            continue
        cdf["continuum_position"] = pd.to_numeric(cdf["continuum_position"], errors="coerce")
        # Build category label map (position → name)
        pos_map = {pos: cat for cat, pos in cont_info["categories"]}

        # Aggregate: % edits per gender per category, ordered by position
        agg = (cdf.groupby(["continuum_position", "gender"])
                  .size()
                  .reset_index(name="n"))
        totals = agg.groupby("continuum_position")["n"].transform("sum")
        agg["pct"] = agg["n"] / totals * 100
        pivot = (agg.pivot(index="continuum_position", columns="gender", values="pct")
                    .reindex(columns=["female", "male", "unknown", "anon"])
                    .fillna(0)
                    .sort_index())         # female-coded (0) at top → male-coded (9) at bottom
        pivot.index = [pos_map.get(p, str(p)) for p in pivot.index]

        # Draw
        fig, ax = plt.subplots(figsize=(11, 0.65 * len(pivot) + 1.8))
        left = pd.Series([0.0] * len(pivot), index=pivot.index)
        for gender in ["female", "male", "unknown", "anon"]:
            if gender not in pivot.columns:
                continue
            vals = pivot[gender]
            bars = ax.barh(pivot.index, vals, left=left,
                           color=COLORS[gender], label=gender.capitalize(), height=0.6)
            for bar, val in zip(bars, vals):
                if val > 5:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_y() + bar.get_height() / 2,
                            f"{val:.0f}%", ha="center", va="center",
                            fontsize=8, color="white", fontweight="bold")
            left += vals

        ax.set_xlim(0, 100)
        ax.set_xlabel("% of edits", fontsize=10)
        ax.set_title(f"{cont_info[\\'title\\']}\\nGender distribution of edits per category",
                     fontsize=12, fontweight="bold", pad=10)
        ax.legend(loc="lower right", fontsize=9, framealpha=0.8)
        ax.invert_yaxis()                 # put female-coded categories at top
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()

        out_path = f"{CHARTS_DIR}/{cont_key}_gender_spectrum.png"
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  [chart] saved → {Path(out_path).name}")

    print(f"  [charts] done — {datetime.now().strftime(\\'%H:%M:%S\\')}")

print("✓ Chart renderer loaded")'''))

# ── Main Loop ─────────────────────────────────────────────────────────────────
CELLS.append(md_cell("loop-header", '''\
## ▶ Main Loop

Run the cell below. It will run **forever** until:
- Every article in every category has been processed (unlikely — WikiHow has thousands), **or**
- **genderize.io** returns HTTP 429 (daily free quota of ~1,000 names exhausted)

In either case it saves all caches to Drive and prints a clear summary before stopping.

> **Resuming after a stop or Colab disconnect:** just re-run **Config → Setup → Gender Engine
> → Charts → this cell**. The progress tracker skips already-done articles automatically.'''))

CELLS.append(code_cell("main-loop", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║                      MAIN LOOP                               ║
# ║  Runs continuously. Stops ONLY on genderize.io quota limit.  ║
# ╚══════════════════════════════════════════════════════════════╝

# ── Load gender cache from Drive ──────────────────────────────────────────────
if Path(CONTRIB_CACHE).exists():
    with open(CONTRIB_CACHE, encoding="utf-8") as f:
        contrib_cache = json.load(f)
else:
    contrib_cache = {}

def _flush_cache():
    """Write the contributor cache and contributors.csv to Drive."""
    with open(CONTRIB_CACHE, "w", encoding="utf-8") as f:
        json.dump(contrib_cache, f, ensure_ascii=False)
    # Rebuild contributors.csv
    revdf     = _read_all_revisions(dtype=str)
    anon_mask = revdf["is_anon"].str.lower() == "true"
    named     = revdf[~anon_mask]
    rev_counts  = named.groupby("username").size().to_dict()
    art_counts  = named.groupby("username")["article_title"].nunique().to_dict()
    cont_counts = named.groupby("username")["continuum"].nunique().to_dict()
    rows = []
    for uname, info in contrib_cache.items():
        rows.append({
            "username"             : uname,
            "global_editcount"     : info.get("global_editcount", 0),
            "registration_date"    : info.get("registration_date", ""),
            "gender"               : info.get("gender", "unknown"),
            "gender_source"        : info.get("gender_source", "none"),
            "revisions_in_dataset" : rev_counts.get(uname, 0),
            "articles_in_dataset"  : art_counts.get(uname, 0),
            "continuums_in_dataset": cont_counts.get(uname, 0),
        })
    with open(CONTRIBUTORS_CSV, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CONTRIBUTORS_COLS).writeheader()
        csv.DictWriter(f, fieldnames=CONTRIBUTORS_COLS).writerows(rows)
    # Rebuild articles.csv
    revdf2 = _read_all_revisions(dtype=str)
    revdf2["timestamp"] = pd.to_datetime(revdf2["timestamp"], errors="coerce", utc=True)
    group_cols = ["article_title", "pageid", "continuum", "category", "continuum_position"]
    art_rows = []
    for keys, grp in revdf2.groupby(group_cols, sort=False):
        gs = grp.sort_values("timestamp")
        art_rows.append({
            "article_title"     : keys[0], "pageid": keys[1],
            "continuum"         : keys[2], "category": keys[3],
            "continuum_position": keys[4], "total_revisions": len(grp),
            "first_edit_ts"     : str(gs["timestamp"].iloc[0]),
            "first_editor"      : gs["username"].iloc[0],
            "last_edit_ts"      : str(gs["timestamp"].iloc[-1]),
            "last_editor"       : gs["username"].iloc[-1],
        })
    with open(ARTICLES_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ARTICLES_COLS)
        w.writeheader(); w.writerows(art_rows)
    print(f"  [flush] cache + contributors.csv ({len(rows):,} users) + articles.csv ({len(art_rows):,} articles) saved")

# ── State variables ───────────────────────────────────────────────────────────
new_users_seen   = []   # buffer of named users not yet through the gender pipeline
articles_this_run = 0
revisions_this_run = 0

print("=" * 62)
print("MAIN LOOP — starting")
print(f"  Already done : {len(completed_articles):,} articles")
print(f"  Active shard : {Path(shard_path).name}  ({shard_rows:,} rows)")
print("=" * 62)

try:
    for cont_key, cont_info in CONTINUUMS.items():
        print(f"\\n── {cont_info[\\'title\\']} ──")

        for category, position in cont_info["categories"]:
            print(f"  [{position}] {category:<42}", end=" ", flush=True)

            try:
                articles = _get_all_category_articles(category)
            except Exception as exc:
                print(f"→ CATEGORY ERROR: {exc}")
                continue

            if not articles:
                print("→ empty")
                continue

            cat_new = 0
            for art in articles:
                title   = art["title"]
                pageid  = art.get("pageid", "")
                art_key = f"{cont_key}|{category}|{title}"

                if art_key in completed_articles:
                    continue

                if not _passes_filter(title, keywords):
                    cat_skipped += 1
                    completed_articles.add(art_key)
                    continue

                # ── Fetch revisions ───────────────────────────────────────────
                try:
                    revisions = _get_all_revisions(title)
                except Exception as exc:
                    print(f"\\n    [ERR] {title[:50]}: {exc}")
                    continue

                if not revisions:
                    completed_articles.add(art_key)
                    _save_progress(completed_articles)
                    continue

                # ── Build rows ────────────────────────────────────────────────
                rows = []
                for rev in revisions:
                    ts        = rev.get("timestamp", "")
                    year, per = _year_period(ts)
                    uname     = rev.get("user", "")
                    is_a      = rev.get("_anon", _is_anon(uname))
                    if not is_a and uname and uname not in contrib_cache and uname not in new_users_seen:
                        new_users_seen.append(uname)
                    rows.append({
                        "article_title"     : title,
                        "pageid"            : pageid,
                        "continuum"         : cont_key,
                        "category"          : category,
                        "continuum_position": position,
                        "revision_id"       : rev.get("revid", ""),
                        "parent_id"         : rev.get("parentid", ""),
                        "timestamp"         : ts,
                        "year"              : year,
                        "year_period"       : per,
                        "username"          : uname,
                        "is_anon"           : is_a,
                        "edit_size_bytes"   : rev.get("size", 0),
                        "size_delta_bytes"  : rev.get("_delta", 0),
                        "comment"           : rev.get("parsedcomment", rev.get("comment", "")),
                        "is_revert"         : bool(re.search(r"\b(undo|undid|revert|reverted|reverting)\b", rev.get("parsedcomment", rev.get("comment", "")).lower())),
                        "gender"            : contrib_cache.get(uname, {}).get("gender", ""),
                        "gender_source"     : contrib_cache.get(uname, {}).get("gender_source", ""),
                    })

                # ── Stream write ──────────────────────────────────────────────
                shard_path, shard_rows = _append_to_shard(rows, shard_path, shard_rows)
                completed_articles.add(art_key)
                _save_progress(completed_articles)

                cat_new            += 1
                articles_this_run  += 1
                revisions_this_run += len(rows)

                # ── Gender resolution batch ───────────────────────────────────
                # NOTE: GenderizeLimitReached propagates out of this block
                if len(new_users_seen) >= GENDER_BATCH:
                    print(f"\\n    [gender] resolving {len(new_users_seen)} new users …", flush=True)
                    resolve_genders(new_users_seen, contrib_cache)   # may raise
                    new_users_seen.clear()
                    _flush_cache()

                # ── Periodic chart update ─────────────────────────────────────
                if articles_this_run % CHART_INTERVAL == 0:
                    print(f"\n    [charts] updating after {articles_this_run} articles …", flush=True)
                    render_charts(contrib_cache)

            print(f"→ {len(articles)} articles, {cat_new} new, {cat_skipped} filtered")

    # ── All continuums exhausted ──────────────────────────────────────────────
    print("\\n" + "=" * 62)
    print("All articles processed!")
    if new_users_seen:
        print(f"Resolving final {len(new_users_seen)} users …")
        resolve_genders(new_users_seen, contrib_cache)
        new_users_seen.clear()
    _flush_cache()
    render_charts(contrib_cache)
    print(f"  Articles this run  : {articles_this_run:,}")
    print(f"  Revisions this run : {revisions_this_run:,}")
    print("=" * 62)

except GenderizeLimitReached as exc:
    # ── Clean stop on genderize.io quota ─────────────────────────────────────
    print("\\n" + "!" * 62)
    print("STOPPED — genderize.io daily limit reached")
    print(str(exc))
    print("Saving all progress to Drive …")
    if new_users_seen:
        # add them to cache as unknown so they get a record
        for u in new_users_seen:
            if u not in contrib_cache:
                contrib_cache[u] = {"gender": "unknown", "gender_source": "pending_genderize",
                                    "global_editcount": 0, "registration_date": ""}
    _flush_cache()
    render_charts(contrib_cache)
    print(f"  Articles this run  : {articles_this_run:,}")
    print(f"  Revisions this run : {revisions_this_run:,}")
    print(f"  Total done         : {len(completed_articles):,}")
    print("  Resume tomorrow by re-running Config → Setup → Gender Engine → Charts → Main Loop")
    print("!" * 62)'''))

# ── Verify ────────────────────────────────────────────────────────────────────
CELLS.append(md_cell("verify-header", '''\
## Verification & Progress Summary

Run this cell at **any time** — it reads Drive data without modifying anything.
Safe to run while the main loop is paused between Colab sessions.'''))

CELLS.append(code_cell("verify", '''\
# ╔══════════════════════════════════════════════════════════════╗
# ║               VERIFICATION & PROGRESS SUMMARY               ║
# ╚══════════════════════════════════════════════════════════════╝
from collections import Counter
SEP = "=" * 62

revdf  = _read_all_revisions()
contdf = pd.read_csv(CONTRIBUTORS_CSV) if Path(CONTRIBUTORS_CSV).exists() else pd.DataFrame()
artdf  = pd.read_csv(ARTICLES_CSV)     if Path(ARTICLES_CSV).exists()     else pd.DataFrame()

print(SEP)
print("COLLECTION VERIFICATION SUMMARY")
print(SEP)

# ── Shard inventory ───────────────────────────────────────────────────────────
shards = _all_shard_paths()
print(f"\\n-- Shard inventory ({len(shards)} files) --")
for sp in shards:
    sz = Path(sp).stat().st_size // 1024
    with open(sp) as f:
        rows = sum(1 for _ in f) - 1
    print(f"  {Path(sp).name}  {rows:>8,} rows   {sz:>6,} KB")

# ── Row counts ────────────────────────────────────────────────────────────────
print(f"\\n-- Dataset totals --")
print(f"  revisions.csv (all shards) : {len(revdf):>10,} rows")
print(f"  contributors.csv           : {len(contdf):>10,} rows")
print(f"  articles.csv               : {len(artdf):>10,} rows")

if revdf.empty:
    print("\\nNo revision data yet.")
else:
    is_anon = revdf["is_anon"].astype(str).str.lower() == "true"
    named   = revdf[~is_anon]

    print("\\n-- Anonymous vs named revisions --")
    print(f"  Named     : {len(named):>8,}  ({len(named)/len(revdf)*100:.1f}%)")
    print(f"  Anonymous : {int(is_anon.sum()):>8,}  ({is_anon.sum()/len(revdf)*100:.1f}%)")

    if "gender" in revdf.columns:
        print("\\n-- Gender distribution (named revisions only) --")
        for g, n in named["gender"].value_counts().items():
            print(f"  {g:<12}: {n:>8,}  ({n/len(named)*100:.1f}%)")

    print("\\n-- Revisions by continuum --")
    for cont, n in revdf["continuum"].value_counts().items():
        print(f"  {cont:<20}: {n:>8,}")

    print("\\n-- Revisions by year period --")
    pc = revdf["year_period"].value_counts()
    for p in ["2005-2009", "2010-2014", "2015-2019", "2020-2024", "2025-2026", "Unknown"]:
        if p in pc.index:
            print(f"  {p} : {pc[p]:>8,}")

    if not artdf.empty:
        print("\\n-- Top 10 most-edited articles --")
        top = artdf.nlargest(10, "total_revisions")[
            ["article_title", "continuum", "category", "total_revisions"]]
        print(top.to_string(index=False))

if not contdf.empty:
    print("\\n-- Gender resolution sources --")
    for src, n in contdf["gender_source"].value_counts().items():
        print(f"  {src:<22}: {n:>6,}  ({n/len(contdf)*100:.1f}%)")

print(f"\\n  Charts: {CHARTS_DIR}")
print(f"  Progress tracker: {len(_load_progress()):,} articles marked done")
print(SEP)'''))

# ── Build notebook JSON ────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "colab": {"name": "wikihow_data_collection.ipynb", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": CELLS,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Written: {len(CELLS)} cells -> {OUT}")