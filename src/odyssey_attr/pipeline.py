"""End-to-end reproducible Odyssey attributional semantics pipeline."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import __version__
from .alignment import compute_alignment, write_alignment
from .analysis import (
    bootstrap_chronology,
    category_divergence,
    chronological_tests,
    contextual_embeddings,
    lexical_distinctiveness,
    save_tables,
    translation_summaries,
)
from .corpus import books_to_anchors, load_all_books, write_book_anchors, write_books
from .extract import extract_events, write_events
from .hypergraph import construct_hypergraphs, null_similarity_tests
from .reporting import make_figures, write_report

SEED = 20260717


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _write_validation_sample(events: pd.DataFrame, path: Path, per_stratum: int = 3) -> None:
    frame = events.copy()
    grouping_columns = ["translation_id", "category", "relation"]
    sampled_indices: list[int] = []
    for _, group in frame.groupby(grouping_columns, sort=True, dropna=False):
        sampled_indices.extend(
            group.sample(n=min(per_stratum, len(group)), random_state=SEED).index.tolist()
        )
    sample = frame.loc[sampled_indices].reset_index(drop=True)
    if len(sample) > 360:
        sample = sample.sample(n=360, random_state=SEED)
    sample = sample.sort_values(["translation_id", "book", "anchor_id", "sentence_index"])
    sample["gold_target_correct"] = ""
    sample["gold_attribute_correct"] = ""
    sample["gold_relation_correct"] = ""
    sample["gold_category_correct"] = ""
    sample["gold_revised_target"] = ""
    sample["gold_revised_attribute"] = ""
    sample["gold_revised_category"] = ""
    sample["annotator"] = ""
    sample["notes"] = ""
    path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(path, index=False, lineterminator="\n")


def _write_validation_instructions(path: Path) -> None:
    text = """# Manual validation protocol

Review each sampled event in its sentence context. Mark `gold_target_correct`, `gold_attribute_correct`, `gold_relation_correct`, and `gold_category_correct` as `1` or `0`. If a field is incorrect, enter the corrected canonical value in the corresponding revision column. Use `notes` for ambiguity, OCR artifacts, archaic syntax, or cases requiring a larger passage window.

Report precision with Wilson 95% intervals overall and separately by translation, ontology category, and extraction relation. Do not interpret category rates substantively if overall precision is below 0.80 or if any central category has fewer than 30 reviewed examples or precision below 0.70. Inter-annotator agreement should be estimated on at least 20% of the sample using Cohen’s kappa for binary correctness and Krippendorff’s alpha for revised categorical labels.
"""
    path.write_text(text, encoding="utf-8")


def _manifest(root: Path, start: datetime, end: datetime, counts: dict) -> dict:
    include_paths = [
        root / "config",
        root / "data" / "raw",
        root / "data" / "processed",
        root / "docs",
        root / "src",
        root / "scripts",
        root / "tests",
        root / "models",
        root / "outputs",
        root / "README.md",
        root / "Makefile",
        root / "pyproject.toml",
        root / "requirements-lock.txt",
        root / "environment.freeze.txt",
        root / "data" / "raw_checksums.sha256",
    ]
    candidate_files: set[Path] = set()
    for include_path in include_paths:
        if include_path.is_file():
            candidate_files.add(include_path)
        elif include_path.is_dir():
            candidate_files.update(item for item in include_path.rglob("*") if item.is_file())
    files = []
    for path in sorted(candidate_files):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(
            {
                "path": str(relative),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    packages = {}
    for name in ["numpy", "pandas", "scipy", "scikit-learn", "networkx", "matplotlib", "seaborn", "tabulate", "pytest"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "project_title": "Attributional Semantics in English Translations of Homer’s Odyssey: Color, Character, and Hypergraphs",
        "pipeline_version": __version__,
        "started_utc": start.isoformat(),
        "completed_utc": end.isoformat(),
        "random_seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "git_commit": _git_commit(root),
        "counts": counts,
        "files": files,
    }


def run(root: Path) -> dict:
    root = root.resolve()
    started = datetime.now(timezone.utc)
    config_dir = root / "config"
    processed_dir = root / "data" / "processed"
    table_dir = root / "outputs" / "tables"
    figure_dir = root / "outputs" / "figures"
    report_dir = root / "outputs" / "reports"
    hypergraph_dir = root / "outputs" / "hypergraphs"
    model_dir = root / "models"
    for directory in [processed_dir, table_dir, figure_dir, report_dir, hypergraph_dir, model_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    books = load_all_books(root, config_dir / "corpus.json")
    anchors = books_to_anchors(books)
    write_books(processed_dir / "books.csv", books)
    write_book_anchors(processed_dir / "book_anchors.csv", anchors)

    events = extract_events(anchors, config_dir / "ontology.json", config_dir / "entities.json")
    write_events(processed_dir / "attribution_events.csv", processed_dir / "attribution_events.jsonl", events)

    books_frame = pd.DataFrame([asdict(item) for item in books])
    anchors_frame = pd.DataFrame([asdict(item) for item in anchors])
    events_frame = pd.DataFrame([asdict(item) for item in events])

    pairwise_alignment, anchor_alignment = compute_alignment(anchors)
    write_alignment(processed_dir / "alignment_pairwise.csv", processed_dir / "alignment_book_anchors.csv", pairwise_alignment, anchor_alignment)
    pairwise_frame = pd.DataFrame(pairwise_alignment)
    anchor_frame = pd.DataFrame(anchor_alignment)

    summaries = translation_summaries(anchors_frame, events_frame)
    translation_meta = summaries["translation"][["translation_id", "translator", "year", "form"]]
    divergence = category_divergence(summaries["category"], translation_meta)
    chronology = chronological_tests(summaries["category"], translation_meta)
    bootstrap = bootstrap_chronology(anchors_frame, events_frame, translation_meta, iterations=500, seed=SEED)
    distinctiveness = lexical_distinctiveness(summaries["attribute"])
    centroid_table, context_comparisons = contextual_embeddings(events_frame, model_dir, dimensions=40)

    hypergraph_metrics, hypergraph_similarity = construct_hypergraphs(events_frame, hypergraph_dir)
    hypergraph_null = null_similarity_tests(events_frame, hypergraph_similarity, iterations=250, seed=SEED)

    tables = {
        "translation_summary": summaries["translation"],
        "category_summary": summaries["category"],
        "target_summary": summaries["target"],
        "attribute_summary": summaries["attribute"],
        "category_divergence": divergence,
        "chronological_tests": chronology,
        "bootstrap_chronology": bootstrap,
        "lexical_distinctiveness": distinctiveness,
        "context_centroids": centroid_table,
        "context_centroid_comparisons": context_comparisons,
        "hypergraph_metrics": hypergraph_metrics,
        "hypergraph_similarity": hypergraph_similarity,
        "hypergraph_null_tests": hypergraph_null,
        "alignment_pairwise": pairwise_frame,
        "alignment_anchors": anchor_frame,
        "book_segmentation_diagnostics": books_frame.drop(columns=["text"]),
    }
    save_tables(tables, table_dir)
    _write_validation_sample(events_frame, processed_dir / "validation_sample.csv")
    _write_validation_instructions(report_dir / "manual_validation_protocol.md")
    figures = make_figures(tables, figure_dir)
    write_report(tables, report_dir / "analysis_report.md", figures)

    completed = datetime.now(timezone.utc)
    counts = {
        "translations": int(anchors_frame["translation_id"].nunique()),
        "books": len(books_frame),
        "native_book_anchors": int(anchors_frame["anchor_id"].nunique()),
        "book_anchor_records": len(anchors_frame),
        "corpus_words": int(anchors_frame["word_count"].sum()),
        "attribution_events": len(events_frame),
        "targets": int(events_frame["target"].nunique()),
        "attributes": int(events_frame["attribute"].nunique()),
        "categories": int(events_frame["category"].nunique()),
    }
    manifest = _manifest(root, started, completed, counts)
    (root / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
