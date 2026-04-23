# Week 4 — Reflection (C2, C3, C4)

Related artifacts in this folder: `fetch_reviews.py`, `analyze_helpful_votes.py`, `fetch_met_museum_objects.py`, sample CSVs, commit history.

---

## Competency focus

Which competencies are you claiming this week?

- [ ] **C1** — Vibecoding and rapid prototyping *(skipped this week)*
- [x] **C2** — Code literacy and documentation
- [x] **C3** — Data cleaning and file handling
- [x] **C4** — APIs and data acquisition

**One sentence — what did you ship or practice?**

I practiced reading and explaining API scripts, handling real-world API behavior when writing CSVs, and using official Met documentation to request and interpret structured collection data.

---

## C1 — Vibecoding and rapid prototyping

*Skipped — not claiming C1 this week.*

---

## C2 — Code literacy and documentation

**Q4 — Read the code:** Pick `fetch_met_museum_objects.py` *or* `fetch_reviews.py`. Without running it, trace the path from `main()` to the CSV on disk—in plain English.

**Your answer:**

`main()` first calls `fetch_json()` to connect to the API root and print basic API information. Then it calls `fetch_json()` again to get the review data. It extracts the `category`, `helpful_votes`, and `verified_purchase` fields from each review and stores them in a list of dictionaries. Finally, it opens `reviews_export.csv`, writes the column headers, and writes all of those rows into the CSV file.

*(Script referenced: `fetch_reviews.py`.)*

**Q5 — Safe change:** Name one small refactor you trust yourself to do (rename, comment, extract a function). What mistake would cause a confusing bug?

**Your answer:**

A small change I can make safely is to rename the variable `r` in the `for` loop to something clearer—for example, `for review in reviews`. If I am not careful and only rename it in one place, the loop will break.

**Q6 — Legibility:** What does a classmate need (Python version, folder to `cd` into, `.env` keys, env vars like `MET_SEARCH_QUERY`) to run your scripts? Where did you put that information (file top comments, README, commits)?

**Your answer:**

A classmate would need **Python 3** installed to run my script, since it uses standard Python libraries such as `csv`, `json`, and `urllib`. They would need to open the terminal, `cd` into the folder where the script is saved, and run the file from there so the output CSV is created in the correct working directory. They would also need an **internet connection** because the script pulls review data from an online API.

My script does **not** require any `.env` file, API keys, or environment variables like `MET_SEARCH_QUERY`, so setup is simple.

I placed some of this information in the **comments at the top of the file**, which explain what the script does and that it only uses the Python standard library. If I were sharing it with classmates, I would also include clear run instructions in a **README**, such as the Python version needed, the command to run the script, and the name of the CSV output file.

---

## C3 — Data cleaning and file handling

**Q7 — Messy data:** For the CSVs you produced this week, what kinds of inconsistency or missingness showed up in the *source* data (API or file), and how did your script handle it (defaults, skips, types)?

**Your answer:**

*(Add if you want — optional for your submission.)*

**Q8 — Repeatability:** If you deleted the output CSV and re-ran the script, what would match exactly? What could legitimately differ the next day?

**Your answer:**

*(Add if you want — optional for your submission.)*

**Q9 — One error story:** Describe one error or traceback you hit while reading/writing data. What was the fix in human terms?

**Your answer:**

One error happened when I was fetching data from the **Met API**. I did not set a limit on the number of requests I could make to the API per second, which caused an error. To fix it, I added some code that sets a limit on the number of requests, as well as a time lapse between each request.

---

## C4 — APIs and data acquisition

**Q10 — Documentation:** Which API(s) did you call (Met Collection, HCDE530 week4 reviews, both)? What doc or page told you the URL shape and which JSON keys to trust?

**Your answer:**

I used **The Metropolitan Museum of Art Collection API**. The main documentation page that helped me was the official developer site: [https://metmuseum.github.io/](https://metmuseum.github.io/). It explained the URL structure for endpoints such as the search endpoint and the objects endpoint, including how to format query parameters. It also described the JSON response fields, which helped me know which keys to trust, such as `objectIDs` from search results and fields like `title`, `artistDisplayName`, `objectDate`, and `primaryImage` from object records. The documentation was the main source I used to understand how to build requests and interpret the returned data.

**Q11 — Fields:** Name **three** fields you extract (e.g. `department`, `helpful_votes`, `isHighlight`) and **why each matters** for a reader or an analysis—not “because the rubric asked.”

**Your answer:**

The fields I extracted each add useful context for understanding and analyzing objects from the Metropolitan Museum of Art Collection API.

- **`objectID`** matters because it is the museum’s unique identifier for each object, which helps track records accurately and prevents confusion between similar works.
- **`isHighlight`** matters because it shows whether the museum considers an object especially notable or featured, which can help readers identify important works quickly.
- **`department`** matters because it shows how the museum organizes the collection, such as European Paintings or Asian Art, making it easier to compare categories of objects.
- **`title`** matters because it gives the name of the artwork or object, allowing readers to immediately understand what each record represents.
- **`culture`** matters because it provides cultural origin or association, which adds historical and geographic context.
- **`medium`** matters because it describes the materials or techniques used, such as oil on canvas or bronze, helping readers understand how the work was made.
- **`objectBeginDate`** matters because it gives the year or starting date of the object, which is useful for placing works in historical timelines.
- **`period`** matters because it identifies a historical or stylistic era, such as Renaissance or Edo period, adding interpretive context beyond a single year.
- **`artistDisplayName`** matters because it names the creator associated with the object, which is valuable for readers and for comparing works by artist.
- **`artistNationality`** matters because it gives the nationality label of the artist, which can support analysis of representation across regions or cultures within the collection.

**Q12 — Auth:** Did any call require a secret key? If yes, where is it stored and how is it loaded? If no, how would you add a key safely later?

**Your answer:**

No API call in my script required a secret key. The Met Collection API is public, so the requests work without authentication. My code even says this in the top docstring and in the `load_local_env()` comment: the `.env` loader is included as a safe pattern for optional settings or future keys, but the current API does not need one. The script loads `.env` values from a file next to the script into `os.environ`, and then reads optional settings like `MET_SEARCH_QUERY`, `MET_MAX_OBJECTS`, and `MET_REQUEST_DELAY_SEC` from environment variables.

If I needed to add a key later, I would store it in a local `.env` file that is ignored by Git, load it into `os.environ`, and read it in the script with `os.environ.get(...)` instead of hard-coding it. That would be safer because the key would stay out of the source code and out of version control.

**Q13 — Limits / failures:** What happens on a bad network day, HTTP 403/429, or a missing object? Point to the part of your code that retries, waits, or skips—and say whether you are happy with that behavior.

**Your answer:**

On a bad network day, the script does have some protection, but not for every kind of failure. In `fetch_json()`, it retries when the server returns HTTP 403 or 429 by using exponential backoff, waiting longer after each failed attempt before trying again. That is the part of the code that handles rate limiting or temporary blocking.

In `main()`, when the script fetches each object record, it skips missing objects that return 404 instead of crashing the whole run. It also skips objects that still return 403 or 429 after retries, and it prints a message suggesting that the request delay should be increased. If the API returns an incomplete payload without an `objectID`, the script skips that too.

For the initial search request, though, a broader `URLError` causes the script to print an error and exit instead of retrying. So the script is somewhat resilient for object-detail requests, but less resilient for complete network outages or failures during the first search call.

I am mostly happy with this behavior because it avoids losing the entire run when just a few objects fail. The main weakness is that it does not retry general network failures like a timeout or DNS error, and the search step exits immediately if that happens. If I improved it later, I would probably add retries for `URLError` in `fetch_json()` too.

---

## Cross-cutting

**Q14 — One extra hour:** If you had one more hour this week, what would you improve first?

**Your answer:**

*(Add if you want.)*

**Q15 — Pride:** What is one thing you are proud of from Week 4?

**Your answer:**

*(Add if you want.)*
