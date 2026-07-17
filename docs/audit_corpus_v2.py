#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROMANS = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12,
    "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17,
    "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21, "XXII": 22,
    "XXIII": 23, "XXIV": 24,
}
BOOK_RE = re.compile(r"(?im)^\s*(?:book|bk\.?)[\s:.-]+(xxiv|xxiii|xxii|xxi|xx|xix|xviii|xvii|xvi|xv|xiv|xiii|xii|xi|x|ix|viii|vii|vi|v|iv|iii|ii|i)\b")
WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def pdf_extract(path: Path) -> tuple[str, dict]:
    info = run(["pdfinfo", str(path)])
    info_map = {}
    for line in info.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info_map[key.strip()] = value.strip()
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        out = Path(tmp.name)
    proc = run(["pdftotext", "-layout", str(path), str(out)])
    text = out.read_text(encoding="utf-8", errors="replace") if out.exists() else ""
    out.unlink(missing_ok=True)
    meta = {
        "extract_returncode": proc.returncode,
        "extract_error": proc.stderr.strip()[:500],
        "pages": int(info_map.get("Pages", "0") or 0),
        "encrypted": info_map.get("Encrypted", "unknown"),
        "title_metadata": info_map.get("Title", ""),
        "author_metadata": info_map.get("Author", ""),
    }
    return text, meta


def epub_extract(path: Path) -> tuple[str, dict]:
    with zipfile.ZipFile(path) as zf:
        bad_member = zf.testzip()
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = next(el for el in container.iter() if el.tag.endswith("rootfile"))
        opf_name = rootfile.attrib["full-path"]
        opf_dir = Path(opf_name).parent
        opf = ET.fromstring(zf.read(opf_name))
        manifest = {}
        for el in opf.iter():
            if el.tag.endswith("item") and "id" in el.attrib and "href" in el.attrib:
                manifest[el.attrib["id"]] = el.attrib
        spine = []
        for el in opf.iter():
            if el.tag.endswith("itemref") and "idref" in el.attrib:
                spine.append(el.attrib["idref"])
        parts = []
        used = 0
        for item_id in spine:
            item = manifest.get(item_id)
            if not item:
                continue
            media = item.get("media-type", "")
            href = item["href"].split("#", 1)[0]
            if "html" not in media and not href.lower().endswith((".xhtml", ".html", ".htm")):
                continue
            member = str((opf_dir / href).as_posix())
            try:
                raw = zf.read(member)
            except KeyError:
                continue
            soup = BeautifulSoup(raw, "html.parser")
            parts.append(soup.get_text("\n", strip=True))
            used += 1
        text = "\n\n".join(parts)
        meta = {
            "extract_returncode": 0 if text else 1,
            "extract_error": "" if text else "No readable spine documents",
            "pages": None,
            "encrypted": "no",
            "title_metadata": "",
            "author_metadata": "",
            "epub_bad_member": bad_member or "",
            "spine_items": len(spine),
            "spine_text_items": used,
        }
    return text, meta


def text_metrics(text: str) -> dict:
    words = WORD_RE.findall(text)
    headings = [ROMANS[x.upper()] for x in BOOK_RE.findall(text)]
    unique_books = sorted(set(headings))
    alpha = sum(c.isalpha() for c in text)
    printable = sum(c.isprintable() or c in "\n\t" for c in text)
    replacement = text.count("�")
    return {
        "text_chars": len(text),
        "word_tokens": len(words),
        "alpha_ratio": round(alpha / max(len(text), 1), 6),
        "printable_ratio": round(printable / max(len(text), 1), 6),
        "replacement_chars": replacement,
        "book_heading_hits": len(headings),
        "unique_books_detected": ",".join(map(str, unique_books)),
        "unique_book_count": len(unique_books),
        "has_book_1": 1 in unique_books,
        "has_book_24": 24 in unique_books,
    }


def main(paths: list[str], out_csv: Path, out_json: Path) -> None:
    rows = []
    for raw in paths:
        path = Path(raw)
        row = {
            "file_name": path.name,
            "source_path": str(path),
            "extension": path.suffix.lower(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        try:
            if path.suffix.lower() == ".pdf":
                text, meta = pdf_extract(path)
            elif path.suffix.lower() == ".epub":
                text, meta = epub_extract(path)
            else:
                raise ValueError("Unsupported extension")
            row.update(meta)
            row.update(text_metrics(text))
            row["python_processable"] = bool(row["extract_returncode"] == 0 and row["word_tokens"] >= 1000)
        except Exception as exc:
            row.update({
                "extract_returncode": 1,
                "extract_error": f"{type(exc).__name__}: {exc}",
                "python_processable": False,
                **text_metrics(""),
            })
        rows.append(row)

    fieldnames = sorted({key for row in rows for key in row})
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(rows), "csv": str(out_csv), "json": str(out_json)}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("Usage: audit_corpus_v2.py OUT.csv OUT.json FILE...")
    main(sys.argv[3:], Path(sys.argv[1]), Path(sys.argv[2]))
