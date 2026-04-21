"""
timing_test.py
==============
Measures real-world API timing for the WikiHow data collection pipeline.
Tests ARTICLES_PER_CAT articles per category for the domestic continuum (10 categories).

Run with:  py timing_test.py

Reports per-article and per-category breakdowns for:
  - Category article listing
  - Revision fetching
  - Tier 1 gender (MediaWiki batch)
  - Tier 2 gender (profile pronoun scan) -- sampled only
"""

import sys, io, os, time, re, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ARTICLES_PER_CAT = 3    # how many articles to test per category
T2_SAMPLE        = 5    # max users to run tier-2 profile scan on
RATE_LIMIT       = 1.0  # seconds between api calls

BASE_URL   = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (test) - timing benchmark"

# Domestic continuum -- all 10 categories (verified WikiHow names)
CATEGORIES = [
    ("Babies and Infants", 0), ("Baking", 1), ("Home Decor", 2),
    ("Laundry", 3), ("Gardening", 4), ("Personal Finance", 5),
    ("Home Improvement", 6), ("Appliance Repair", 7),
    ("Plumbing", 8), ("Electrical Wiring", 9),
]

_last_req = 0.0

def _req(params, retries=5):
    global _last_req
    params.setdefault("format", "json")
    for attempt in range(1, retries + 1):
        gap = time.time() - _last_req
        if gap < RATE_LIMIT:
            time.sleep(RATE_LIMIT - gap)
        try:
            r = requests.get(BASE_URL, params=params,
                             headers={"User-Agent": USER_AGENT}, timeout=20)
            _last_req = time.time()
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                code = data["error"].get("code", "")
                if "ratelimit" in code.lower():
                    time.sleep(min(2**attempt + 5, 60))
                    continue
            return data
        except Exception as exc:
            if attempt == retries:
                raise
            time.sleep(2**attempt)


def get_articles(category, limit=ARTICLES_PER_CAT):
    cat = f"Category:{category}"
    data = _req({"action": "query", "list": "categorymembers",
                 "cmtitle": cat, "cmlimit": 10, "cmtype": "page"})
    return data.get("query", {}).get("categorymembers", [])[:limit]


def get_revisions(title):
    results = []
    params = {"action": "query", "prop": "revisions", "titles": title,
              "rvprop": "ids|user|timestamp|size", "rvlimit": 500}
    while True:
        data = _req(params)
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return []
            results.extend(page.get("revisions", []))
        cont = data.get("continue", {})
        if "rvcontinue" not in cont:
            break
        params["rvcontinue"] = cont["rvcontinue"]
    return results


def tier1_gender(usernames):
    result = {}
    chunk = usernames[:50]
    data = _req({"action": "query", "list": "users",
                 "ususers": "|".join(chunk), "usprop": "gender"})
    for u in data.get("query", {}).get("users", []):
        result[u["name"]] = u.get("gender", "unknown")
    return result


def tier2_profile(username):
    data = _req({"action": "query", "titles": f"User:{username}",
                 "prop": "revisions", "rvprop": "content", "rvslots": "main"})
    text = ""
    for page in data.get("query", {}).get("pages", {}).values():
        revs = page.get("revisions", [])
        if revs:
            text = revs[0].get("slots", {}).get("main", {}).get("*", "")
    t = text.lower()
    if re.search(r"\b(she/her|he/him|they/them)\b", t):
        return "found_pronouns"
    return "no_pronouns"


# ── Run ───────────────────────────────────────────────────────────────────────
print("=" * 68)
print(f"WikiHow Pipeline -- Timing Benchmark")
print(f"  {ARTICLES_PER_CAT} articles per category x {len(CATEGORIES)} categories")
print("=" * 68)

results = []
all_users = []
total_start = time.time()

for cat_name, pos in CATEGORIES:
    print(f"\n[{pos}] {cat_name:<30}", end="", flush=True)

    t0 = time.time()
    articles = get_articles(cat_name)
    list_t = time.time() - t0
    print(f"  listing: {list_t:.1f}s  ({len(articles)} articles)", end="", flush=True)

    if not articles:
        print("  -> EMPTY (category not found on WikiHow)")
        continue

    cat_rev_t = 0
    cat_rev_n = 0
    cat_users = set()
    article_times = []

    for art in articles:
        t0 = time.time()
        revs = get_revisions(art["title"])
        rev_t = time.time() - t0
        cat_rev_t += rev_t
        cat_rev_n += len(revs)
        article_times.append((art["title"], len(revs), rev_t))
        cat_users.update(
            r.get("user", "") for r in revs
            if "anon" not in r and r.get("user", "")
        )

    all_users.extend(list(cat_users))
    avg_rev_t = cat_rev_t / max(len(articles), 1)
    print(f"\n    revisions: {cat_rev_t:.1f}s total  "
          f"({cat_rev_n} revs, avg {avg_rev_t:.1f}s/article, "
          f"{len(cat_users)} unique users)")
    for title, n, t in article_times:
        print(f"      {title[:50]:<50}  {n:>4} revs  {t:.1f}s")

    results.append({
        "category": cat_name,
        "articles": len(articles),
        "list_t":   list_t,
        "rev_t":    cat_rev_t,
        "revisions": cat_rev_n,
        "users":    len(cat_users),
    })

# ── Tier 1: MediaWiki batch gender lookup ─────────────────────────────────────
print(f"\n{'─'*68}")
unique_users = list(dict.fromkeys(all_users))[:50]
print(f"Tier 1 (MediaWiki batch): {len(unique_users)} unique users ...")
t0 = time.time()
t1_result = tier1_gender(unique_users)
t1_t = time.time() - t0
t1_resolved = sum(1 for g in t1_result.values() if g != "unknown")
print(f"  Time: {t1_t:.1f}s  ->  {t1_resolved}/{len(t1_result)} resolved "
      f"({t1_resolved/max(len(t1_result),1)*100:.0f}%)")
t1_per_user = t1_t / max(len(unique_users), 1)

# ── Tier 2: Profile pronoun scan (sampled) ────────────────────────────────────
t2_cands = [u for u, g in t1_result.items() if g == "unknown"][:T2_SAMPLE]
print(f"\nTier 2 (profile scan): sampling {len(t2_cands)} unknown users ...")
t2_times = []
for uname in t2_cands:
    t0 = time.time()
    outcome = tier2_profile(uname)
    t2_times.append(time.time() - t0)
    print(f"  {uname:<35}  {outcome}  ({t2_times[-1]:.1f}s)")
t2_avg = sum(t2_times) / max(len(t2_times), 1)

# ── Summary ───────────────────────────────────────────────────────────────────
total_t = time.time() - total_start

print(f"\n{'='*68}")
print("TIMING SUMMARY")
print(f"{'='*68}")
print(f"  Total benchmark time   : {total_t:.1f}s")
print()
print(f"  {'Category':<25} {'Articles':>8} {'Revs':>6} {'List t':>7} {'Rev t':>7} {'Users':>6}")
print(f"  {'-'*63}")
for r in results:
    print(f"  {r['category']:<25} {r['articles']:>8} {r['revisions']:>6} "
          f"{r['list_t']:>6.1f}s {r['rev_t']:>6.1f}s {r['users']:>6}")

tot_arts    = sum(r["articles"] for r in results)
tot_revs    = sum(r["revisions"] for r in results)
tot_rev_t   = sum(r["rev_t"] for r in results)
tot_users   = sum(r["users"] for r in results)
avg_per_art = tot_rev_t / max(tot_arts, 1)

print(f"\n  Total articles fetched   : {tot_arts}")
print(f"  Total revisions fetched  : {tot_revs:,}")
print(f"  Avg time per article     : {avg_per_art:.1f}s  (revision fetch only)")
print(f"  Tier 1 gender time       : {t1_t:.1f}s for {len(unique_users)} users  "
      f"({t1_per_user:.2f}s/user -- batch call)")
print(f"  Tier 2 profile time      : {t2_avg:.1f}s/user  (individual calls)")

# ── Extrapolations ────────────────────────────────────────────────────────────
print(f"\n  EXTRAPOLATIONS (assuming ~50 articles/category, 40 categories total):")
est_arts        = 50 * 40
est_rev_t       = avg_per_art * est_arts
est_u_per_art   = tot_users / max(tot_arts, 1)
est_total_users = int(est_u_per_art * est_arts * 0.4)   # ~40% unique across all
est_t1_t        = t1_per_user * est_total_users
t2_fraction     = 1 - (t1_resolved / max(len(t1_result), 1))
est_t2_t        = t2_avg * int(est_total_users * t2_fraction)

print(f"    Est. total articles         : {est_arts:,}")
print(f"    Est. revision fetch time    : {est_rev_t/3600:.1f}h")
print(f"    Est. unique contributors    : ~{est_total_users:,}")
print(f"    Est. Tier 1 (batch) time    : {est_t1_t/3600:.2f}h")
print(f"    Est. Tier 2 (per-call) time : {est_t2_t/3600:.1f}h  (for ~{t2_fraction*100:.0f}% unknowns)")
print(f"  NOTE: genderize.io (Tier 3) cap: ~1,000 lookups/day on free plan.")
print(f"{'='*68}")
