# Poem-Only Corpus Preparation and Native Book Anchors

## Purpose

This repository compares the six retained English translations of Homer’s *Odyssey* at the **native Book I–XXIV level**. The analytical unit is therefore a complete Homeric book, represented in every translation as `book_01` through `book_24`. The project intentionally does **not** construct a fixed number of proportional slices within each book. This rule prevents an arbitrary grid from becoming an unacknowledged source of alignment, resampling, and inferential variation.

> A native book anchor is the complete printed translation text corresponding to one Homeric book. It is a structural comparison unit, not a claim of line-by-line Greek alignment.

## Inclusion and exclusion policy

Prepared derivatives contain the translated poem only. They exclude front and back matter, including tables of contents, title-page material, translator prefaces, introductions, editorial commentary, explanatory notes, appendices, indices, publisher catalogues, and navigation documents. All analytical text files are delimited by explicit markers in the form `<<<BOOK_01>>>` through `<<<BOOK_24>>>`.

| Translation | Source format | Preparation route | Native-book evidence |
|---|---|---|---|
| George Chapman (1616) | Project Gutenberg EPUB | Edition-specific poem extraction | EPUB book documents and printed book headings |
| Alexander Pope (1726) | Project Gutenberg EPUB | Edition-specific poem extraction | EPUB book documents and printed book headings |
| William Cowper (1791) | Project Gutenberg EPUB | Edition-specific poem extraction | Verse containers only; notes excluded |
| Butcher and Lang (1879) | Project Gutenberg EPUB | Edition-specific poem extraction | Poem-bearing book documents only |
| Samuel Butler (1900) | Project Gutenberg EPUB | Edition-specific poem extraction | Native-book headings and poem containers only |
| A. T. Murray (1919) | Original Loeb PDF scans | English-page classification plus audited book page boundaries | Original printed title/running pages with page-level provenance |

## Murray page-boundary audit

Murray’s 1919 Loeb edition requires source-specific treatment because the source is an OCR-bearing bilingual scan. The preparation script retains Latin-dominant English translation pages, removes running headers, printed page furniture, and lower-margin explanatory notes, then splits only at audited native book starts. Four printed headings are not reliably recognized by OCR; their starts were verified from the original scan by the opening wording and PDF page.

| Book | Volume | PDF start page | Audit note |
|---:|---|---:|---|
| I | 1 | 22 | Printed Book I title page |
| II | 1 | 56 | Printed Book II title page |
| III | 1 | 88 | OCR-obscured title page; opening verified against the source scan |
| IV | 1 | 126 | Printed Book IV title page |
| V | 1 | 190 | OCR-obscured title page; opening verified against the source scan |
| VI | 1 | 226 | Printed Book VI title page |
| VII | 1 | 252 | Printed Book VII title page |
| VIII | 1 | 278 | Printed Book VIII title page |
| IX | 1 | 322 | OCR-obscured title page; opening verified against the source scan |
| X | 1 | 364 | Printed Book X title page |
| XI | 1 | 406 | OCR-obscured title page; opening verified against the source scan |
| XII | 1 | 452 | Final translation page ends before PDF page 486; advertisements excluded |
| XIII | 2 | 12 | Printed Book XIII title page |
| XIV | 2 | 44 | Printed Book XIV title page |
| XV | 2 | 84 | Printed Book XV title page |
| XVI | 2 | 126 | Printed Book XVI title page |
| XVII | 2 | 162 | Printed Book XVII title page |
| XVIII | 2 | 206 | Printed Book XVIII title page |
| XIX | 2 | 238 | Printed Book XIX title page |
| XX | 2 | 284 | Printed Book XX title page |
| XXI | 2 | 314 | Printed Book XXI title page |
| XXII | 2 | 346 | Printed Book XXII title page |
| XXIII | 2 | 384 | Printed Book XXIII title page; scan OCR mislabels the numeral |
| XXIV | 2 | 412 | Final translation page ends before PDF page 454; advertisements excluded |

The generated provenance sidecar records each book’s volume, inclusive start page, exclusive end page, source-page count, and post-cleaning token count. The page-level English OCR transcript is retained separately for audit; it is not consumed as the analytical corpus.

## Reproduction and verification

Run the deterministic source-preparation stage before executing the pipeline:

```bash
make prepare-sources
make test
make reproduce
```

The main structured products are `data/processed/books.csv`, `data/processed/book_anchors.csv`, `data/processed/alignment_book_anchors.csv`, and `data/processed/attribution_events.csv`. Every row in `book_anchors.csv` is one whole native book from one translation; the file must therefore contain `6 × 24 = 144` records and exactly 24 shared anchor identifiers.

## Interpretation boundary

Book-level anchoring controls the major narrative location but cannot identify exact Greek-line correspondences or distinguish every local addition, omission, compression, and rearrangement. The cross-translation similarity diagnostics are consequently **comparability diagnostics**, not evidence of source fidelity. Any claim requiring sentence- or line-level correspondence should add a separately audited Greek-to-English alignment layer rather than reintroducing arbitrary subdivisions.
