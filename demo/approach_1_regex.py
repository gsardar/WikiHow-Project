"""
APPROACH 1 — Simple Regex Extraction (SUCCEEDS)
================================================
Profile : User:RubyRoseRain  — has explicit "Pronouns: she/her"
Browser : Headed, maximised, using your native Chrome session so
          wikihow loads logged in.

Expected result: SUCCESS -> Female
"""

import re
import csv
import os
import base64

from seleniumbase import SB

DEMO_DIR      = os.path.dirname(os.path.abspath(__file__))
PROFILE_URL   = "https://www.wikihow.com/User:RubyRoseRain"
OUTPUT_PDF    = os.path.join(DEMO_DIR, "approach1_profile_context.pdf")
OUTPUT_CSV    = os.path.join(DEMO_DIR, "demo_results_regex.csv")
USER_DATA_DIR = os.path.abspath(os.path.join(DEMO_DIR, "..", "data", "native_session"))


def simple_regex_extractor(text):
    """Rigid pattern matching — only catches standard pronoun formats."""
    patterns = [
        (r"\bshe/her\b",          "Female"),
        (r"\bhe/him\b",           "Male"),
        (r"\bthey/them\b",        "Non-Binary"),
        (r"Pronouns?:\s*she/her", "Female"),
        (r"Pronouns?:\s*he/him",  "Male"),
    ]
    for pat, gender in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return gender
    return "Unknown"


def run():
    print("=" * 60)
    print("  APPROACH 1 — Simple Regex")
    print("=" * 60)
    print(f"  Profile : {PROFILE_URL}")
    print()

    with SB(
        uc=True,
        headless=False,
        maximize=True,
        user_data_dir=USER_DATA_DIR,
    ) as sb:

        print("[Browser] Loading profile ...")
        sb.open(PROFILE_URL)
        sb.sleep(3)

        # Print to PDF for reference
        print(f"[Browser] Saving PDF -> {OUTPUT_PDF}")
        data = sb.driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
        with open(OUTPUT_PDF, "wb") as f:
            f.write(base64.b64decode(data["data"]))

        page_text = sb.get_text("body")

        print("\n[Regex] Running pattern matching ...")
        detected = simple_regex_extractor(page_text)
        status   = "SUCCESS" if detected != "Unknown" else "FAIL"

        print(f"[Regex] Detected Gender : {detected}")
        print(f"[Regex] Status          : [{status}]")

        sb.sleep(4)   # hold for screen recording

    rows = [{
        "User":    "RubyRoseRain",
        "URL":     PROFILE_URL,
        "Method":  "Simple Regex",
        "Gender":  detected,
        "Status":  status,
        "PDF":     OUTPUT_PDF,
    }]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[Output] {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    run()
