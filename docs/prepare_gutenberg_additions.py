#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11,
    "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16,
    "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21,
    "XXII": 22, "XXIII": 23, "XXIV": 24,
}

ORDINALS = {
    "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
    "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
    "NINTH": 9, "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12,
    "THIRTEENTH": 13, "FOURTEENTH": 14, "FIFTEENTH": 15,
    "SIXTEENTH": 16, "SEVENTEENTH": 17, "EIGHTEENTH": 18,
    "NINETEENTH": 19, "TWENTIETH": 20,
    "TWENTY-FIRST": 21, "TWENTY-SECOND": 22,
    "TWENTY-THIRD": 23, "TWENTY-FOURTH": 24,
    "ONE AND TWENTIETH": 21, "ONE-AND-TWENTIETH": 21,
    "TWO AND TWENTIETH": 22, "TWO-AND-TWENTIETH": 22,
    "THREE AND TWENTIETH": 23, "THREE-AND-TWENTIETH": 23,
    "FOUR AND TWENTIETH": 24, "FOUR-AND-TWENTIETH": 24,
}


def normalize_heading(text: str) -> str:
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip().upper()


def heading_to_book(text: str) -> int | None:
    h = normalize_heading(text)
    if "END OF" in h:
        return None
    match = re.search(r"\bBOOK\s+([IVX]{1,6})\b", h)
    if match and match.group(1) in ROMAN:
        return ROMAN[match.group(1)]
    if "BOOK OF HOMER'S ODYSSEYS" in h:
        match = re.search(r"^THE\s+(.+?)\s+BOOK OF HOMER'S ODYSSEYS", h)
        if match:
            return ORDINALS.get(match.group(1).strip())
    return None


def spine_documents(epub: Path) -> list[tuple[str, str]]:
    with zipfile.ZipFile(epub) as zf:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None:
            raise ValueError(f"No OPF rootfile in {epub}")
        opf_name = rootfile.attrib["full-path"]
        opf_dir = PurePosixPath(opf_name).parent
        opf = ET.fromstring(zf.read(opf_name))
        manifest = {
            item.attrib["id"]: item.attrib["href"]
            for item in opf.findall(".//{*}manifest/{*}item")
        }
        docs = []
        for itemref in opf.findall(".//{*}spine/{*}itemref"):
            href = manifest.get(itemref.attrib.get("idref", ""))
            if not href:
                continue
            member = str(opf_dir / href) if str(opf_dir) != "." else href
            if member not in zf.namelist():
                continue
            raw = zf.read(member)
            try:
                html = raw.decode("utf-8")
            except UnicodeDecodeError:
                html = raw.decode("utf-8", errors="replace")
            docs.append((member, html))
        return docs


def extract_books(epub: Path) -> tuple[dict[int, str], list[dict]]:
    books: dict[int, str] = {}
    provenance: list[dict] = []
    for member, html in spine_documents(epub):
        soup = BeautifulSoup(html, "html.parser")
        candidates = []
        for heading in soup.find_all(re.compile(r"^h[1-6]$")):
            number = heading_to_book(heading.get_text(" ", strip=True))
            if number is not None:
                candidates.append((number, heading))
        distinct = sorted({number for number, _ in candidates})
        if len(distinct) != 1:
            continue
        number, heading = candidates[0]
        if number in books:
            continue
        for tag in soup(["script", "style", "nav"]):
            tag.decompose()
        document_text = soup.get_text("\n", strip=True)
        heading_text = heading.get_text(" ", strip=True)
        start = document_text.find(heading_text)
        if start < 0:
            raise ValueError(f"Opening heading not found in flattened text: {epub.name}, Book {number}")
        body = document_text[start + len(heading_text):].strip()
        end_match = re.search(r"\bTHE\s+END\s+OF\s+THE\b.{0,120}?\bBOOK\b", body, flags=re.I | re.S)
        if end_match:
            body = body[: end_match.start()].strip()
        if len(body.split()) < 300:
            raise ValueError(f"Implausibly short Book {number} in {epub.name}: {len(body.split())} tokens")
        books[number] = body
        provenance.append({
            "book": number,
            "epub_member": member,
            "heading": heading.get_text(" ", strip=True),
            "word_tokens": len(re.findall(r"\b\w+\b", body)),
        })
    missing = [n for n in range(1, 25) if n not in books]
    if missing:
        raise ValueError(f"Missing books in {epub.name}: {missing}")
    return books, sorted(provenance, key=lambda row: row["book"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("epubs", nargs="+", type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for epub in args.epubs:
        books, provenance = extract_books(epub)
        stem = epub.stem
        out_text = args.out_dir / f"{stem}_books_1_24.txt"
        out_json = args.out_dir / f"{stem}_book_provenance.json"
        out_text.write_text(
            "\n\n".join(f"<<<BOOK_{n:02d}>>>\n{books[n]}" for n in range(1, 25)) + "\n",
            encoding="utf-8",
        )
        out_json.write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
        total = sum(row["word_tokens"] for row in provenance)
        summary.append({"epub": epub.name, "books": 24, "word_tokens": total, "text": out_text.name})
    (args.out_dir / "gutenberg_additions_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
