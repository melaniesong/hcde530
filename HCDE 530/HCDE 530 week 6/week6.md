# Week 6 reflection

## Competencies you are claiming

- **C3 — Data cleaning and file handling**
- **C5 — Data analysis with pandas**
- **C6 — Data visualization**

## Where your work lives

Primary artifact: **`week6_mp1_starter.ipynb`**, in **`HCDE 530/HCDE 530 week 6/`**. Supporting file: **`restaurants_cleaned.csv`** (cleaned export from the raw Kaggle **`380K_US_Restaurants.csv`**). Chart exports: **`*.png`** files written from Plotly in the same folder (for example cuisine bar, state choropleths, share map—match whatever filenames you committed).

---

## Framing

This week I connected **MP1a** questions about **Asian cuisine representation** and **ratings** to a large restaurant listing export. I treated the scrape as **platform-shaped data** (Google-style `Category` labels and addresses), not a perfect census of restaurants. My goal was to make **representation** (counts, geography, and stars) easier to reason about after **deduplication** and **consistent cuisine grouping**, then to communicate findings in **charts** a reader can skim.

---

## C3 — Data cleaning and file handling

I started from the raw **`380K_US_Restaurants.csv`** export and produced **`restaurants_cleaned.csv`** so later notebook cells could rely on one stable, reproducible table instead of re-parsing the full scrape every time.

The messiest problem was **duplicate rows for the same real-world restaurant**: the same venue could appear many times when **`Title`**, **`Address`**, **`Phone`**, and **`Latitude`/`Longitude`** (or equivalent location fields) matched—signals that listings were repeated rather than genuinely distinct venues. Cleaning that mattered because **representation counts and state totals** would otherwise be inflated by copy-paste or re-scraped duplicates.

Along the way I also handled other “real CSV” issues the notebook calls out: **mixed types** on some columns (so reads use explicit handling like `low_memory=False` where needed), **missing or blank `Category` / `Rating`**, and **text rules** that avoid false positives (for example treating **`Caucasian restaurant`** as not Asian when keyword patterns are applied). A remaining limitation is that any **dedupe rule is a judgment**: two rows can look identical in the key fields but still be wrong to merge, and some true venues may still be split if their listing text differs.

---

## C5 — Data analysis with pandas

**Questions (one line each)**

1. **Q1:** Which Asian cuisines (for example Chinese, Japanese, Thai, Vietnamese) are **most and least represented** among restaurants in the dataset?  
2. **Q2:** How does the representation of Asian cuisines **vary across U.S. states**—which states show **higher or lower proportions** of Asian-cuisine restaurants?  
3. **Q3:** Do **average ratings** differ across Asian cuisine types, and are some cuisines **consistently higher or lower** than others?

**Main table or variable per question**

- **Q1:** A cuisine-level summary table (**`counts`**) with one row per mapped cuisine, including **row counts** and **each cuisine’s percent of all Asian-mapped rows**. The bar chart uses a small combined slice (**`top_bottom`**) from **`nlargest` / `nsmallest`** so the figure stresses extremes without listing every cuisine at once.  
- **Q2:** A **per-state** summary (**`state_summary`** in the notebook workflow): after flagging Asian-related categories and extracting **state** from **address** text, I grouped by **`State`** and computed **`total_restaurants`**, **`asian_restaurants`**, and **`asian_share_pct`**. For **ranking** states by Asian **share** without tiny denominators, I also used **`state_summary_filtered`**, keeping states with **`total_restaurants` ≥ 500**. The **choropleth** figures are built from the same style of per-state aggregates (counts and share).  
- **Q3:** A per-cuisine summary (**`q3_summary`**) from **`groupby("Cuisine_Group").agg(...)`** on **`rating_num`** (mean, median, standard deviation, and counts). I restricted comparisons to cuisine groups with **at least 50 restaurants**. The **jittered scatter** is built from per-row **`asian_ratings`** so the **distribution** of ratings is visible, not only the means in **`q3_summary`**.

**What I computed**

- **Q1:** Row counts per **Asian cuisine group** after dropping missing categories and **mapping** raw **`Category`** labels into broader groups (Chinese, Japanese, Korean, and so on). I also computed **each cuisine’s percentage of total Asian-mapped rows**. Only rows that successfully mapped to an Asian cuisine group were included.  
- **Q2:** For each state, **total** restaurant rows, **Asian-flagged** row counts, and **Asian share (%)** of that state’s rows. I excluded states with **fewer than 500 total restaurants** when using the filtered table for **fairer share comparisons**.  
- **Q3:** **Mean, median, and standard deviation** of **`rating_num`** by cuisine group, plus **counts per group**, after coercing ratings to numeric and dropping invalid values. The **n ≥ 50** rule avoids unstable averages from very small groups.

**Pandas tools I used**

I relied on **`pd.read_csv`**, **`.copy()`**, **`.fillna()`**, **`.astype()`**, **`.str.strip()`**, **`.str.lower()`**, **`.str.contains()`** (including regex-style patterns), **`.str.extract()`** for state codes, **`pd.to_numeric(..., errors="coerce")`**, **boolean row filtering** (`df[...]`), **`.map()`** for label standardization, **`groupby()`** with **`.agg()`**, **`.value_counts()`** where helpful, **`.rename_axis()`** / **`.reset_index()`**, **`.sort_values()`**, **`.round()`**, **`.notna()`**, and **`.head()` / `.tail()`** for quick checks—plus **`nlargest` / `nsmallest`** (and related steps) for the top-vs-bottom cuisine view.

---

## C6 — Data visualization

**What I am submitting**

- **Q1 — Horizontal bar chart:** plots **`top_bottom`** (merged **top 5** and **bottom 5** cuisines by count from **`counts`**) with **restaurant counts** on the axis.  
- **Q2 — Two choropleths:** both use the **per-state** table (**`choropleth`** in the visualization cells): one encodes **Asian restaurant count** by **`State`**, the other encodes **`asian_share_pct`** by **`State`**, so **volume** and **proportion** are not confused.  
- **Q3 — Jittered scatter plot:** plots per-restaurant **`rating_num`** against **jittered cuisine positions** from **`asian_ratings`** (with **`pd.Categorical`** codes plus small random jitter), colored by **`Cuisine_Group`**.

**Why these chart types**

- **Q1:** A **top vs bottom horizontal bar** makes the **contrast between the most and least represented** Asian cuisine types obvious without crowding the chart with every category.  
- **Q2:** **Choropleths** match a **geographic** question: they show **where** counts and **where** shares are high or low across states. Two maps separate **“how many listings”** from **“what fraction of that state’s listings”**.  
- **Q3:** A **jittered strip scatter** fits **many restaurants per cuisine**: ratings **pile up** near typical values but still have a **spread** of higher and lower stars, which a single average bar would flatten.

**Titles, axes, and export**

I wrote **finding-first titles** (stating what the evidence suggests, not only the variable names) and set **readable axis labels** through Plotly Express **`labels={...}`** (and layout updates where needed—for example cuisine tick labels on the jittered x-axis). For a long **Q1** title I used **`textwrap`** with **`<br>`** line breaks and a bit of extra **top margin** so the title does not clip. I exported static figures with **`fig.write_image(...)`** and **`fig2.write_image(...)`** after installing **`kaleido`** in the setup cell, so PNGs can live in the repo next to the notebook.

---

## Honesty and limits

These charts summarize **listing labels and scraped rows**, not verified ground truth about every restaurant in the United States. **`Category`** is vendor- and platform-defined; “Pan-Asian / General Asian” style buckets **blur** cuisine identity. **Address-based state parsing** drops rows that do not match the expected pattern. **Star ratings** reflect reviewer behavior, chains, and missingness—not a neutral measure of food quality. **Deduping** changes denominators, so any “percent” is **percent of this cleaned table**, not an official statistic.
