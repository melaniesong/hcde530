"""
Fetch reviews from the Week 4 API, rank helpful_votes, compute summary stats,
and save one CSV with per-review ranks plus dataset mean/median/mode/min/max.

Reuses fetch_json from fetch_reviews.py (stdlib only).
"""

import csv
import sys
from statistics import mean, median, multimode

import urllib.error

from fetch_reviews import BASE_URL, REVIEWS_URL, fetch_json

OUTPUT_CSV = "helpful_votes_analysis.csv"


def competition_ranks(reviews):
    """Sort by helpful_votes descending; ties share the same rank (1,2,2,4 style)."""
    sorted_rows = sorted(
        reviews,
        key=lambda r: (-int(r.get("helpful_votes") or 0), r.get("id", 0)),
    )
    ranked = []
    for i, row in enumerate(sorted_rows):
        if i == 0:
            rank = 1
        else:
            prev = sorted_rows[i - 1]
            cur_v = int(row.get("helpful_votes") or 0)
            prev_v = int(prev.get("helpful_votes") or 0)
            if cur_v == prev_v:
                rank = ranked[-1][1]
            else:
                rank = i + 1
        ranked.append((row, rank))
    return ranked


def format_mode(votes):
    modes = multimode(votes)
    if not modes:
        return ""
    if len(modes) <= 5:
        return "|".join(str(m) for m in sorted(modes))
    return f"{modes[0]} (+{len(modes) - 1} other modes)"


def main():
    # 1) API root
    try:
        meta = fetch_json(f"{BASE_URL}/")
    except urllib.error.URLError as e:
        print(f"Could not reach API root: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"API: {meta.get('name', 'unknown')}\n")

    # 2) Reviews (limit=500)
    try:
        payload = fetch_json(REVIEWS_URL)
    except urllib.error.URLError as e:
        print(f"Could not fetch reviews: {e}", file=sys.stderr)
        sys.exit(1)

    reviews = payload.get("reviews") or []
    if not reviews:
        print("No reviews in response.", file=sys.stderr)
        sys.exit(1)

    votes = [int(r.get("helpful_votes") or 0) for r in reviews]
    m_mean = mean(votes)
    m_median = median(votes)
    m_mode = format_mode(votes)
    m_min = min(votes)
    m_max = max(votes)

    print("Helpful votes — dataset summary")
    print(f"  count:  {len(votes)}")
    print(f"  mean:   {m_mean:.2f}")
    print(f"  median: {m_median}")
    print(f"  mode:   {m_mode}")
    print(f"  min:    {m_min}")
    print(f"  max:    {m_max}\n")

    ranked = competition_ranks(reviews)

    fieldnames = [
        "review_id",
        "helpful_votes",
        "rank",
        "dataset_mean",
        "dataset_median",
        "dataset_mode",
        "dataset_min",
        "dataset_max",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row, rank in ranked:
            writer.writerow(
                {
                    "review_id": row.get("id", ""),
                    "helpful_votes": row.get("helpful_votes", ""),
                    "rank": rank,
                    "dataset_mean": f"{m_mean:.6f}",
                    "dataset_median": m_median,
                    "dataset_mode": m_mode,
                    "dataset_min": m_min,
                    "dataset_max": m_max,
                }
            )

    print(f"Wrote {len(ranked)} ranked rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
