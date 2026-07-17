"""Statistical and distributional analyses for attribution events."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


def _weighted_events(events: pd.DataFrame) -> pd.Series:
    sign = np.where(events["negated"].astype(bool), -0.5, 1.0)
    return events["extraction_confidence"].astype(float) * sign


def translation_summaries(passages: pd.DataFrame, events: pd.DataFrame) -> dict[str, pd.DataFrame]:
    words = (
        passages.groupby(["translation_id", "translator", "year", "form"], as_index=False)["word_count"]
        .sum()
        .rename(columns={"word_count": "corpus_words"})
    )
    enriched = events.copy()
    enriched["weighted_event"] = _weighted_events(enriched)
    event_counts = enriched.groupby("translation_id", as_index=False).agg(
        event_count=("event_id", "count"),
        weighted_event_count=("weighted_event", "sum"),
        mean_extraction_confidence=("extraction_confidence", "mean"),
        median_extraction_confidence=("extraction_confidence", "median"),
    )
    overall = words.merge(event_counts, on="translation_id", how="left").fillna(0)
    overall["events_per_10k_words"] = overall["event_count"] / overall["corpus_words"] * 10000
    overall["weighted_events_per_10k_words"] = overall["weighted_event_count"] / overall["corpus_words"] * 10000

    category = (
        enriched.groupby(["translation_id", "category"], as_index=False)
        .agg(event_count=("event_id", "count"), weighted_event_count=("weighted_event", "sum"))
        .merge(words[["translation_id", "corpus_words"]], on="translation_id", how="left")
    )
    category["events_per_10k_words"] = category["event_count"] / category["corpus_words"] * 10000
    category["weighted_events_per_10k_words"] = category["weighted_event_count"] / category["corpus_words"] * 10000

    target = (
        enriched.groupby(["translation_id", "target", "target_type"], as_index=False)
        .agg(event_count=("event_id", "count"), weighted_event_count=("weighted_event", "sum"))
        .merge(words[["translation_id", "corpus_words"]], on="translation_id", how="left")
    )
    target["events_per_10k_words"] = target["event_count"] / target["corpus_words"] * 10000

    attribute = (
        enriched.groupby(["translation_id", "attribute", "category", "valence"], as_index=False)
        .agg(event_count=("event_id", "count"), weighted_event_count=("weighted_event", "sum"))
        .merge(words[["translation_id", "corpus_words"]], on="translation_id", how="left")
    )
    attribute["events_per_10k_words"] = attribute["event_count"] / attribute["corpus_words"] * 10000
    return {"translation": overall, "category": category, "target": target, "attribute": attribute}


def category_divergence(category: pd.DataFrame, translation_meta: pd.DataFrame) -> pd.DataFrame:
    matrix = category.pivot(index="translation_id", columns="category", values="weighted_event_count").fillna(0.0)
    matrix = matrix.clip(lower=0) + 1e-6
    matrix = matrix.div(matrix.sum(axis=1), axis=0)
    meta = translation_meta.set_index("translation_id")
    rows: list[dict] = []
    for left, right in itertools.combinations(matrix.index, 2):
        js = float(jensenshannon(matrix.loc[left], matrix.loc[right], base=2.0) ** 2)
        cosine = float(np.dot(matrix.loc[left], matrix.loc[right]) / (np.linalg.norm(matrix.loc[left]) * np.linalg.norm(matrix.loc[right])))
        rows.append(
            {
                "translation_a": left,
                "translation_b": right,
                "year_a": int(meta.loc[left, "year"]),
                "year_b": int(meta.loc[right, "year"]),
                "year_distance": abs(int(meta.loc[left, "year"]) - int(meta.loc[right, "year"])),
                "jensen_shannon_divergence": js,
                "category_cosine_similarity": cosine,
            }
        )
    return pd.DataFrame(rows)


def _slope_per_century(years: np.ndarray, values: np.ndarray) -> float:
    x = (years - years.mean()) / 100.0
    denominator = float(np.dot(x, x))
    return float(np.dot(x, values - values.mean()) / denominator) if denominator else 0.0


def _holm_adjust(pvalues: list[float]) -> list[float]:
    count = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = np.empty(count, dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        value = min(1.0, (count - rank) * pvalues[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted.tolist()


def chronological_tests(category: pd.DataFrame, translation_meta: pd.DataFrame) -> pd.DataFrame:
    translations = translation_meta.sort_values("year")["translation_id"].tolist()
    years = translation_meta.set_index("translation_id").loc[translations, "year"].to_numpy(dtype=float)
    rate_matrix = (
        category.pivot(index="translation_id", columns="category", values="weighted_events_per_10k_words")
        .reindex(translations)
        .fillna(0.0)
    )
    rows: list[dict] = []
    for category_name in rate_matrix.columns:
        values = rate_matrix[category_name].to_numpy(dtype=float)
        observed = _slope_per_century(years, values)
        null = np.array([_slope_per_century(np.array(permutation, dtype=float), values) for permutation in itertools.permutations(years)])
        p_value = (np.sum(np.abs(null) >= abs(observed)) + 1) / (len(null) + 1)
        correlation = float(np.corrcoef(years, values)[0, 1]) if np.std(values) > 0 else 0.0
        rows.append(
            {
                "category": category_name,
                "slope_events_per_10k_per_century": observed,
                "pearson_r_year": correlation,
                "exact_permutation_p": float(p_value),
                "n_translations": len(translations),
                "interpretation_boundary": "descriptive chronology; translator and period are not causally separable",
            }
        )
    adjusted = _holm_adjust([row["exact_permutation_p"] for row in rows])
    for row, value in zip(rows, adjusted):
        row["holm_adjusted_p"] = value
    return pd.DataFrame(rows).sort_values("exact_permutation_p")


def bootstrap_chronology(
    passages: pd.DataFrame,
    events: pd.DataFrame,
    translation_meta: pd.DataFrame,
    iterations: int = 500,
    seed: int = 20260717,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    translations = translation_meta.sort_values("year")["translation_id"].tolist()
    years = translation_meta.set_index("translation_id").loc[translations, "year"].to_numpy(dtype=float)
    categories = sorted(events["category"].unique())
    anchors = sorted(passages["passage_id"].unique())
    word_grid = passages.pivot_table(index="passage_id", columns="translation_id", values="word_count", aggfunc="sum").reindex(index=anchors, columns=translations, fill_value=0)
    enriched = events.copy()
    enriched["weighted_event"] = _weighted_events(enriched)
    event_grid = (
        enriched.pivot_table(index="passage_id", columns=["translation_id", "category"], values="weighted_event", aggfunc="sum", fill_value=0)
        .reindex(index=anchors, fill_value=0)
    )
    slopes = {category: [] for category in categories}
    for _ in range(iterations):
        sample_indices = rng.integers(0, len(anchors), len(anchors))
        sampled_words = word_grid.to_numpy()[sample_indices].sum(axis=0)
        for category in categories:
            values = []
            for translation_index, translation_id in enumerate(translations):
                column = (translation_id, category)
                weighted = event_grid[column].to_numpy()[sample_indices].sum() if column in event_grid.columns else 0.0
                values.append(weighted / sampled_words[translation_index] * 10000 if sampled_words[translation_index] else 0.0)
            slopes[category].append(_slope_per_century(years, np.asarray(values)))
    rows = []
    for category, values in slopes.items():
        array = np.asarray(values)
        rows.append(
            {
                "category": category,
                "bootstrap_iterations": iterations,
                "slope_mean": float(array.mean()),
                "slope_ci_2_5": float(np.quantile(array, 0.025)),
                "slope_ci_97_5": float(np.quantile(array, 0.975)),
                "probability_positive": float(np.mean(array > 0)),
            }
        )
    return pd.DataFrame(rows).sort_values("slope_mean")


def lexical_distinctiveness(attribute: pd.DataFrame) -> pd.DataFrame:
    counts = attribute.pivot_table(index="attribute", columns="translation_id", values="event_count", aggfunc="sum", fill_value=0.0)
    totals = counts.sum(axis=0)
    global_counts = counts.sum(axis=1)
    global_total = float(global_counts.sum())
    prior_strength = 0.5
    rows: list[dict] = []
    for translation in counts.columns:
        local_total = float(totals[translation])
        other_total = global_total - local_total
        for attribute_name in counts.index:
            local = float(counts.loc[attribute_name, translation])
            other = float(global_counts[attribute_name] - local)
            alpha = prior_strength + float(global_counts[attribute_name] / max(global_total, 1.0)) * 20.0
            local_odds = (local + alpha) / max(local_total - local + 20.0 - alpha, 1e-9)
            other_odds = (other + alpha) / max(other_total - other + 20.0 - alpha, 1e-9)
            log_odds = math.log(local_odds) - math.log(other_odds)
            variance = 1.0 / (local + alpha) + 1.0 / (other + alpha)
            z = log_odds / math.sqrt(variance)
            rows.append(
                {
                    "translation_id": translation,
                    "attribute": attribute_name,
                    "local_count": local,
                    "other_count": other,
                    "log_odds_ratio": log_odds,
                    "z_score": z,
                }
            )
    return pd.DataFrame(rows).sort_values(["translation_id", "z_score"], ascending=[True, False])


def contextual_embeddings(events: pd.DataFrame, model_dir: Path, dimensions: int = 40) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_dir.mkdir(parents=True, exist_ok=True)
    documents = events["context"].fillna("").astype(str).tolist()
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        max_features=12000,
        sublinear_tf=True,
        dtype=np.float32,
    )
    sparse = vectorizer.fit_transform(documents)
    effective_dimensions = min(dimensions, max(2, min(sparse.shape) - 1))
    svd = TruncatedSVD(n_components=effective_dimensions, random_state=20260717)
    vectors = normalize(svd.fit_transform(sparse).astype(np.float32))
    event_ids = events["event_id"].astype(str).to_numpy(dtype=str)
    np.savez_compressed(model_dir / "event_context_svd.npz", event_ids=event_ids, vectors=vectors)
    np.save(model_dir / "svd_components.npy", svd.components_.astype(np.float32))
    vocabulary = {str(term): int(index) for term, index in vectorizer.vocabulary_.items()}
    (model_dir / "tfidf_vocabulary.json").write_text(json.dumps(vocabulary, sort_keys=True), encoding="utf-8")
    (model_dir / "embedding_metadata.json").write_text(
        json.dumps(
            {
                "method": "TF-IDF unigrams+bigrams followed by TruncatedSVD and L2 normalization",
                "dimensions": effective_dimensions,
                "documents": len(documents),
                "vocabulary_size": len(vectorizer.vocabulary_),
                "explained_variance_ratio_sum": float(svd.explained_variance_ratio_.sum()),
                "random_state": 20260717,
                "scope": "memory-bounded contextual distributional baseline; not a transformer embedding",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    metadata = events[["event_id", "translation_id", "year", "target", "attribute", "category", "extraction_confidence"]].reset_index(drop=True)
    metadata.to_csv(model_dir / "event_context_metadata.csv", index=False)

    centroids: list[dict] = []
    for (translation, target, category), index_values in metadata.groupby(["translation_id", "target", "category"]).groups.items():
        indices = np.asarray(list(index_values), dtype=int)
        if len(indices) < 2:
            continue
        centroid = vectors[indices].mean(axis=0)
        norm = np.linalg.norm(centroid)
        centroid = centroid / norm if norm else centroid
        centroids.append(
            {
                "translation_id": translation,
                "target": target,
                "category": category,
                "event_count": len(indices),
                "centroid": centroid,
            }
        )
    comparisons: list[dict] = []
    centroid_frame = pd.DataFrame(centroids)
    if not centroid_frame.empty:
        for (target, category), group in centroid_frame.groupby(["target", "category"]):
            records = group.to_dict("records")
            for left, right in itertools.combinations(records, 2):
                similarity = float(np.dot(left["centroid"], right["centroid"]))
                comparisons.append(
                    {
                        "target": target,
                        "category": category,
                        "translation_a": left["translation_id"],
                        "translation_b": right["translation_id"],
                        "events_a": left["event_count"],
                        "events_b": right["event_count"],
                        "context_cosine_similarity": similarity,
                    }
                )
    centroid_table = centroid_frame.drop(columns=["centroid"]) if not centroid_frame.empty else pd.DataFrame(columns=["translation_id", "target", "category", "event_count"])
    comparison_table = pd.DataFrame(comparisons)
    return centroid_table, comparison_table


def save_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
