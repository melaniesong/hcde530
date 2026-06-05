# UX Research Analyzer — Project Spec

## Overview

A Streamlit app for UX researchers that takes raw session notes and transcripts,
runs thematic analysis using the Claude API, and outputs a structured Excel
spreadsheet of recurring themes, quotes, and findings.

---

## Project structure

```
ux-research-analyzer/
├── app.py               # Streamlit UI
├── analyzer.py          # Claude API calls and analysis logic
├── exporter.py          # Excel file generation
├── utils.py             # File parsing helpers (.txt, .docx)
├── requirements.txt
└── SPEC.md
```

---

## Requirements

```
streamlit
anthropic
python-docx
openpyxl
pandas
```

---

## UI layout (app.py)

Build a single-page Streamlit app with four clearly labeled steps.
No sidebar. All content in the main column with `st.container()` sections.

### Header
- App title: "Research Analyzer"
- Subtitle: "Upload session notes and transcripts to surface themes across your research."

### Step 1 — Upload files
- `st.file_uploader()` with `accept_multiple_files=True`
- Accepted types: `.txt`, `.docx`
- After upload, show a list of uploaded filenames with a file icon

### Step 2 — Configure
- Two inputs side by side using `st.columns(2)`:
  - Text input: "Research focus (optional)" — placeholder: "e.g. checkout flow usability"
  - Selectbox: "Max themes to surface" — options: ["Auto-detect", "5", "10", "15"]
- Store values in `st.session_state`

### Step 3 — Run analysis
- "Run analysis" button — full width using `use_container_width=True`
- While running, show a `st.progress()` bar and status text like:
  "Analyzing session-1-transcript.txt... (1 of 3)"
- On completion, store results in `st.session_state["results"]`

### Step 4 — Results
Only show this section if `st.session_state["results"]` exists.

- Three metric cards using `st.columns(3)`:
  - Themes found
  - Sessions analyzed
  - Quotes extracted
- For each theme, show an `st.expander()` with:
  - Theme name and severity badge (High / Medium / Low) in the header
  - Representative quote in a blockquote style
  - Source filenames
- Download button: `st.download_button()` for the Excel file
  - Label: "Download .xlsx"
  - Place above the theme list

---

## Analysis logic (analyzer.py)

### Two-pass approach

**Pass 1 — per-session analysis**
For each uploaded file:
1. Extract text (see utils.py)
2. Send to Claude with this system prompt:

```
You are a UX research analyst. Analyze the following session notes or transcript
and extract key usability themes. For each theme, provide:
- A short theme name (3-6 words)
- A severity: High, Medium, or Low based on how strongly the participant
  expressed it
- One representative verbatim quote from the text
- A 1-2 sentence summary of the theme

Return your response as JSON in this exact format:
{
  "themes": [
    {
      "name": "string",
      "severity": "High" | "Medium" | "Low",
      "quote": "string",
      "timestamp": "string or null",
      "summary": "string"
    }
  ]
}

Return only valid JSON. No preamble, no markdown code fences.
```

User message: `[research focus context if provided]\n\n[session text]`

**Pass 2 — cross-session synthesis**
After all sessions are analyzed:
1. Combine all per-session themes into one payload
2. Send to Claude with this system prompt:

```
You are a UX research analyst. You have been given themes extracted from
multiple usability sessions. Your job is to:
1. Merge duplicate or overlapping themes
2. Identify which themes recur across multiple sessions
3. Rank themes by frequency and severity
4. Return a final consolidated theme list

Return your response as JSON in this exact format:
{
  "themes": [
    {
      "name": "string",
      "severity": "High" | "Medium" | "Low",
      "frequency": number,
      "summary": "string",
      "sessions": ["filename1", "filename2"],
      "quotes": [
        { "text": "string", "source": "filename", "timestamp": "string or null" }
      ]
    }
  ]
}

Return only valid JSON. No preamble, no markdown code fences.
```

### Claude API setup
- Model: `claude-opus-4-5` (use latest available)
- Max tokens: 2000 per call
- Use the `anthropic` Python SDK
- Read API key from environment variable: `ANTHROPIC_API_KEY`
- Wrap all API calls in try/except and surface errors via `st.error()`

---

## File parsing (utils.py)

```python
def extract_text(file) -> str:
    """
    Takes an uploaded Streamlit file object.
    Returns extracted plain text as a string.
    Supports .txt and .docx.
    """
```

- For `.txt`: decode as UTF-8
- For `.docx`: use `python-docx`, join all paragraph texts with newlines
- Timestamps may appear in formats like [00:32], 00:32:15, or (0:32), do not strip them during extraction
- If file type is unrecognized, raise a clear ValueError

---

## Excel export (exporter.py)

Use `openpyxl` to generate a `.xlsx` file with four tabs:

### Tab 1: Themes Summary
Columns: Theme | Severity | Frequency (sessions) | Summary

### Tab 2: Quotes by Theme
Columns: Theme | Quote | Source File

### Tab 3: Session Summaries
Columns: Session File | Top Themes | Notable Observations

### Tab 4: Raw Analysis
Columns: Session File | Full JSON analysis (stringified)

Style notes:
- Bold header row on each tab
- Auto-fit column widths
- Freeze the top row on each tab

Return the file as a `BytesIO` object so Streamlit can serve it as a download.

---

## Environment setup

Create a `.env` file (not committed to git):
```
ANTHROPIC_API_KEY=your_key_here
```

Load it in `app.py` with:
```python
from dotenv import load_dotenv
load_dotenv()
```

Add `python-dotenv` to requirements.txt.

---

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Build order for Cursor

Build in this sequence — do not skip ahead:

1. `utils.py` — file parsing only, test with sample files
2. `analyzer.py` — Claude API calls, test pass 1 then pass 2 separately
3. `exporter.py` — Excel generation with dummy data first
4. `app.py` — wire everything together in the UI

---

## Out of scope (v1)

- Audio/video transcription (recordings)
- User authentication
- Saving results between sessions
- Editing or tagging themes manually in the UI
