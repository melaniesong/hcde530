"""Streamlit UI for the UX Research Analyzer."""

from __future__ import annotations

from typing import Any

import streamlit as st
from dotenv import load_dotenv

from analyzer import AnalysisError, analyze_session, synthesize_sessions
from exporter import export_to_excel
from utils import extract_text

load_dotenv()

MAX_THEMES_OPTIONS = ["Auto-detect", "5", "10", "15"]

SEVERITY_STYLES = {
    "High": ("badge-high", "#c0392b"),
    "Medium": ("badge-medium", "#b8860b"),
    "Low": ("badge-low", "#2e7d32"),
}


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        .step-label {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8a8a8a;
            margin: 0 0 0.75rem 0;
        }

        .file-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            margin: 0.25rem 0.5rem 0.25rem 0;
            font-size: 0.875rem;
            color: #333;
        }

        .metric-card {
            background: #f7f4ef;
            border-radius: 10px;
            padding: 1rem 1.25rem;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #111;
            line-height: 1.1;
        }

        .theme-card {
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            background: #fff;
        }

        .theme-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }

        .theme-title {
            font-size: 1rem;
            font-weight: 700;
            color: #111;
            margin: 0;
        }

        .severity-badge {
            border-radius: 999px;
            padding: 0.2rem 0.65rem;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .badge-high {
            background: #fdecea;
            color: #c0392b;
        }

        .badge-medium {
            background: #fff4e0;
            color: #b8860b;
        }

        .badge-low {
            background: #e8f5e9;
            color: #2e7d32;
        }

        .theme-quote {
            border-left: 3px solid #d0d0d0;
            padding-left: 0.85rem;
            margin: 0 0 0.65rem 0;
            font-style: italic;
            color: #444;
        }
        .quote-timestamp {
            font-style: normal;
            font-weight: 600;
            color: #555;
        }

        .quote-source {
            font-style: normal;
            font-size: 0.82rem;
            color: #666;
        }

        .supporting-quotes-label {
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #888;
            margin: 0.75rem 0 0.35rem 0;
        }

        .theme-sources {
            font-size: 0.82rem;
            color: #666;
        }

        div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] {
            border-style: dashed;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _step_label(text: str) -> None:
    st.markdown(f'<p class="step-label">{text}</p>', unsafe_allow_html=True)


def _init_session_state() -> None:
    defaults = {
        "research_focus": "",
        "max_themes": "Auto-detect",
        "results": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _build_research_context() -> str | None:
    parts: list[str] = []
    focus = st.session_state.research_focus.strip()
    if focus:
        parts.append(f"Research focus: {focus}")

    max_themes = st.session_state.max_themes
    if max_themes != "Auto-detect":
        parts.append(f"Extract at most {max_themes} themes.")

    return "\n".join(parts) if parts else None


def _render_uploaded_files(files: list[Any]) -> None:
    if not files:
        return

    chips = "".join(
        f'<span class="file-chip">📄 {file.name}</span>' for file in files
    )
    st.markdown(chips, unsafe_allow_html=True)


def _count_quotes(consolidated: dict[str, Any]) -> int:
    return sum(len(theme.get("quotes", [])) for theme in consolidated.get("themes", []))


def _severity_badge(severity: str, frequency: int) -> str:
    badge_class, _ = SEVERITY_STYLES.get(severity, ("badge-medium", "#666"))
    session_label = "session" if frequency == 1 else "sessions"
    return (
        f'<span class="severity-badge {badge_class}">'
        f"{severity} — {frequency} {session_label}"
        f"</span>"
    )

def _format_quote_line(quote: dict[str, Any]) -> str:
    """Format one supporting quote with optional timestamp and source."""
    text = quote.get("text", "")
    timestamp = quote.get("timestamp")
    source = quote.get("source", "")

    ts_prefix = f'<span class="quote-timestamp">[{timestamp}]</span> ' if timestamp else ""
    source_suffix = f' <span class="quote-source">({source})</span>' if source else ""

    return f'<p class="theme-quote">{ts_prefix}"{text}"{source_suffix}</p>'

def _render_theme_card(theme: dict[str, Any]) -> None:
    quotes = theme.get("quotes", [])
    sessions = ", ".join(theme.get("sessions", []))
    frequency = theme.get("frequency", len(theme.get("sessions", [])))

    if quotes:
        quote_html = "".join(_format_quote_line(q) for q in quotes)
        quotes_section = (
            '<p class="supporting-quotes-label">Supporting quotes</p>'
            f"{quote_html}"
        )
    else:
        quotes_section = f'<p class="theme-quote">"{theme.get("summary", "")}"</p>'

    st.markdown(
        f"""
        <div class="theme-card">
            <div class="theme-card-header">
                <p class="theme-title">{theme.get("name", "Untitled theme")}</p>
                {_severity_badge(theme.get("severity", "Medium"), frequency)}
            </div>
            {quotes_section}
            <p class="theme-sources">📄 {sessions}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _run_analysis(uploaded_files: list[Any]) -> None:
    research_context = _build_research_context()
    per_session_results: list[dict[str, Any]] = []
    total_steps = len(uploaded_files) + 1

    progress = st.progress(0.0)
    status = st.empty()

    try:
        for index, uploaded_file in enumerate(uploaded_files, start=1):
            status.markdown(
                f"Analyzing **{uploaded_file.name}**… "
                f"<span style='float:right;color:#666;'>{index} of {len(uploaded_files)} files</span>",
                unsafe_allow_html=True,
            )
            session_text = extract_text(uploaded_file)
            analysis = analyze_session(session_text, research_context)
            per_session_results.append(
                {"filename": uploaded_file.name, "analysis": analysis}
            )
            progress.progress(index / total_steps)

        status.markdown(
            "**Synthesizing themes across sessions…**",
            unsafe_allow_html=True,
        )
        pass1_payload = [
            {"filename": entry["filename"], "themes": entry["analysis"]["themes"]}
            for entry in per_session_results
        ]
        consolidated = synthesize_sessions(pass1_payload)
        progress.progress(1.0)
        status.empty()
        progress.empty()

        st.session_state.results = {
            "consolidated": consolidated,
            "per_session": per_session_results,
        }

    except ValueError as exc:
        progress.empty()
        status.empty()
        st.error(str(exc))
    except AnalysisError as exc:
        progress.empty()
        status.empty()
        st.error(str(exc))


def main() -> None:
    st.set_page_config(
        page_title="Research Analyzer",
        page_icon="📋",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_styles()
    _init_session_state()

    st.title("Research Analyzer")
    st.markdown(
        "Upload session notes and transcripts to surface themes across your research."
    )

    with st.container():
        _step_label("Step 1 — Upload files")
        uploaded_files = st.file_uploader(
            "Upload session files",
            type=["txt", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        st.caption("Supports .txt and .docx")
        if uploaded_files:
            _render_uploaded_files(uploaded_files)

    st.divider()

    with st.container():
        _step_label("Step 2 — Configure")
        col_focus, col_themes = st.columns(2)
        with col_focus:
            st.text_input(
                "Research focus (optional)",
                key="research_focus",
                placeholder="e.g. checkout flow usability",
            )
        with col_themes:
            st.selectbox(
                "Max themes to surface",
                MAX_THEMES_OPTIONS,
                key="max_themes",
            )

    st.divider()

    with st.container():
        _step_label("Step 3 — Analyze")
        run_clicked = st.button(
            "▷ Run analysis",
            type="primary",
            use_container_width=True,
        )
        if run_clicked:
            if not uploaded_files:
                st.error("Upload at least one .txt or .docx file before running analysis.")
            else:
                _run_analysis(uploaded_files)

    results = st.session_state.get("results")
    if results:
        consolidated = results["consolidated"]
        per_session = results["per_session"]
        themes = consolidated.get("themes", [])

        st.divider()

        with st.container():
            header_col, download_col = st.columns([3, 1])
            with header_col:
                _step_label("Step 4 — Results")
            with download_col:
                excel_bytes = export_to_excel(consolidated, per_session)
                st.download_button(
                    label="Download .xlsx",
                    data=excel_bytes.getvalue(),
                    file_name="research_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            metric_cols = st.columns(3)
            metrics = [
                ("Themes found", len(themes)),
                ("Sessions analyzed", len(per_session)),
                ("Quotes extracted", _count_quotes(consolidated)),
            ]
            for col, (label, value) in zip(metric_cols, metrics):
                with col:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{value}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

            for theme in themes:
                _render_theme_card(theme)


if __name__ == "__main__":
    main()
