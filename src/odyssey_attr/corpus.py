"""Corpus loading, normalization, book segmentation, and passage binning."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'][A-Za-zÀ-ÖØ-öø-ÿ]+)?(?:-[A-Za-zÀ-ÖØ-öø-ÿ]+)*")
PAGE_RE = re.compile(r"(?m)^<<<PDF_PAGE_\d+>>>\s*$")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"”’)]*)\s+(?=[A-ZÀ-ÖØ-Þ“‘\"])")
ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


@dataclass(frozen=True)
class BookText:
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
class Passage:
    translation_id: str
    translator: str
    year: int
    form: str
    book: int
    passage: int
    passage_id: str
    rel_start: float
    rel_end: float
    word_count: int
    text: str
    segmentation_confidence: float


def load_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def roman_to_int(value: str) -> int:
    value = value.upper().replace("J", "I")
    total = 0
    previous = 0
    for char in reversed(value):
        current = ROMAN_VALUES.get(char, 0)
        if current < previous:
            total -= current
        else:
            total += current
            previous = current
    return total


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
        substitutions = {
            "‘": "'",
            "’": "'",
            "“": '"',
            "”": '"',
            "VILL": "VIII",
        }
        for source, target in substitutions.items():
            text = text.replace(source, target)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = [piece.strip() for piece in SENTENCE_RE.split(text) if piece.strip()]
    return sentences or [text]


def _slice_by_word_counts(text: str, counts: list[int]) -> list[str]:
    matches = list(WORD_RE.finditer(text))
    if sum(counts) > len(matches):
        raise ValueError(f"Requested {sum(counts)} tokens from text containing {len(matches)}")
    slices: list[str] = []
    cursor = 0
    for count in counts:
        start_index = cursor
        end_index = cursor + count
        start_char = matches[start_index].start()
        end_char = matches[end_index - 1].end()
        slices.append(text[start_char:end_char].strip())
        cursor = end_index
    return slices


def segment_gutenberg(entry: dict, root: Path) -> list[BookText]:
    """Segment validated Project Gutenberg derivatives by explicit book markers.

    The preparation step writes ``<<<BOOK_XX>>>`` boundaries into every retained
    derivative.  These character-level anchors are authoritative; provenance
    token counts were produced by a different tokenizer and are diagnostics,
    not slicing coordinates.
    """
    source_path = root / entry["prepared_text"]
    provenance_path = root / entry["book_provenance"]
    raw = normalize_text(source_path.read_text(encoding="utf-8"))
    provenance = load_json(provenance_path)
    if len(provenance) != 24:
        raise ValueError(f"{entry['id']} provenance does not contain 24 books")

    markers = list(re.finditer(r"(?m)^<<<BOOK_(\d{2})>>>\s*$", raw))
    observed = [int(match.group(1)) for match in markers]
    if observed != list(range(1, 25)):
        raise ValueError(f"{entry['id']} prepared text has invalid book markers: {observed}")

    books: list[BookText] = []
    for offset, marker in enumerate(markers):
        end = markers[offset + 1].start() if offset < 23 else len(raw)
        chunk = raw[marker.end() : end].strip()
        if len(words(chunk)) < 500:
            raise ValueError(f"{entry['id']} book {offset + 1} is implausibly short")
        books.append(
            BookText(
                translation_id=entry["id"],
                translator=entry["translator"],
                year=int(entry["year"]),
                form=entry["form"],
                book=offset + 1,
                text=chunk,
                word_count=len(words(chunk)),
                segmentation_method="validated_explicit_book_markers",
                segmentation_confidence=0.995,
            )
        )
    return books


def segment_butler(entry: dict, root: Path) -> list[BookText]:
    raw = normalize_text((root / entry["prepared_text"]).read_text(encoding="utf-8"))
    matches = list(re.finditer(r"(?m)^BOOK\s+([IVXLC]+)\.?\s*$", raw))
    body_start = None
    for index, match in enumerate(matches[:-1]):
        if roman_to_int(match.group(1)) == 1 and roman_to_int(matches[index + 1].group(1)) == 2:
            if matches[index + 1].start() - match.end() > 3000:
                body_start = index
                break
    if body_start is None:
        raise ValueError("Could not find Butler body-level BOOK I marker")
    body_matches = matches[body_start : body_start + 24]
    if [roman_to_int(item.group(1)) for item in body_matches] != list(range(1, 25)):
        raise ValueError("Butler book markers are incomplete or non-sequential")
    books: list[BookText] = []
    for offset, match in enumerate(body_matches):
        end = body_matches[offset + 1].start() if offset < 23 else len(raw)
        chunk = raw[match.end() : end].strip()
        books.append(
            BookText(
                translation_id=entry["id"],
                translator=entry["translator"],
                year=int(entry["year"]),
                form=entry["form"],
                book=offset + 1,
                text=chunk,
                word_count=len(words(chunk)),
                segmentation_method="body_book_headings",
                segmentation_confidence=0.98,
            )
        )
    return books


def _murray_anchors(raw: str) -> list[tuple[int, int, int]]:
    """Return corrected (book, start, end-of-heading) OCR anchors."""
    pattern = re.compile(r"(?m)^\s*BOOK\s+([IVXLC1]+)\s*$")
    anchors: list[tuple[int, int, int]] = []
    previous = 0
    for match in pattern.finditer(raw):
        token = match.group(1).upper()
        number = 1 if token == "1" else roman_to_int(token)
        if number == 22 and previous == 22:
            number = 23
        if not anchors and number != 1:
            continue
        if anchors and number <= previous:
            continue
        if 1 <= number <= 24:
            anchors.append((number, match.start(), match.end()))
            previous = number
    return anchors


def _proportional_token_slices(text: str, template_counts: list[int]) -> list[str]:
    tokens = list(WORD_RE.finditer(text))
    if not tokens:
        return [""] * len(template_counts)
    total_template = sum(template_counts)
    allocations: list[int] = []
    used = 0
    for index, count in enumerate(template_counts):
        if index == len(template_counts) - 1:
            allocation = len(tokens) - used
        else:
            allocation = max(1, round(len(tokens) * count / total_template))
            allocation = min(allocation, len(tokens) - used - (len(template_counts) - index - 1))
        allocations.append(allocation)
        used += allocation
    return _slice_by_word_counts(text, allocations)


def segment_murray(entry: dict, root: Path, template_counts: list[int]) -> list[BookText]:
    raw = normalize_text((root / entry["prepared_text"]).read_text(encoding="utf-8"), ocr=True)
    anchors = _murray_anchors(raw)
    expected = [1, 2, 4, 6, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    observed = [item[0] for item in anchors]
    if observed != expected:
        raise ValueError(f"Unexpected Murray OCR anchors: {observed}")
    chunks: dict[int, str] = {}
    confidence: dict[int, float] = {}
    for index, (book, start, heading_end) in enumerate(anchors):
        next_start = anchors[index + 1][1] if index + 1 < len(anchors) else len(raw)
        next_book = anchors[index + 1][0] if index + 1 < len(anchors) else 25
        interval = raw[heading_end:next_start].strip()
        represented = list(range(book, next_book))
        split_chunks = _proportional_token_slices(interval, [template_counts[item - 1] for item in represented])
        for represented_book, chunk in zip(represented, split_chunks):
            chunks[represented_book] = chunk
            confidence[represented_book] = 0.92 if represented_book == book else 0.72
    if sorted(chunks) != list(range(1, 25)):
        raise ValueError(f"Murray segmentation produced books {sorted(chunks)}")
    return [
        BookText(
            translation_id=entry["id"],
            translator=entry["translator"],
            year=int(entry["year"]),
            form=entry["form"],
            book=book,
            text=chunks[book],
            word_count=len(words(chunks[book])),
            segmentation_method=("ocr_heading_anchor" if confidence[book] > 0.9 else "ocr_gap_proportional_split"),
            segmentation_confidence=confidence[book],
        )
        for book in range(1, 25)
    ]


def load_all_books(root: Path, corpus_config: Path) -> list[BookText]:
    registry = load_json(corpus_config)
    entries = registry["translations"]
    books: list[BookText] = []
    template_counts: list[int] | None = None
    deferred_murray: dict | None = None
    for entry in entries:
        if entry["id"] == "murray_1919":
            deferred_murray = entry
            continue
        if "book_provenance" in entry:
            segmented = segment_gutenberg(entry, root)
        elif entry["id"] == "butler_1900":
            segmented = segment_butler(entry, root)
        else:
            raise ValueError(f"No segmenter for {entry['id']}")
        books.extend(segmented)
        if entry["id"] == "butcher_lang_1879":
            template_counts = [item.word_count for item in segmented]
    if deferred_murray:
        if template_counts is None:
            raise ValueError("Butcher-Lang template counts are required for Murray fallback segmentation")
        books.extend(segment_murray(deferred_murray, root, template_counts))
    books.sort(key=lambda item: (item.year, item.book))
    if len(books) != len(entries) * 24:
        raise ValueError(f"Expected {len(entries) * 24} book records; obtained {len(books)}")
    return books


def books_to_passages(books: Iterable[BookText], bins_per_book: int = 20) -> list[Passage]:
    passages: list[Passage] = []
    for book in books:
        token_matches = list(WORD_RE.finditer(book.text))
        token_count = len(token_matches)
        if token_count < bins_per_book:
            raise ValueError(f"Book {book.translation_id}/{book.book} is too short for {bins_per_book} bins")
        for passage_index in range(1, bins_per_book + 1):
            start_token = round((passage_index - 1) * token_count / bins_per_book)
            end_token = round(passage_index * token_count / bins_per_book)
            start_char = token_matches[start_token].start()
            end_char = token_matches[end_token - 1].end()
            chunk = book.text[start_char:end_char].strip()
            passages.append(
                Passage(
                    translation_id=book.translation_id,
                    translator=book.translator,
                    year=book.year,
                    form=book.form,
                    book=book.book,
                    passage=passage_index,
                    passage_id=f"b{book.book:02d}_p{passage_index:02d}",
                    rel_start=(passage_index - 1) / bins_per_book,
                    rel_end=passage_index / bins_per_book,
                    word_count=len(words(chunk)),
                    text=chunk,
                    segmentation_confidence=book.segmentation_confidence,
                )
            )
    return passages


def write_books(path: Path, books: Iterable[BookText]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(books)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_passages(path: Path, passages: Iterable[Passage]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(passages)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
