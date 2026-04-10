"""demo_word_count.py — read survey responses from a CSV and report word counts.

What this script does (in order):
1. Load every row from demo_responses.csv into a list of dicts.
2. For each row, count words in the response text and print a table row.
3. Print summary stats: how many responses, shortest/longest/average word count.
"""

import csv

# --- Load CSV into memory ----------------------------------------------------
filename = "demo_responses.csv"
responses = []

with open(filename, newline="", encoding="utf-8") as f:
    # DictReader maps each CSV row to a dict using the header names.
    reader = csv.DictReader(f)
    for row in reader:
        responses.append(row)


def count_words(response):
    """Return how many words are in a single response string.

    Words are split on whitespace (spaces, newlines, tabs). Multiple spaces
    between words still produce one split, so extra spacing does not inflate
    the count. Empty or whitespace-only strings count as zero words.

    Args:
        response: The free-text answer from one participant (a string).

    Returns:
        An integer: the number of words in that string.
    """
    return len(response.split())


# --- Print one line per response ---------------------------------------------
print(f"{'ID':<6} {'Role':<22} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 75)

# Stores one integer word-count per response; after the loop we use this list
# for min / max / average in the summary block below.
word_counts = []

# Loop once per survey row: each time through, we read one person's answers,
# count words in their long text response, save that number, and print a row.
for row in responses:
    # Each `row` is a dict keyed by CSV column name (participant_id, role, response).
    participant = row["participant_id"]
    role = row["role"]
    response = row["response"]

    # Word count: `count_words` splits the string on whitespace and counts pieces.
    count = count_words(response)
    # Keep the count so the summary can scan every count without re-reading the CSV.
    word_counts.append(count)

    # Show only the start of long answers so the table stays readable in the terminal.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    # Width specifiers (<6, <22, etc.) keep columns lined up under the header.
    print(f"{participant:<6} {role:<22} {count:<6} {preview}")

# --- Summary over all responses ----------------------------------------------
print()
print("── Summary ─────────────────────────────────")
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")
