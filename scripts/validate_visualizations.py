#!/usr/bin/env python3
"""Validate configurable Gephi, PyVis, static projection, and native XGI artifacts."""

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
    parser.add_argument("--output-root", type=Path, default=None)
    return parser.parse_args()


def hex_rgb(value: str) -> tuple[int, int, int]:
    cleaned = value.lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Expected six-digit hexadecimal color, received {value!r}")
    return tuple(int(cleaned[index : index + 2], 16) for index in (0, 2, 4))


def validate(root: Path, output_root: Path | None = None) -> dict[str, int | str]:
    source = root / "outputs" / "hypergraphs"
    output = output_root or root / "outputs" / "hypergraph_visualizations"
    if not output.is_absolute():
        output = root / output
    config = json.loads((root / "config" / "visualizations.json").read_text(encoding="utf-8"))
    formats = config["output_formats"]
    expected_background = hex_rgb(config["theme"]["figure_background"])

    source_projections = sorted(source.glob("*_projection.graphml"))
    source_hypergraphs = sorted(source.glob("*_hypergraph.json"))
    png_files = sorted(output.rglob("*.png"))
    svg_files = sorted(output.rglob("*.svg"))
    html_files = sorted(output.rglob("*.html"))
    expected_static = len(source_projections) + len(source_hypergraphs)
    expected_png = expected_static if formats["png"] else 0
    expected_svg = expected_static if formats["svg"] else 0
    expected_html = len(source_projections) if formats["interactive_html"] else 0
    if len(png_files) != expected_png:
        raise ValueError(f"Expected {expected_png} PNG files, found {len(png_files)}")
    if len(svg_files) != expected_svg:
        raise ValueError(f"Expected {expected_svg} SVG files, found {len(svg_files)}")
    if len(html_files) != expected_html:
        raise ValueError(f"Expected {expected_html} PyVis HTML files, found {len(html_files)}")

    for path in png_files:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            width, height = rgb.size
            corner = rgb.getpixel((0, 0))
        if width < 600 or height < 400:
            raise ValueError(f"Visualization is unexpectedly small: {path.relative_to(root)} = {width}x{height}")
        if any(abs(corner[index] - expected_background[index]) > 3 for index in range(3)):
            raise ValueError(
                f"PNG corner does not match configured figure background: {path.relative_to(root)} = {corner}, expected {expected_background}"
            )

    for path in svg_files:
        ET.parse(path)
        if path.stat().st_size < 10_000:
            raise ValueError(f"SVG appears incomplete: {path.relative_to(root)}")

    configured_background = config["theme"]["figure_background"].lower()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        required = ("vis-network", "data-renderer='pyvis'", "pyvis interactive", configured_background)
        if any(token not in lowered for token in required):
            raise ValueError(f"PyVis HTML lacks renderer labeling, configured background, or network content: {path.relative_to(root)}")
        if path.parent.name != "projection_pyvis":
            raise ValueError(f"PyVis HTML is not stored in projection_pyvis/: {path.relative_to(root)}")
        if path.stat().st_size < 500_000:
            raise ValueError(f"PyVis HTML does not appear self-contained: {path.relative_to(root)}")

    inventory_path = output / "visualization_inventory.csv"
    with inventory_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(source_projections) + len(source_hypergraphs):
        raise ValueError("Visualization inventory row count is inconsistent with source artifacts")
    for row in rows:
        for field in ("png", "svg", "html", "gephi_graphml"):
            relative = row.get(field, "")
            if relative and not (output / relative).is_file():
                raise ValueError(f"Inventory references a missing file: {relative}")
        if row["visualization"].endswith("_projection"):
            if "PyVis" not in row["renderer"] or "Gephi" not in row["renderer"]:
                raise ValueError("Projection inventory must identify both PyVis and Gephi deliverables")

    readme_path = output / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    for required_text in ("## Gephi projection files", "Download Gephi GraphML", "## PyVis interactive projections", "Download PyVis HTML"):
        if required_text not in readme:
            raise ValueError(f"Gallery README lacks required guidance: {required_text}")
    markdown_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    for relative in markdown_links:
        if relative.startswith("http") or relative.startswith("#"):
            continue
        if not (output / relative).is_file():
            raise ValueError(f"Gallery README references a missing file: {relative}")

    return {
        "configured_background": config["theme"]["figure_background"],
        "source_projection_graphs": len(source_projections),
        "source_native_hypergraphs": len(source_hypergraphs),
        "png_files_checked": len(png_files),
        "svg_files_checked": len(svg_files),
        "pyvis_html_files_checked": len(html_files),
        "inventory_rows_checked": len(rows),
        "gallery_links_checked": len(markdown_links),
    }


def main() -> None:
    args = parse_args()
    print(json.dumps(validate(args.root.resolve(), args.output_root), indent=2))


if __name__ == "__main__":
    main()
