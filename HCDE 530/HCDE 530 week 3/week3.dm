# Week 3 — Competency reflection (C2 and C5) + real-data risks

Related script(s): `week3_analysis_buggy.py`, `week3_survey_messy.csv` → cleaned output / Figma subset.

---

## 1) Which competency are you claiming?

**Check all that apply:**

- [x] **C2 — Code Literacy and Documentation**  
  Focus: reading code, explaining what it does, and how clear names / comments / structure help others (and future you) use and maintain it.

- [x] **C5 — Data Cleaning and Preparation**  
  Focus: turning messy or inconsistent raw data into something reliable for analysis (handling missing values, inconsistent labels, edge cases, and documenting assumptions).

**Why this fits what I did this week (one sentence)**

Through the exercises this week, I figured out how to clean data in Python with Cursor’s help—but I didn’t ask it to write the code for me exactly. I asked Cursor to **guide me step by step** while I wrote the code myself. I also practiced **code literacy and documentation** by adding comments in my code so I could follow what each part was doing.

---

## 2) Questions to support your claim

### C2 — Code Literacy and Documentation

**Pick one function: inputs, outputs, and what it does**

I’m highlighting `parse_experience_years(raw_value)` (around lines 11–23). I added comments there so I can see **what is being cleaned**, **what gets returned**, and **what the exception path** is for values that are not plain integers.

The function parses the “years of experience” field so that messy text can be turned into a **number** when possible. It takes a **text** value from the CSV. It first tries normal integer parsing; if that fails, it checks a **word-to-number** mapping (`WORD_TO_INT`, e.g. `"fifteen"` → `15`). If neither works, it returns **`None`** so later steps can skip or handle that row instead of crashing.

**Walk through one “happy path” (raw row → something you can analyze)**

A row comes in as strings from the CSV. When the script needs a numeric experience value, it passes the experience field into `parse_experience_years`. If the value is something like `"7"` or `"fifteen"`, the function returns an integer. That integer can then be used safely in averages or filters without the program failing on mixed text and numbers.

**Documentation: what I added or would still add**

I added **comments** that help *me* understand what the function does at a glance—especially around parsing, the word map, and when `None` is returned. I could still add a short **docstring** that lists expected examples (`"5"`, `"twelve"`) and explicitly says “returns `None` if the value cannot be parsed,” so someone opening the file cold knows the contract without reading every line.

---

### C5 — Data Cleaning and Preparation

**What kinds of “mess” show up, and how does the code address them?**

This exercise had **two main bugs** I ran into. One was a **text value** in the years-of-experience field (e.g. **“fifteen”**), which broke assumptions that everything was already a number. The other was around **sorting / handling satisfaction scores**—the “mess” there was partly about **types and logic** (what gets compared and how), not only spelling.

**Normalization: roles, tools, experience—why it matters**

I focused on **normalizing the experience field** so that values become **numbers** when possible. That way the field can be **used in math and analysis** (for example averages) instead of failing or mixing incomparable types. Separately, the script also uses patterns like **stripping and casing** for text fields (e.g. roles, tools) so labels line up for counting and filtering.

**Quality checks: how I’d trust or distrust the cleaned output**

I would **deliberately put another bad or word-based value** in the original CSV (for example **“eleven”**) and re-run the script to confirm that `parse_experience_years` (and anything downstream) behaves the way I expect. I’d also spot-check a few rows in the output file and compare counts before/after filters (e.g. Figma-only rows) so I’m not silently dropping or miscounting data.

---

## 3) Real dataset instead of the demo CSV

**What would change on a real dataset?**

It would be different because my **number mappings are hardcoded** in the script. On a small class CSV, that’s workable; on **real** survey or product data, I’d expect **more variety** in how people type numbers and more edge cases. In practice I might use a **library** or a more systematic approach so parsing doesn’t “die halfway” when a new wording appears that isn’t in my dictionary.

**What could go wrong?**

Real datasets often have **column names or formats that don’t match** what the script expects, so the program might error—or worse, run but **mis-parse** values. Any experience wording that isn’t in the hardcoded map would still become **`None`** (or be skipped), which could **bias averages** if many rows are dropped. Satisfaction scores might include **unexpected text**, decimals, or scales (1–5 vs 1–10). Large files could also surface **performance** or **memory** limits that don’t show up in the demo.

**How would you know?**

I’d watch for **Python errors** (missing keys, bad `int()` conversions) versus **silent issues** (too many `None`s, suspicious averages). I’d compare **row counts** before and after cleaning, use **`summarize_data`** (or similar checks) on the cleaned rows, and **open the exported CSV** to spot-check a few participants. I’d also repeat the kind of test I mentioned—**inject values like `"eleven"`**—and add a couple of **edge-case rows** on purpose to see if the script fails loudly or hides the problem.

---

## 4) Optional: one concrete next improvement

If I had another hour, I’d add a small **validation step at the top** that checks required columns exist, prints how many experience values **could not be parsed**, and maybe moves the word-to-number list into a **separate data file** so new words don’t require editing the main script.
