#!/usr/bin/env python3
"""Create poem-only Project Gutenberg derivatives with native Book I–XXIV markers.

Each supported EPUB exposes one spine document per Odyssey book.  This module
uses edition-specific structural selectors to omit arguments, prose synopses,
footnotes, and final-book end matter before writing a common marker format.
The output carries no artificial within-book word-count partitions.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup, Tag

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11,
    "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16,
    "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21,
    "XXII": 22, "XXIII": 23, "XXIV": 24,
}

ORDINALS = {
    "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
    "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
    "NINTH": 9, "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12,
    "THIRTEENTH": 13, "FOURTEENTH": 14, "FIFTEENTH": 15,
    "SIXTEENTH": 16, "SEVENTEENTH": 17, "EIGHTEENTH": 18,
    "NINETEENTH": 19, "TWENTIETH": 20,
    "TWENTY-FIRST": 21, "TWENTY-SECOND": 22,
    "TWENTY-THIRD": 23, "TWENTY-FOURTH": 24,
    "ONE AND TWENTIETH": 21, "ONE-AND-TWENTIETH": 21,
    "TWO AND TWENTIETH": 22, "TWO-AND-TWENTIETH": 22,
    "THREE AND TWENTIETH": 23, "THREE-AND-TWENTIETH": 23,
    "FOUR AND TWENTIETH": 24, "FOUR-AND-TWENTIETH": 24,
}

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'][A-Za-zÀ-ÖØ-öø-ÿ]+)?")
HEADING_TAG_RE = re.compile(r"^h[1-6]$")


# The identifiers are deliberately based on source filename rather than
# translator metadata.  They implement the source-specific markup audit.
EDITION_RULES = {
    "Homer_Odyssey_Butcher_Lang_PG1728": {
        "mode": "paragraphs_after_heading",
        "start_class": None,
        "excluded_classes": {"letter", "footnote"},
        "description": "ordinary poem paragraphs after synopsis; letter and footnote paragraphs excluded",
    },
    "Homer_Odyssey_Chapman_PG48895": {
        "mode": "paragraphs_after_heading",
        "start_class": "noindent",
        "excluded_classes": {"footnote"},
        "description": "poem begins at p.noindent; argument and footnote paragraphs excluded",
    },
    "Homer_Odyssey_Cowper_PG24269": {
        "mode": "poem_divisions",
        "start_class": None,
        "excluded_classes": {"footnotes", "argument"},
        "description": "div.poem only; argument and footnote containers excluded",
    },
    "Homer_Odyssey_Pope_PG3160": {
        "mode": "paragraphs_after_heading",
        "start_class": "noindent",
        "excluded_classes": {"letter", "footnote", "center"},
        "description": "poem begins at p.noindent; argument and synopsis paragraphs excluded",
    },
    "Homer_Odyssey_Butler_1900_ProjectGutenberg": {
        "mode": "paragraphs_after_heading",
        "start_class": None,
        "excluded_classes": {"letter", "footnote"},
        "description": "ordinary poem/prose paragraphs after book subtitle; letter and footnote paragraphs excluded",
    },
}


def normalize_heading(text: str) -> str:
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip().upper()


def heading_to_book(text: str) -> int | None:
    heading = normalize_heading(text)
    if "END OF" in heading:
        return None
    match = re.match(r"^(?:THE\s+)?BOOK\s+([IVX]{1,6})\b", heading)
    if match and match.group(1) in ROMAN:
        return ROMAN[match.group(1)]
    if "BOOK OF HOMER'S ODYSSEYS" in heading:
        match = re.search(r"^THE\s+(.+?)\s+BOOK OF HOMER'S ODYSSEYS", heading)
        if match:
            return ORDINALS.get(match.group(1).strip())
    return None


def spine_documents(epub: Path) -> list[tuple[str, str]]:
    with zipfile.ZipFile(epub) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None:
            raise ValueError(f"No OPF rootfile in {epub}")
        opf_name = rootfile.attrib["full-path"]
        opf_dir = PurePosixPath(opf_name).parent
        opf = ET.fromstring(archive.read(opf_name))
        manifest = {
            item.attrib["id"]: item.attrib["href"].split("#", 1)[0]
            for item in opf.findall(".//{*}manifest/{*}item")
        }
        documents: list[tuple[str, str]] = []
        for itemref in opf.findall(".//{*}spine/{*}itemref"):
            href = manifest.get(itemref.attrib.get("idref", ""))
            if not href:
                continue
            member = str(opf_dir / href) if str(opf_dir) != "." else href
            if member not in archive.namelist():
                continue
            documents.append((member, archive.read(member).decode("utf-8", errors="replace")))
    return documents


def _classes(node: Tag) -> set[str]:
    return set(node.get("class", []))


def _has_excluded_ancestor(node: Tag, excluded: set[str]) -> bool:
    for candidate in [node, *node.parents]:
        if isinstance(candidate, Tag) and _classes(candidate).intersection(excluded):
            return True
    return False


def _clean_node_text(node: Tag) -> str:
    """Return text after removing navigation, note markers, and script content."""
    clone = BeautifulSoup(str(node), "html.parser")
    for tag in clone.find_all(["script", "style", "nav", "sup"]):
        tag.decompose()
    for tag in clone.find_all("a"):
        text = tag.get_text(" ", strip=True)
        if re.fullmatch(r"\[?\d+\]?", text or "") or "fnnum" in _classes(tag):
            tag.decompose()
    return re.sub(r"\s+", " ", clone.get_text(" ", strip=True)).strip()


def _is_end_marker(node: Tag) -> bool:
    """Recognize structural end labels without matching ordinary poem wording."""
    text = normalize_heading(node.get_text(" ", strip=True))
    if HEADING_TAG_RE.match(node.name or ""):
        return (
            text.startswith("FINIS LIBRI")
            or text.startswith("THE END OF THE") and "BOOK" in text
            or "END OF THE PROJECT GUTENBERG" in text
        )
    return node.name == "p" and text == "END OF THE ODYSSEY"


def _paragraphs_after_heading(soup: BeautifulSoup, heading: Tag, rule: dict) -> list[str]:
    """Extract non-note paragraphs after a source-native book heading."""
    started = rule["start_class"] is None
    pieces: list[str] = []
    ordered = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"])
    heading_seen = False
    for node in ordered:
        if node is heading:
            heading_seen = True
            continue
        if not heading_seen:
            continue
        if _is_end_marker(node):
            break
        if node.name != "p" or _has_excluded_ancestor(node, set(rule["excluded_classes"])):
            continue
        if not started:
            if rule["start_class"] in _classes(node):
                started = True
            else:
                continue
        text = _clean_node_text(node)
        if text:
            pieces.append(text)
    if not started:
        raise ValueError(f"Could not find source-defined poem start class {rule['start_class']!r}")
    return pieces


def _poem_divisions(soup: BeautifulSoup, heading: Tag, rule: dict) -> list[str]:
    """Extract Cowper's explicitly tagged poem division(s) without footnotes."""
    heading_seen = False
    pieces: list[str] = []
    for node in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "div", "p"]):
        if node is heading:
            heading_seen = True
            continue
        if not heading_seen:
            continue
        if _is_end_marker(node):
            break
        if node.name == "div" and "poem" in _classes(node):
            text = _clean_node_text(node)
            if text:
                pieces.append(text)
    return pieces


def extract_poem_only_book(epub: Path, book_num: int) -> tuple[str, dict]:
    """Return poem-only text and provenance for one native book in a supported EPUB."""
    rule = EDITION_RULES.get(epub.stem)
    if rule is None:
        raise ValueError(f"No audited poem-only extraction rule for {epub.name}")
    matches: list[tuple[str, BeautifulSoup, Tag]] = []
    for member, html in spine_documents(epub):
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav"]):
            tag.decompose()
        candidates = [
            heading
            for heading in soup.find_all(HEADING_TAG_RE)
            if heading_to_book(heading.get_text(" ", strip=True)) == book_num
        ]
        # A navigation document can repeat a Book I label.  It is not a
        # source book document if it lacks substantive running text.
        if candidates and len(WORD_RE.findall(soup.get_text(" ", strip=True))) >= 300:
            matches.append((member, soup, candidates[0]))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one source document for {epub.name}, Book {book_num}; found {len(matches)}")
    member, soup, heading = matches[0]
    if rule["mode"] == "poem_divisions":
        pieces = _poem_divisions(soup, heading, rule)
    else:
        pieces = _paragraphs_after_heading(soup, heading, rule)
    text = "\n\n".join(pieces).strip()
    token_count = len(WORD_RE.findall(text))
    if token_count < 300:
        raise ValueError(f"Implausibly short poem-only Book {book_num} in {epub.name}: {token_count} tokens")
    if re.search(r"\b(?:THE|ANOTHER)\s+ARGUMENT\b", text, flags=re.I):
        raise ValueError(f"Argument material survived poem-only extraction for {epub.name}, Book {book_num}")
    return text, {
        "book": book_num,
        "epub_member": member,
        "heading": heading.get_text(" ", strip=True),
        "extraction_method": "edition_specific_poem_only_html_selectors",
        "selector_rule": rule["description"],
        "word_tokens": token_count,
    }


def extract_books(epub: Path) -> tuple[dict[int, str], list[dict]]:
    books: dict[int, str] = {}
    provenance: list[dict] = []
    for book_num in range(1, 25):
        text, row = extract_poem_only_book(epub, book_num)
        books[book_num] = text
        provenance.append(row)
    return books, provenance


def write_book_derivative(epub: Path, out_dir: Path, *, prefix: str | None = None) -> dict:
    """Write a marker-delimited poem-only derivative and its provenance sidecar."""
    out_dir.mkdir(parents=True, exist_ok=True)
    books, provenance = extract_books(epub)
    stem = prefix or epub.stem
    out_text = out_dir / f"{stem}_books_1_24.txt"
    out_json = out_dir / f"{stem}_book_provenance.json"
    out_text.write_text(
        "\n\n".join(f"<<<BOOK_{book_num:02d}>>>\n{books[book_num]}" for book_num in range(1, 25)) + "\n",
        encoding="utf-8",
    )
    out_json.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "epub": epub.name,
        "books": 24,
        "word_tokens": sum(item["word_tokens"] for item in provenance),
        "text": out_text.name,
        "provenance": out_json.name,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("epubs", nargs="+", type=Path)
    args = parser.parse_args()
    summary = [write_book_derivative(epub, args.out_dir) for epub in args.epubs]
    (args.out_dir / "gutenberg_additions_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
