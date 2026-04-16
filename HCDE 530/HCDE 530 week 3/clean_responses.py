"""Clean survey response CSV data.

Reads `responses.csv`, removes rows where `name` is empty, uppercases values in
the `role` column, and writes the cleaned rows to `responses_cleaned.csv`.
"""

import csv

INPUT_FILE = "responses.csv"
OUTPUT_FILE = "responses_cleaned.csv"


def is_empty(value):
    """Return True if a CSV field is missing or only whitespace."""
    return value is None or value.strip() == ""


with open(INPUT_FILE, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames or []

    cleaned_rows = []
    for row in reader:
        if is_empty(row.get("name", "")):
            continue

        row["role"] = row.get("role", "").upper()
        cleaned_rows.append(row)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Wrote {len(cleaned_rows)} cleaned rows to {OUTPUT_FILE}")
