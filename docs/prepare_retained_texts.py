#!/usr/bin/env python3
"""Prepare rights-safe poem-only source derivatives with native Book I–XXIV anchors.

This script replaces the former whole-spine and proportional-splitting route.
Butler is extracted with the edition-specific Project Gutenberg selectors in
``prepare_gutenberg_additions.py``.  Murray is extracted directly from the
original Loeb scan using auditable title-page anchors, including the four
OCR-obscured headings independently checked against the source PDF.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from prepare_gutenberg_additions import WORD_RE, write_book_derivative

LATIN_RE = re.compile(r"[A-Za-z]")
GREEK_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
MURRAY_HEADER_RE = re.compile(r"^\s*THE\s+ODYSSEY\s*,?\s*[IVXLCDM]+\.?\s*(?:[\dIIVXLCDM].*)?$", re.I)
MURRAY_TITLE_RE = re.compile(r"^\s*Β?Ο?Ο?Κ\s+[IVXLCDM]+\s*$", re.I)
# In the Loeb layout explanatory notes begin in the lower page area with a
# locally numbered, indented capitalized line; dialogue/verse line numbers do
# not meet this combined condition.  The first detected note ends the page.
MURRAY_FOOTNOTE_START_RE = re.compile(r"^\s{4,}(?:[1-9]|1\d|2[0-5])\s+(?:[A-Z‘“])")

# The native book openings are the English title/running-text pages in the
# original 1919 Loeb PDFs.  Books III, V, IX, and XI lack usable OCR headings;
# their exact starts were verified at volume 1 pages 88, 190, 322, and 406.
MURRAY_BOOK_STARTS: dict[int, tuple[str, int, str]] = {
    1: ("vol1", 22, "printed Book I title page"),
    2: ("vol1", 56, "printed Book II title page"),
    3: ("vol1", 88, "OCR-obscured printed Book III title page; opening verified as ‘And now the sun, leaving the beauteous mere’"),
    4: ("vol1", 126, "printed Book IV title page"),
    5: ("vol1", 190, "OCR-obscured printed Book V title page; opening verified as ‘Now Dawn arose from bed’"),
    6: ("vol1", 226, "printed Book VI title page"),
    7: ("vol1", 252, "printed Book VII title page"),
    8: ("vol1", 278, "printed Book VIII title page"),
    9: ("vol1", 322, "OCR-obscured printed Book IX title page; opening verified as ‘Then Odysseus, of many wiles, answered him’"),
    10: ("vol1", 364, "printed Book X title page"),
    11: ("vol1", 406, "OCR-obscured printed Book XI title page; opening verified as ‘But when we had come down to the ship and to the sea’"),
    12: ("vol1", 452, "printed Book XII title page"),
    13: ("vol2", 12, "printed Book XIII title page"),
    14: ("vol2", 44, "printed Book XIV title page"),
    15: ("vol2", 84, "printed Book XV title page"),
    16: ("vol2", 126, "printed Book XVI title page"),
    17: ("vol2", 162, "printed Book XVII title page"),
    18: ("vol2", 206, "printed Book XVIII title page"),
    19: ("vol2", 238, "printed Book XIX title page"),
    20: ("vol2", 284, "printed Book XX title page"),
    21: ("vol2", 314, "printed Book XXI title page"),
    22: ("vol2", 346, "printed Book XXII title page"),
    23: ("vol2", 384, "printed Book XXIII title page; OCR label is erroneous"),
    24: ("vol2", 412, "printed Book XXIV title page"),
}

# The final translation pages precede publisher advertisements.  Values are
# exclusive PDF-page boundaries established from the final running headers.
MURRAY_TERMINAL_ENDS: dict[int, tuple[str, int]] = {
    12: ("vol1", 486),
    24: ("vol2", 454),
}


def classify_pdf_pages(path: Path) -> tuple[dict[int, str], list[dict]]:
    """Return English-dominant PDF pages and a complete classification audit."""
    proc = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    english_pages: dict[int, str] = {}
    page_map: list[dict] = []
    for page_no, page in enumerate(proc.stdout.split("\f"), start=1):
        latin = len(LATIN_RE.findall(page))
        greek = len(GREEK_RE.findall(page))
        words = len(WORD_RE.findall(page))
        # The Loeb scan alternates Greek and English pages.  English title pages
        # and running-text pages are Latin-dominant and contain substantive text.
        is_english = words >= 55 and latin >= max(4 * greek, 180)
        page_map.append(
            {
                "pdf_page": page_no,
                "latin_letters": latin,
                "greek_letters": greek,
                "ascii_word_tokens": words,
                "keep_as_english": is_english,
            }
        )
        if is_english:
            english_pages[page_no] = page
    return english_pages, page_map


def clean_murray_page(page: str) -> str:
    """Remove page furniture and lower-margin notes from Murray’s translation pages."""
    raw_lines = page.splitlines()
    kept: list[str] = []
    note_zone_start = max(8, round(len(raw_lines) * 0.58))
    for line_no, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue
        if MURRAY_HEADER_RE.match(line) or MURRAY_TITLE_RE.match(line):
            continue
        # The first lower-margin, indented numbered note excludes itself and
        # all subsequent bottom apparatus (including the printed page number).
        if line_no >= note_zone_start and MURRAY_FOOTNOTE_START_RE.match(raw_line):
            break
        if re.fullmatch(r"\d{1,3}[,.:]?", line):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def write_murray_raw_page_audit(english_by_volume: dict[str, dict[int, str]], out_dir: Path) -> None:
    """Keep a provenance-only page transcript separate from the analytical corpus."""
    combined: list[str] = []
    for volume in ("vol1", "vol2"):
        pages = english_by_volume[volume]
        volume_text = "\n\n".join(
            f"<<<MURRAY_{volume.upper()}_PDF_PAGE_{page_no:03d}>>>\n{page.strip()}"
            for page_no, page in sorted(pages.items())
        ) + "\n"
        (out_dir / f"murray_1919_{volume}_english_pages.txt").write_text(volume_text, encoding="utf-8")
        combined.append(volume_text)
    (out_dir / "murray_1919_english_pages.txt").write_text("\n".join(combined), encoding="utf-8")


def _end_page_for_book(book_num: int, volume: str, english_pages: dict[str, dict[int, str]]) -> int:
    """Use the next native start, or an audited terminal boundary for each volume."""
    if book_num in MURRAY_TERMINAL_ENDS:
        terminal_volume, terminal_page = MURRAY_TERMINAL_ENDS[book_num]
        if terminal_volume != volume:
            raise ValueError(f"Terminal boundary volume mismatch for Murray Book {book_num}")
        return terminal_page
    for next_book in range(book_num + 1, 25):
        next_volume, next_page, _ = MURRAY_BOOK_STARTS[next_book]
        if next_volume == volume:
            return next_page
    return max(english_pages[volume]) + 1


def extract_murray_books(english_pages: dict[str, dict[int, str]]) -> tuple[dict[int, str], list[dict]]:
    """Split Murray exclusively at native printed book starts, never by length."""
    books: dict[int, str] = {}
    provenance: list[dict] = []
    for book_num in range(1, 25):
        volume, start_page, source_note = MURRAY_BOOK_STARTS[book_num]
        end_page = _end_page_for_book(book_num, volume, english_pages)
        source_pages = [
            page_no
            for page_no in sorted(english_pages[volume])
            if start_page <= page_no < end_page
        ]
        if not source_pages or source_pages[0] != start_page:
            raise ValueError(f"Murray Book {book_num} lacks its audited start page {volume}:{start_page}")
        pieces = [clean_murray_page(english_pages[volume][page_no]) for page_no in source_pages]
        text = "\n\n".join(piece for piece in pieces if piece).strip()
        tokens = len(WORD_RE.findall(text))
        if tokens < 300:
            raise ValueError(f"Murray Book {book_num} is implausibly short after source cleaning: {tokens} tokens")
        books[book_num] = text
        provenance.append(
            {
                "book": book_num,
                "source": "Homer, Odyssey, A. T. Murray trans., Loeb Classical Library (1919) original scan",
                "volume": volume,
                "pdf_start_page": start_page,
                "pdf_end_page_exclusive": end_page,
                "source_page_count": len(source_pages),
                "source_note": source_note,
                "extraction_method": "native_printed_book_start_pages_no_proportional_allocation",
                "word_tokens": tokens,
            }
        )
    return books, provenance


def write_murray_derivative(english_pages: dict[str, dict[int, str]], out_dir: Path) -> dict:
    books, provenance = extract_murray_books(english_pages)
    text_path = out_dir / "murray_1919_books_1_24.txt"
    provenance_path = out_dir / "murray_1919_book_provenance.json"
    text_path.write_text(
        "\n\n".join(f"<<<BOOK_{book_num:02d}>>>\n{books[book_num]}" for book_num in range(1, 25)) + "\n",
        encoding="utf-8",
    )
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "books": 24,
        "word_tokens": sum(row["word_tokens"] for row in provenance),
        "text": text_path.name,
        "provenance": provenance_path.name,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--butler-epub", type=Path, required=True)
    ap.add_argument("--murray-vol1", type=Path, required=True)
    ap.add_argument("--murray-vol2", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    butler_summary = write_book_derivative(
        args.butler_epub,
        args.out_dir,
        prefix="butler_1900_poem_only",
    )
    english_by_volume: dict[str, dict[int, str]] = {}
    all_maps: dict[str, list[dict]] = {}
    for label, path in (("vol1", args.murray_vol1), ("vol2", args.murray_vol2)):
        english_by_volume[label], all_maps[label] = classify_pdf_pages(path)
    write_murray_raw_page_audit(english_by_volume, args.out_dir)
    murray_summary = write_murray_derivative(english_by_volume, args.out_dir)
    (args.out_dir / "murray_1919_page_classification.json").write_text(
        json.dumps(all_maps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    summary = {
        "butler": butler_summary,
        "murray": murray_summary,
        "murray_vol1_kept_pages": len(english_by_volume["vol1"]),
        "murray_vol2_kept_pages": len(english_by_volume["vol2"]),
        "native_book_anchor_count_per_translation": 24,
    }
    (args.out_dir / "preparation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
