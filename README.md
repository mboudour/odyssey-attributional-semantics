# Attributional Semantics in English Translations of Homer’s *Odyssey*: Color, Character, and Hypergraphs

This repository provides a **rights-safe, reproducible computational research package** for comparing color-related and evaluative adjective–noun attributions across six public-domain English translations of Homer’s *Odyssey*. The pipeline combines rule-based attribution extraction, structurally aligned passage comparison, confidence-weighted statistics, memory-bounded contextual semantics, and weighted multilayer hypergraphs.

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

The package also preserves a documented audiovisual extension for *L’Odissea* (1911), including English subtitle files distributed under **CC BY-SA 4.0**. The film material is retained as an auditable extension and is not pooled with the six-translation estimands in the main pipeline.

## Methods

The workflow segments each translation into 24 books and 20 relative passage bins per book, producing a common grid of **480 anchors per translation**. It extracts canonical target–attribute events using explicit syntactic templates, records segmentation and extraction confidence, and retains sentence context for manual auditing.

The analysis reports confidence-weighted event rates, pairwise Jensen–Shannon divergence, exploratory lexical distinctiveness, exact chronological permutation tests, matched-passage bootstrap intervals, and a sparse contextual baseline based on TF–IDF unigrams/bigrams followed by Truncated SVD. Each translation is also represented as a weighted hypergraph in which canonical targets are hyperedges and normalized attributes are vertices.

> The automatic extraction results are a research baseline, not a substitute for human annotation. Substantive interpretation should follow review of `data/processed/validation_sample.csv` under the supplied protocol.

## Quick start

Python 3.12 is required. From the repository root, create an isolated environment and reproduce the complete run:

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements-lock.txt
make reproduce
```

To run only the tests:

```bash
make test
```

To regenerate only the static, vector, interactive, and native XGI hypergraph visualizations:

```bash
make visualize
```

The visualization index is rendered at [`outputs/hypergraph_visualizations/README.md`](outputs/hypergraph_visualizations/README.md).

Thread counts are capped by the `Makefile` to keep numerical work memory-bounded. The pipeline uses deterministic random seeds and writes SHA-256 metadata to `run_manifest.json`.

## Main outputs

| Location | Contents |
|---|---|
| `outputs/reports/analysis_report.md` | Integrated computational results report with embedded figures |
| `outputs/figures/` | Seven publication-oriented PNG figures |
| `outputs/tables/` | Corpus, alignment, statistics, embedding, and hypergraph result tables |
| `outputs/hypergraphs/` | JSON hypergraphs and GraphML target/attribute projections |
| [`outputs/hypergraph_visualizations/`](outputs/hypergraph_visualizations/README.md) | Eighteen PNG figures, eighteen SVG figures, twelve standalone interactive HTML projections, and a documented XGI gallery |
| `data/processed/attribution_events.csv` | Complete machine-readable attribution event table |
| `data/processed/validation_sample.csv` | Stratified 360-event annotation sample |
| `models/` | TF–IDF/SVD vocabulary, components, event vectors, centroids, and metadata |
| `run_manifest.json` | Run counts, environment details, Git revision, and file checksums |
| `docs/Odyssey_Computational_Protocol_v2.md` | Formal research protocol and estimands |

The successful reference run contains **762,798 corpus words**, **12,176 extracted attribution events**, **96 canonical targets**, **179 normalized attributes**, and **12 ontology categories**.

## Validation and interpretation

The manual validation protocol requires correctness judgments for targets, attributes, relation templates, and ontology categories. It specifies Wilson intervals, category- and translation-level diagnostics, and inter-annotator agreement. Results should not be interpreted substantively if overall precision is below the stated threshold or if central categories lack adequate reviewed support.

Chronological estimates are descriptive. Publication year is confounded with translator identity, verse/prose form, historical language, and source preparation. The six public-domain witnesses do not support a causal ideological trend claim, nor do they represent twentieth- and twenty-first-century translation practice.

## Rights and provenance

The authoritative registry in `config/corpus.json`, the decision log in `docs/corpus_decision_log.csv`, the manifest in `docs/corpus_manifest.json`, and `data/raw_checksums.sha256` document provenance and rights metadata. Modern copyrighted translations are intentionally excluded from the distributable package. Researchers may add lawfully obtained restricted texts locally under ignored private directories, but must not redistribute them through this repository.

## Repository status

The project is designed for a private GitHub repository named `odyssey-attributional-semantics`. Authentication secrets must never be stored in source files, command history, documentation, archives, or chat transcripts.
