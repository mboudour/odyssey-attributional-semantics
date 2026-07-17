#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "odyssey_av_text_audit.csv"
METRICS_PATH = ROOT / "prepared" / "lodissea_1911_en_metrics.json"
REQUIRED_COLUMNS = {
    "work_id",
    "title",
    "year",
    "medium",
    "adaptation_scope",
    "text_source",
    "text_format",
    "timecoded",
    "coverage_verified",
    "provenance_class",
    "rights_or_license",
    "python_status",
    "corpus_decision",
    "source_url",
    "notes",
}

with CSV_PATH.open(encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    rows = list(reader)
    assert reader.fieldnames is not None
    assert set(reader.fieldnames) == REQUIRED_COLUMNS, reader.fieldnames

assert len(rows) == 10, len(rows)
assert len({row["work_id"] for row in rows}) == len(rows)
assert all(all(value is not None for value in row.values()) for row in rows)
assert all(row["source_url"].startswith("https://") for row in rows)

public_rows = [row for row in rows if row["corpus_decision"] == "include_in_redistributable_av_corpus"]
assert [row["work_id"] for row in public_rows] == ["lodissea_1911"]
assert "CC BY-SA 4.0" in public_rows[0]["rights_or_license"]

metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
assert metrics["cue_count"] == 58
assert metrics["overlap_count"] == 0
assert metrics["token_count"] == 623
assert metrics["last_end_s"] == 2632.68

required_files = [
    ROOT / "public_subtitles" / "lodissea_1911_en.srt",
    ROOT / "public_subtitles" / "lodissea_1911_en.vtt",
    ROOT / "prepared" / "lodissea_1911_en_cues.csv",
    ROOT / "prepared" / "lodissea_1911_en_cues.jsonl",
    ROOT / "prepared" / "lodissea_1911_en_plain.txt",
]
assert all(path.is_file() and path.stat().st_size > 0 for path in required_files)

print(json.dumps({
    "audit_rows": len(rows),
    "redistributable_tracks": len(public_rows),
    "validated_public_work": public_rows[0]["work_id"],
    "cue_count": metrics["cue_count"],
    "token_count": metrics["token_count"],
    "status": "PASS",
}, indent=2))
