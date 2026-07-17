#!/usr/bin/env python3
"""Validate generated projection and native XGI visualization artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def validate(root: Path) -> dict[str, int]:
    source = root / "outputs" / "hypergraphs"
    output = root / "outputs" / "hypergraph_visualizations"
    static = output / "projection_static"
    interactive = output / "projection_interactive"
    xgi_native = output / "xgi_native"

    source_projections = sorted(source.glob("*_projection.graphml"))
    source_hypergraphs = sorted(source.glob("*_hypergraph.json"))
    png_files = sorted(output.rglob("*.png"))
    svg_files = sorted(output.rglob("*.svg"))
    html_files = sorted(output.rglob("*.html"))

    expected_png = len(source_projections) + len(source_hypergraphs)
    expected_svg = len(source_projections) + len(source_hypergraphs)
    if len(png_files) != expected_png:
        raise ValueError(f"Expected {expected_png} PNG files, found {len(png_files)}")
    if len(svg_files) != expected_svg:
        raise ValueError(f"Expected {expected_svg} SVG files, found {len(svg_files)}")
    if len(html_files) != len(source_projections):
        raise ValueError(f"Expected {len(source_projections)} HTML files, found {len(html_files)}")

    for path in png_files:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
        if width < 2400 or height < 1400:
            raise ValueError(f"Visualization is undersized: {path.relative_to(root)} = {width}x{height}")

    for path in svg_files:
        ET.parse(path)
        if path.stat().st_size < 10_000:
            raise ValueError(f"SVG appears incomplete: {path.relative_to(root)}")

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "vis-network" not in text or "Weighted core" not in text:
            raise ValueError(f"Interactive HTML lacks expected network content: {path.relative_to(root)}")
        if path.stat().st_size < 500_000:
            raise ValueError(f"Interactive HTML does not appear self-contained: {path.relative_to(root)}")

    inventory_path = output / "visualization_inventory.csv"
    with inventory_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(source_projections) + len(source_hypergraphs):
        raise ValueError("Visualization inventory row count is inconsistent with source artifacts")
    for row in rows:
        for field in ("png", "svg", "html"):
            relative = row.get(field, "")
            if relative and not (output / relative).is_file():
                raise ValueError(f"Inventory references a missing file: {relative}")

    readme_path = output / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    markdown_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    for relative in markdown_links:
        if relative.startswith("http") or relative.startswith("#"):
            continue
        if not (output / relative).is_file():
            raise ValueError(f"Gallery README references a missing file: {relative}")

    return {
        "source_projection_graphs": len(source_projections),
        "source_native_hypergraphs": len(source_hypergraphs),
        "png_files_checked": len(png_files),
        "svg_files_checked": len(svg_files),
        "interactive_html_files_checked": len(html_files),
        "inventory_rows_checked": len(rows),
        "gallery_links_checked": len(markdown_links),
    }


def main() -> None:
    args = parse_args()
    print(json.dumps(validate(args.root.resolve()), indent=2))


if __name__ == "__main__":
    main()
