# Odyssey Audiovisual Texts: Source Audit and Computational Integration Protocol

**Author:** Manus AI  
**Audit date:** 17 July 2026

## 1. Executive finding

Subtitles are the most tractable audiovisual text source because **SRT, WebVTT, and ASS/SSA preserve utterance-sized text with timestamps**. Nevertheless, format availability and legal reusability are separate questions. A user-uploaded SRT may be technically excellent while lacking verified authorization or a licence for redistribution.

This audit identified one immediately redistributable timed-text corpus: the English SRT and WebVTT for the public-domain 1911 silent film *L'Odissea*. Wikimedia Commons supplies 58 cues spanning the complete 43-minute film; the subtitle text is available under CC BY-SA 4.0.[1] The validated Python extraction contains 623 tokens and no overlapping cues.

Several later adaptations have discoverable English subtitles or transcripts, especially *The Odyssey* (1997), but their sources are unofficial and carry no verified reusable licence. They should therefore be represented in the project by **metadata and acquisition instructions**, not redistributed text. Nolan's *The Odyssey* (2026) has official theatrical captions and a forthcoming commercial screenplay, but no authorized public SRT, VTT, or free transcript was located as of the audit date.[2] [3]

> **Corpus rule:** include subtitle or screenplay text in a distributable corpus only when authorization or a reusable licence is explicit. For protected works, process a lawfully obtained copy locally and publish only derived, non-reconstructive measurements unless permission permits more.

## 2. Verified source matrix

| Work | Year | Text evidence | Coverage and quality | Reuse status | Decision |
|---|---:|---|---|---|---|
| *L'Odissea* | 1911 | Commons SRT and VTT | 58 cues; complete film; 623 tokens | CC BY-SA 4.0 subtitle text; film marked public domain | **Include and redistribute with attribution** |
| *Ulysses* | 1954 | Subtitle catalogue and web transcript | A purported English track exists, but inspected text is garbled; web transcript contains apparent corruption | No verified licence | Exclude until a better source is obtained |
| *L'Odissea* | 1968 | Episode-level SRT and captioned uploads | Episode 1 verified; dialogue, narration, and annotations are mixed; full eight-episode English set not independently verified | No verified licence | Catalogue for lawful local processing |
| *Ulysses 31* | 1981–82 | English dub and fan-captioned uploads | No complete licensed 26-episode text corpus verified | No verified licence | Optional derivative corpus, not core |
| *Nostos: The Return* | 1989 | No useful English transcript located | Minimal speech in an invented language; primarily visual narration | Protected film | Exclude from lexical analysis; consider visual-semiotic study |
| *The Odyssey* | 1997 | Release-matched SRT catalogue | **1,737 cues through 02:51:04.879**, covering the combined full miniseries | User-uploaded; no reusable licence verified | Strongest protected local candidate |
| *O Brother, Where Art Thou?* | 2000 | Published Faber screenplay and unofficial online texts/SRTs | Complete commercial screenplay exists; indirect adaptation | Copyrighted | Optional, separate indirect-adaptation stratum |
| *Odysseus* | 2013 | Twelve transcript pages listed | Episode-by-episode English timed coverage not fully verified | Unofficial; no reusable licence | Catalogue pending validation |
| *The Return* | 2024 | Official screenplay sample and press kit; unofficial SRT catalogues | Full authorized text not publicly available | Copyrighted | Process only from a lawful local source |
| Nolan's *The Odyssey* | 2026 | Faber commercial screenplay; BFI SDH screenings | Captions exist in exhibition; no official public file found | Copyrighted | Wait for authorized screenplay/caption acquisition |

The complete machine-readable audit is supplied as `odyssey_av_text_audit.csv`. It distinguishes **publicly reusable**, **lawful-local-only**, **technically defective**, and **not yet available** sources.

## 3. Nolan's 2026 film

The current evidence requires a precise distinction. BFI lists SDH theatrical screenings, so a professional caption track exists operationally.[3] That does **not** imply that an SRT or VTT file has been publicly released. Faber lists Christopher Nolan's complete screenplay as a commercial paperback and ebook, ISBN 9780571403387, with publication scheduled for 30 July 2026.[2]

Unofficial subtitle sites already display entries for the new film. Because the film has just opened, such files could be placeholders, trailer text, machine-generated material, release mismatches, or unauthorized copies. They were deliberately not downloaded or treated as evidence. The defensible routes are to acquire the published screenplay, obtain official captions with lawful media access, or secure research permission from the rights holder.

## 4. Python-ready public corpus

The package includes the following public files and derivatives:

| File | Role |
|---|---|
| `public_subtitles/lodissea_1911_en.srt` | Canonical English timed text |
| `public_subtitles/lodissea_1911_en.vtt` | WebVTT equivalent |
| `prepared/lodissea_1911_en_cues.csv` | Tabular cue-level representation |
| `prepared/lodissea_1911_en_cues.jsonl` | Streamable structured representation |
| `prepared/lodissea_1911_en_plain.txt` | Normalized text for NLP |
| `prepared/lodissea_1911_en_metrics.json` | Technical and provenance metrics |
| `parse_public_srt.py` | Dependency-free reproducible parser |
| `validate_av_audit.py` | Rights-boundary and integrity validator |

The cue record should remain the atomic unit:

```text
work_id, release_id, cue_id, start_ms, end_ms, raw_text,
normalized_text, language, layer, speaker, source_url,
licence, checksum, alignment_confidence
```

`layer` must distinguish `dialogue`, `narration`, `intertitle`, `scene_direction`, `sound_description`, `song`, and `editorial_annotation`. The 1911 film contains translated intertitles rather than spoken dialogue, so comparisons must not collapse it into the same linguistic channel as a sound film.

## 5. Computational integration with the translation project

### 5.1 Separate adaptation from translation

Films are not additional translations in the same statistical sample. They alter plot coverage, dialogue proportion, visual description, chronology, speaker structure, and audience constraints. The correct architecture is a **multimodal adaptation layer** linked to the source-aligned translation corpus through Homeric episodes.

The principal comparison unit should be an episode ontology such as `CYCLOPS`, `CIRCE`, `SIRENS`, `CALYPSO`, `NAUSICAA`, `UNDERWORLD`, `RECOGNITION`, and `SUITORS`. Each subtitle window or screenplay scene receives zero, one, or multiple episode labels with probabilities. This makes omissions and conflations explicit.

### 5.2 Alignment algorithm

A robust alignment pipeline should operate as follows. First, concatenate adjacent cues into 20–60 second windows while retaining cue boundaries. Second, retrieve candidate Homeric passages and translation passages using sparse BM25 and dense sentence embeddings. Third, rerank the candidate pairs with a cross-encoder. Fourth, apply sequence constraints with dynamic programming, but allow skips, flashbacks, and episode reordering. Fifth, send low-confidence and structurally novel matches to manual review.

The alignment output should be a many-to-many table:

```text
av_window_id, homer_book, homer_line_start, homer_line_end,
episode_id, retrieval_score, reranker_score, sequence_penalty,
final_probability, reviewer_status
```

Alignment accuracy should be reported separately for direct adaptations and loose derivatives. A model that performs well on the 1997 miniseries may fail on *O Brother, Where Art Thou?* because correspondence is analogical rather than lexical.

### 5.3 Attribution extraction

SRT files generally lack speaker names and scene directions. Speaker attribution therefore requires a hierarchy of evidence: explicit caption labels; screenplay speaker fields; recurring address forms; cast/entity constraints; and, when lawful audiovisual material is available, speaker diarization combined with face/shot information. Unknown speakers must remain `UNKNOWN` rather than being guessed.

Attribution extraction should combine dependency parsing, semantic-role labeling, apposition patterns, copular constructions, vocatives, and event predicates. Each result must preserve its textual layer and uncertainty:

```text
(work_id, episode_id, target_entity, attribute_lemma,
 attribute_surface, attribute_family, layer, polarity,
 modality, speaker, confidence, start_ms, end_ms)
```

For color analysis, spoken adjectives and visual production descriptions answer different questions. A screenplay phrase such as “the black ship” is narratorial/visual design evidence; a character saying “dark-hearted man” is dialogue evidence. They must be estimated separately before any combined interpretation.

### 5.4 Statistical design

The primary estimands should compare matched episodes rather than raw corpus frequencies. Recommended outcomes include the probability that a source attribution is lexicalized in dialogue, the probability that it is shifted from physical/color description to moral or psychological evaluation, and the probability that an entity receives an adaptation-specific attribute absent from aligned translations.

A hierarchical model can use an observation-level binary or multinomial outcome with random intercepts for Homeric episode, entity, source lemma, and work. Fixed effects should distinguish medium, year, directness of adaptation, text layer, and prose/verse screenplay style. Uncertainty from episode alignment, speaker attribution, and NLP extraction should enter through posterior weighting or multiple imputation. With only a few films, chronological coefficients must be treated as exploratory rather than as evidence of ideological change.

### 5.5 Hypergraph representation

For each work `f`, define a hypergraph as a dictionary whose **keys are target nouns/entities (hyperedges)** and whose **values are sets of attributed nodes**:

```python
H_f = {
    "ODYSSEUS": {"cunning", "proud", "weary", "dark-haired"},
    "PENELOPE": {"faithful", "patient", "grieving"},
    "SEA": {"dark", "wine-coloured", "hostile"},
}
```

Retain a separate weighted incidence tensor `W[f, episode, layer, target, attribute]`. Binary set overlap alone discards frequency, episode coverage, textual layer, and confidence. Comparisons should include weighted Jaccard similarity, Jensen–Shannon divergence over attribute-family distributions, hyperedge-size and overlap profiles, entity centrality, and permutation tests that preserve each work's episode coverage and number of extracted attributions.

## 6. Recommended acquisition sequence

The most valuable next protected source is *The Odyssey* (1997) because a technically complete, release-matched English timed transcript is discoverable. The project should obtain it only through a lawful route or user-supplied subtitle track and keep it outside any redistributable package. The next priorities are the 1968 miniseries, because of its directness and length; *The Return* (2024), because it concentrates on the Ithacan return and recognition scenes; and Nolan's screenplay after its commercial publication.

For every acquired protected file, store only its checksum, provenance, edition/release identifier, technical metrics, and derived non-reconstructive statistics in the shareable repository. Keep the text in an access-controlled local directory excluded by `.gitignore`.

## 7. Conclusion

The audiovisual extension is feasible, but it should be built as a **rights-aware, episode-aligned adaptation corpus**, not by pooling random internet transcripts. One public timed text can be included immediately. Several protected works are computationally promising for lawful local research, with the 1997 miniseries the strongest existing candidate. Nolan's 2026 film is not yet represented by an authorized public timed-text file; its commercial screenplay and theatrical captions should be treated as acquisition leads, not open corpus data.

## References

[1]: https://commons.wikimedia.org/wiki/TimedText:L%27Odissea_(Milano_Films,_1911)_.webm.en.srt "Wikimedia Commons: English timed text for L'Odissea (1911)"
[2]: https://www.faber.co.uk/product/9780571403387-the-odyssey/ "Faber: The Odyssey (Screenplay) by Christopher Nolan"
[3]: https://whatson.bfi.org.uk/imax/Online/default.asp?BOparam::WScontent::loadArticle::permalink=odyssey-the-film-imax-70mm-2026-sdh "BFI IMAX: The Odyssey SDH screenings"
[4]: https://www.subtitlecat.com/subs/70/The.Odyssey.1997.DVDRip.XviD-ETRG.html "SubtitleCat: The Odyssey (1997) timed transcript catalogue"
[5]: https://ns1.tvsubtitles.net/subtitle-100689.html "TVsubtitles: The Odyssey (1997) release-matched English SRT record"
[6]: https://subtitlecat.com/subs/414/Odissea%20-%20%281968%2C%20Franco%20Rosi%29%201%20di%208.html "SubtitleCat: L'Odissea (1968), episode 1"
[7]: https://www.writtenby.com/member-voices/articles/2024/a-tale-as-old-as-time "Written By: The Return screenplay sample and discussion"
[8]: https://books.google.com/books/about/O_Brother_where_Art_Thou.html?id=KeZNwgEACAAJ "Google Books: O Brother, Where Art Thou? Faber screenplay edition"
