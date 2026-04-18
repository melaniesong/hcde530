import csv

WORD_TO_INT = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20
}

def parse_experience_years(raw_value):
    # Clean one experience value so later math does not crash on messy text.
    # Returns an integer if possible, otherwise returns None so the row can be skipped.
    text = (raw_value or "").strip().lower()
    # First try normal integer parsing (e.g., "7")
    try:
        return int(text)
    except ValueError:
        pass
    # Then try word-based values (e.g., "fifteen")
    if text in WORD_TO_INT:
        return WORD_TO_INT[text]
    return None

def count_responses_by_normalized_role(rows):
    """Return a dictionary of role -> count using normalized role names.
    Each row's `role` value is stripped and title-cased so variations like
    "ux researcher" and "UX Researcher" are counted together.
    """
    role_counts = {}
    for row in rows:
    # Get role value safely, remove extra spaces, normalize capitalization
        role = row.get("role", "").strip().title()
    # Count the role if it exists, otherwise add it to the dictionary
        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts[role] = 1
    return role_counts

def clean_row(row):
    """Return one cleaned survey row with normalized text and parsed numbers."""
    satisfaction_text = row.get("satisfaction_score", "").strip()
    return {
        "response_id": row.get("response_id", "").strip(),
        "participant_name": row.get("participant_name", "").strip(),
        "role": row.get("role", "").strip().title(),
        "department": row.get("department", "").strip().title(),
        "age_range": row.get("age_range", "").strip(),
        "experience_years": parse_experience_years(row.get("experience_years", "")),
        "satisfaction_score": int(satisfaction_text) if satisfaction_text else None,
        "primary_tool": row.get("primary_tool", "").strip().lower(),
        "response_text": row.get("response_text", "").strip(),
    }

def extract_cleaned_figma_rows(rows):
    """Return cleaned rows for only the participants whose primary tool is Figma."""
    figma_rows = []
    for row in rows:
        cleaned = clean_row(row)
        if cleaned["primary_tool"] == "figma":
            figma_rows.append(cleaned)
    return figma_rows

def write_cleaned_figma_csv(rows, output_filename):
    """Write cleaned Figma-only rows to a new CSV file."""
    figma_rows = extract_cleaned_figma_rows(rows)
    fieldnames = [
        "response_id",
        "participant_name",
        "role",
        "department",
        "age_range",
        "experience_years",
        "satisfaction_score",
        "primary_tool",
        "response_text",
    ]
    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(figma_rows)


def summarize_data(cleaned_rows):
    """Return a short plain-language summary of cleaned survey rows.

    Covers total row count, distinct non-empty values in ``role``, and how many
    rows have an empty name. Names are read from ``name`` or ``participant_name``
    (whichever is present), matching :func:`clean_row`.
    """
    n = len(cleaned_rows)
    roles = []
    for row in cleaned_rows:
        r = (row.get("role") or "").strip()
        if r:
            roles.append(r)
    unique_roles = sorted(set(roles))
    unique_count = len(unique_roles)

    def row_name(row):
        return (row.get("name") or row.get("participant_name") or "").strip()

    empty_names = sum(1 for row in cleaned_rows if not row_name(row))

    if unique_count == 0:
        role_part = "There are no non-empty values in the role column."
    elif unique_count == 1:
        role_part = f"The only role listed is {unique_roles[0]}."
    else:
        listed = ", ".join(unique_roles[:-1]) + f", and {unique_roles[-1]}"
        role_part = (
            f"There are {unique_count} distinct roles: {listed}."
        )

    name_part = (
        f"There {'is' if empty_names == 1 else 'are'} {empty_names} row"
        f"{'s' if empty_names != 1 else ''} with an empty name field."
    )

    return (
        f"This dataset has {n} row{'s' if n != 1 else ''}. {role_part} {name_part}"
    )


# Load the survey data from a CSV file
filename = "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    # Loop through each CSV row and store it as a dictionary in `rows`.
    for row in reader:
        rows.append(row)

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

role_counts = count_responses_by_normalized_role(rows)

# Print the role counts
print("Responses by role:")
# Sort the role counts by role name
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")


#for row in rows:
    # This loop standardizes role labels and counts how many times each role appears.
#    role = row["role"].strip().title()
 #   if role in role_counts:
 #       role_counts[role] += 1
 #   else:
 #       role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
valid_experience_count = 0
for row in rows:
    # This loop parses each experience value and keeps only valid numeric values
    # for the average calculation.
    years = parse_experience_years(row.get("experience_years", ""))
    if years is None:
        continue
    total_experience += years
    valid_experience_count += 1
##total_experience += int(row["experience_years"])

if valid_experience_count > 0:
    avg_experience = total_experience / valid_experience_count
    print(f"\nAverage years of experience: {avg_experience:.1f}")
else:
    print("\nAverage years of experience: no valid data")
    
##avg_experience = total_experience / len(rows)
##print(f"\nAverage years of experience: {avg_experience:.1f}")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in rows:
    # This loop collects participant + score pairs for rows that have a score value.
    if row["satisfaction_score"].strip():
        scored_rows.append((row["participant_name"], int(row["satisfaction_score"])))

scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]



print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")

output_filename = "week3_analysis_figma.csv"
write_cleaned_figma_csv(rows, output_filename)
print(f"\nWrote cleaned Figma rows to {output_filename}")
