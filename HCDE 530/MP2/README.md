# Research Analyzer (MP2)

## Public URL

**GitHub repository:** [github.com/melaniesong/hcde530/tree/main/HCDE%20530/MP2](https://github.com/melaniesong/hcde530/tree/main/HCDE%20530/MP2)

This project is a Python + Streamlit app (not a Jupyter notebook), so there is no hosted deployment URL. When run locally, it opens a web app in your browser where you can upload usability session files and download an Excel report of themes and quotes.

---

## What it does

Research Analyzer helps **UX researchers** turn raw usability session notes and transcripts into structured findings. You upload `.txt` or `.docx` files from multiple sessions, optionally describe your research focus, and the tool uses AI to:

1. Extract usability themes from each session
2. Merge overlapping themes across sessions
3. Surface recurring issues with severity, supporting quotes, timestamps (when present in transcripts), and source filenames
4. Export a four-tab Excel workbook you can share with your team or use for further analysis

---

## Who it is for

This tool is for **UX researchers, product designers, and anyone running qualitative usability studies** who needs to quickly identify patterns across multiple participant sessions without manually re-reading every transcript. It is especially useful after a round of usability testing when you have several session notes or transcripts and want a consolidated theme list with evidence (quotes) tied back to each source file.

You do **not** need to be a developer to use it — the Streamlit interface walks you through upload, configuration, analysis, and download in four steps.

---

## How to run it locally

### Prerequisites

- Python 3.10 or newer
- An [Anthropic API key](https://console.anthropic.com/) (the tool uses Claude for thematic analysis)

### Setup

```bash
git clone https://github.com/melaniesong/hcde530.git
cd hcde530/HCDE\ 530/MP2

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your key:
# ANTHROPIC_API_KEY=your_key_here
```

### Start the app

```bash
streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in your browser, upload session files, click **Run analysis**, and download the `.xlsx` report from the Results section.

### Sample files

Example session notes live in `data/sample/`. For timestamp testing, use a transcript with lines like `[00:32] Participant: ...`.

---

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI |
| `analyzer.py` | Claude API analysis (pass 1 per session, pass 2 cross-session synthesis) |
| `exporter.py` | Excel export (four tabs) |
| `utils.py` | File parsing for `.txt` and `.docx` |
| `SPEC.md` | Full project specification |

---

## Excel output

The downloaded spreadsheet has four tabs:

1. **Themes Summary** — consolidated themes with severity and frequency
2. **Quotes by Theme** — supporting quotes with timestamps and source files
3. **Session Summaries** — per-session top themes and observations
4. **Raw Analysis** — full JSON from each session

---

## Notes

- **Do not commit** your `.env` file or real participant data. Both are gitignored.
- API usage incurs cost on your Anthropic account depending on session length and file count.
- Audio/video transcription is out of scope for this version — upload text notes or transcripts only.
