#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

LATIN_RE = re.compile(r"[A-Za-z]")
GREEK_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")


def epub_spine_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = next(el for el in container.iter() if el.tag.endswith("rootfile"))
        opf_name = rootfile.attrib["full-path"]
        opf_dir = Path(opf_name).parent
        opf = ET.fromstring(zf.read(opf_name))
        manifest = {
            el.attrib["id"]: el.attrib
            for el in opf.iter()
            if el.tag.endswith("item") and "id" in el.attrib and "href" in el.attrib
        }
        spine = [
            el.attrib["idref"]
            for el in opf.iter()
            if el.tag.endswith("itemref") and "idref" in el.attrib
        ]
        parts = []
        for item_id in spine:
            item = manifest.get(item_id)
            if not item:
                continue
            href = item["href"].split("#", 1)[0]
            if "html" not in item.get("media-type", "") and not href.lower().endswith((".html", ".htm", ".xhtml")):
                continue
            member = str((opf_dir / href).as_posix())
            try:
                raw = zf.read(member)
            except KeyError:
                continue
            soup = BeautifulSoup(raw, "html.parser")
            parts.append(soup.get_text("\n", strip=True))
    text = "\n\n".join(parts)
    start = re.search(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.I | re.S)
    end = re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.I | re.S)
    if start:
        text = text[start.end():]
    if end:
        text = text[:end.start()]
    return text.strip() + "\n"


def classify_pdf_pages(path: Path) -> tuple[list[str], list[dict]]:
    proc = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    pages = proc.stdout.split("\f")
    kept = []
    page_map = []
    for page_no, page in enumerate(pages, start=1):
        latin = len(LATIN_RE.findall(page))
        greek = len(GREEK_RE.findall(page))
        words = len(WORD_RE.findall(page))
        # The Loeb scan alternates Greek and English pages. Keep Latin-dominant
        # pages with enough running text; retain front matter only in the map.
        is_english = words >= 55 and latin >= max(4 * greek, 180)
        page_map.append({
            "pdf_page": page_no,
            "latin_letters": latin,
            "greek_letters": greek,
            "ascii_word_tokens": words,
            "keep_as_english": is_english,
        })
        if is_english:
            kept.append(f"\n\n<<<PDF_PAGE_{page_no}>>>\n{page.strip()}\n")
    return kept, page_map


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--butler-epub", type=Path, required=True)
    ap.add_argument("--murray-vol1", type=Path, required=True)
    ap.add_argument("--murray-vol2", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    butler = epub_spine_text(args.butler_epub)
    (args.out_dir / "butler_1900_raw_spine.txt").write_text(butler, encoding="utf-8")

    all_murray = []
    all_maps = {}
    for label, path in (("vol1", args.murray_vol1), ("vol2", args.murray_vol2)):
        kept, page_map = classify_pdf_pages(path)
        all_murray.extend(kept)
        all_maps[label] = page_map
        (args.out_dir / f"murray_1919_{label}_english_pages.txt").write_text("".join(kept), encoding="utf-8")
    (args.out_dir / "murray_1919_english_pages.txt").write_text("".join(all_murray), encoding="utf-8")
    (args.out_dir / "murray_1919_page_classification.json").write_text(
        json.dumps(all_maps, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "butler_words": len(WORD_RE.findall(butler)),
        "murray_vol1_kept_pages": sum(x["keep_as_english"] for x in all_maps["vol1"]),
        "murray_vol2_kept_pages": sum(x["keep_as_english"] for x in all_maps["vol2"]),
        "murray_words": len(WORD_RE.findall("".join(all_murray))),
    }
    (args.out_dir / "preparation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
