import csv

WORD_TO_INT = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20
}

def parse_experience_years(raw_value):
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

# Load the survey data from a CSV file
filename = "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

for row in rows:
    role = row["role"].strip().title()
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

print("Responses by role:")
for role, count in sorted(role_counts.items()):
    print(f"  {role}: {count}")

# Calculate the average years of experience
total_experience = 0
valid_experience_count = 0
for row in rows:
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
    if row["satisfaction_score"].strip():
        scored_rows.append((row["participant_name"], int(row["satisfaction_score"])))

scored_rows.sort(key=lambda x: x[1], reverse=True)
top5 = scored_rows[:5]



print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")
