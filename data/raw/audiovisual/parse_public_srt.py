#!/usr/bin/env python3
"""Parse and validate a Wikimedia Commons SRT track without external packages."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "public_subtitles" / "lodissea_1911_en.srt"
OUT = ROOT / "prepared"
TIME_RE = re.compile(
    r"^(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2}),(?P<sms>\d{3})\s+-->\s+"
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2}),(?P<ems>\d{3})$"
)
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)


def seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    blocks = re.split(r"\n{2,}", raw)
    cues: list[dict] = []
    for block_no, block in enumerate(blocks, start=1):
        lines = [line.rstrip() for line in block.splitlines()]
        if len(lines) < 3:
            raise ValueError(f"Malformed block {block_no}: {block!r}")
        try:
            cue_id = int(lines[0].strip())
        except ValueError as exc:
            raise ValueError(f"Non-integer cue id in block {block_no}") from exc
        match = TIME_RE.fullmatch(lines[1].strip())
        if not match:
            raise ValueError(f"Malformed timestamp in cue {cue_id}: {lines[1]!r}")
        gd = match.groupdict()
        start = seconds(gd["sh"], gd["sm"], gd["ss"], gd["sms"])
        end = seconds(gd["eh"], gd["em"], gd["es"], gd["ems"])
        if end <= start:
            raise ValueError(f"Non-positive duration in cue {cue_id}")
        text_lines = [line.strip() for line in lines[2:] if line.strip()]
        text = " ".join(text_lines)
        cues.append(
            {
                "cue_id": cue_id,
                "start_s": round(start, 3),
                "end_s": round(end, 3),
                "duration_s": round(end - start, 3),
                "text": text,
                "line_count": len(text_lines),
                "token_count": len(WORD_RE.findall(text)),
            }
        )
    ids = [cue["cue_id"] for cue in cues]
    expected = list(range(1, len(cues) + 1))
    if ids != expected:
        raise ValueError(f"Cue sequence is not contiguous: expected {expected[:3]}...{expected[-3:]}")
    for previous, current in zip(cues, cues[1:]):
        if current["start_s"] < previous["start_s"]:
            raise ValueError(f"Cue order regresses at {current['cue_id']}")
    return cues


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cues = parse_srt(SOURCE)

    jsonl_path = OUT / "lodissea_1911_en_cues.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for cue in cues:
            record = {
                "work_id": "lodissea_1911_bertolini",
                "language": "en",
                "track_type": "translated_intertitles",
                **cue,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    csv_path = OUT / "lodissea_1911_en_cues.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cues[0].keys()))
        writer.writeheader()
        writer.writerows(cues)

    text_path = OUT / "lodissea_1911_en_plain.txt"
    text_path.write_text("\n".join(cue["text"] for cue in cues) + "\n", encoding="utf-8")

    source_bytes = SOURCE.read_bytes()
    metrics = {
        "source_file": SOURCE.name,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "cue_count": len(cues),
        "first_start_s": cues[0]["start_s"],
        "last_end_s": cues[-1]["end_s"],
        "covered_duration_s": round(sum(cue["duration_s"] for cue in cues), 3),
        "token_count": sum(cue["token_count"] for cue in cues),
        "mean_tokens_per_cue": round(sum(cue["token_count"] for cue in cues) / len(cues), 3),
        "mean_cue_duration_s": round(sum(cue["duration_s"] for cue in cues) / len(cues), 3),
        "overlap_count": sum(
            1 for previous, current in zip(cues, cues[1:]) if current["start_s"] < previous["end_s"]
        ),
        "license": "CC BY-SA 4.0 (Wikimedia Commons unstructured text)",
        "source_url": "https://commons.wikimedia.org/wiki/TimedText:L%27Odissea_(Milano_Films,_1911)_.webm.en.srt",
        "retrieved_utc": "2026-07-17",
    }
    (OUT / "lodissea_1911_en_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
