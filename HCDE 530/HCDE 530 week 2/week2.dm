# Week 2 — Competency 2 reflections

## Competency 2 (what it is)

**Read and explain what a given block of code does.**

The goal is not to memorize syntax, but to look at a small piece of code and describe—in plain language—what it is doing step by step.

---

## Example block I practiced on

**File:** `app_review_word_count.py`  
**Lines:** 64–67

```python
for i, review in enumerate(reviews, start=1):
    count = count_words(review)
    word_counts.append(count)
    print(f"{i:<9} {count:<5} {review}")
```

### What this block does (my explanation)

This is a loop that goes through a list of text reviews, counts the number of words in each one, stores that count, and prints everything in a nicely formatted way.

### What was hardest when I first read it

Figuring out how exactly the loop works—especially how the **count** for each review is produced and used—took the most careful reading.

### Note to Future Me (for a comment above this loop)

> This is a loop that goes through a list of text reviews, counts the number of words in each one, stores that count, and prints everything in a nicely formatted way.

Use this sentence (or a shorter version) so you can skim the file later and still know what the loop is responsible for.

---

## Why this matters for my practice

Being able to read and explain code helps me **understand what engineers are doing when they implement design**—so I can ask better questions, spot constraints earlier, and align on what is actually being built.

It also helps me **write my own small scripts for research** (for example, working with survey or review data) without depending on someone else for every step.
