"""
HCDE 530 — Met Museum Collection API exercise (public API, no key required).

The Met documents object details at:
  GET https://collectionapi.metmuseum.org/public/collection/v1/objects/{objectID}

There is no bulk "download everything" URL at .../objects with no ID, so this
script first calls /search to get object IDs, then calls /objects/{id} for each.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def load_local_env():
    """Load KEY=VALUE lines from a .env file next to this script into os.environ.

    The Met Collection API used here does **not** require an API key, but this matches
    the course pattern: keep optional settings (or future keys) out of the code and
    out of git by using a local .env file (listed in .gitignore).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                continue
            key = key.strip()
            value = value.strip().strip("'\"")
            # Do not overwrite variables you already exported in the terminal session.
            os.environ.setdefault(key, value)


load_local_env()

# Base path for the Collection API (all requests start from here).
COLLECTION_API_BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

# Optional: override search text without editing code (can be set in .env or the terminal).
# Example: MET_SEARCH_QUERY="egypt" python3 fetch_met_museum_objects.py
SEARCH_QUERY = os.environ.get("MET_SEARCH_QUERY", "gold")

# Optional: cap how many objects we fetch so the script finishes in reasonable time.
MAX_OBJECTS = int(os.environ.get("MET_MAX_OBJECTS", "60"))

# Met docs: stay **under** ~80 requests/second. That is a *ceiling*, not a target.
# With one request at a time, 80/sec would mean spacing ≥ 1/80 ≈ 0.0125s between calls.
# Default 0.35s between object-detail calls ≈ 2.9/sec — well under the limit, and gentler
# on the CDN (reduces random HTTP 403s). Lower MET_REQUEST_DELAY_SEC only if you need speed.
REQUEST_DELAY_SEC = float(os.environ.get("MET_REQUEST_DELAY_SEC", "0.35"))

# CSV written next to this script.
OUTPUT_CSV = "met_museum_objects.csv"

# --- Endpoints this script uses (Met Collection API v1) ---
#
# 1) GET {COLLECTION_API_BASE}/search?q=<text>
#    Parameters we use:
#      - q (required): free-text search string (here: SEARCH_QUERY, e.g. "gold").
#    The Met supports more query parameters (departmentIds, geoLocation, date range, etc.);
#    this script keeps it minimal and only passes "q".
#    JSON returned (simplified):
#      {
#        "total": <how many matches exist overall>,
#        "objectIDs": [<numeric id>, <numeric id>, ...]   # ordered list of object IDs to request next
#      }
#
# 2) GET {COLLECTION_API_BASE}/objects/{objectID}
#    Parameters we use:
#      - objectID (path): the integer ID from "objectIDs" above.
#    JSON returned: one big object with many keys (title, department, constituents, etc.).
#    We only copy the keys listed in OUTPUT_FIELDS into the CSV (see meanings below).
#
# CSV columns / JSON keys we extract (blank in CSV means the Met had no value / null):
OUTPUT_FIELDS = [
    "objectID",  # Met's unique ID for this artwork/object (integer in JSON).
    "isHighlight",  # True if the Met flags it as a highlighted collection object (bool).
    "department",  # Curatorial department name, e.g. "European Paintings" (string).
    "title",  # Object title or short descriptive name (string).
    "culture",  # Culture of origin or association, when known (string).
    "medium",  # Materials / technique description, e.g. "Oil on canvas" (string).
    "objectBeginDate",  # Start of date range or single year as provided by the museum (often int/string).
    "period",  # Historical / stylistic period label when provided (string).
    "artistDisplayName",  # Primary maker or artist name as shown to visitors (string).
    "artistNationality",  # Nationality label for the primary artist when provided (string).
]


def fetch_json(url):
    """GET JSON from the Met API with small retries if the server rate-limits us.

    A plain ``Python-urllib/...`` user-agent (or very fast back-to-back calls) often
    triggers **HTTP 403 Forbidden** from the museum's CDN. Spacing requests out plus a
    normal browser-style User-Agent reduces that risk.
    """
    headers = {
        "Accept": "application/json",
        # Browser-like UA: some CDNs block or throttle obvious script clients.
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 HCDE530/1.0"
        ),
    }
    # How many attempts for a single URL if the server returns 403/429 (rate limit / block).
    retries = int(os.environ.get("MET_FETCH_RETRIES", "4"))
    # Base seconds for exponential backoff: wait backoff, then 2x, then 4x, ... between retries.
    backoff = float(os.environ.get("MET_FETCH_BACKOFF_SEC", "1.0"))

    last_error = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            # urlopen performs the GET; read() returns raw bytes we decode to JSON.
            with urllib.request.urlopen(req, timeout=45) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return json.loads(resp.read().decode(charset))
        except urllib.error.HTTPError as e:
            last_error = e
            # 429 = too many requests; 403 sometimes appears when throttled — wait and retry.
            if e.code in (403, 429) and attempt < retries - 1:
                wait = backoff * (2**attempt)
                time.sleep(wait)
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("fetch_json: unreachable")


def search_object_ids(query, limit):
    # Call /search with only "q" (see OUTPUT_FIELDS / endpoint notes above for the response shape).
    safe_query = urllib.parse.quote(query)  # encode spaces/special characters for the URL query
    url = f"{COLLECTION_API_BASE}/search?q={safe_query}"
    # Response: {"total": <int>, "objectIDs": [<int>, ...]} — see big comment block above OUTPUT_FIELDS.
    payload = fetch_json(url)
    ids = payload.get("objectIDs") or []
    # "limit" is our script cap, not an API parameter — we only fetch details for the first N IDs.
    return ids[:limit]


def extract_fields(obj):
    # Map one /objects/{id} JSON document into a flat dict row for csv.DictWriter.
    # "obj" has many keys from the Met; we only keep OUTPUT_FIELDS so the CSV stays readable.
    row = {}
    for key in OUTPUT_FIELDS:
        if key == "objectID":
            row[key] = obj.get("objectID", "")
        else:
            val = obj.get(key, "")
            if isinstance(val, bool):
                row[key] = val
            else:
                row[key] = val if val is not None else ""
    return row


def main():
    print(f"Searching Met Collection for: {SEARCH_QUERY!r} (max {MAX_OBJECTS} objects)\n")

    try:
        object_ids = search_object_ids(SEARCH_QUERY, MAX_OBJECTS)
    except urllib.error.URLError as e:
        print(f"Search request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not object_ids:
        print("No object IDs returned from search.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for i, oid in enumerate(object_ids, start=1):
        # Be polite: a short pause between calls lowers the chance of a 403 from rate limits.
        if i > 1:
            time.sleep(REQUEST_DELAY_SEC)

        # Detail endpoint: returns one JSON object per ID (see doc block above for fields we keep).
        detail_url = f"{COLLECTION_API_BASE}/objects/{oid}"
        try:
            obj = fetch_json(detail_url)  # full record; extract_fields() pulls the columns we need
        except urllib.error.HTTPError as e:
            # Some IDs can 404 or be unavailable; skip instead of crashing the whole run.
            if e.code == 404:
                print(f"  [{i}/{len(object_ids)}] skip {oid}: not found")
                continue
            if e.code in (403, 429):
                print(
                    f"  [{i}/{len(object_ids)}] skip {oid}: HTTP {e.code} "
                    f"(try raising MET_REQUEST_DELAY_SEC, e.g. 0.6)",
                    file=sys.stderr,
                )
                continue
            raise

        # Skip records that are not full objects (API sometimes returns a small error payload).
        if not obj.get("objectID"):
            print(f"  [{i}/{len(object_ids)}] skip {oid}: incomplete payload")
            continue

        # Extract the assignment fields: highlights, cataloguing, materials, dating, artist info.
        rows.append(extract_fields(obj))
        title = (obj.get("title") or "")[:60]
        print(f"  [{i}/{len(object_ids)}] ok {oid}: {title}")

    if not rows:
        print("No rows to write.", file=sys.stderr)
        sys.exit(1)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
