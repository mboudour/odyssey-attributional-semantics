# Attributional Semantics in English Translations of Homer’s *Odyssey*

## Computational Results Report

### Executive statement

This report documents a fully reproducible, rights-safe baseline analysis of **six complete English translations** published from 1616 to 1919. The processed corpus contains **735,316 words** and the explicit extraction grammar identified **13,226 target–attribute events**. Results quantify translation-specific attribution patterns; they do **not** establish a causal ideological evolution because translator, period, verse/prose form, and historical language are confounded.

### Corpus-level diagnostics

| translation_id    | translator                    |   year | form   |   corpus_words |   event_count |   events_per_10k_words |   mean_extraction_confidence |
|:------------------|:------------------------------|-------:|:-------|---------------:|--------------:|-----------------------:|-----------------------------:|
| chapman_1616      | George Chapman                |   1616 | verse  |         133440 |          2175 |                162.995 |                       0.7566 |
| pope_1726         | Alexander Pope                |   1726 | verse  |         108596 |          2305 |                212.255 |                       0.7658 |
| cowper_1791       | William Cowper                |   1791 | verse  |         109201 |          1880 |                172.16  |                       0.7608 |
| butcher_lang_1879 | S. H. Butcher and Andrew Lang |   1879 | prose  |         134673 |          2789 |                207.094 |                       0.7957 |
| butler_1900       | Samuel Butler                 |   1900 | prose  |         117320 |          1523 |                129.816 |                       0.7699 |
| murray_1919       | A. T. Murray                  |   1919 | prose  |         132086 |          2554 |                193.359 |                       0.7479 |

The common alignment coordinate is the complete native Homeric **Book I–XXIV** unit, yielding 24 matched anchors per translation. It is a transparent book-level structural alignment, not Greek-line alignment. Murray’s OCR-obscured Book III, V, IX, and XI starts are audited against original scan pages; no book is inferred by proportional allocation. OCR-derived text retains a reduced segmentation-confidence value.

The ten weakest anchors are:

| anchor_id   |   mean_pairwise_cosine |   mean_length_ratio |   anchor_confidence |
|:------------|-----------------------:|--------------------:|--------------------:|
| book_20     |                 0.2667 |              0.8597 |              0.5039 |
| book_23     |                 0.2683 |              0.86   |              0.505  |
| book_01     |                 0.2861 |              0.8761 |              0.5221 |
| book_02     |                 0.2895 |              0.8728 |              0.5228 |
| book_06     |                 0.2938 |              0.8668 |              0.523  |
| book_16     |                 0.3115 |              0.8566 |              0.5296 |
| book_19     |                 0.3036 |              0.8798 |              0.5341 |
| book_13     |                 0.3151 |              0.8735 |              0.5384 |
| book_14     |                 0.3169 |              0.8724 |              0.5391 |
| book_17     |                 0.3132 |              0.8863 |              0.5425 |

### Primary distributional comparisons

The largest category-profile divergences are:

| translation_a     | translation_b   |   year_distance |   jensen_shannon_divergence |   category_cosine_similarity |
|:------------------|:----------------|----------------:|----------------------------:|-----------------------------:|
| butler_1900       | pope_1726       |             174 |                      0.0547 |                       0.9414 |
| butcher_lang_1879 | pope_1726       |             153 |                      0.0485 |                       0.9404 |
| murray_1919       | pope_1726       |             193 |                      0.041  |                       0.9437 |
| butler_1900       | cowper_1791     |             109 |                      0.0407 |                       0.9575 |
| butcher_lang_1879 | butler_1900     |              21 |                      0.0388 |                       0.9609 |
| butler_1900       | murray_1919     |              19 |                      0.03   |                       0.9713 |
| chapman_1616      | pope_1726       |             110 |                      0.0262 |                       0.9685 |
| butcher_lang_1879 | cowper_1791     |              88 |                      0.0257 |                       0.9696 |
| butcher_lang_1879 | chapman_1616    |             263 |                      0.0251 |                       0.9795 |
| butler_1900       | chapman_1616    |             284 |                      0.0247 |                       0.9827 |

The analysis uses weighted event counts, where each event is weighted by extraction confidence. Negated predicates receive a 0.5 magnitude multiplier and remain explicitly marked in the event table.

### Chronological estimands

For every ontology category, the pipeline estimates the descriptive slope in weighted events per 10,000 words per century. With only six translations, p-values come from all **720 exact permutations** of publication years. Holm adjustment controls family-wise error across categories. These tests assess chronological ordering under exchangeability; they do not identify ideology.

| category             |   slope_events_per_10k_per_century |   pearson_r_year |   exact_permutation_p |   holm_adjusted_p |
|:---------------------|-----------------------------------:|-----------------:|----------------------:|------------------:|
| social_status        |                            -1.5488 |          -0.8438 |                0.0347 |            0.4161 |
| color_material       |                             0.5795 |           0.6084 |                0.2205 |            1      |
| color_complex        |                             0.9097 |           0.556  |                0.2524 |            1      |
| appearance_age       |                             1.6874 |           0.4689 |                0.3454 |            1      |
| moral_evaluation     |                            -1.5234 |          -0.4482 |                0.3675 |            1      |
| affect_state         |                            -0.6578 |          -0.3498 |                0.5201 |            1      |
| behavior_disposition |                            -1.3224 |          -0.3444 |                0.5562 |            1      |
| cognitive_evaluation |                             0.9735 |           0.2843 |                0.57   |            1      |
| color_hue            |                             0.6015 |           0.261  |                0.613  |            1      |
| luminosity           |                            -0.4852 |          -0.2163 |                0.6741 |            1      |
| agency_capacity      |                            -0.0933 |          -0.1039 |                0.8544 |            1      |
| scale_intensity      |                            -0.4126 |          -0.0839 |                0.8585 |            1      |

Matched-book bootstrap intervals resample the 24 common native-book anchors, preserving within-anchor cross-translation dependence:

| category             |   slope_mean |   slope_ci_2_5 |   slope_ci_97_5 |   probability_positive |
|:---------------------|-------------:|---------------:|----------------:|-----------------------:|
| moral_evaluation     |      -1.5651 |        -2.8031 |         -0.0946 |                  0.01  |
| social_status        |      -1.5455 |        -2.0751 |         -0.9854 |                  0     |
| behavior_disposition |      -1.33   |        -1.7686 |         -0.913  |                  0     |
| affect_state         |      -0.6899 |        -1.3838 |         -0.0033 |                  0.026 |
| luminosity           |      -0.4618 |        -0.8204 |         -0.065  |                  0.016 |
| scale_intensity      |      -0.3849 |        -1.34   |          0.7303 |                  0.236 |
| agency_capacity      |      -0.0832 |        -0.4448 |          0.2965 |                  0.3   |
| color_material       |       0.5934 |         0.1985 |          0.9931 |                  1     |
| color_hue            |       0.5944 |         0.0363 |          1.2274 |                  0.976 |
| color_complex        |       0.9137 |         0.6182 |          1.2123 |                  1     |
| cognitive_evaluation |       0.9751 |         0.2753 |          1.6888 |                  0.996 |
| appearance_age       |       1.6816 |         0.6456 |          2.6021 |                  1     |

### Hypergraph comparisons

Each translation is represented as a weighted hypergraph in which canonical **targets are hyperedges** and normalized attributes are vertices. Incidence weights equal summed event confidences. Pairwise comparisons include weighted and unweighted Jaccard similarity, cosine similarity, and mean target-level edge overlap.

| translation_a     | translation_b   |   weighted_jaccard |   incidence_cosine |   unweighted_jaccard |   mean_target_edge_jaccard |
|:------------------|:----------------|-------------------:|-------------------:|---------------------:|---------------------------:|
| butcher_lang_1879 | murray_1919     |             0.4267 |             0.8028 |               0.3927 |                     0.3363 |
| chapman_1616      | pope_1726       |             0.1995 |             0.5113 |               0.2105 |                     0.1426 |
| chapman_1616      | murray_1919     |             0.1966 |             0.4912 |               0.2167 |                     0.1588 |
| butler_1900       | murray_1919     |             0.1928 |             0.4842 |               0.216  |                     0.1542 |
| butcher_lang_1879 | chapman_1616    |             0.1916 |             0.483  |               0.2206 |                     0.1682 |
| butler_1900       | chapman_1616    |             0.1832 |             0.4673 |               0.1898 |                     0.1328 |
| cowper_1791       | pope_1726       |             0.1796 |             0.6912 |               0.1881 |                     0.126  |
| butcher_lang_1879 | butler_1900     |             0.1793 |             0.4597 |               0.218  |                     0.1636 |
| chapman_1616      | cowper_1791     |             0.1705 |             0.4197 |               0.1976 |                     0.1346 |
| butcher_lang_1879 | cowper_1791     |             0.1612 |             0.5054 |               0.1874 |                     0.1253 |
| cowper_1791       | murray_1919     |             0.158  |             0.4099 |               0.193  |                     0.1375 |
| butler_1900       | cowper_1791     |             0.1407 |             0.3784 |               0.1633 |                     0.1119 |
| butcher_lang_1879 | pope_1726       |             0.1372 |             0.4719 |               0.1524 |                     0.102  |
| murray_1919       | pope_1726       |             0.1358 |             0.3949 |               0.1519 |                     0.1011 |
| butler_1900       | pope_1726       |             0.1208 |             0.3916 |               0.1382 |                     0.1027 |

The associated null model permutes attribute labels within each translation, preserving target degrees, attribute frequencies, and event weights. JSON hypergraphs and GraphML target/attribute projections are included under `outputs/hypergraphs/`.

### Memory-bounded contextual semantics

Event contexts are represented with TF–IDF unigrams/bigrams followed by Truncated SVD and L2 normalization. This sparse distributional baseline permits target/category centroid comparisons without loading a transformer on the memory-constrained cloud machine. It is intentionally labeled a baseline; transformer embeddings can be added later under the same event and alignment schema.

### Translation-distinctive attributes

Weighted log-odds-style z scores identify attributes that are comparatively distinctive within each translation. They are exploratory lexical diagnostics, not direct evidence of ideology.

| translation_id    | attribute   |   local_count |   log_odds_ratio |   z_score |
|:------------------|:------------|--------------:|-----------------:|----------:|
| butcher_lang_1879 | evil        |           118 |           1.146  |    9.2609 |
| butcher_lang_1879 | gray-eyed   |            56 |           3.2185 |    8.7927 |
| butcher_lang_1879 | steadfast   |            54 |           2.1286 |    8.7686 |
| butcher_lang_1879 | wise        |           199 |           0.5678 |    6.6544 |
| butcher_lang_1879 | fair        |           205 |           0.5438 |    6.4927 |
| butler_1900       | good        |           134 |           0.8648 |    8.8365 |
| butler_1900       | wicked      |            24 |           2.7968 |    7.8391 |
| butler_1900       | just        |            53 |           1.2437 |    7.5854 |
| butler_1900       | angry       |            35 |           1.4981 |    7.1198 |
| butler_1900       | young       |            62 |           1.0141 |    6.9109 |
| chapman_1616      | free        |            71 |           1.8291 |   10.4395 |
| chapman_1616      | sacred      |            64 |           1.0141 |    6.5852 |
| chapman_1616      | good        |           149 |           0.5717 |    6.0554 |
| chapman_1616      | sad         |            36 |           0.9867 |    4.8358 |
| chapman_1616      | divine      |            75 |           0.6368 |    4.7428 |
| cowper_1791       | deep        |           160 |           1.1279 |   11.7462 |
| cowper_1791       | noble       |            82 |           1.1187 |    8.3245 |
| cowper_1791       | prudent     |            27 |           2.1444 |    7.2547 |
| cowper_1791       | sable       |            28 |           1.8371 |    6.883  |
| cowper_1791       | ancient     |            30 |           1.6505 |    6.6952 |
| murray_1919       | evil        |           116 |           1.2282 |    9.9096 |
| murray_1919       | wise        |           215 |           0.8078 |    9.6565 |
| murray_1919       | beautiful   |            61 |           2.0213 |    9.5192 |
| murray_1919       | enduring    |            26 |           2.3561 |    6.4749 |
| murray_1919       | bronze      |            52 |           1.1731 |    6.4051 |
| pope_1726         | royal       |            88 |           1.9449 |   11.7343 |
| pope_1726         | faithful    |            41 |           2.2204 |    8.3714 |
| pope_1726         | fierce      |            45 |           1.7316 |    7.9197 |
| pope_1726         | friendly    |            28 |           2.1669 |    6.878  |
| pope_1726         | bold        |            40 |           1.3618 |    6.4371 |

### Validation and interpretation boundaries

The extraction layer is deliberately auditable. Every event records the surface target and attribute, canonical normalization, ontology category, relation template, token distance, negation, full sentence context, segmentation confidence, and extraction confidence. The package includes a stratified manual-validation sample and annotation template. Automatic estimates should not be interpreted substantively until that sample is reviewed and precision is reported by category, relation template, and translation.

The corpus is appropriate for testing historical translation variation and the computational pipeline. It is not adequate for a 1900–2017 trend claim because only one retained translation is later than 1900. Modern copyrighted translations should be analyzed locally as a governed, non-redistributed extension if lawful access and the applicable text-and-data-mining rules permit.

### Figures

![01_translation_event_rates](../figures/01_translation_event_rates.png)
![02_category_rate_heatmap](../figures/02_category_rate_heatmap.png)
![03_category_divergence](../figures/03_category_divergence.png)
![04_alignment_confidence](../figures/04_alignment_confidence.png)
![05_chronological_slopes](../figures/05_chronological_slopes.png)
![06_hypergraph_similarity](../figures/06_hypergraph_similarity.png)
![07_top_target_rates](../figures/07_top_target_rates.png)

### Reproducibility

Run `make reproduce` from the repository root. The pipeline uses pinned dependencies, deterministic seeds, SHA-256 input/output manifests, and unit/integration tests. Machine-readable data, models, figures, tables, hypergraphs, logs, and this report are all included in the downloadable archive.
