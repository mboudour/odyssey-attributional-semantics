# Odyssey audiovisual-text source notes

## Verified current and official sources

- Christopher Nolan, *The Odyssey* (2026): Faber & Faber has an official screenplay product page, ISBN 9780571403387, described as the screenplay/complete screenplay. Source: https://www.faber.co.uk/product/9780571403387-the-odyssey/ . This is commercially published and copyrighted, not a free transcript or redistributable corpus source.
- The 2026 film opened 17 July 2026 and open-caption/SDH theatrical screenings exist, but no verified publicly downloadable official SRT/VTT has yet been located. Search evidence includes the BFI SDH listing and cinema open-caption listings; these establish captions in exhibition, not file availability.

## Public-domain film source

- *L'Odissea* (Milano Films, 1911), directed by Francesco Bertolini: Wikimedia Commons hosts the complete 43:54 WebM at https://commons.wikimedia.org/wiki/File:L%27Odissea_(Milano_Films,_1911)_.webm . The Commons page marks the film public domain in the country of origin and United States, with a CC Public Domain Mark. The page exposes a TimedText tab, but the extracted page did not show an actual caption track; API verification is still required. As a silent film, the relevant transcript unit is intertitles, not spoken dialogue.

## Verified unofficial subtitle/transcript catalogues

- *The Odyssey* (1997 miniseries): SubtitleCat displays a complete user-uploaded English timed transcript for the release `The.Odyssey.1997.DVDRip.XviD-ETRG`, with downloadable English subtitles. Source: https://www.subtitlecat.com/subs/70/The.Odyssey.1997.DVDRip.XviD-ETRG.html . The page exposes numbered SRT cues beginning at 00:00:10.504. Provenance is user-uploaded and it is not an authorized public-domain source.
- A second catalogue records `Odyssey The.DVDRip.ETRG.en.srt`, 41.6 kB, uploaded 5 March 2016. Source: https://ns1.tvsubtitles.net/subtitle-100689.html . This corroborates file existence and release matching but not authorization.
- SubsLikeScript lists transcript-style pages for *The Odyssey* (1997) and *Odysseus* (2013), but these should be classified as unofficial transcript derivatives, not primary or redistributable texts.

## Candidate adaptation inventory

Direct or substantial Odyssey screen adaptations to audit include: *L'Odissea* (1911 silent film); *Ulysses/Ulisse* (1954); *L'Odissea/The Odyssey* (1968 eight-episode miniseries); *The Odyssey* (1997 miniseries); *O Brother, Where Art Thou?* (2000, indirect adaptation); *Ulysses 31* (1981–1982 animated series, indirect/futurist); *Odysseus* (2013 television series); *The Return* (2024); and Christopher Nolan's *The Odyssey* (2026). Other derivative or loose adaptations should be separated from direct retellings.

## Rights rule

SRT/VTT/ASS files are technically ideal for Python but are not automatically free to redistribute. For protected films, the safe deliverable is a metadata catalogue, checksum, timing/quality diagnostics, and local extraction instructions for lawfully obtained media—not the subtitle text itself. User-uploaded subtitle sites are discovery evidence only unless licence or authorization is verified.

## Additional subtitle verification

- Wikimedia Commons API confirms that *L'Odissea* (1911) has both English SRT and WebVTT timed-text tracks. API metadata: https://commons.wikimedia.org/w/api.php?action=query&prop=videoinfo&titles=File%3AL%27Odissea%20%28Milano%20Films%2C%201911%29%20.webm&viprop=timedtext%7Curl&format=json . Direct English SRT endpoint: https://commons.wikimedia.org/w/api.php?action=timedtext&title=File%3AL%27Odissea_%28Milano_Films%2C_1911%29_.webm&lang=en&trackformat=srt&origin=%2A . The track contains 58 cues spanning 00:00:00–00:43:52.680. TimedText page: https://commons.wikimedia.org/wiki/TimedText:L%27Odissea_(Milano_Films,_1911)_.webm.en.srt . Commons states that unstructured page text is CC BY-SA 4.0; therefore this SRT can be redistributed only with attribution/share-alike compliance, even though the underlying film is public domain.
- *Ulysses* (1954): SubtitleCat lists an English download, but the inspected source cues render mostly as punctuation/garbled non-Latin text. This catalogue entry is not reliable as an English corpus without downloading and language-quality validation. Source: https://www.subtitlecat.com/subs/17/Ulysses%20%281954%29.html . SubsLikeScript provides a full dialogue-style transcript page, but its text displays signs of machine translation or OCR corruption (e.g., altered proper names), so it is discovery-only. Source: https://subslikescript.com/movie/Ulysses-47630 .
- *L'Odissea* (1968): SubtitleCat has a user-uploaded English timed text for episode 1 of 8 at https://subtitlecat.com/subs/414/Odissea%20-%20%281968%2C%20Franco%20Rosi%29%201%20di%208.html . Its cues include dialogue, narrator text, and editorial annotations/footnotes marked with brackets or asterisks. It is computationally parseable but requires separating spoken dialogue, narration, and annotator commentary. Authorization/licence is unverified. YouTube playlists also expose English subtitles but upload authorization is uncertain.
- *Odysseus* (2013): SubsLikeScript lists twelve episode transcript pages, source index https://subslikescript.com/series/Odysseus-2141869 . A separate subtitle index reports season-level subtitle availability, but search evidence is inconsistent about whether all episodes have English tracks. This remains a protected, unofficial-source candidate requiring episode-by-episode verification.
- *The Return* (2024): Official/reputable evidence includes a Writers Guild article with a screenplay page sample, https://www.writtenby.com/member-voices/articles/2024/a-tale-as-old-as-time , and official press notes naming the screenplay authors, https://s3.amazonaws.com/cdn.filmtrackonline.com/mongrelmedia/starcm_vault_root/media%2Fpublicwebassets%2FTHE_RETURN_Mongrel_press_kit_%7Bf2d809e2-4992-ef11-ba59-0efdbb9167fd%7D.pdf . User-uploaded English SRTs are catalogued by SubtitleCat/SubDL, but no authorized free full screenplay or official downloadable SRT has yet been verified.

## Completeness checks

The user-uploaded English timed transcript for *The Odyssey* (1997) contains 1,737 cues and runs to 02:51:04.879, so it covers the combined full miniseries rather than only one installment. The independent TVsubtitles catalogue lists the matching `DVDRip.ETRG` SRT at 41.6 kB, uploaded 5 March 2016. These facts establish technical completeness and release matching, but not authorization or a reusable licence.

The Faber publisher page for Christopher Nolan's *The Odyssey (Screenplay)* identifies Christopher Nolan as author, ISBN 9780571403387, ebook and paperback formats, price £12.99, and publication date 30 July 2026. As of 17 July 2026 it is a commercial pre-order; the official page offers no free screenplay, transcript, SRT, or VTT download. Source: https://www.faber.co.uk/product/9780571403387-the-odyssey/ .
