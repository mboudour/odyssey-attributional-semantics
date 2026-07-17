"""Rule-based attribution candidate extraction with explicit uncertainty."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from .corpus import Passage, WORD_RE, split_sentences

COPULA_RE = re.compile(
    r"\b(?:am|art|are|be|become|became|been|being|is|seem|seemed|seems|was|wast|were|wert|wax|waxed)\b",
    re.IGNORECASE,
)
PRONOUN_RE = re.compile(r"\b(?:he|she|they|him|her|them|his|hers|their)\b", re.IGNORECASE)
NEGATION_RE = re.compile(r"\b(?:not|never|no|neither|nor)\b", re.IGNORECASE)


@dataclass(frozen=True)
class AttributionEvent:
    event_id: str
    translation_id: str
    translator: str
    year: int
    form: str
    book: int
    passage: int
    passage_id: str
    sentence_index: int
    target: str
    target_surface: str
    target_type: str
    attribute: str
    attribute_surface: str
    category: str
    valence: str
    relation: str
    negated: bool
    token_distance: int
    segmentation_confidence: float
    extraction_confidence: float
    context: str


def _phrase_pattern(phrases: Iterable[str]) -> re.Pattern[str]:
    alternatives = sorted({re.escape(item) for item in phrases}, key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z])(?:" + "|".join(alternatives) + r")(?![A-Za-z])", re.IGNORECASE)


def _token_index(text: str, char_position: int) -> int:
    return sum(1 for match in WORD_RE.finditer(text) if match.start() < char_position)


def _load_resources(ontology_path: Path, entities_path: Path) -> tuple[dict, dict]:
    with ontology_path.open("r", encoding="utf-8") as handle:
        ontology = json.load(handle)
    with entities_path.open("r", encoding="utf-8") as handle:
        entities = json.load(handle)
    return ontology, entities


def _attribute_maps(ontology: dict) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    category_map: dict[str, str] = {}
    for category, terms in ontology["categories"].items():
        for term in terms:
            category_map[term.lower()] = category
    normalization = {key.lower(): value.lower() for key, value in ontology.get("normalization", {}).items()}
    valence_map: dict[str, str] = {}
    for valence, terms in ontology.get("valence", {}).items():
        for term in terms:
            valence_map[normalization.get(term.lower(), term.lower())] = valence
    return category_map, normalization, valence_map


def _entity_aliases(entities: dict) -> list[tuple[str, str, str]]:
    aliases: list[tuple[str, str, str]] = []
    for canonical, variants in entities["entities"].items():
        if canonical in {"SEA", "SKY", "EARTH", "DAWN", "NIGHT", "SUN", "MOON", "WINE", "BLOOD", "FATE", "DEATH", "HOME", "JOURNEY", "WAR", "ANGER", "SORROW", "MIND", "SPEECH", "SHIP", "PALACE", "BOW", "SPEAR", "SWORD", "SHIELD", "FIRE", "STORM"}:
            target_type = "concept_or_setting"
        elif canonical in {"PHAEACIANS", "SUITORS", "GODS", "MORTALS", "ACHAEANS", "TROJANS", "CYCLOPES"}:
            target_type = "group"
        elif canonical in {"ITHACA", "TROY"}:
            target_type = "place"
        else:
            target_type = "character"
        for alias in variants:
            aliases.append((alias.lower(), canonical, target_type))
    aliases.sort(key=lambda item: len(item[0]), reverse=True)
    return aliases


def _find_targets(sentence: str, aliases: list[tuple[str, str, str]], generic_heads: list[str]) -> list[dict]:
    targets: list[dict] = []
    occupied: list[tuple[int, int]] = []
    for alias, canonical, target_type in aliases:
        pattern = re.compile(r"(?<![A-Za-z])" + re.escape(alias) + r"(?![A-Za-z])", re.IGNORECASE)
        for match in pattern.finditer(sentence):
            if any(not (match.end() <= start or match.start() >= end) for start, end in occupied):
                continue
            occupied.append((match.start(), match.end()))
            targets.append(
                {
                    "surface": match.group(0),
                    "canonical": canonical,
                    "type": target_type,
                    "start": match.start(),
                    "end": match.end(),
                    "token": _token_index(sentence, match.start()),
                }
            )
    generic_pattern = _phrase_pattern(generic_heads)
    for match in generic_pattern.finditer(sentence):
        if any(not (match.end() <= start or match.start() >= end) for start, end in occupied):
            continue
        targets.append(
            {
                "surface": match.group(0),
                "canonical": "GENERIC_" + re.sub(r"\W+", "_", match.group(0).upper()).strip("_"),
                "type": "generic",
                "start": match.start(),
                "end": match.end(),
                "token": _token_index(sentence, match.start()),
            }
        )
    return targets


def _relation(sentence: str, attribute: dict, target: dict) -> tuple[str | None, float, int]:
    distance = target["token"] - attribute["token"]
    absolute = abs(distance)
    if 0 < distance <= 4:
        between = sentence[attribute["end"] : target["start"]]
        if len(words_between := WORD_RE.findall(between)) <= 3:
            return "prepositive_modifier", 0.94, absolute
    if -10 <= distance < 0:
        between = sentence[target["end"] : attribute["start"]]
        if COPULA_RE.search(between):
            return "copular_predicate", 0.97, absolute
        if re.search(r"[,;:]", between) and absolute <= 6:
            return "postpositive_apposition", 0.82, absolute
    if absolute <= 3:
        return "local_apposition", 0.72, absolute
    return None, 0.0, absolute


def _event_id(parts: list[str]) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:20]


def extract_events(
    passages: Iterable[Passage], ontology_path: Path, entities_path: Path
) -> list[AttributionEvent]:
    ontology, entities = _load_resources(ontology_path, entities_path)
    category_map, normalization, valence_map = _attribute_maps(ontology)
    attribute_pattern = _phrase_pattern(category_map)
    aliases = _entity_aliases(entities)
    generic_heads = [item.lower() for item in entities["generic_target_heads"]]
    events: list[AttributionEvent] = []

    for passage in passages:
        last_character: dict | None = None
        for sentence_index, sentence in enumerate(split_sentences(passage.text), start=1):
            targets = _find_targets(sentence, aliases, generic_heads)
            explicit_characters = [item for item in targets if item["type"] == "character"]
            if explicit_characters:
                last_character = explicit_characters[-1]
            attributes = []
            for match in attribute_pattern.finditer(sentence):
                surface = match.group(0)
                raw = surface.lower()
                canonical = normalization.get(raw, raw)
                source_category = category_map.get(raw, category_map.get(canonical))
                attributes.append(
                    {
                        "surface": surface,
                        "canonical": canonical,
                        "category": source_category,
                        "start": match.start(),
                        "end": match.end(),
                        "token": _token_index(sentence, match.start()),
                    }
                )
            for attribute in attributes:
                candidates: list[tuple[float, dict, str, int]] = []
                for target in targets:
                    relation, base_score, distance = _relation(sentence, attribute, target)
                    if relation:
                        type_bonus = 0.02 if target["type"] != "generic" else -0.08
                        candidates.append((base_score + type_bonus, target, relation, distance))
                if not candidates and last_character and PRONOUN_RE.search(sentence):
                    pronoun = min(
                        PRONOUN_RE.finditer(sentence),
                        key=lambda item: abs(_token_index(sentence, item.start()) - attribute["token"]),
                    )
                    pronoun_distance = abs(_token_index(sentence, pronoun.start()) - attribute["token"])
                    if pronoun_distance <= 8:
                        candidates.append(
                            (
                                0.58,
                                {
                                    **last_character,
                                    "surface": pronoun.group(0),
                                    "token": _token_index(sentence, pronoun.start()),
                                },
                                "pronoun_carryover",
                                pronoun_distance,
                            )
                        )
                if not candidates:
                    continue
                candidates.sort(key=lambda item: (-item[0], item[3], item[1]["canonical"]))
                base_score, target, relation, distance = candidates[0]
                ambiguity_penalty = 1.0 if len(candidates) == 1 else 0.90
                negation_window_start = max(0, attribute["start"] - 45)
                negated = bool(NEGATION_RE.search(sentence[negation_window_start : attribute["end"]]))
                extraction_confidence = min(
                    0.99,
                    max(0.05, base_score * ambiguity_penalty * passage.segmentation_confidence),
                )
                event_key = [
                    passage.translation_id,
                    passage.passage_id,
                    str(sentence_index),
                    target["canonical"],
                    attribute["canonical"],
                    str(attribute["start"]),
                ]
                events.append(
                    AttributionEvent(
                        event_id=_event_id(event_key),
                        translation_id=passage.translation_id,
                        translator=passage.translator,
                        year=passage.year,
                        form=passage.form,
                        book=passage.book,
                        passage=passage.passage,
                        passage_id=passage.passage_id,
                        sentence_index=sentence_index,
                        target=target["canonical"],
                        target_surface=target["surface"],
                        target_type=target["type"],
                        attribute=attribute["canonical"],
                        attribute_surface=attribute["surface"],
                        category=attribute["category"],
                        valence=valence_map.get(attribute["canonical"], "unassigned"),
                        relation=relation,
                        negated=negated,
                        token_distance=distance,
                        segmentation_confidence=passage.segmentation_confidence,
                        extraction_confidence=round(extraction_confidence, 4),
                        context=sentence,
                    )
                )
    events.sort(key=lambda item: (item.year, item.book, item.passage, item.sentence_index, item.target, item.attribute))
    return events


def write_events(csv_path: Path, jsonl_path: Path, events: Iterable[AttributionEvent]) -> None:
    rows = list(events)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for event in rows:
            writer.writerow(asdict(event))
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for event in rows:
            handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
