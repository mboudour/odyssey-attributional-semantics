# Odyssey Audiovisual Text Audit

This package contains a verified source audit, a public timed-text sample, reproducible parsing code, and integration recommendations for adding film and television adaptations to the Odyssey translation project.

## Rights boundary

Only the English SRT and VTT for *L'Odissea* (Milano Films, 1911) are included as subtitle text. The underlying film is marked public domain by Wikimedia Commons; the unstructured English subtitle text is CC BY-SA 4.0 and must retain attribution and share-alike terms.

No subtitle or transcript text from the protected 1954, 1968, 1981–82, 1989, 1997, 2000, 2013, 2024, or 2026 works is distributed. The CSV records discovery evidence and recommended handling only.

## Reproduce

```bash
python3 parse_public_srt.py
python3 validate_av_audit.py
```

The parser requires only Python's standard library.

## Contents

| Path | Purpose |
|---|---|
| `Odyssey_Audiovisual_Text_Audit.md` | Research report and computational integration protocol |
| `odyssey_av_text_audit.csv` | Machine-readable source, rights, completeness, and decision matrix |
| `public_subtitles/` | Public English SRT and VTT for the 1911 film |
| `prepared/` | Cue-level CSV/JSONL, normalized text, and technical metrics |
| `parse_public_srt.py` | Dependency-free SRT parser |
| `validate_av_audit.py` | Structural and rights-boundary validator |
| `research_notes.md` | Research evidence and source URLs |

## Adding a protected local subtitle

Store a lawfully obtained SRT/VTT in a private directory excluded from version control. Record its title, release identifier, language, checksum, source, and permission basis. Run the parser locally, but publish only non-reconstructive aggregate results unless the licence or permission allows redistribution.
