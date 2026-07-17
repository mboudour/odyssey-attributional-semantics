"""Book-level alignment diagnostics for native Book I–XXIV anchors."""

from __future__ import annotations

import csv
import itertools
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .corpus import BookAnchor


def compute_alignment(anchors: Iterable[BookAnchor]) -> tuple[list[dict], list[dict]]:
    """Measure cross-translation resemblance within each complete native book."""
    rows = list(anchors)
    texts = [row.text for row in rows]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        max_features=20000,
        norm="l2",
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(texts)
    grouped: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        grouped.setdefault(row.anchor_id, []).append(index)

    pairwise: list[dict] = []
    anchor_rows: list[dict] = []
    for anchor_id, indices in sorted(grouped.items()):
        if len(indices) < 2:
            continue
        similarities: list[float] = []
        length_ratios: list[float] = []
        for left_index, right_index in itertools.combinations(indices, 2):
            left = rows[left_index]
            right = rows[right_index]
            cosine = float(matrix[left_index].multiply(matrix[right_index]).sum())
            length_ratio = min(left.word_count, right.word_count) / max(left.word_count, right.word_count)
            confidence = 0.55 * cosine + 0.25 * length_ratio + 0.20 * min(
                left.segmentation_confidence, right.segmentation_confidence
            )
            similarities.append(cosine)
            length_ratios.append(length_ratio)
            pairwise.append(
                {
                    "anchor_id": anchor_id,
                    "book": left.book,
                    "translation_a": left.translation_id,
                    "translation_b": right.translation_id,
                    "cosine_similarity": round(cosine, 6),
                    "length_ratio": round(length_ratio, 6),
                    "alignment_confidence": round(confidence, 6),
                }
            )
        anchor_confidence = float(np.mean(similarities)) * 0.60 + float(np.mean(length_ratios)) * 0.40
        anchor_rows.append(
            {
                "anchor_id": anchor_id,
                "book": rows[indices[0]].book,
                "translation_count": len(indices),
                "mean_pairwise_cosine": round(float(np.mean(similarities)), 6),
                "min_pairwise_cosine": round(float(np.min(similarities)), 6),
                "mean_length_ratio": round(float(np.mean(length_ratios)), 6),
                "anchor_confidence": round(anchor_confidence, 6),
            }
        )
    return pairwise, anchor_rows


def write_alignment(pairwise_path: Path, anchor_path: Path, pairwise: list[dict], anchors: list[dict]) -> None:
    pairwise_path.parent.mkdir(parents=True, exist_ok=True)
    with pairwise_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pairwise[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(pairwise)
    with anchor_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(anchors[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(anchors)
