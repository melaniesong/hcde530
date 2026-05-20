# MP1 — Competency claims

**Name:** Melanie Song  
**Artifacts in this folder:** `week6_mp1_starter.ipynb`, `380K_US_Restaurants.csv`, `restaurants_deduped.csv`, `restaurants_cleaned.csv`, chart PNGs, and this file.

---

## C3 — Data cleaning and file handling

The two most important cleaning steps were **deduplication** and **removing restaurants without ratings**, saved as separate files so I would not overwrite the deduped data. I deduplicated on **Title, Address, Phone, Latitude, and Longitude** and wrote **`restaurants_deduped.csv`** (~183,725 rows); without that step, **Q1 cuisine counts and Q2 state totals would be inflated** because the same venue could be counted many times. I then dropped rows with missing or invalid **`Rating`** and wrote **`restaurants_cleaned.csv`** (~161,587 rows); without that step, **Q3 averages and any “share of restaurants with a given rating” logic would be biased** because unrated listings would distort denominators and means. I also excluded false positives such as **“Caucasian restaurant”** from Asian keyword matches so Q2 geography would not count unrelated labels as Asian cuisine.

---

## C5 — Data analysis with pandas

My strongest finding was in **Q2 (geography)**: **raw counts and state-level share tell different stories**. Large states such as **California** rank at the top for **how many** Asian-flagged listings appear, which partly reflects how many restaurant rows those states have in the scrape overall—not only “more Asian food culture.” When I computed **`asian_share_pct`** (Asian-flagged rows ÷ all rows in each state), states such as **Hawaii** and **Arizona** also stood out for **high proportional presence**, even when they were not #1 on raw count. I used **`str.extract`** on **`Address`** to get **`State`**, then **`groupby("State").agg(...)`** for totals and Asian counts, and filtered to states with **at least 500 total restaurants** before ranking shares so tiny states would not look artificially extreme. That pattern suggests **“many Asian restaurants” ≠ “Asian cuisine is a large fraction of that state’s listings”**—readers need both metrics.

---

## C6 — Data visualization

The **second Q2 choropleth (share % by state)** was the strongest chart for my argument because it forced a fair comparison across states with different market sizes. The **first choropleth (raw counts)** still matters—it shows where the database piles up the most Asian-flagged listings (for example **California**)—but it can make big states look like the only story. The **share map** shows where Asian labels are **unusually common relative to that state’s full listing mix**, which is closer to a visibility/proportion question than a population-size question. I used **finding-first titles**, labeled legends (count vs. **Asian share (%)**), and exported both maps as **PNG** files with **`fig.write_image`** so the comparison is easy to review without re-running code.

---

## C7 — Critical evaluation and professional judgment (limits)

I will **not** claim that star ratings prove one Asian cuisine is “better” than another, or that this scrape is a complete census of U.S. restaurants or demographics. The data are **platform listing labels** (`Category` strings), not a verified cuisine taxonomy; **address-based state parsing** drops some rows; and **deduping plus the n ≥ 50 rule** change who gets counted. I showed that restraint by pairing **mean-rating bars with a jittered scatter** (overlap matters), using **two choropleths** instead of one geographic view, and stating in conclusions that patterns describe **this cleaned table’s visibility and aggregates**—not causal food quality or true population mix.
