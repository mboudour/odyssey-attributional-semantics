from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from odyssey_attr.analysis import contextual_embeddings
from odyssey_attr.pipeline import _write_validation_sample


def test_validation_sample_preserves_grouping_columns(tmp_path: Path) -> None:
    events = pd.DataFrame(
        [
            {
                "event_id": f"event-{index}",
                "translation_id": translation,
                "category": category,
                "relation": relation,
                "book": 1,
                "passage": index + 1,
                "sentence_index": 1,
            }
            for index, (translation, category, relation) in enumerate(
                [
                    ("chapman_1616", "color_hue", "prepositive_modifier"),
                    ("chapman_1616", "color_hue", "prepositive_modifier"),
                    ("pope_1726", "moral_evaluation", "copular_predicate"),
                    ("pope_1726", "moral_evaluation", "copular_predicate"),
                ]
            )
        ]
    )
    destination = tmp_path / "validation_sample.csv"

    _write_validation_sample(events, destination, per_stratum=1)

    sample = pd.read_csv(destination)
    assert {"translation_id", "category", "relation", "book", "passage"} <= set(sample.columns)
    assert len(sample) == 2
    assert sample.groupby(["translation_id", "category", "relation"]).size().max() == 1


def test_contextual_embedding_vocabulary_is_json_serializable(tmp_path: Path) -> None:
    events = pd.DataFrame(
        [
            {
                "event_id": f"event-{index}",
                "translation_id": translation,
                "year": year,
                "target": target,
                "attribute": attribute,
                "category": category,
                "extraction_confidence": 0.9,
                "context": context,
            }
            for index, (translation, year, target, attribute, category, context) in enumerate(
                [
                    ("chapman_1616", 1616, "SEA", "dark", "color_complex", "The dark sea rolled under night."),
                    ("chapman_1616", 1616, "SEA", "dark", "color_complex", "Across the dark sea the ship went."),
                    ("pope_1726", 1726, "SEA", "bright", "luminosity", "The bright sea shone at dawn."),
                    ("pope_1726", 1726, "SEA", "bright", "luminosity", "Across the bright sea the ship went."),
                ]
            )
        ]
    )

    contextual_embeddings(events, tmp_path, dimensions=2)

    vocabulary = json.loads((tmp_path / "tfidf_vocabulary.json").read_text(encoding="utf-8"))
    assert vocabulary
    assert all(isinstance(term, str) and isinstance(index, int) for term, index in vocabulary.items())
