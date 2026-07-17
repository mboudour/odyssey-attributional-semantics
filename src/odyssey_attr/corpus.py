"""Corpus loading, normalization, and native Book I–XXIV anchoring."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'][A-Za-zÀ-ÖØ-öø-ÿ]+)?(?:-[A-Za-zÀ-ÖØ-öø-ÿ]+)*")
PAGE_RE = re.compile(r"(?m)^<<<(?:PDF|MURRAY_[A-Z0-9_]+)_PAGE_\d+>>>\s*$")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"”’)]*)\s+(?=[A-ZÀ-ÖØ-Þ“‘\"])")


@dataclass(frozen=True)
class BookText:
    """One translation’s text for a native Homeric book."""

    translation_id: str
    translator: str
    year: int
    form: str
    book: int
    text: str
    word_count: int
    segmentation_method: str
    segmentation_confidence: float


@dataclass(frozen=True)
class BookAnchor:
    """A complete native Book I–XXIV comparison unit across translations."""

    translation_id: str
    translator: str
    year: int
    form: str
    book: int
    anchor_id: str
    word_count: int
    text: str
    segmentation_confidence: float


def load_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def words(text: str) -> list[str]:
    return [match.group(0) for match in WORD_RE.finditer(text)]


def normalize_text(text: str, *, ocr: bool = False) -> str:
    """Normalize layout artifacts while preserving lexical evidence and punctuation."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "").replace("\ufeff", "")
    text = PAGE_RE.sub("\n", text)
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n[ ]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if ocr:
        for source, target in {"‘": "'", "’": "'", "“": '"', "”": '"'}.items():
            text = text.replace(source, target)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = [piece.strip() for piece in SENTENCE_RE.split(text) if piece.strip()]
    return sentences or [text]


def segment_prepared_books(entry: dict, root: Path) -> list[BookText]:
    """Load a poem-only prepared derivative with explicit native book markers."""
    source_path = root / entry["prepared_text"]
    provenance_path = root / entry["book_provenance"]
    raw = normalize_text(source_path.read_text(encoding="utf-8"), ocr=entry["id"] == "murray_1919")
    provenance = load_json(provenance_path)
    if not isinstance(provenance, list) or len(provenance) != 24:
        raise ValueError(f"{entry['id']} provenance does not contain 24 books")
    provenance_by_book = {int(item["book"]): item for item in provenance}
    if sorted(provenance_by_book) != list(range(1, 25)):
        raise ValueError(f"{entry['id']} provenance book numbers are incomplete")

    markers = list(re.finditer(r"(?m)^<<<BOOK_(\d{2})>>>\s*$", raw))
    observed = [int(match.group(1)) for match in markers]
    if observed != list(range(1, 25)):
        raise ValueError(f"{entry['id']} prepared text has invalid book markers: {observed}")

    books: list[BookText] = []
    for offset, marker in enumerate(markers):
        book_number = offset + 1
        end = markers[offset + 1].start() if offset < 23 else len(raw)
        chunk = raw[marker.end() : end].strip()
        word_count = len(words(chunk))
        if word_count < 500:
            raise ValueError(f"{entry['id']} Book {book_number} is implausibly short: {word_count} words")
        source_record = provenance_by_book[book_number]
        is_ocr = entry["id"] == "murray_1919"
        books.append(
            BookText(
                translation_id=entry["id"],
                translator=entry["translator"],
                year=int(entry["year"]),
                form=entry["form"],
                book=book_number,
                text=chunk,
                word_count=word_count,
                segmentation_method=source_record.get("extraction_method", "validated_explicit_book_markers"),
                segmentation_confidence=0.94 if is_ocr else 0.995,
            )
        )
    return books


def load_all_books(root: Path, corpus_config: Path) -> list[BookText]:
    """Load all approved translations, each fixed to its twenty-four native books."""
    registry = load_json(corpus_config)
    entries = registry["translations"]
    books: list[BookText] = []
    for entry in entries:
        if "prepared_text" not in entry or "book_provenance" not in entry:
            raise ValueError(f"{entry['id']} must provide prepared poem-only text and book provenance")
        books.extend(segment_prepared_books(entry, root))
    books.sort(key=lambda item: (item.year, item.book))
    if len(books) != len(entries) * 24:
        raise ValueError(f"Expected {len(entries) * 24} book records; obtained {len(books)}")
    return books


def books_to_anchors(books: Iterable[BookText]) -> list[BookAnchor]:
    """Convert each complete native book into one transparent alignment anchor."""
    anchors: list[BookAnchor] = []
    for book in books:
        if book.word_count < 500:
            raise ValueError(f"Book {book.translation_id}/{book.book} is too short for a native-book anchor")
        anchors.append(
            BookAnchor(
                translation_id=book.translation_id,
                translator=book.translator,
                year=book.year,
                form=book.form,
                book=book.book,
                anchor_id=f"book_{book.book:02d}",
                word_count=book.word_count,
                text=book.text,
                segmentation_confidence=book.segmentation_confidence,
            )
        )
    return anchors


def write_books(path: Path, books: Iterable[BookText]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(books)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_book_anchors(path: Path, anchors: Iterable[BookAnchor]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(anchors)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
