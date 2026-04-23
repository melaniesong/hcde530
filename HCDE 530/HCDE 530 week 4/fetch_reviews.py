"""
Fetch app reviews from the HCDE 530 Week 4 API, print category + helpful votes,
and save category, helpful_votes, and verified_purchase to a CSV file.

Uses only the Python standard library (no pip installs).
"""

import csv
import json
import sys
import urllib.error
import urllib.request

BASE_URL = "https://hcde530-week4-api.onrender.com"
REVIEWS_URL = f"{BASE_URL}/reviews?limit=500"
OUTPUT_CSV = "reviews_export.csv"


def fetch_json(url):
    req = urllib.request.Request(  # object describing this HTTP request (URL + headers) for urlopen
        url,
        headers={"Accept": "application/json", "User-Agent": "hcde530-week4-fetch/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def main():
    # 1) Call the API root (course endpoint)
    try:
        meta = fetch_json(f"{BASE_URL}/")
    except urllib.error.URLError as e:
        print(f"Could not reach API root: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"API: {meta.get('name', 'unknown')}")
    print(f"Description: {meta.get('description', '')}\n")

    # 2) Request review data (category, helpful votes, verified purchase)
    try:
        payload = fetch_json(REVIEWS_URL)
    except urllib.error.URLError as e:
        print(f"Could not fetch reviews: {e}", file=sys.stderr)
        sys.exit(1)

    reviews = payload.get("reviews") or []
    if not reviews:
        print("No reviews in response.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for r in reviews:
        rows.append(
            {
                "category": r.get("category", ""),
                "helpful_votes": r.get("helpful_votes", ""),
                "verified_purchase": r.get("verified_purchase", ""),
            }
        )

    # 3) Loop and print category + helpful votes
    print("category | helpful_votes")
    print("-" * 40)
    for row in rows:
        print(f"{row['category']} | {row['helpful_votes']}")

    # 4) Save to CSV
    fieldnames = ["category", "helpful_votes", "verified_purchase"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
