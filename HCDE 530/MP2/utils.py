"""File parsing helpers for uploaded session notes and transcripts."""

from __future__ import annotations

import io
from pathlib import Path

from docx import Document


def _extension(filename: str) -> str:
    """Return lowercase extension including the dot, e.g. '.txt'."""
    return Path(filename).suffix.lower()


def _extract_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Could not decode .txt file as UTF-8. Re-save the file as UTF-8 and try again."
        ) from exc


def _extract_docx(data: bytes) -> str:
    document = Document(io.BytesIO(data))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file) -> str:
    """
    Extract plain text from an uploaded file.
    
    Timestamps in transcripts (e.g. [00:32], 00:32:15, (0:32)) are preserved
    as-is so downstream analysis can attach them to quotes.

    Parameters
    ----------
    file
        A Streamlit ``UploadedFile`` or any object with ``name`` (str) and
        ``read()`` -> bytes (e.g. pathlib path opened in binary mode via a
        thin wrapper for local testing).

    Returns
    -------
    str
        Extracted plain text.

    Raises
    ------
    ValueError
        If the file type is not supported or text cannot be extracted.
    """
    filename = getattr(file, "name", None)
    if not filename:
        raise ValueError("Uploaded file has no filename; expected .txt or .docx.")

    ext = _extension(filename)
    data = file.read()
    if hasattr(file, "seek"):
        file.seek(0)

    if not data:
        raise ValueError(f'File "{filename}" is empty.')

    if ext == ".txt":
        text = _extract_txt(data)
    elif ext == ".docx":
        text = _extract_docx(data)
    else:
        raise ValueError(
            f'Unsupported file type "{ext}" for "{filename}". '
            "Accepted types: .txt, .docx"
        )

    text = text.strip()
    if not text:
        raise ValueError(f'No readable text found in "{filename}".')

    return text
