"""Weighted multilayer attribution hypergraphs and comparison statistics."""

from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


def _incidence(events: pd.DataFrame) -> dict[tuple[str, str], float]:
    frame = events.copy()
    frame["weight"] = frame["extraction_confidence"].astype(float) * np.where(frame["negated"].astype(bool), 0.5, 1.0)
    grouped = frame.groupby(["target", "attribute"], as_index=False)["weight"].sum()
    return {(row.target, row.attribute): float(row.weight) for row in grouped.itertuples(index=False)}


def _weighted_jaccard(left: dict, right: dict) -> float:
    keys = sorted(set(left) | set(right))
    if not keys:
        return 1.0
    numerator = sum(min(left.get(key, 0.0), right.get(key, 0.0)) for key in keys)
    denominator = sum(max(left.get(key, 0.0), right.get(key, 0.0)) for key in keys)
    return numerator / denominator if denominator else 1.0


def _cosine(left: dict, right: dict) -> float:
    keys = sorted(set(left) | set(right))
    if not keys:
        return 1.0
    left_vector = np.asarray([left.get(key, 0.0) for key in keys], dtype=float)
    right_vector = np.asarray([right.get(key, 0.0) for key in keys], dtype=float)
    denominator = np.linalg.norm(left_vector) * np.linalg.norm(right_vector)
    return float(np.dot(left_vector, right_vector) / denominator) if denominator else 0.0


def _edge_set_similarity(left: dict, right: dict) -> float:
    targets = sorted({key[0] for key in left} | {key[0] for key in right})
    values: list[float] = []
    for target in targets:
        left_attributes = {attribute for row_target, attribute in left if row_target == target}
        right_attributes = {attribute for row_target, attribute in right if row_target == target}
        union = left_attributes | right_attributes
        values.append(len(left_attributes & right_attributes) / len(union) if union else 1.0)
    return float(np.mean(values)) if values else 1.0


def construct_hypergraphs(events: pd.DataFrame, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    incidence_by_translation: dict[str, dict[tuple[str, str], float]] = {}
    metrics: list[dict] = []
    for translation, group in events.groupby("translation_id"):
        incidence = _incidence(group)
        incidence_by_translation[translation] = incidence
        targets = sorted({key[0] for key in incidence})
        attributes = sorted({key[1] for key in incidence})
        edges: dict[str, list[dict]] = defaultdict(list)
        category_lookup = group.drop_duplicates(["attribute"]).set_index("attribute")["category"].to_dict()
        for (target, attribute), weight in sorted(incidence.items()):
            edges[target].append(
                {
                    "attribute": attribute,
                    "category": category_lookup.get(attribute, "unknown"),
                    "weight": round(weight, 6),
                }
            )
        payload = {
            "translation_id": translation,
            "representation": "target-as-hyperedge over attribute vertices",
            "vertices": attributes,
            "hyperedges": edges,
            "incidence_weight": "sum of event extraction confidences; negated events multiplied by 0.5",
        }
        (output_dir / f"{translation}_hypergraph.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        possible = len(targets) * len(attributes)
        weights = np.asarray([incidence[key] for key in sorted(incidence)], dtype=float)
        probabilities = weights / weights.sum() if weights.sum() else weights
        entropy = float(-np.sum(probabilities * np.log2(probabilities))) if len(probabilities) else 0.0
        metrics.append(
            {
                "translation_id": translation,
                "target_hyperedges": len(targets),
                "attribute_vertices": len(attributes),
                "nonzero_incidences": len(incidence),
                "incidence_density": len(incidence) / possible if possible else 0.0,
                "mean_attributes_per_target": len(incidence) / len(targets) if targets else 0.0,
                "weighted_incidence_sum": float(weights.sum()),
                "incidence_entropy_bits": entropy,
            }
        )
        _write_projections(translation, incidence, output_dir)

    similarities: list[dict] = []
    for left, right in itertools.combinations(sorted(incidence_by_translation), 2):
        left_incidence = incidence_by_translation[left]
        right_incidence = incidence_by_translation[right]
        left_keys = set(left_incidence)
        right_keys = set(right_incidence)
        union = left_keys | right_keys
        similarities.append(
            {
                "translation_a": left,
                "translation_b": right,
                "weighted_jaccard": _weighted_jaccard(left_incidence, right_incidence),
                "incidence_cosine": _cosine(left_incidence, right_incidence),
                "unweighted_jaccard": len(left_keys & right_keys) / len(union) if union else 1.0,
                "mean_target_edge_jaccard": _edge_set_similarity(left_incidence, right_incidence),
            }
        )
    return pd.DataFrame(metrics), pd.DataFrame(similarities)


def null_similarity_tests(
    events: pd.DataFrame,
    observed: pd.DataFrame,
    iterations: int = 250,
    seed: int = 20260717,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    grouped = {translation: group.reset_index(drop=True) for translation, group in events.groupby("translation_id")}
    rows: list[dict] = []
    for observed_row in observed.itertuples(index=False):
        left = grouped[observed_row.translation_a]
        right = grouped[observed_row.translation_b]
        left_incidence = _incidence(left)
        null_values: list[float] = []
        right_attributes = right["attribute"].to_numpy(copy=True)
        for _ in range(iterations):
            permuted = right.copy()
            permuted["attribute"] = rng.permutation(right_attributes)
            null_values.append(_weighted_jaccard(left_incidence, _incidence(permuted)))
        null_array = np.asarray(null_values)
        standard_deviation = float(null_array.std(ddof=1))
        z_score = (observed_row.weighted_jaccard - float(null_array.mean())) / standard_deviation if standard_deviation else 0.0
        p_upper = (np.sum(null_array >= observed_row.weighted_jaccard) + 1) / (iterations + 1)
        rows.append(
            {
                "translation_a": observed_row.translation_a,
                "translation_b": observed_row.translation_b,
                "observed_weighted_jaccard": observed_row.weighted_jaccard,
                "null_mean": float(null_array.mean()),
                "null_sd": standard_deviation,
                "z_score": z_score,
                "upper_tail_p": float(p_upper),
                "iterations": iterations,
                "null_model": "permute attribute labels within translation; preserve target degrees, attribute frequencies, and event weights",
            }
        )
    return pd.DataFrame(rows)


def _write_projections(translation: str, incidence: dict[tuple[str, str], float], output_dir: Path) -> None:
    target_to_attributes: dict[str, dict[str, float]] = defaultdict(dict)
    attribute_to_targets: dict[str, dict[str, float]] = defaultdict(dict)
    for (target, attribute), weight in incidence.items():
        target_to_attributes[target][attribute] = weight
        attribute_to_targets[attribute][target] = weight

    target_graph = nx.Graph(translation_id=translation, projection="targets_shared_attributes")
    for target, attributes in target_to_attributes.items():
        target_graph.add_node(target, kind="target", degree_in_hypergraph=len(attributes))
    for left, right in itertools.combinations(sorted(target_to_attributes), 2):
        shared = set(target_to_attributes[left]) & set(target_to_attributes[right])
        if shared:
            weight = sum(min(target_to_attributes[left][item], target_to_attributes[right][item]) for item in sorted(shared))
            target_graph.add_edge(left, right, weight=float(weight), shared_attribute_count=len(shared))
    nx.write_graphml(target_graph, output_dir / f"{translation}_target_projection.graphml")

    attribute_graph = nx.Graph(translation_id=translation, projection="attributes_shared_targets")
    for attribute, targets in attribute_to_targets.items():
        attribute_graph.add_node(attribute, kind="attribute", degree_in_hypergraph=len(targets))
    for left, right in itertools.combinations(sorted(attribute_to_targets), 2):
        shared = set(attribute_to_targets[left]) & set(attribute_to_targets[right])
        if shared:
            weight = sum(min(attribute_to_targets[left][item], attribute_to_targets[right][item]) for item in sorted(shared))
            attribute_graph.add_edge(left, right, weight=float(weight), shared_target_count=len(shared))
    nx.write_graphml(attribute_graph, output_dir / f"{translation}_attribute_projection.graphml")
