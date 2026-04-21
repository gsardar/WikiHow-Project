import sys
import os
import json
import argparse
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wikihow.api import get_revisions, get_article_details, get_talk_page, sync_browser_cookies, load_session_cookies, get_revision_diff

def classify_revisions(revisions, expert_name=None):
    # Basic classification and Revert detection
    for i, rev in enumerate(revisions):
        summary = rev.get("summary", "").lower()
        change = rev.get("change", 0)
        user = rev.get("user", "")
        rev_id = rev.get("id")
        
        rev["is_expert"] = (user == expert_name)
        rev["status"] = "active"
        
        if "rv" in summary or "revert" in summary or "undid" in summary:
            rev["contribution_type"] = "revert"
        elif "typo" in summary or "spelling" in summary or "grammar" in summary or "formatting" in summary:
            rev["contribution_type"] = "cleanup"
        elif "reference" in summary or "source" in summary or "cite" in summary:
            rev["contribution_type"] = "sourcing"
        elif abs(change) > 500:
            rev["contribution_type"] = "major_addition" if change > 0 else "major_deletion"
        elif change > 0:
            rev["contribution_type"] = "addition"
        elif change < 0:
            rev["contribution_type"] = "deletion"
        else:
            rev["contribution_type"] = "adjustment"

        # Look for reverts in newer revisions
        for j in range(i):
            newer_rev = revisions[j]
            newer_summary = newer_rev.get("summary", "").lower()
            if "revert" in newer_summary or "undid" in newer_summary:
                if (rev_id and str(rev_id) in newer_summary) or (user.lower() in newer_summary):
                    rev["status"] = "reverted"
                    rev["reverted_by"] = newer_rev.get("user")
                    break
    return revisions

def main():
    parser = argparse.ArgumentParser(description="Extract deep contribution data from a WikiHow article.")
    parser.add_argument("title", help="Article title (e.g. 'Bake a Cake')")
    parser.add_argument("--limit", type=int, default=0, help="Number of revisions to fetch (0 for Infinity)")
    parser.add_argument("--continuum", help="Research continuum")
    parser.add_argument("--subcategory", help="Article subcategory")
    args = parser.parse_args()

    load_session_cookies()
    title = args.title
    print(f"[*] Deep Extracting: {title}")

    # 1. Article Details
    print("  [1/3] Fetching featured authors and metadata...")
    details = get_article_details(title)
    if not details:
        print("  ERROR: Failed to fetch article details.")
        return
    
    expert_name = details.get("expert")

    # 2. Revisions Discovery
    print(f"  [2/3] Fetching {args.limit} revisions (Discovery)...")
    revisions = get_revisions(title, limit=args.limit)
    if not revisions:
        print("  ERROR: Failed to fetch any revisions. Aborting to protect existing data.")
        return
    revisions = classify_revisions(revisions, expert_name)

    # 3. Talk Page
    print("  [3/3] Fetching Talk page discussions...")
    discussions = get_talk_page(title)

    # Output path setup
    safe_title = re.sub(r'[^\w\-_\. ]', '_', title).replace(' ', '_')
    if args.continuum and args.subcategory:
        out_dir = os.path.join("data", "contributions", "continuum", args.continuum, args.subcategory)
    else:
        out_dir = os.path.join("data", "contributions")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_title}.json")

    # [SMART RESUME] Load existing data to avoid re-fetching
    if os.path.exists(out_path):
        print(f"[*] Found existing data for {title}. Attempting to Resume...")
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                def is_valid_diff(r):
                    ec = r.get("exact_contribution")
                    if not ec: return False
                    return bool(ec.get("added") or ec.get("removed"))

                old_rev_map = {r["id"]: r for r in old_data.get("revisions", []) if is_valid_diff(r)}
                print(f"    [+] Loaded {len(old_rev_map)} valid previously extracted contributions.")
                for rev in revisions:
                    if rev["id"] in old_rev_map:
                        rev["exact_contribution"] = old_rev_map[rev["id"]]["exact_contribution"]
        except Exception as e:
            print(f"    [!] Resume failed: {e}. Starting fresh.")

    def save_checkpoint(current_revisions):
        output = {
            "title": title,
            "continuum": args.continuum,
            "subcategory": args.subcategory,
            "timestamp": datetime.now().isoformat(),
            "co_authors_list": details.get("co_authors", []),
            "expert": expert_name,
            "expert_title": details.get("expert_title"),
            "stats": details.get("stats", {}),
            "revisions": current_revisions,
            "discussions": discussions
        }
        # Safety Backup
        if os.path.exists(out_path):
            import shutil
            shutil.copy2(out_path, out_path + ".tmp_bak")
            
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        # If successfully written, we keep the last stable one
        if os.path.exists(out_path + ".tmp_bak"):
             shutil.move(out_path + ".tmp_bak", out_path + ".bak")

    # [PASS 3] Parallel Fetch + Hot Save
    to_diff = [r for r in revisions if not r.get("exact_contribution") or (not r["exact_contribution"].get("added") and not r["exact_contribution"].get("removed"))]
    
    if to_diff:
        print(f"    [+] Swarming {len(to_diff)} contributions with Ironclad-Retry (6 Workers)...")
        _STOP_SWARM = False
        
        def fetch_worker(rev):
            nonlocal _STOP_SWARM
            if _STOP_SWARM: return None
            
            diff = get_revision_diff(rev["id"])
            if diff is None: # Actual failure after retries
                return False
                
            if "BLOCK_DETECTED" in diff.get("added", []):
                _STOP_SWARM = True
                return None
                
            rev["exact_contribution"] = diff
            return True

        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_rev = {executor.submit(fetch_worker, r): r for r in to_diff}
            count = 0
            for future in as_completed(future_to_rev):
                count += 1
                if count % 50 == 0:
                    print(f"        -> [HOT-SAVE] Milestone: {count}/{len(to_diff)} edits committed.")
                    save_checkpoint(revisions)
                if _STOP_SWARM:
                    print("\n[!!!] EMERGENCY STOP: Proxy Block Detected.")
                    break
    
    # Final Save
    save_checkpoint(revisions)
    
    # Save CSV summary
    import csv
    csv_path = out_path.replace(".json", "_summary.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Revision ID", "Timestamp", "User", "Is Expert", "Type", "Status", "Reverted By", "Change Size", "Summary"])
        for rev in revisions:
            writer.writerow([rev.get("id"), rev.get("timestamp"), rev.get("user"), rev.get("is_expert"), rev.get("contribution_type"), rev.get("status"), rev.get("reverted_by", ""), rev.get("change"), rev.get("summary")])

    print(f"\n[+] Extraction Successful!")
    print(f"    Master JSON: {out_path}")

if __name__ == "__main__":
    main()
