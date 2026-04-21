
"""
WikiHow Mass Extraction Orchestrator
=====================================
Reads the master article CSV, extracts all article slugs,
and runs deep_contribution_extractor.py for each one sequentially
with full progress tracking, resume support, and a live manifest.

Usage:
    python scripts/run_all_extractions.py
    python scripts/run_all_extractions.py --continuum domestic
    python scripts/run_all_extractions.py --limit 10   (test mode: first 10 articles)
"""

import os
import sys
import csv
import json
import time
import argparse
import subprocess
import re
from datetime import datetime
import msvcrt  # Windows-specific key detection

def check_safe_stop():
    """Check if the 'S' key was pressed to signal a graceful exit."""
    if msvcrt.kbhit():
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 's':
            print("\n\n [!] SAFE-STOP SIGNAL RECEIVED. Finishing current article and exiting...")
            return True
    return False

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV = os.path.join(BASE_DIR, "data", "DataVersions", "v1", "backup1", "discovery", "domestic", "cleaned_domestic_master.csv")
OUT_DIR    = os.path.join(BASE_DIR, "data", "contributions", "continuum")
MANIFEST   = os.path.join(BASE_DIR, "data", "extraction_manifest.json")

CONTINUUM_MAP = {
    # Domestic Continuum
    "Baby Care":               ("domestic", "baby_care"),
    "Baking":                  ("domestic", "baking"),
    "Electrical Wiring":       ("domestic", "electrical"),
    "Gardening":               ("domestic", "gardening"),
    "Home-and-Garden":         ("domestic", "home_garden"),
    "Housekeeping":            ("domestic", "housekeeping"),
    "Interior Design":         ("domestic", "interior_design"),
    "Laundry":                 ("domestic", "laundry"),
    "Personal Care":           ("domestic", "personal_care"),
    "Pets":                    ("domestic", "pets"),
    "Relationships":           ("domestic", "relationships"),
}

def load_manifest():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": {}, "failed": {}, "skipped": [], "last_updated": None}

def save_manifest(manifest):
    manifest["last_updated"] = datetime.now().isoformat()
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def title_to_slug(title: str) -> str:
    """Convert Google/WikiHow article title to a clean slug for the extractor."""
    # Strip trailing qualifiers like "(with Pictures)"
    title = re.sub(r"\s*\(with Pictures\).*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*- how to articles.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^How to ", "", title, flags=re.IGNORECASE)
    # Convert spaces to hyphens, strip non-alphanum
    slug = title.strip().replace(" ", "-")
    slug = re.sub(r"[^\w\-]", "", slug)
    return slug

def is_already_done(slug, continuum, subcategory, manifest):
    """Check if this article already has a valid completed JSON."""
    key = f"{continuum}/{subcategory}/{slug}"
    if key in manifest["completed"]:
        return True
    # Also check filesystem
    json_path = os.path.join(OUT_DIR, continuum, subcategory, f"{slug}.json")
    if os.path.exists(json_path):
        try:
            size = os.path.getsize(json_path)
            if size > 5000:  # At least 5KB = has some real data
                manifest["completed"][key] = {
                    "size_bytes": size,
                    "completed_at": datetime.fromtimestamp(os.path.getmtime(json_path)).isoformat()
                }
                return True
        except:
            pass
    return False

def run_extraction(slug, continuum, subcategory):
    """Run the extractor script as a subprocess and return success/failure."""
    cmd = [
        sys.executable,
        os.path.join(BASE_DIR, "scripts", "deep_contribution_extractor.py"),
        slug,
        "--continuum", continuum,
        "--subcategory", subcategory,
    ]
    print(f"\n  [RUN] python deep_contribution_extractor.py \"{slug}\" --continuum {continuum} --subcategory {subcategory}")
    start = time.time()
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, timeout=1800, capture_output=False)
        elapsed = time.time() - start
        return result.returncode == 0, elapsed
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {slug} timed out after 30 minutes.")
        return False, 1800
    except Exception as e:
        print(f"  [ERROR] {slug}: {e}")
        return False, 0

def print_progress(done, total, failed, start_time):
    elapsed = time.time() - start_time
    rate = done / elapsed if elapsed > 0 else 0
    remaining = (total - done) / rate if rate > 0 else float("inf")
    pct = done / total * 100 if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"  PROGRESS: {done}/{total} ({pct:.1f}%) | Failed: {failed}")
    if remaining < float("inf"):
        hrs = int(remaining // 3600)
        mins = int((remaining % 3600) // 60)
        print(f"  ETA: ~{hrs}h {mins}m remaining")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--continuum", default=None, help="Filter to one continuum (e.g. domestic)")
    parser.add_argument("--limit",     type=int, default=0, help="Max articles to process (0=all)")
    parser.add_argument("--dryrun",    action="store_true", help="Print what would run, don't execute")
    args = parser.parse_args()

    # Load master article list
    articles = []
    with open(MASTER_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            category    = row.get("Category", "").strip()
            google_title = row.get("Google Title", "").strip()
            real_title   = row.get("Real WikiHow Title", "").strip()
            title = real_title or google_title
            if not title or not category: continue
            slug = title_to_slug(title)
            if not slug: continue
            mapping = CONTINUUM_MAP.get(category)
            if not mapping: continue
            continuum, subcategory = mapping
            if args.continuum and continuum != args.continuum: continue
            articles.append((slug, continuum, subcategory, title))

    # Deduplicate slugs within same continuum/subcategory
    seen = set()
    unique = []
    for item in articles:
        key = (item[0], item[1], item[2])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    articles = unique

    if args.limit:
        articles = articles[:args.limit]

    manifest = load_manifest()
    total    = len(articles)
    done     = 0
    failed   = 0
    start_t  = time.time()

    print(f"\n{'='*60}")
    print(f"  WIKIHOW MASS EXTRACTOR — ORCHESTRATOR")
    print(f"  Articles queued  : {total}")
    print(f"  DryRun mode      : {args.dryrun}")
    print(f"  Manifest path    : {MANIFEST}")
    print(f"{'='*60}")

    for i, (slug, continuum, subcategory, title) in enumerate(articles):
        manifest_key = f"{continuum}/{subcategory}/{slug}"

        print(f"\n[{i+1}/{total}] {slug}  ({continuum}/{subcategory})")

        # Resume check
        if is_already_done(slug, continuum, subcategory, manifest):
            print(f"  [SKIP] Already completed.")
            done += 1
            save_manifest(manifest)
            continue

        if manifest_key in manifest.get("failed", {}):
            fail_count = manifest["failed"][manifest_key].get("attempts", 0)
            if fail_count >= 3:
                print(f"  [SKIP] Failed {fail_count}x before. Skipping permanently.")
                continue

        if args.dryrun:
            print(f"  [DRYRUN] Would extract: {slug}")
            done += 1
            continue

        success, elapsed = run_extraction(slug, continuum, subcategory)

        if success:
            done += 1
            json_path = os.path.join(OUT_DIR, continuum, subcategory, f"{slug}.json")
            size = os.path.getsize(json_path) if os.path.exists(json_path) else 0
            manifest["completed"][manifest_key] = {
                "title": title,
                "slug": slug,
                "size_bytes": size,
                "elapsed_seconds": round(elapsed),
                "completed_at": datetime.now().isoformat()
            }
            manifest["failed"].pop(manifest_key, None)
            print(f"  [DONE] {slug} ({size/1024:.0f}KB, {elapsed:.0f}s)")
        else:
            failed += 1
            if manifest_key not in manifest["failed"]:
                manifest["failed"][manifest_key] = {"attempts": 0}
            manifest["failed"][manifest_key]["attempts"] += 1
            manifest["failed"][manifest_key]["last_attempt"] = datetime.now().isoformat()
            print(f"  [FAIL] {slug} — will retry on next run.")

        save_manifest(manifest)
        print_progress(done, total, failed, start_t)
        
        # Safe Stop Check
        if check_safe_stop():
            break
            
        time.sleep(2)  # Polite pause between articles

    print(f"\n{'='*60}")
    print(f"  EXTRACTION COMPLETE")
    print(f"  Completed : {done}")
    print(f"  Failed    : {failed}")
    print(f"  Manifest  : {MANIFEST}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
