"""Figures and automatically generated analysis report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", context="talk")


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_figures(tables: dict[str, pd.DataFrame], figure_dir: Path) -> list[Path]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    translation = tables["translation_summary"].sort_values("year")
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=translation, x="translator", y="events_per_10k_words", hue="form", dodge=False, ax=ax)
    ax.set_title("Extracted attribution events by translation")
    ax.set_xlabel("")
    ax.set_ylabel("Events per 10,000 words")
    ax.tick_params(axis="x", rotation=35)
    path = figure_dir / "01_translation_event_rates.png"
    _save(fig, path)
    outputs.append(path)

    category = tables["category_summary"]
    category_order = category.groupby("category")["events_per_10k_words"].sum().sort_values(ascending=False).index
    translation_order = translation["translation_id"].tolist()
    category_matrix = category.pivot(index="translation_id", columns="category", values="events_per_10k_words").reindex(index=translation_order, columns=category_order).fillna(0)
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(category_matrix, cmap="mako", linewidths=0.3, ax=ax)
    ax.set_title("Attribution-category rates")
    ax.set_xlabel("Ontology category")
    ax.set_ylabel("Translation")
    path = figure_dir / "02_category_rate_heatmap.png"
    _save(fig, path)
    outputs.append(path)

    divergence = tables["category_divergence"]
    labels = translation_order
    js_matrix = pd.DataFrame(np.zeros((len(labels), len(labels))), index=labels, columns=labels)
    for row in divergence.itertuples(index=False):
        js_matrix.loc[row.translation_a, row.translation_b] = row.jensen_shannon_divergence
        js_matrix.loc[row.translation_b, row.translation_a] = row.jensen_shannon_divergence
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(js_matrix, annot=True, fmt=".3f", cmap="rocket_r", ax=ax)
    ax.set_title("Jensen–Shannon divergence of category profiles")
    path = figure_dir / "03_category_divergence.png"
    _save(fig, path)
    outputs.append(path)

    alignment = tables["alignment_pairwise"]
    fig, ax = plt.subplots(figsize=(11, 6))
    pair_labels = alignment["translation_a"].str.replace(r"_\d+$", "", regex=True) + " / " + alignment["translation_b"].str.replace(r"_\d+$", "", regex=True)
    alignment_plot = alignment.assign(pair=pair_labels)
    pair_order = alignment_plot.groupby("pair")["alignment_confidence"].median().sort_values(ascending=False).index
    sns.boxplot(data=alignment_plot, x="pair", y="alignment_confidence", order=pair_order, color="#4C78A8", fliersize=1, ax=ax)
    ax.set_title("Native Book I–XXIV alignment confidence")
    ax.set_xlabel("")
    ax.set_ylabel("Composite confidence")
    ax.tick_params(axis="x", rotation=70, labelsize=8)
    path = figure_dir / "04_alignment_confidence.png"
    _save(fig, path)
    outputs.append(path)

    chronology = tables["chronological_tests"].sort_values("slope_events_per_10k_per_century")
    fig, ax = plt.subplots(figsize=(11, 7))
    colors = ["#D95F02" if value < 0 else "#1B9E77" for value in chronology["slope_events_per_10k_per_century"]]
    ax.barh(chronology["category"], chronology["slope_events_per_10k_per_century"], color=colors)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Descriptive chronological slopes by category")
    ax.set_xlabel("Weighted events per 10,000 words per century")
    ax.set_ylabel("")
    path = figure_dir / "05_chronological_slopes.png"
    _save(fig, path)
    outputs.append(path)

    hyper = tables["hypergraph_similarity"]
    hyper_matrix = pd.DataFrame(np.eye(len(labels)), index=labels, columns=labels)
    for row in hyper.itertuples(index=False):
        hyper_matrix.loc[row.translation_a, row.translation_b] = row.weighted_jaccard
        hyper_matrix.loc[row.translation_b, row.translation_a] = row.weighted_jaccard
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(hyper_matrix, annot=True, fmt=".3f", cmap="crest", vmin=0, vmax=1, ax=ax)
    ax.set_title("Weighted hypergraph incidence similarity")
    path = figure_dir / "06_hypergraph_similarity.png"
    _save(fig, path)
    outputs.append(path)

    top_targets = tables["target_summary"].groupby("target")["event_count"].sum().nlargest(20).index
    target_matrix = (
        tables["target_summary"].query("target in @top_targets")
        .pivot(index="target", columns="translation_id", values="events_per_10k_words")
        .reindex(index=top_targets, columns=translation_order)
        .fillna(0)
    )
    fig, ax = plt.subplots(figsize=(11, 10))
    sns.heatmap(target_matrix, cmap="flare", linewidths=0.2, ax=ax)
    ax.set_title("Rates for the twenty most frequent targets")
    ax.set_xlabel("Translation")
    ax.set_ylabel("Canonical target")
    path = figure_dir / "07_top_target_rates.png"
    _save(fig, path)
    outputs.append(path)

    return outputs


def _markdown_table(frame: pd.DataFrame, columns: list[str], rows: int = 10) -> str:
    subset = frame.loc[:, columns].head(rows).copy()
    for column in subset.select_dtypes(include=["float"]).columns:
        subset[column] = subset[column].map(lambda value: f"{value:.4f}")
    return subset.to_markdown(index=False)


def write_report(tables: dict[str, pd.DataFrame], report_path: Path, figure_paths: list[Path]) -> None:
    translation = tables["translation_summary"].sort_values("year")
    events_total = int(translation["event_count"].sum())
    corpus_words = int(translation["corpus_words"].sum())
    lowest_alignment = tables["alignment_anchors"].nsmallest(10, "anchor_confidence")
    chronology = tables["chronological_tests"].sort_values("exact_permutation_p")
    bootstrap = tables["bootstrap_chronology"].sort_values("slope_mean")
    divergence = tables["category_divergence"].sort_values("jensen_shannon_divergence", ascending=False)
    hyper = tables["hypergraph_similarity"].sort_values("weighted_jaccard", ascending=False)
    distinct = tables["lexical_distinctiveness"].sort_values(["translation_id", "z_score"], ascending=[True, False]).groupby("translation_id").head(5)

    figures = "\n".join(f"![{path.stem}](../figures/{path.name})" for path in figure_paths)
    text = f"""# Attributional Semantics in English Translations of Homer’s *Odyssey*

## Computational Results Report

### Executive statement

This report documents a fully reproducible, rights-safe baseline analysis of **six complete English translations** published from 1616 to 1919. The processed corpus contains **{corpus_words:,} words** and the explicit extraction grammar identified **{events_total:,} target–attribute events**. Results quantify translation-specific attribution patterns; they do **not** establish a causal ideological evolution because translator, period, verse/prose form, and historical language are confounded.

### Corpus-level diagnostics

{_markdown_table(translation, ["translation_id", "translator", "year", "form", "corpus_words", "event_count", "events_per_10k_words", "mean_extraction_confidence"], rows=20)}

The common alignment coordinate is the complete native Homeric **Book I–XXIV** unit, yielding 24 matched anchors per translation. It is a transparent book-level structural alignment, not Greek-line alignment. Murray’s OCR-obscured Book III, V, IX, and XI starts are audited against original scan pages; no book is inferred by proportional allocation. OCR-derived text retains a reduced segmentation-confidence value.

The ten weakest anchors are:

{_markdown_table(lowest_alignment, ["anchor_id", "mean_pairwise_cosine", "mean_length_ratio", "anchor_confidence"], rows=10)}

### Primary distributional comparisons

The largest category-profile divergences are:

{_markdown_table(divergence, ["translation_a", "translation_b", "year_distance", "jensen_shannon_divergence", "category_cosine_similarity"], rows=10)}

The analysis uses weighted event counts, where each event is weighted by extraction confidence. Negated predicates receive a 0.5 magnitude multiplier and remain explicitly marked in the event table.

### Chronological estimands

For every ontology category, the pipeline estimates the descriptive slope in weighted events per 10,000 words per century. With only six translations, p-values come from all **720 exact permutations** of publication years. Holm adjustment controls family-wise error across categories. These tests assess chronological ordering under exchangeability; they do not identify ideology.

{_markdown_table(chronology, ["category", "slope_events_per_10k_per_century", "pearson_r_year", "exact_permutation_p", "holm_adjusted_p"], rows=20)}

Matched-book bootstrap intervals resample the 24 common native-book anchors, preserving within-anchor cross-translation dependence:

{_markdown_table(bootstrap, ["category", "slope_mean", "slope_ci_2_5", "slope_ci_97_5", "probability_positive"], rows=20)}

### Hypergraph comparisons

Each translation is represented as a weighted hypergraph in which canonical **targets are hyperedges** and normalized attributes are vertices. Incidence weights equal summed event confidences. Pairwise comparisons include weighted and unweighted Jaccard similarity, cosine similarity, and mean target-level edge overlap.

{_markdown_table(hyper, ["translation_a", "translation_b", "weighted_jaccard", "incidence_cosine", "unweighted_jaccard", "mean_target_edge_jaccard"], rows=15)}

The associated null model permutes attribute labels within each translation, preserving target degrees, attribute frequencies, and event weights. JSON hypergraphs and GraphML target/attribute projections are included under `outputs/hypergraphs/`.

### Memory-bounded contextual semantics

Event contexts are represented with TF–IDF unigrams/bigrams followed by Truncated SVD and L2 normalization. This sparse distributional baseline permits target/category centroid comparisons without loading a transformer on the memory-constrained cloud machine. It is intentionally labeled a baseline; transformer embeddings can be added later under the same event and alignment schema.

### Translation-distinctive attributes

Weighted log-odds-style z scores identify attributes that are comparatively distinctive within each translation. They are exploratory lexical diagnostics, not direct evidence of ideology.

{_markdown_table(distinct, ["translation_id", "attribute", "local_count", "log_odds_ratio", "z_score"], rows=30)}

### Validation and interpretation boundaries

The extraction layer is deliberately auditable. Every event records the surface target and attribute, canonical normalization, ontology category, relation template, token distance, negation, full sentence context, segmentation confidence, and extraction confidence. The package includes a stratified manual-validation sample and annotation template. Automatic estimates should not be interpreted substantively until that sample is reviewed and precision is reported by category, relation template, and translation.

The corpus is appropriate for testing historical translation variation and the computational pipeline. It is not adequate for a 1900–2017 trend claim because only one retained translation is later than 1900. Modern copyrighted translations should be analyzed locally as a governed, non-redistributed extension if lawful access and the applicable text-and-data-mining rules permit.

### Figures

{figures}

### Reproducibility

Run `make reproduce` from the repository root. The pipeline uses pinned dependencies, deterministic seeds, SHA-256 input/output manifests, and unit/integration tests. Machine-readable data, models, figures, tables, hypergraphs, logs, and this report are all included in the downloadable archive.
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")
