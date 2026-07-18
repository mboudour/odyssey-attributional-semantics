# Attributional Semantics in English Translations of Homer’s *Odyssey*: Color, Character, and Hypergraphs

## **Moses Boudourides**

## *Project in Progress*

---

This repository provides a **rights-safe, reproducible computational research package** for comparing color-related and evaluative adjective–noun attributions across six public-domain English translations of Homer’s *Odyssey*. The pipeline uses poem-only prepared text, native Book I–XXIV comparison anchors, rule-based attribution extraction, confidence-weighted statistics, memory-bounded contextual semantics, and weighted multilayer hypergraphs.

## Corpus

The distributable corpus contains six complete English translations whose source files and prepared texts are registered in `config/corpus.json`.

| Translation ID | Translator(s) | Year | Form | Source status |
|---|---|---:|---|---|
| `chapman_1616` | George Chapman | 1616 | Verse | Public domain in the United States |
| `pope_1726` | Alexander Pope | 1726 | Verse | Public domain in the United States |
| `cowper_1791` | William Cowper | 1791 | Verse | Public domain in the United States |
| `butcher_lang_1879` | S. H. Butcher and Andrew Lang | 1879 | Prose | Public domain in the United States |
| `butler_1900` | Samuel Butler | 1900 | Prose | Public domain in the United States |
| `murray_1919` | A. T. Murray | 1919 | Prose | Public domain in the United States |

The project intends to extend its audiovisual component to include a transcript of Christopher Nolan’s 2026 film "The Odyssey" if an official transcript becomes publicly available under terms that permit scholarly reuse and repository distribution. Until then, the documented audiovisual component consists of the English subtitle files for L’Odissea (1911), distributed under CC BY-SA 4.0, which serve as an auditable placeholder and, thus, it is not pooled with the six-translation estimands in the main pipeline.

## Methods

The workflow retains poem text only: it excludes contents pages, translator prefaces, introductions, editorial notes, appendices, glosses, publisher advertisements, and other paratext. Each translation is anchored to its **24 native Homeric books** (`book_01` through `book_24`); it does not subdivide books into artificial proportional bins. Butler’s and the four Gutenberg editions are extracted from book-level source markup. Murray is extracted from original Loeb scan pages with page-level provenance and audited native starts, including the OCR-obscured Books III, V, IX, and XI.

The analysis reports confidence-weighted event rates, pairwise Jensen–Shannon divergence, exploratory lexical distinctiveness, exact chronological permutation tests, matched-book bootstrap intervals, and a sparse contextual baseline based on TF–IDF unigrams/bigrams followed by Truncated SVD. Each translation is also represented as a weighted hypergraph in which canonical targets are hyperedges and normalized attributes are vertices.

> The automatic extraction results are a research baseline, not a substitute for human annotation. Substantive interpretation should follow review of `data/processed/validation_sample.csv` under the supplied protocol.

## Quick start

Python 3.12 is required. From the repository root, create an isolated environment and reproduce the complete run:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-lock.txt
make reproduce
```

To run only the tests:

```bash
make test
```

Visualization design is controlled by [`config/visualizations.json`](config/visualizations.json); routine changes do not require editing Python. Generate a one-translation review set before changing the complete gallery:

```bash
make preview-visualizations
```

After approving the preview, regenerate the complete static, vector, white-background PyVis, and native XGI gallery:

```bash
make visualize
```

The gallery at [`outputs/hypergraph_visualizations/README.md`](outputs/hypergraph_visualizations/README.md) separates three deliverable types. The complete `*_projection.graphml` networks are labeled as **Gephi** downloads and must be downloaded before opening in Gephi. The standalone `projection_pyvis/*.html` files are explicitly labeled **PyVis** and should be downloaded before opening in a web browser. The `xgi_native/` directory contains XGI hull and bipartite-incidence figures. See [`docs/VISUALIZATION_CONFIGURATION.md`](docs/VISUALIZATION_CONFIGURATION.md) for every editable parameter and the per-translation override format.

Thread counts are capped by the `Makefile` to keep numerical work memory-bounded. The pipeline uses deterministic random seeds and writes SHA-256 metadata to `run_manifest.json`.

## Main outputs

| Location | Contents |
|---|---|
| `outputs/reports/analysis_report.md` | Integrated computational results report with embedded figures |
| `outputs/figures/` | Seven publication-oriented PNG figures |
| `outputs/tables/` | Corpus, alignment, statistics, embedding, and hypergraph result tables |
| `outputs/hypergraphs/` | Complete JSON hypergraphs and **Gephi-compatible GraphML** target/attribute projections |
| [`outputs/hypergraph_visualizations/projection_pyvis/`](outputs/hypergraph_visualizations/projection_pyvis/) | Twelve standalone, white-background **PyVis** interactive HTML projections |
| [`outputs/hypergraph_visualizations/projection_static/`](outputs/hypergraph_visualizations/projection_static/) | Twelve configurable static projection figures in PNG and SVG |
| [`outputs/hypergraph_visualizations/xgi_native/`](outputs/hypergraph_visualizations/xgi_native/) | Six configurable native XGI hull and bipartite-incidence figures in PNG and SVG |
| [`config/visualizations.json`](config/visualizations.json) | User-editable colors, fonts, sizes, labels, layouts, selection limits, PyVis physics, and output formats |
| `data/processed/book_anchors.csv` | One complete native Book I–XXIV anchor per translation and book |
| `data/processed/alignment_book_anchors.csv` | Pairwise and aggregate diagnostics for the 24 native book anchors |
| `data/processed/attribution_events.csv` | Complete machine-readable attribution event table |
| `data/processed/validation_sample.csv` | Stratified 360-event annotation sample |
| `models/` | TF–IDF/SVD vocabulary, components, event vectors, centroids, and metadata |
| `run_manifest.json` | Run counts, environment details, Git revision, and file checksums |
| [`docs/NATIVE_BOOK_ANCHOR_METHOD.md`](docs/NATIVE_BOOK_ANCHOR_METHOD.md) | Poem-only source policy, audited book boundaries, and native-anchor design |
| `docs/Odyssey_Computational_Protocol_v2.md` | Formal research protocol and estimands |

The successful native-book reference run contains **735,316 corpus words**, **13,226 extracted attribution events**, **96 canonical targets**, **181 normalized attributes**, and **12 ontology categories**.

## Validation and interpretation

The manual validation protocol requires correctness judgments for targets, attributes, relation templates, and ontology categories. It specifies Wilson intervals, category- and translation-level diagnostics, and inter-annotator agreement. Results should not be interpreted substantively if overall precision is below the stated threshold or if central categories lack adequate reviewed support.

Chronological estimates are descriptive. Publication year is confounded with translator identity, verse/prose form, historical language, and source preparation. The six public-domain witnesses do not support a causal ideological trend claim, nor do they represent twentieth- and twenty-first-century translation practice.

## Rights and provenance

The authoritative registry in `config/corpus.json`, the decision log in `docs/corpus_decision_log.csv`, the manifest in `docs/corpus_manifest.json`, the per-book provenance sidecars in `data/interim/seed_prepared_text/`, and `data/raw_checksums.sha256` document provenance and rights metadata. Modern copyrighted translations are intentionally excluded from the distributable package. Researchers may add lawfully obtained restricted texts locally under ignored private directories, but must not redistribute them through this repository.

## Repository status

The project is designed for a private GitHub repository named `odyssey-attributional-semantics`. Authentication secrets must never be stored in source files, command history, documentation, archives, or chat transcripts.

## Copyright

© 2026 Moses Boudourides. All rights reserved.

This repository and its contents are made available for academic peer review purposes only. No part of this work may be reproduced, distributed, or used in any form without the express written permission of the authors.
