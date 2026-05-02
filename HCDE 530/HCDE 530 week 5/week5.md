# Week 5 reflection

## Competency - Competency C5

Using pandas to answer analytical questions: **filtering**, **grouping**, **summarizing**, **handling missing data**, and **choosing the right operation for the question**.

## Framing

This week I used my **MP1 restaurant dataset** to understand the table beyond a quick glance. **My pandas work for this week is in `HCDE 530/Week 5 Demo files/MP1 Restaurants/MP1 analysis A5.ipynb`** so a reader can open that file and follow the same steps.

The questions I focused on were: **how many distinct primary categories exist** and how listings are spread across them; **among Asian-related cuisine labels**, which Google `Category` strings appear most often; and **by time zone**, how many restaurant listings fall in each zone and what the **average rating** looks like in each.

To build that picture I used **`df.head()`** and **`df.info()`** for structure and sanity checks, **`df.isnull().sum()`** to see where the export is incomplete, a **boolean filter** on `Category` (`.str.contains(...)`) to build the Asian-related subset, **`df["Category"].value_counts()`** (turned into a small **`DataFrame`** with counts and **`pct_of_all_rows`**) for the **full-file** category distribution, **`value_counts()` again on the filtered slice** (with **`pct_of_asian_slice`**) for **within–Asian-related** label shares, and **`df.groupby("Time_Zone").agg(...)`** with **`size`** and **`mean`** on **`Rating`** for regional summaries.

## Choosing the right operation

For “what exists in the table?” **`head`** and **`info`** were the right first step because they answer shape, dtypes, and non-null counts before any aggregate. For “how common is each label?” **`value_counts`** on **`Category`** answers a *distribution* question, not an average—so counts plus an explicit **percent of all rows** fit better than jumping straight to means. For the Asian slice, **`value_counts` on the filtered `DataFrame`** answers “within this subset, which label wins?” using a **percent of the slice**, not of the full file. For “by region,” **`groupby("Time_Zone")`** matches the unit of analysis (one row per zone) and **`mean`** on `Rating` only makes sense once `Rating` is numeric and I understand how **missing ratings** shrink the effective denominator.

## Filtering

I filtered to restaurants whose **`Category`** text matches **Asian, Chinese, Vietnamese, Thai, or Indian** (case-insensitive pattern). That subset is my working definition of an **Asian diaspora–related food landscape** in this scrape: it is imperfect (labels are vendor-chosen and can overlap), but it is **repeatable** and **inspectable**.

That filter mattered because the **full table** answers “what dominates overall,” while the **subset** answers “within Asian-related labels, what dominates *relative to each other*?” Patterns like one label vastly outnumbering another would be **diluted or invisible** if I only looked at the whole file.

## Grouping and summarizing

I summarized in two main ways:

1. **By `Category` (full table)** — **`value_counts`** with a companion **`pct_of_all_rows`** column so each label has a count and its share of **all** listings in the export.
2. **By `Time_Zone`** — **`groupby("Time_Zone").agg(...)`** with **`n_listings`** (row count per zone) and **`avg_rating`** (mean `Rating` in that zone, skipping missing ratings).

Each grouped row maps to something concrete: for example **`America/Los_Angeles`** is the Pacific time zone bucket in this dataset; **`n_listings`** is how many listings landed there in the export, and **`avg_rating`** describes the **average of non-missing ratings** in that bucket—so it is a real regional summary *for this file*, not a claim about every restaurant in the world.

## Missing data

Several columns had missing values, especially **`Rating`**, **`Category`**, and other fields such as **`Website`** or **`Time_Zone`** (depending on the row). Missing ratings mean that **average rating** only reflects restaurants **with** a reported rating, not literally every row in the table. Missing categories can exclude some restaurants from both the **full category distribution** and the **Asian-related subset**, which can **slightly bias** representation counts and any percentages built on row totals.

After seeing how many values were missing, I interpreted **average ratings more cautiously**: they summarize **the rated subset**, so they may not fully represent all restaurants in a category or region.

## Honesty and limits

Pandas made it **easy to summarize** a very large table quickly—for example **`value_counts`** for category frequencies and **`groupby` + `agg`** for counts and average ratings by time zone (see **`Week 5 Demo files/MP1 Restaurants/MP1 analysis A5.ipynb`**).

At the same time, the **`Category`** field is **messy and inconsistent**, with many near-duplicate labels (for example **“Chinese restaurant”** versus **“Chinese takeaway”**). That makes “clean” cuisine comparisons hard without **explicit rules** (like keyword filters or a manual mapping).

If I repeated this analysis, I would **standardize or clean `Category` first**—for example mapping related labels to a smaller set of cuisine types—so comparisons are **less ambiguous** and easier to defend in writing.

## What I would do next

Beyond cleaning categories, I would add an explicit **count of non-null ratings per `Time_Zone`** next to the mean, so “high average, few ratings” is visible in one view rather than implied.
