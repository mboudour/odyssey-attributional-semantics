from __future__ import annotations

import json
from pathlib import Path

from odyssey_attr.corpus import books_to_anchors, load_all_books
from odyssey_attr.extract import extract_events

ROOT = Path(__file__).resolve().parents[1]


def test_corpus_registry_contains_six_rights_safe_translations() -> None:
    registry = json.loads((ROOT / "config" / "corpus.json").read_text(encoding="utf-8"))
    assert len(registry["translations"]) == 6
    assert all(item["rights_status"] == "public_domain_us" for item in registry["translations"])
    assert {item["id"] for item in registry["translations"]} == {
        "chapman_1616",
        "pope_1726",
        "cowper_1791",
        "butcher_lang_1879",
        "butler_1900",
        "murray_1919",
    }


def test_all_translations_segment_to_twenty_four_books() -> None:
    books = load_all_books(ROOT, ROOT / "config" / "corpus.json")
    assert len(books) == 6 * 24
    per_translation: dict[str, set[int]] = {}
    for book in books:
        per_translation.setdefault(book.translation_id, set()).add(book.book)
        assert book.word_count > 500
        assert 0 < book.segmentation_confidence <= 1
    assert all(numbers == set(range(1, 25)) for numbers in per_translation.values())


def test_native_book_anchors_and_event_schema() -> None:
    books = load_all_books(ROOT, ROOT / "config" / "corpus.json")
    anchors = books_to_anchors(books)
    assert len(anchors) == 6 * 24
    assert {anchor.anchor_id for anchor in anchors} == {f"book_{book:02d}" for book in range(1, 25)}
    assert all(anchor.anchor_id == f"book_{anchor.book:02d}" for anchor in anchors)
    events = extract_events(
        anchors,
        ROOT / "config" / "ontology.json",
        ROOT / "config" / "entities.json",
    )
    assert events
    assert all(0 < event.extraction_confidence <= 1 for event in events)
    assert all(event.target and event.attribute and event.category and event.anchor_id for event in events)
    assert {event.relation for event in events} <= {
        "prepositive_modifier",
        "copular_predicate",
        "postpositive_apposition",
        "local_apposition",
        "pronoun_carryover",
    }
