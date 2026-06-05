"""Claude API analysis for usability session notes and transcripts."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import anthropic

MODEL = "claude-opus-4-5"
MAX_TOKENS_PASS1 = 4096
MAX_TOKENS_PASS2 = 8192
MAX_PARSE_RETRIES = 1

JSON_REPAIR_PROMPT = (
    "Your previous response was not valid JSON. Return ONLY valid JSON matching "
    "the required schema. Escape double quotes inside strings with a backslash. "
    "No preamble and no markdown code fences."
)

PASS1_SYSTEM_PROMPT = """You are a UX research analyst. Analyze the following session notes or transcript
and extract key usability themes. For each theme, provide:
- A short theme name (3-6 words)
- A severity: High, Medium, or Low based on how strongly the participant
  expressed it
- One representative verbatim quote from the text
- The timestamp when the participant said the quote, if present in the transcript
  (e.g. [00:32], 00:32:15, or (0:32)); use null for session notes without timestamps
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
Return only valid JSON. No preamble, no markdown code fences."""

PASS2_SYSTEM_PROMPT = """You are a UX research analyst. You have been given themes extracted from
multiple usability sessions. Your job is to:
1. Merge duplicate or overlapping themes
2. Identify which themes recur across multiple sessions
3. Rank themes by frequency and severity
4. Return a final consolidated theme list
5. Preserve timestamp values from the input themes when building each quote; use null if unavailable
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
Return only valid JSON. No preamble, no markdown code fences."""


class AnalysisError(Exception):
    """Raised when analysis or response parsing fails."""


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AnalysisError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )
    return anthropic.Anthropic(api_key=api_key)


def _build_user_message(session_text: str, research_focus: str | None = None) -> str:
    text = session_text.strip()
    if research_focus and research_focus.strip():
        return f"{research_focus.strip()}\n\n{text}"
    return text


def _clean_json_content(raw: str) -> str:
    content = raw.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start : end + 1]

    # Remove trailing commas before closing braces/brackets.
    content = re.sub(r",(\s*[}\]])", r"\1", content)
    return content.strip()


def _parse_json_response(raw: str) -> dict[str, Any]:
    content = _clean_json_content(raw)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AnalysisError(f"Model returned invalid JSON: {exc}") from exc

    if not isinstance(data, dict) or "themes" not in data:
        raise AnalysisError('JSON response must be an object with a "themes" key.')

    return data


def _extract_response_text(response: anthropic.types.Message) -> str:
    if not response.content:
        raise AnalysisError("Claude API returned an empty response.")

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    if not raw_text.strip():
        raise AnalysisError("Claude API returned no text content.")
    return raw_text


def _call_claude(
    system_prompt: str,
    user_message: str,
    *,
    max_tokens: int = MAX_TOKENS_PASS1,
    client: anthropic.Anthropic | None = None,
) -> dict[str, Any]:
    api = client or _get_client()
    messages: list[dict[str, str]] = [{"role": "user", "content": user_message}]
    tokens = max_tokens

    for attempt in range(MAX_PARSE_RETRIES + 1):
        try:
            response = api.messages.create(
                model=MODEL,
                max_tokens=tokens,
                system=system_prompt,
                messages=messages,
            )
        except anthropic.APIError as exc:
            raise AnalysisError(f"Claude API error: {exc}") from exc
        except AnalysisError:
            raise
        except Exception as exc:
            raise AnalysisError(f"Unexpected error calling Claude API: {exc}") from exc

        raw_text = _extract_response_text(response)

        if response.stop_reason == "max_tokens":
            if attempt < MAX_PARSE_RETRIES:
                tokens = min(tokens * 2, 16384)
                continue
            raise AnalysisError(
                "Claude response was cut off before finishing (token limit reached). "
                "Try fewer files, set Max themes to 5, or use a shorter transcript."
            )

        try:
            return _parse_json_response(raw_text)
        except AnalysisError:
            if attempt >= MAX_PARSE_RETRIES:
                raise
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": raw_text},
                {"role": "user", "content": JSON_REPAIR_PROMPT},
            ]

    raise AnalysisError("Claude API returned an unexpected empty result.")


def analyze_session(
    session_text: str,
    research_focus: str | None = None,
    *,
    client: anthropic.Anthropic | None = None,
) -> dict[str, Any]:
    """
    Pass 1 — analyze one session's notes or transcript.

    Returns parsed JSON:
    {"themes": [{"name", "severity", "quote", "timestamp", "summary"}, ...]}
    """
    if not session_text or not session_text.strip():
        raise AnalysisError("Session text is empty.")

    user_message = _build_user_message(session_text, research_focus)
    return _call_claude(PASS1_SYSTEM_PROMPT, user_message, client=client)


def synthesize_sessions(
    per_session_results: list[dict[str, Any]],
    *,
    client: anthropic.Anthropic | None = None,
) -> dict[str, Any]:
    """
    Pass 2 — merge themes across sessions.

    Parameters
    ----------
    per_session_results
        List of dicts, each with:
        - ``filename`` (str): source session file name
        - ``themes`` (list): pass 1 theme objects, OR a full pass 1 result
          dict containing ``themes``

    Returns
    -------
    dict
        Consolidated JSON with frequency, sessions, and quotes (with timestamps) per theme.
    """
    if not per_session_results:
        raise AnalysisError("No session results provided for synthesis.")

    payload_sessions: list[dict[str, Any]] = []
    for entry in per_session_results:
        filename = entry.get("filename")
        if not filename:
            raise AnalysisError('Each session result must include a "filename".')

        if "themes" in entry:
            themes = entry["themes"]
        elif "analysis" in entry and isinstance(entry["analysis"], dict):
            themes = entry["analysis"].get("themes", [])
        else:
            raise AnalysisError(
                f'Session "{filename}" must include "themes" or "analysis.themes".'
            )

        payload_sessions.append({"filename": filename, "themes": themes})

    user_message = json.dumps({"sessions": payload_sessions}, indent=2)
    return _call_claude(
        PASS2_SYSTEM_PROMPT,
        user_message,
        max_tokens=MAX_TOKENS_PASS2,
        client=client,
    )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    SAMPLE_SESSIONS = [
        {
            "filename": "session-1-notes.txt",
            "text": """
Session: Checkout usability test — Participant A
Date: 2026-05-01

- Participant struggled to find the promo code field; looked under "Payment" first.
- Said "I didn't know I had to scroll down to see shipping options."
- Completed purchase but mentioned trust concerns: "I'm not sure this total is right."
- Positive: liked the product image gallery and size selector.
""".strip(),
        },
        {
            "filename": "session-2-transcript.txt",
            "text": """
Session: Checkout usability test — Participant B
Date: 2026-05-02

[00:08] Facilitator: Please try to complete checkout.
[00:32] Participant: Could not find where to enter a discount code.
[01:05] Participant: I almost missed shipping.
[01:42] Participant: Worried the order total changed after selecting express shipping.
[02:10] Participant: Appreciated clear product photos and the size guide link.
""".strip(),
        },
    ]

    RESEARCH_FOCUS = "Research focus: checkout flow usability"

    try:
        pass1_results: list[dict[str, Any]] = []

        print("=== Pass 1: per-session analysis ===\n")
        for session in SAMPLE_SESSIONS:
            print(f"Analyzing {session['filename']}...")
            analysis = analyze_session(session["text"], RESEARCH_FOCUS)
            pass1_results.append(
                {"filename": session["filename"], "themes": analysis["themes"]}
            )
            print(json.dumps(analysis, indent=2))
            print()

        print("=== Pass 2: cross-session synthesis ===\n")
        consolidated = synthesize_sessions(pass1_results)
        print(json.dumps(consolidated, indent=2))

        print("\n=== Consolidated theme list ===\n")
        for i, theme in enumerate(consolidated.get("themes", []), start=1):
            sessions = ", ".join(theme.get("sessions", []))
            print(
                f"{i}. {theme.get('name')} "
                f"[{theme.get('severity')}] "
                f"(frequency: {theme.get('frequency')}, sessions: {sessions})"
            )
            print(f"   {theme.get('summary')}")
            for quote in theme.get("quotes", []):
                ts = quote.get("timestamp")
                ts_label = f"[{ts}] " if ts else ""
                print(f'   - {ts_label}"{quote.get("text")}" ({quote.get("source")})')
            print()

    except AnalysisError as exc:
        print(f"Analysis failed: {exc}")
