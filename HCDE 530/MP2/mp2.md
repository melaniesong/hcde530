# MP2 — Competency claims

**Name:** Melanie Song  
**Artifacts in this folder:** `app.py`, `analyzer.py`, `exporter.py`, `utils.py`, `README.md`, `SPEC.md`, and this file.

**Public URL:** [github.com/melaniesong/hcde530/tree/main/HCDE%20530/MP2](https://github.com/melaniesong/hcde530/tree/main/HCDE%20530/MP2)

---

## C8 — Building and deploying a complete tool

UX researchers often spend hours manually reading session transcripts and notes after usability testing, trying to spot patterns across participants. **Research Analyzer** automates that first pass: it ingests multiple `.txt` or `.docx` files, extracts themes, pulls representative quotes (with timestamps when the transcript includes them), and returns a structured summary so researchers can spend more time on interpretation and decisions instead of sorting raw text.

I scoped v1 deliberately. **In scope:** batch upload of notes and transcripts, optional research focus, two-pass AI analysis, in-browser results, and Excel export. **Out of scope:** audio/video transcription (would require Whisper or a paid transcription API), user authentication, saving results between sessions, and manual theme editing in the UI. Keeping that boundary made the project shippable instead of endless.

The researcher flow is four steps in **`app.py`**: (1) upload one or more session files, (2) optionally set a research focus and max themes, (3) run analysis with a progress bar per file, (4) review theme cards with supporting quotes and download a `.xlsx` report. What ships is a working Streamlit app plus a four-tab workbook: **Themes Summary**, **Quotes by Theme**, **Session Summaries**, and **Raw Analysis**.

I built in dependency order and tested each layer before wiring the UI: **`utils.py`** (text extraction) → **`analyzer.py`** (API + JSON) → **`exporter.py`** (Excel with dummy data) → **`app.py`** (connect everything). That order mattered because broken file parsing or invalid API JSON would make the UI useless no matter how polished it looked.

Build was not smooth. Claude sometimes returned JSON wrapped in markdown fences despite the prompt, which broke **`json.loads()`** until I added cleanup and a retry path. Longer transcripts hit token limits until I raised **`max_tokens`** for pass 1 and pass 2. Adding timestamps meant updating **`SPEC.md`**, then **`analyzer.py`**, **`exporter.py`**, and **`app.py`** in that design order—not just patching one file. I also caught a **`PASS1_SYSTEM_PROMPT`** naming typo that stopped analysis entirely until it was fixed.

I will **not** claim this replaces tools like Dovetail or Aurelius. There is no persistent storage, team collaboration, or video support. It requires an Anthropic API key and costs money per run. Claude can miss themes, misattribute quotes, or infer timestamps incorrectly when transcript formatting is inconsistent. Output quality depends heavily on input quality.

---

## C4 — APIs and data acquisition

I used the **Anthropic Claude API** via the **`anthropic`** Python SDK to pull structured theme data from unstructured session text. **Pass 1** (`analyze_session`) returns JSON per file: a **`themes`** array where each item has **`name`**, **`severity`** (High / Medium / Low), a verbatim **`quote`**, **`timestamp`** (string or null), and a **`summary`**. **Pass 2** (`synthesize_sessions`) returns consolidated **`themes`** with **`frequency`**, **`sessions`**, and a **`quotes`** array of **`text`**, **`source`**, and **`timestamp`**.

Authentication is handled safely: the real key lives in **`.env`**, which is **gitignored**; **`/.env.example`** with a placeholder is committed so cloners know what to create. For a cloud deployment, the same key would go in Streamlit Secrets—not in the repo.

From the API docs and SDK I configured **`claude-opus-4-5`**, system prompts that enforce JSON-only responses with an exact schema, and user messages that prepend the research focus when provided. I started with 2000 max tokens per call (per spec) and later increased pass 1 to **4096** and pass 2 to **8192** after truncated JSON failures on longer transcripts.

I used **two passes** instead of one mega-call because a single request with all transcripts risks token limits, blurs file-level attribution, and mixes two different tasks (extract vs merge). Pass 1 keeps full per-session context; pass 2 merges overlapping themes and ranks by frequency and severity.

When the API fails, errors surface through **`st.error()`** in the UI. **`AnalysisError`** wraps API failures and JSON parse problems. Invalid JSON triggers fence-stripping, trailing-comma cleanup, and one repair retry before the user sees a clear error—including a specific message when the response was cut off by the token limit.

Data flows: uploaded files → **`extract_text()`** (plain strings) → **`analyze_session()` / `synthesize_sessions()`** (Python dicts) → **`export_to_excel()`** ( **`BytesIO`** workbook) → **`st.download_button()`** in **`app.py`**.

Honest limits: each call has a small cost that adds up across runs. JSON reliability depends on the model following the schema; it does not always. Timestamps appear only when they exist and are consistently formatted in the source transcript (with pass 1 backfill in **`exporter.py`** when pass 2 omits them). Very long transcripts may still need chunking in a future version.

---

## C2 — Code literacy and documentation

I can read and explain the module split: **`utils.py`** extracts plain text from `.txt` and `.docx` uploads while preserving timestamp patterns like `[00:32]`. **`analyzer.py`** sends session text to Claude in two passes and returns structured theme dicts. **`exporter.py`** writes those dicts into a formatted four-tab Excel file as a **`BytesIO`** object. **`app.py`** is the Streamlit UI that connects all three into the researcher-facing tool.

I wrote or revised meaningful pieces myself: **`SPEC.md`** (including the timestamp schema update), the system prompts in **`analyzer.py`**, timestamp support across **`analyzer.py`**, **`exporter.py`**, and **`app.py`**, JSON parsing hardening (fence stripping, retry, higher token limits), and bug fixes such as the **`PASS1_SYSTEM_PROMPT`** typo. I relied on docstrings where they clarify contracts—for example **`extract_text()`** documents supported formats and return type, and **`analyze_session()`** documents inputs, return shape, and **`AnalysisError`**.

**`README.md`** is written for someone who found the repo but was not in class: what the tool does, who it is for, how to install dependencies, set up **`.env`**, and run **`streamlit run app.py`**. A reasonable commit message for the timestamp work would be: **`add timestamp extraction to analyzer, exporter, and app`**.

A stranger with Python and an Anthropic key should be able to clone, follow **`README.md`**, copy **`.env.example`** to **`.env`**, and run the app without asking me questions— that was the documentation goal.

What might confuse a new reader: the two-pass design in **`analyzer.py`** is not obvious without context (extract per session vs synthesize across sessions are different jobs). The custom **`AnalysisError`** exists so **`app.py`** can catch analysis failures separately from generic Python errors and show researcher-readable messages instead of stack traces.

---

## Honesty and limits

This tool supports a **first-pass thematic summary** for usability research—it does not replace human coding, team review, or a full research repository. Findings depend on Claude’s interpretation of the prompts and the uploaded text. Treat sensitive participant content carefully; **`.env`** and **`data/raw/`** stay out of git, but researchers are still responsible for what they upload and what they share from the Excel export.
