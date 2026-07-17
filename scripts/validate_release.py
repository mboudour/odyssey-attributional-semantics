#!/usr/bin/env python3
"""Validate the integrity and expected scale of a completed Odyssey pipeline release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def validate(root: Path) -> dict[str, int | str]:
    manifest_path = root / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    counts = manifest["counts"]

    expected_rows = {
        "data/processed/books.csv": counts["books"],
        "data/processed/passages.csv": counts["passage_records"],
        "data/processed/attribution_events.csv": counts["attribution_events"],
        "data/processed/validation_sample.csv": 360,
        "outputs/tables/alignment_anchors.csv": counts["matched_passage_anchors"],
        "outputs/tables/translation_summary.csv": counts["translations"],
        "outputs/tables/category_summary.csv": counts["translations"] * counts["categories"],
        "models/event_context_metadata.csv": counts["attribution_events"],
    }
    for relative, expected in expected_rows.items():
        observed = csv_rows(root / relative)
        if observed != expected:
            raise ValueError(f"{relative}: expected {expected} data rows, observed {observed}")

    manifest_files = manifest["files"]
    if not manifest_files:
        raise ValueError("Manifest contains no file records")
    for record in manifest_files:
        path = root / record["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Manifest file missing: {record['path']}")
        if path.stat().st_size != record["bytes"]:
            raise ValueError(f"Size mismatch: {record['path']}")
        if sha256(path) != record["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {record['path']}")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            raise ValueError(f"Transient bytecode must not be manifested: {record['path']}")

    hypergraph_json = sorted((root / "outputs" / "hypergraphs").glob("*_hypergraph.json"))
    graphml_files = sorted((root / "outputs" / "hypergraphs").glob("*.graphml"))
    figure_files = sorted((root / "outputs" / "figures").glob("*.png"))
    if len(hypergraph_json) != counts["translations"]:
        raise ValueError("Expected one JSON hypergraph per translation")
    if len(graphml_files) != counts["translations"] * 2:
        raise ValueError("Expected two GraphML projections per translation")
    if len(figure_files) != 7:
        raise ValueError("Expected seven PNG figures")

    for path in hypergraph_json:
        json.loads(path.read_text(encoding="utf-8"))
    for path in graphml_files:
        ET.parse(path)
    for path in figure_files:
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Invalid PNG signature: {path.relative_to(root)}")

    vectors = np.load(root / "models" / "event_context_svd.npz", allow_pickle=False)
    event_ids = vectors["event_ids"]
    embeddings = vectors["vectors"]
    if event_ids.shape[0] != counts["attribution_events"]:
        raise ValueError("Embedding event-ID count does not match the manifest")
    if embeddings.shape[0] != counts["attribution_events"]:
        raise ValueError("Embedding row count does not match the manifest")
    embedding_metadata = json.loads((root / "models" / "embedding_metadata.json").read_text(encoding="utf-8"))
    if embeddings.shape[1] != embedding_metadata["dimensions"]:
        raise ValueError("Embedding dimensions do not match embedding metadata")

    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if manifest.get("git_commit") != head:
        raise ValueError(
            f"Manifest source commit {manifest.get('git_commit')} does not match HEAD {head}"
        )

    return {
        "manifest_files_verified": len(manifest_files),
        "csv_tables_checked": len(expected_rows),
        "figures_checked": len(figure_files),
        "hypergraphs_checked": len(hypergraph_json),
        "graphml_files_checked": len(graphml_files),
        "embedding_rows_checked": int(embeddings.shape[0]),
        "source_commit": head,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = validate(args.root.resolve())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
