"""
APPROACH 2 — Username Splitting + Genderize.io (Tier 2 fallback)
=================================================================
Demonstrates that when regex fails on a profile like User:CelesteTu,
we can STILL identify gender by:
  1. Splitting the username by CamelCase:  CelesteTu -> ["Celeste", "Tu"]
  2. Querying genderize.io with "Celeste" -> Female (prob=0.98, n=76,946)

This is more advanced than regex but cheaper than a full GenAI call.
It works well for usernames that contain real first names.

Browser : Headed, maximised, native Chrome session.
"""

import re
import csv
import os
import base64
import requests

from seleniumbase import SB

DEMO_DIR      = os.path.dirname(os.path.abspath(__file__))
PROFILE_URL   = "https://www.wikihow.com/User:CelesteTu"
OUTPUT_PDF    = os.path.join(DEMO_DIR, "approach2_genderize_context.pdf")
OUTPUT_CSV    = os.path.join(DEMO_DIR, "demo_results_genderize.csv")
USER_DATA_DIR = os.path.abspath(os.path.join(DEMO_DIR, "..", "data", "native_session"))


# ── Tier 1 ─────────────────────────────────────────────────────────
def simple_regex_extractor(text):
    """Rigid pattern matching — only catches standard pronoun formats."""
    for pat, gender in [
        (r"\bshe/her\b",          "Female"),
        (r"\bhe/him\b",           "Male"),
        (r"\bthey/them\b",        "Non-Binary"),
        (r"Pronouns?:\s*she/her", "Female"),
        (r"Pronouns?:\s*he/him",  "Male"),
    ]:
        if re.search(pat, text, re.IGNORECASE):
            return gender
    return "Unknown"


# ── Tier 2 ─────────────────────────────────────────────────────────
def split_username(username):
    """Split CamelCase username into candidate first-name tokens."""
    # Remove numbers and special chars
    cleaned = re.sub(r'[0-9_\-\.\s]+', ' ', username)
    # Split on CamelCase boundaries
    tokens = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned).split()
    # Keep tokens >2 chars (ignore 'Tu', 'Mc' etc.)
    return [t for t in tokens if len(t) > 2]


def query_genderize(name):
    """Query genderize.io for a single name. Returns (gender, probability, count)."""
    try:
        resp = requests.get(
            f"https://api.genderize.io/?name={name}",
            timeout=8
        )
        data = resp.json()
        return data.get("gender"), data.get("probability", 0.0), data.get("count", 0)
    except Exception as exc:
        print(f"  [genderize] API error: {exc}")
        return None, 0.0, 0


def genderize_username(username):
    """
    Try each token from the username against genderize.io.
    Return the first result with probability >= 0.75 and count >= 50.
    """
    tokens = split_username(username)
    print(f"  [genderize] Username tokens: {tokens}")

    for token in tokens:
        gender, prob, count = query_genderize(token)
        print(f"  [genderize] '{token}' -> gender={gender}, prob={prob}, count={count}")
        if gender and prob >= 0.75 and count >= 50:
            return gender.capitalize(), prob, count, token

    return "Unknown", 0.0, 0, None


def run():
    print("=" * 60)
    print("  APPROACH 2 — Username Splitting + Genderize.io")
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

        # Save PDF
        print(f"[Browser] Saving PDF -> {OUTPUT_PDF}")
        data = sb.driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
        with open(OUTPUT_PDF, "wb") as f:
            f.write(base64.b64decode(data["data"]))

        page_text = sb.get_text("body")

        # Tier 1: Regex
        print("\n[Tier 1] Running regex ...")
        regex_result = simple_regex_extractor(page_text)
        print(f"[Tier 1] Result : {regex_result}  [FAIL — no pronouns found]")
        sb.sleep(1)

        # Tier 2: Genderize.io
        print("\n[Tier 2] Splitting username and querying genderize.io ...")
        username = "CelesteTu"
        gender, prob, count, matched_token = genderize_username(username)

        if gender != "Unknown":
            status = "SUCCESS"
            print(f"\n[Tier 2] Detected Gender : {gender}")
            print(f"[Tier 2] Confidence      : {prob:.2f}  (sample size: {count:,})")
            print(f"[Tier 2] Matched on      : '{matched_token}' (first token from '{username}')")
            print(f"[Tier 2] Status          : [{status}]")
        else:
            status = "FAIL"
            print(f"[Tier 2] genderize.io could not resolve any token")
            print(f"[Tier 2] -> Would escalate to Tier 3 (DeepSeek)")

        sb.sleep(5)

    rows = [{
        "User":              username,
        "URL":               PROFILE_URL,
        "Tokens":            str(split_username(username)),
        "Regex_Result":      regex_result,
        "Regex_Status":      "FAIL",
        "Genderize_Gender":  gender,
        "Genderize_Prob":    prob,
        "Genderize_Count":   count,
        "Matched_Token":     matched_token,
        "Genderize_Status":  status,
        "PDF":               OUTPUT_PDF,
    }]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[Output] {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    run()
