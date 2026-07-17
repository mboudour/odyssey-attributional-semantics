# Source-Aligned Attributional Semantics in English Translations of *The Odyssey*

## Computational Research Protocol, Version 2.0

**Author:** Manus AI  
**Date:** 17 July 2026

> **Scope and legal note.** This document applies a conservative corpus-management rule rather than offering a legal opinion. Copyright status depends on jurisdiction, publication history, edition, licence, and intended use. The redistributable package retains only files that are conservatively public domain in both the United States and EU/UK and that pass reproducible Python extraction tests. A larger corpus of lawfully obtained copyrighted editions may potentially be analysed in a non-consumptive, access-controlled environment, but it must be governed separately and must not be redistributed.

## Executive determination

The research question is computationally viable, but the study must be reframed. It is not, in the strict sense, a conventional diachronic semantic-change experiment. Each English text translates the same ancient source, while translation year is confounded with translator identity, verse or prose form, publisher, edition, and declared poetics. The defensible object of inference is therefore **source-controlled variation in attributional semantics across historically ordered translations**. A claim of ideological change requires evidence that a source-matched translation choice changes systematically across multiple translators and periods after controlling for target frequency, literary form, source wording, narrative location, and extraction uncertainty.

The strict public-domain audit now retains **six distinct translations spanning 1616–1919**: Chapman, Pope, Cowper, Butcher–Lang, Butler, and Murray. This is sufficient for robust pipeline development, historical-language stress testing, and source-aligned comparison across prose and verse traditions, but it is **not sufficient to estimate a 1900–2017 historical trend**: five translations predate 1901, and there is no late-twentieth- or twenty-first-century observation. The original question therefore still requires a second, restricted research layer containing lawfully accessed modern translations. Public-domain files and restricted files should never be mixed in a distributable archive.

| Decision | Consequence |
|---|---|
| Retain Chapman, Pope, Cowper, Butcher–Lang, Butler, and Murray in the redistributable layer | The project can develop and validate extraction, source alignment, historical-language parsing, annotation, and hypergraph construction without rights ambiguity. |
| Exclude modern translations from the distributable package | Wilson, Verity, Fitzgerald, Mandelbaum, Fagles, Lattimore, Rieu, and Lombardo remain outside the package even when technically extractable. |
| Treat copyrighted editions as a separate restricted layer | If the researcher has lawful access and an applicable exception or licence, derived non-consumptive features may be computed locally; source texts should not be shared. |
| Anchor every translation to Greek book and line spans | Pairwise English-to-English similarity no longer substitutes for source control. |
| Represent each attribution as an event, not merely an adjective–noun type | The analysis preserves passage, grammatical relation, referent, source anchor, semantic labels, and uncertainty. |
| Make lexical counts and categorical models primary | Embeddings and hypergraphs become secondary analyses whose results must agree with transparent baselines or be interpreted as exploratory. |

![Formal computational protocol](computational_protocol.png)

## 1. Corpus governance and audit result

### 1.1 Screening rule

The strict retained corpus satisfies four conditions simultaneously: the underlying translation is conservatively public domain in the United States; it is conservatively public domain in EU/UK life-plus-seventy jurisdictions; the supplied or canonical edition does not introduce necessary protected textual matter; and the file is directly extractable by a documented Python procedure. Cornell’s 2026 chart states that U.S. works first published before 1931 are in the public domain, while later works require a more complex notice, renewal, nationality, and restoration analysis.[1] EU protection for literary works is generally seventy years after the author’s death.[2]

This rule is deliberately stricter than the conditions that may govern private scholarly text and data mining. Directive (EU) 2019/790 provides specific text-and-data-mining exceptions subject to lawful access and other conditions, while U.S. research institutions have implemented non-consumptive analysis of protected collections under fair-use reasoning.[3] [4] Those doctrines may support a restricted local-analysis layer, but they do not make the underlying books freely redistributable.

### 1.2 Retained corpus

Project Gutenberg identifies the translators and states that eBooks 1727, 3160, 1728, 48895, and 24269 are public domain in the United States.[5] [11] [12] [13] [14] Internet Archive identifies the two Murray scans as the 1919 Heinemann edition, Volume I and Volume II.[6] [7] Every EPUB is directly parseable in Python. The Murray PDFs expose text layers, and a Python page classifier separates the English pages from the bilingual Greek/English layout.

| Retained file | Translation | Coverage | Prepared extraction | Provenance |
|---|---|---:|---:|---|
| `Homer_Odyssey_Chapman_PG48895.epub` | George Chapman, 1616 | Books I–XXIV plus appended shorter poems | Pass; 146,275 Odyssey tokens; appended works excluded deterministically | Project Gutenberg eBook 48895 |
| `Homer_Odyssey_Pope_PG3160.epub` | Alexander Pope, 1725–1726 | Books I–XXIV | Pass; 115,019 tokens | Project Gutenberg eBook 3160 |
| `Homer_Odyssey_Cowper_PG24269.epub` | William Cowper, 1791 | Books I–XXIV | Pass; 121,498 tokens | Project Gutenberg eBook 24269 |
| `Homer_Odyssey_Butcher_Lang_PG1728.epub` | S. H. Butcher and Andrew Lang, 1879 | Books I–XXIV | Pass; 137,180 tokens | Project Gutenberg eBook 1728 |
| `Homer_Odyssey_Butler_1900_ProjectGutenberg.epub` | Samuel Butler, 1900 | Books I–XXIV | Pass; approximately 130,000 prepared tokens | Project Gutenberg eBook 1727 |
| `Homer_Odyssey_Murray_1919_Vol1.pdf` | A. T. Murray, 1919 | Books I–XII | Pass; 249 English-dominant pages retained | Internet Archive `in.gov.ignca.913` |
| `Homer_Odyssey_Murray_1919_Vol2.pdf` | A. T. Murray, 1919 | Books XIII–XXIV | Pass; 230 English-dominant pages retained | Internet Archive `in.gov.ignca.914` |

The added EPUB extractor follows package-spine order, accepts exactly one opening book heading per content document, requires all twenty-four books, emits explicit `<<<BOOK_NN>>>` boundaries, and records the source member and token count for each book. Chapman requires a dedicated ordinal-heading parser and a stop boundary before the appended *Batrachomyomachia*, hymns, and epigrams. The prepared Murray text contains approximately 140,000 ASCII word tokens; this includes page headers, notes, and OCR artefacts and is an extraction diagnostic, not a final corpus size. Production cleaning must preserve book, file-member or page, and character-offset provenance rather than globally deleting unfamiliar material.

### 1.3 Exclusions and corrections

The supplied Mandelbaum filename is misleading: **1926 is the translator’s birth year**, whereas the file itself carries a 1990 copyright notice. The supplied Murray file contains only Books XIII–XXIV and is replaced by verified 1919 Volumes I and II. The Lawrence translation first appeared in 1932; although the underlying text is likely public domain in EU/UK life-plus-seventy jurisdictions because Lawrence died in 1935, it is not a safe cross-jurisdictional inclusion in the United States in 2026, and the supplied modern Collector’s Library edition may include separately protected matter. Lombardo is explicitly abridged. One Fagles PDF is image-only. The full decision record is in `corpus_decision_log.csv`.

| Exclusion class | Files affected | Methodological implication |
|---|---|---|
| Protected modern translation | Rieu, Lattimore, Fagles, Fitzgerald, Mandelbaum, Lombardo, Verity, Wilson | Exclude from redistributable package; consider only in a separate restricted environment after rights review. |
| Incomplete or abridged | Supplied Murray Volume II; Lombardo abridgment | Do not use whole-poem frequency denominators; replace or restrict to source-matched passages. |
| Technically unusable duplicate | Image-only Fagles PDF | Exclude rather than OCR when a text-layer duplicate exists. |
| Ambiguous cross-jurisdictional status or modern edition | T. E. Lawrence file | Exclude from strict layer; reconsider only after jurisdiction and edition-level review. |
| Public-domain duplicate with weaker provenance | Original Butler EPUB | Replace with canonical Project Gutenberg EPUB. |

## 2. Formal research design

### 2.1 Unit of analysis

The fundamental record is an **attribution event**, not a word pair. Let

\[
r_i=(t_i,s_i,e_i,a_i,g_i,c_i,m_i,q_i),
\]

where \(t_i\) is the translation; \(s_i\) is a canonical source passage identified by Odyssey book and Greek line span; \(e_i\) is the normalized target referent; \(a_i\) is the English attribute expression; \(g_i\) is the grammatical relation; \(c_i\) is a multi-label semantic-category vector; \(m_i\) records literal, metaphorical, formulaic, or ambiguous use; and \(q_i\) is a vector of extraction, alignment, and annotation confidence scores.

This definition solves three problems in the initial plan. It separates repeated occurrences from unique types, distinguishes a grammatical modifier from an inferred evaluation, and permits direct comparison only when events are attached to the same source passage or source attribution.

### 2.2 Target ontology

The original proposal combines heroes, situations, and concepts under “nouns,” but these are not the same computational object. The revised schema distinguishes **entities**, **objects**, **natural phenomena**, **abstract concepts**, and **event frames**. A situation such as the slaughter of the suitors is represented by an event ID even if no single noun names it in a translation.

| Target class | Examples | Representation |
|---|---|---|
| Human or divine entity | Odysseus, Penelope, Athena | Canonical entity ID plus names, epithets, descriptions, and coreferential mentions |
| Group | suitors, crew, Phaeacians | Group entity ID with membership metadata where relevant |
| Object or body part | bow, ship, eyes | Lemmatized concept ID and passage-specific mention |
| Natural phenomenon | sea, dawn, night | Concept ID, with formulaic-expression flag |
| Abstract concept | fate, justice, mind | Concept ID with sense annotation where polysemy matters |
| Event or situation | homecoming, recognition, shipwreck | Event-frame ID anchored to source line span |

### 2.3 Confirmatory estimands

The study should preregister a small family of primary estimands. Let \(N_{t,e,c}\) be the number of validated attributions in category \(c\) assigned to target \(e\) by translation \(t\), and let \(O_{t,e}\) be the number of source-aligned opportunities, defined either as mentions of \(e\) or as Greek attribution instances involving \(e\). The primary rate is

\[
\lambda_{t,e,c}=N_{t,e,c}/O_{t,e}.
\]

The source-matched contrast between translations \(t\) and \(t'\) is

\[
\Delta_{t,t',e,c}=\log\{(N_{t,e,c}+0.5)/(O_{t,e}+1)\}-
\log\{(N_{t',e,c}+0.5)/(O_{t',e}+1)\}.
\]

A second estimand measures **translation operation** relative to a Greek source attribution: preservation, lexical substitution within category, category shift, omission, addition, or redistribution to another target. A third measures evaluative orientation, such as the probability that an attribution is positive, negative, mixed, or neutral conditional on the same source passage.

Crucially, a regression coefficient for calendar year is not identifiable as a historical effect when each year contains one translator. At least two translators in multiple periods, or another design that creates within-period replication, is required before a trend coefficient can be interpreted. Otherwise, report pairwise translator contrasts and avoid the phrase “significant historical shift.”

## 3. Deterministic preprocessing and source alignment

### 3.1 Reproducible extraction

EPUB extraction must follow the package document’s `<spine>` order. Filename sorting can silently reorder books, as occurred in the earlier Lattimore audit. PDF extraction must preserve page IDs and form-feed boundaries. Paratext removal should use edition-specific start and end anchors and must retain an audit trail linking every cleaned span to its source file, page, and character offsets.

The retained package includes `audit_corpus_v2.py`, which records SHA-256 hashes, openability, page or spine counts, word counts, Unicode replacement characters, book-heading diagnostics, and text-layer status. `prepare_retained_texts.py` follows EPUB spine order and classifies Murray pages using Latin-letter, Greek-letter, and running-text thresholds. `prepare_gutenberg_additions.py` deterministically isolates Books I–XXIV from Pope, Butcher–Lang, Chapman, and Cowper, validates completeness, and exports per-book provenance. All classification and extraction decisions are exported rather than hidden so that errors can be reviewed.

A production implementation should generate these immutable tables:

| Table | Primary key | Required fields |
|---|---|---|
| `editions.parquet` | `edition_id` | translator, translation year, edition year, form, source URL, checksum, rights class |
| `passages.parquet` | `translation_id, passage_id` | book, Greek line start/end, English text, source page, character offsets |
| `alignments.parquet` | `alignment_id` | source span, translation span, alignment type, model score, manual status |
| `mentions.parquet` | `mention_id` | target ID, surface form, lemma, sentence ID, coreference chain |
| `attribution_events.parquet` | `event_id` | target, attribute, dependency relation, semantic labels, source anchor, confidence |
| `annotations.parquet` | `event_id, annotator_id` | labels, adjudication status, timestamp, guideline version |

### 3.2 Greek-source inventory

Every English translation should be aligned to one stable Ancient Greek edition with book and line identifiers. The Greek layer should contain tokenization, lemmas, morphology, dependency relations where available, and a manually reviewed list of source attribution constructions. The aim is not to force English syntax to mirror Greek syntax. It is to provide a shared reference that distinguishes preservation, omission, addition, and recategorization.

The source inventory should include adjectival modifiers, copular predicates, participial and appositive epithets, formulaic compounds, genitive constructions that function attributively, and semantically attributive clauses. Each source instance receives an immutable ID such as `Od.05.171-175.attr03`. English events can then be compared against the same source instance even when a translator expands one Greek expression into a clause or suppresses it entirely.

### 3.3 Passage alignment algorithm

Alignment should proceed hierarchically. First, enforce exact book boundaries. Second, divide source and translation into short segments while retaining verse lines or sentences. Third, encode segments with a multilingual sentence model. Fourth, perform monotonic dynamic programming that permits 1:1, 1:m, m:1, and m:n links and penalizes large jumps. Bertalign is relevant because it explicitly supports many-to-many alignment in literary parallel texts.[8] Fifth, refine low-confidence regions using named entities, formulaic markers, and rare lexical anchors. Sixth, manually validate a stratified sample and all alignments used in confirmatory claims.

Pairwise English-to-English alignment is not the primary structure. Each translation aligns to the Greek source, yielding a star topology. Pairwise comparison is then derived by joining on source IDs. This avoids transitivity failures and permits an omitted attribution to remain visible rather than disappearing from an English-only alignment.

## 4. Attribution extraction

### 4.1 Candidate-generation grammar

A dependency parser should generate a high-recall candidate set using explicit relation templates. At minimum, include:

| Construction | Dependency pattern | Example type |
|---|---|---|
| Attributive adjective | `amod(attribute, target)` | “dark sea” |
| Copular predicate | `nsubj(attribute, target)` with copula | “the sea is dark” |
| Object predicative complement | object plus adjectival complement | “they painted the ship black” |
| Appositive or epithetic phrase | apposition or punctuation-bounded modifier | “Odysseus, patient man” |
| Participial attribution | participle linked to target | “Odysseus, enduring…” |
| Hyphenated or compound color expression | compound modifier span | “wine-dark sea” |
| Nominalized evaluation | noun predicate linked to entity | “Odysseus was a schemer” |
| Clause-level inferred state | controlled semantic-role template | “fear seized him” mapped to EXPERIENCER |

The last two categories must not be merged automatically with grammatical adjective–noun pairs. The data should preserve a feature such as `evidence_level = explicit_modifier | explicit_predicate | event_inference`. Confirmatory analyses should begin with explicit relations; inferred psychological states should form a secondary analysis.

### 4.2 Ensemble parsing and calibration

Use two independently trained English pipelines, for example Stanza and a pinned spaCy transformer model. Candidates accepted by both parsers form a high-precision stratum. Disagreements and long-distance relations enter a manual-review or classifier stratum. The project should evaluate parser accuracy on the actual translations rather than relying on benchmark scores from modern prose.

The extraction classifier may be a fine-tuned transformer, but only after creating a gold corpus. Its input should include the sentence, marked target span, marked candidate attribute span, parser relations, and source-passage context. Its outputs should be relation validity and construction type. Class weights or focal loss may be necessary because true relations will be sparse relative to candidate pairs.

### 4.3 Entity and coreference normalization

A curated Odyssey gazetteer should map personal names, patronymics, epithets, roles, and descriptive noun phrases to canonical IDs. Rule-based normalization is preferable for principal characters because the domain is finite and interpretability matters. A neural coreference model may propose pronoun links, but it must be constrained by speaker, scene, gender where textually warranted, and local candidate entities. Coreference confidence must propagate to event confidence.

## 5. Semantic annotation: color, affect, behaviour, and ideology

### 5.1 Multi-dimensional ontology

Ancient Greek chromatic language should not be collapsed into modern basic hue terms. Scholarship emphasizes dimensions such as brightness, materiality, visibility, embodiment, and affect in addition to hue.[9] The ontology should therefore be hierarchical and multi-label.

| Top-level family | Subdimensions |
|---|---|
| Chromatic-hue | red, blue, green, yellow, black, white, brown, purple, mixed/indeterminate |
| Luminance and visibility | bright, shining, pale, dim, dark, clear, obscured |
| Saturation and intensity | vivid, dull, deep, weak, flashing |
| Material and surface | metallic, glossy, blood-like, wine-like, smoky, wet, textured |
| Temperature and atmosphere | warm, cold, fiery, misty |
| Emotion and psychological state | fear, grief, anger, desire, confidence, restraint |
| Behaviour and agency | cunning, endurance, violence, hospitality, loyalty, deception |
| Social and moral evaluation | noble, shameful, civilized, alien, pious, impious |
| Embodied condition | healthy, wounded, exhausted, aged, beautiful |

Each event also receives `literalness`, `formulaicity`, `evaluative_polarity`, `intensity`, and `target_scope`. Annotation should allow `uncertain` and `not_applicable`; forcing a single category would encode modern assumptions into Homeric vocabulary.

### 5.2 Annotation protocol

The gold standard should sample **passages**, not only automatically proposed candidates. Candidate-only validation measures precision but cannot estimate recall. A recommended design is 1,000 source-aligned passage units stratified by book, translator, target class, parser agreement, semantic family, and confidence decile. Two annotators independently mark targets, attributes, relations, source links, semantic labels, and uncertainty. Disagreements are adjudicated by a third pass under versioned guidelines.

Report span F1, target-normalization accuracy, relation F1, macro- and micro-F1 for semantic labels, Cohen’s kappa for binary decisions, and Krippendorff’s alpha for multi-category judgments. Agreement on ideology-related labels must be reported separately because it is expected to be lower and more theory-dependent.

## 6. Statistical inference

### 6.1 Count and rate model

For validated event counts \(Y_{t,e,c,b}\) by translation \(t\), target \(e\), category \(c\), and book \(b\), use a hierarchical negative-binomial model:

\[
Y_{t,e,c,b}\sim\mathrm{NegBin}(\mu_{t,e,c,b},\phi),
\]

\[
\log\mu_{t,e,c,b}=\log O_{t,e,b}+\alpha+u_t+v_e+w_b+\gamma_c+
\beta_1\mathrm{Verse}_t+\beta_2\mathrm{SourceLiteralness}_{t,e,b}+\boldsymbol{x}'\boldsymbol{\beta}.
\]

The offset \(O_{t,e,b}\) is the number of source-aligned opportunities or target mentions. Random effects absorb repeated observations by translator, target, and book. If the corpus contains enough within-period replication, a period effect and translator-within-period effect can be estimated. With one translator per date, do not fit or interpret a linear year trend.

### 6.2 Category distribution model

To test whether translators redistribute attributes among semantic families, model category counts with a hierarchical multinomial or logistic-normal model. This is preferable to running many independent chi-square tests because categories are compositional and correlated. Posterior contrasts or bootstrap confidence intervals should be reported as probability differences and odds ratios, not only p-values.

### 6.3 Matched-passage analysis

For each Greek source attribution, construct a translation-operation vector: preserved, substituted within family, shifted across family, omitted, expanded, or reassigned. Conditional logistic regression, mixed-effects multinomial regression, or exact permutation tests can compare translators while holding the source instance fixed. This is the strongest design for claims about ideological reframing because the source wording and narrative location are controlled directly.

### 6.4 Multiplicity and robustness

Primary targets, categories, and contrasts should be preregistered. Exploratory tests should use hierarchical false-discovery-rate control. Confidence intervals should be generated by resampling source passages or books, not individual tokens, because events within a passage are dependent. Robustness analyses should vary parser, alignment threshold, ontology granularity, opportunity denominator, treatment of formulaic epithets, inclusion of inferred psychological states, and exclusion of paratext-adjacent passages.

A sensitivity analysis should propagate uncertain alignments and labels. One practical method is Monte Carlo multiple imputation: draw event validity, source link, and semantic label from calibrated confidence distributions; rerun the estimator across draws; and combine within- and between-imputation variance. A finding that disappears under plausible annotation error should not be described as a significant shift.

## 7. Hypergraph analysis

### 7.1 Representation

For translator \(t\), define a labelled hypergraph as a dictionary whose **keys are target hyperedges** and whose **values are sets of attribute nodes**, in the requested representation:

```python
H_t = {
    "ODYSSEUS": {"resourceful", "patient", "cunning"},
    "PENELOPE": {"wise", "faithful"},
    "SEA": {"dark", "wine-dark", "grey"},
}
```

Because a set discards frequency, store a separate weighted incidence matrix

\[
W_t[e,a]=\sum_i \mathbf{1}(e_i=e,a_i=a)\,\omega_i,
\]

where \(\omega_i\) may be one for validated events or a calibrated event probability for uncertainty-weighted exploratory analysis. Maintain both lexical and ontology-projected hypergraphs. The lexical graph preserves translator diction; the ontology graph makes semantically comparable attributes share nodes.

### 7.2 Multilayer construction

Treat each translation as one layer. Target hyperedges are coupled across layers by the same canonical target ID, and events are coupled by source attribution ID. This creates two distinct comparison levels: structural change in a target’s attribute set and source-matched change in how the same Greek attribution is rendered.

Recommended quantities include weighted Jaccard similarity for each target hyperedge, Jensen–Shannon divergence between normalized attribute distributions, optimal-transport distance between ontology-aware attribute distributions, target-specific degree and entropy, overlap of hyperedges that share attributes, and spectral distances between normalized incidence operators. HyperNetX provides a practical Python representation for hypergraphs, but all measures should be computed from exported incidence data rather than from opaque visualization state.[10]

### 7.3 Null models and uncertainty

Network or hypergraph measures are not self-interpreting. Compare observed differences with null distributions generated by permuting translation labels **within source passage and target**, thereby preserving passage composition and target frequency. A second null should preserve weighted target degrees and category marginals. Bootstrap source passages or books to produce intervals for hyperedge distances and motif counts. Hypergraph visualizations must not be treated as evidence unless the corresponding statistic departs from an explicit null model.

## 8. Embeddings and deep learning

Embeddings should answer narrowly defined questions and should not replace the event table. For English contextual variation, encode each validated occurrence with a pinned transformer model. A relation representation can concatenate attribute and target vectors and their interaction:

\[
h_i=[h_a;h_e;h_a-h_e;h_a\odot h_e].
\]

Matched-passage distances can then compare translators while conditioning on source ID. Mixed-effects models should test whether embedding distance is associated with semantic-category shift after controlling for lexical identity and passage length. Unsupervised projections such as UMAP are visualization only and should not establish clusters or ideological trends.

A more interpretable alternative is a masked-language-model substitute profile. Mask the attribute expression, generate a probability distribution over plausible substitutes, and compare distributions across translations with Jensen–Shannon divergence. Contextual embeddings have not consistently outperformed simpler methods for semantic-change detection; substitute distributions and lexical baselines therefore provide important checks.[15]

Deep learning is justified in three places: many-to-many passage alignment, relation classification after gold annotation exists, and contextual representation of validated events. It is not justified for replacing corpus governance, source annotation, or statistical identification. Large language models may assist error analysis or propose labels, but their output must remain a separately marked annotation source and cannot be the gold standard.

## 9. Validation thresholds and go/no-go criteria

| Component | Evaluation design | Minimum threshold before full analysis |
|---|---|---:|
| File extraction | Checksum reproducibility, zero extraction errors, manual page inspection | 100% retained files reproducible |
| Book segmentation | Compare detected boundaries with all 24 books | 24/24 books with verified starts and ends |
| Passage alignment | Double-review at least 300 stratified links | Precision ≥ 0.95; recall ≥ 0.90; report many-to-many F1 |
| Explicit attribution extraction | Passage-sampled gold corpus | Precision ≥ 0.90; recall ≥ 0.85; relation F1 ≥ 0.87 |
| Entity normalization | Stratified principal and minor entities | Macro-F1 ≥ 0.95 for principal entities; ≥ 0.90 overall |
| Semantic categories | Double annotation and adjudication | Macro-F1 ≥ 0.80 and alpha ≥ 0.75 for primary families |
| Ideological/evaluative labels | Separate reliability report | Alpha ≥ 0.67 for exploratory use; ≥ 0.80 for confirmatory claims |
| Hypergraph stability | Passage bootstrap and null models | Direction of primary contrast stable in ≥ 90% of bootstrap draws |
| Model robustness | Alternative parser, alignment, denominator, and ontology | Primary effect sign and substantive conclusion invariant |

If alignment or extraction misses these thresholds, the project should remain a manually assisted pilot. Scaling a low-recall pipeline would create precise-looking but invalid translator differences.

## 10. Minimum viable experiment and full study

### Stage A: public-domain pipeline pilot

Use all six public-domain translations to implement and stress-test the complete data model. Their seventeenth- through early-twentieth-century language and their mixture of verse and prose create a demanding parser-robustness benchmark. Select a preregistered stratified pilot comprising Books V, IX, XIX, and XXII because they cover sea travel, alterity, recognition, social evaluation, and violence; these books are for pipeline stress-testing and pre-1920 translation comparison, not inference about 1900–2017. Annotate at least 250 source passage units sampled across all six translations, report extraction and alignment error separately by translator and prose/verse form, and require no translator-specific recall estimate to fall below the preregistered threshold. The deliverable is a validated event table, not a modern ideological claim.

### Stage B: restricted comparative corpus

After an institutional or jurisdiction-specific rights review, create an access-controlled layer for lawfully obtained modern editions. Do not place those files in a public repository. Store only hashes and metadata in the public manifest. Export only non-reconstructive aggregate counts, model coefficients, semantic labels, and short quotations within applicable limits.

A methodologically useful design should include more than one translator in at least two periods. For example, an early group might contain Butler, Murray, and Lawrence where lawful; a mid-century group might contain Rieu, Fitzgerald, and Lattimore; a late group might contain Mandelbaum, Fagles, and Lombardo if a complete edition is obtained; and a contemporary group might contain Powell, Verity, and Wilson. Period is then estimable separately from translator only if the sampling design and lawful access support such replication.

### Stage C: confirmatory analysis

Freeze the ontology and gold set; preregister primary targets, categories, and source operations; run the hierarchical models and matched-source tests; compute hypergraphs from validated events; propagate uncertainty; and select passages for close reading based on preregistered extremes and counterexamples rather than only visually striking cases.

| Phase | Main output | Exit criterion |
|---|---|---|
| 0. Governance | Rights matrix, hashes, provenance | Every file assigned to public, restricted, or excluded layer |
| 1. Extraction | Page/spine-preserving raw text | Deterministic rerun produces identical hashes |
| 2. Source inventory | Greek attribution IDs | Sample reviewed by a Homeric Greek specialist |
| 3. Alignment | Source-to-translation alignment table | Validation thresholds met |
| 4. Gold annotation | Adjudicated passage sample | Relation and category reliability thresholds met |
| 5. NLP models | Calibrated candidates and probabilities | Held-out error analysis approved |
| 6. Confirmatory statistics | Effect estimates and uncertainty | Preregistered models complete |
| 7. Hypergraph/embedding analysis | Secondary relational findings | Consistent with null models and robustness tests |
| 8. Interpretation | Source-controlled close readings | Includes confirming and disconfirming passages |

## 11. Reproducible Python implementation

A suitable repository should use a workflow engine such as Snakemake, pinned environments, unit tests, and data-version metadata. Raw copyrighted files, if used, belong in an ignored access-controlled directory. Public scripts, manifests, gold annotations where quotation limits permit, and aggregate outputs can be versioned.

```text
odyssey-attributions/
├── config/
│   ├── editions.yml
│   ├── ontology.yml
│   └── preregistration.yml
├── data/
│   ├── public_raw/
│   ├── restricted_raw/      # never committed
│   ├── interim/
│   └── derived/
├── src/
│   ├── ingest.py
│   ├── segment.py
│   ├── align.py
│   ├── parse.py
│   ├── coreference.py
│   ├── classify.py
│   ├── hypergraph.py
│   └── models.py
├── annotations/
├── tests/
├── Snakefile
├── pyproject.toml
└── README.md
```

Recommended packages include `lxml` or `BeautifulSoup` for EPUB parsing; `pypdf` or `PyMuPDF` for page-aware PDFs; `stanza` and `spacy` for parsing; `sentence-transformers` and a literary alignment implementation such as Bertalign; `pandas` or `polars` with Parquet; `scikit-learn` and PyTorch for classifiers; `statsmodels` or PyMC for hierarchical models; and `hypernetx` for hypergraph manipulation. Pin model names, model revisions, package versions, random seeds, and hardware-relevant determinism flags.

Automated tests should include EPUB spine order, expected book sequence, removal of known paratext anchors, recovery of hand-written attribution examples, preservation of source IDs after resegmentation, and snapshot tests for incidence matrices. Continuous integration should run only on public fixtures and synthetic structural examples, never on restricted text.

## 12. Interpretation policy

A statistically detectable translator difference is not automatically ideological. The claim ladder should be explicit:

| Evidence level | Permissible wording |
|---|---|
| Lexical difference only | “The translations use different attribute vocabularies.” |
| Source-matched category difference | “Translation A more often renders the same source attributions in category C than Translation B.” |
| Robust period pattern with within-period replication | “The sampled later translations show a higher source-controlled rate of C.” |
| Pattern plus paratextual and historical evidence | “The quantitative and historical evidence is consistent with an ideological reframing.” |
| Unsupported leap | “English ideology changed between 1900 and 2017.” |

The final study should combine quantitative estimates with close reading of passages selected by a transparent protocol: largest confirmed shifts, high-confidence null cases, model disagreements, and counterexamples. This prevents the computational stage from becoming a device for confirming a preselected interpretive thesis.

## Conclusion

The project is feasible and potentially original if it is built around a source-aligned event database, not a bag of adjective–noun pairs. The strict public-domain package now supplies six distinct translations spanning 1616–1919, which is a substantially stronger foundation for engineering, historical-language validation, prose/verse robustness testing, and pre-1920 comparison. It still cannot answer the intended 1900–2017 ideological question, because only Butler and Murray fall within that interval and both are early observations. That question requires a legally governed restricted layer and a design with within-period replication. The computational core should consist of deterministic extraction, Greek-anchored many-to-many alignment, ensemble dependency parsing, controlled entity/coreference resolution, multi-label semantic annotation, hierarchical matched-passage inference, and uncertainty-aware hypergraph comparison. Embeddings and deep learning are useful secondary components, not substitutes for identification, validation, or philological interpretation.

## References

[1]: https://guides.library.cornell.edu/copyright/publicdomain "Cornell University Library — Copyright Term and the Public Domain"
[2]: https://eur-lex.europa.eu/EN/legal-content/summary/copyright-and-related-rights-term-of-protection.html "EUR-Lex — Copyright and related rights: term of protection"
[3]: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32019L0790 "Directive (EU) 2019/790 on copyright in the Digital Single Market"
[4]: https://www.hathitrust.org/the-collection/terms-conditions/non-consumptive-use-policy/ "HathiTrust — Non-Consumptive Use Policy"
[5]: https://www.gutenberg.org/ebooks/1727 "Project Gutenberg eBook 1727 — The Odyssey, translated by Samuel Butler"
[6]: https://archive.org/details/in.gov.ignca.913 "Internet Archive — Homer the Odyssey, A. T. Murray, Volume I (1919)"
[7]: https://archive.org/details/in.gov.ignca.914 "Internet Archive — Homer the Odyssey, A. T. Murray, Volume II (1919)"
[8]: https://academic.oup.com/dsh/article-abstract/38/2/621/6965034 "Bertalign: Improved word embedding-based sentence alignment for literary texts"
[9]: https://jscholarship.library.jhu.edu/bitstreams/586463f4-79a9-4674-956a-e22559481f7a/download "Michele Asuni — Pathos Visible: Color, Affect and Emotion in Ancient Greece"
[10]: https://hypernetx.readthedocs.io/en/latest/hypergraph101.html "HyperNetX — Hypergraph 101"
[11]: https://www.gutenberg.org/ebooks/3160 "Project Gutenberg eBook 3160 — The Odyssey, translated by Alexander Pope"
[12]: https://www.gutenberg.org/ebooks/1728 "Project Gutenberg eBook 1728 — The Odyssey of Homer, translated by S. H. Butcher and Andrew Lang"
[13]: https://www.gutenberg.org/ebooks/48895 "Project Gutenberg eBook 48895 — The Odysseys of Homer, translated by George Chapman"
[14]: https://www.gutenberg.org/ebooks/24269 "Project Gutenberg eBook 24269 — The Odyssey of Homer, translated by William Cowper"
[15]: https://aclanthology.org/2023.acl-short.52/ "Dallas Card — Substitution-based Semantic Change Detection using Contextual Embeddings"
