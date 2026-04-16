"""Count role frequency from responses.csv.

Processing rules:
1. Skip rows where the `name` field is empty or whitespace.
2. Normalize role values to uppercase so role labels count together.
3. Print role counts to the terminal.
4. Write role counts to role_counts.csv.
"""

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "responses.csv"
OUTPUT_FILE = BASE_DIR / "role_counts.csv"


def is_empty(value):
    """Return True if a CSV field is missing or only whitespace."""
    return value is None or value.strip() == ""


role_counts = {}

with open(INPUT_FILE, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        if is_empty(row.get("name", "")):
            continue

        role = row.get("role", "").strip().upper()
        if role == "":
            continue

        role_counts[role] = role_counts.get(role, 0) + 1

sorted_counts = sorted(role_counts.items(), key=lambda item: (-item[1], item[0]))

print("Role counts")
print("-" * 30)
for role, count in sorted_counts:
    print(f"{role:<24} {count}")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["role", "count"])
    writer.writerows(sorted_counts)

print()
print(f"Wrote {len(sorted_counts)} role counts to {OUTPUT_FILE.name}")
