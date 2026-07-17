# Manual validation protocol

Review each sampled event in its sentence context. Mark `gold_target_correct`, `gold_attribute_correct`, `gold_relation_correct`, and `gold_category_correct` as `1` or `0`. If a field is incorrect, enter the corrected canonical value in the corresponding revision column. Use `notes` for ambiguity, OCR artifacts, archaic syntax, or cases requiring a larger passage window.

Report precision with Wilson 95% intervals overall and separately by translation, ontology category, and extraction relation. Do not interpret category rates substantively if overall precision is below 0.80 or if any central category has fewer than 30 reviewed examples or precision below 0.70. Inter-annotator agreement should be estimated on at least 20% of the sample using Cohen’s kappa for binary correctness and Krippendorff’s alpha for revised categorical labels.
