# Reader V3.1 — 061 Maze of Ith, individual candidate (October 27, 2026)

## Authority, stage and preservation

Starting accepted `main`: `7fffc2982b2c994333e8bc603ce531e44d41b7db`; accepted numbered Reader wave **051–060**. This report covers the **source-backed single-page 061 candidate**, not acceptance of the ten-page 061–070 wave. The current public score is **51/100 accepted roadmap points**, with **60/100 initial Reader pages accepted**; candidate 061 is deliberately not yet counted. The next individual authoring task is **062 — The Tabernacle at Pendrell Vale**.

Changed article: `061-maze-of-ith.html` only, preserving navigation, deck archive records, canonical art URLs, and other articles. Added source-specific evidence in `research-dossiers/reader-v31-061-070/`, corrected the original 061 research dossier, and added a source-bound validation tool and machine-readable candidate metrics.

## Grounded article changes

- **Identity:** original **The Dark (August 1, 1994)** land illustrated by **Anson Maddocks**. Maze does not tap to add mana. [Original printing](https://www.mtg.wtf/card/drk/117/Maze-of-Ith)
- **Official mechanics:** a vigilant and hence untapped attacker may be targeted; the target remains an attacking creature; attacking triggers are not undone; the ability prevents combat damage from and to only that target; a postdamage untap does not rewind earlier combat damage. [Official Dominaria Remastered release notes](https://magic.wizards.com/en/news/feature/dominaria-remastered-release-notes)
- **Documented deck:** organizer-published **Mark Arce — Mono Black**, Eternal Weekend Old School 2015, contains **one Maze of Ith** in its business section alongside `Hypnotic Specter`, with Swamps listed among actual mana sources. [Eternal Central original registration](https://www.eternalcentral.com/oldschoolew2015/)
- **Reader opening:** a first-person reconstruction with a tapped Specter, opposing untapped Serra Angel, Kird Ape and Taiga, one Maze activation and the exact **6 → 4** life change. The opposing deck is fictional; the report does not claim this is an actual Arce game or that a named tournament opponent used those exact cards.
- **Presentation:** standard opening `play-vignette` component, hidden zero-mana/tap-only payment metadata and rules review, structural placement immediately before Strategic legacy, inline readability/contrast CSS, first-printing artist and derived read-time data.
- **Editorial rewrite:** replaces generic and repetitive source/history/format/technical/testimony passages with article-specific discussion and separates hypothetical stories from documentary tournament evidence.
- **Research dossier:** replaces generic eight-way source attribution with discrete source IDs, dated historical evidence, corrected card playbook, one confirmed published deck binding, and explicit research limitations.

## Evidence and validation

`research-dossiers/reader-v31-061-070/061-review.json` records actual mechanics/chronology review; `source-verification.json` records four specific claims. `tools/validate_reader_061_candidate.py` checks the dossier schema, source bindings, exact named deck, zero-mana activation, derived word count/read time, article hash, and consistency with the single-page story record. Derived story and metrics are refreshed deterministically rather than hand-counted.

The approved release checks remain the project's current quick, V2-refresh, full, navigation and desktop/mobile browser suites. **Only mark any of these as passing once GitHub Actions has actually completed successfully.** Retain the incumbent warning queues separately.

## Verified candidate metrics and successful release refresh

The branch-local refresh on October 27, 2026 **passed** its read-time refresh, source/dossier consistency check, quick and V2-refresh suites, complete release suite, internal navigation and retained 051–060 checkpoint verification. See [successful GitHub Actions refresh run](https://github.com/Diabolicdonut/Compulsive-Research/actions/runs/40568283043). The temporary write-enabled refresh workflow was subsequently removed.

- Reader 061 article: **3,432 derived editorial words**; **18-minute** reading time at 200 wpm.
- First-person opening: **92 words**, one exact documentary deck-reference title.
- Source-verification records: **4 individually scoped checks**.
- Candidate file SHA-256: `120bc1e9fa093dc1e66cd1bfd9e2d33647ada3aca757fc3a0baeafb7adf36f4e`.
- Generated `validation/reader-v3.1-061-candidate-metrics.json` and `061-story-candidate.json` encode this candidate; they do **not** modify the accepted 051–060 ledger.

This reflects candidate acceptance only. PR CI must still validate the reviewable candidate before merging; neither the 061–070 wave nor the whole-site research backlog is complete.

## Remaining gates

1. Source-review any unverified claims inherited in the rest of 061, particularly alternate deck-archive registrations and printings (no generic link qualifies as event attribution).
2. Convert **062–070** individually, with accurate opening reconstructions and source dossiers; create the wave's ten-article metrics and cumulative Reader migration ledger.
3. Validate the full ten-article batch against protected article hashes and all release checks; only after merging the accepted batch should the public Reader figure advance from 60/100 to 70/100.
4. Do not update weighted **overall 51%** until its **061–100 12-point gate** is fully accepted or a new weighted subdivision has been expressly approved.

This report deliberately does not assert independent historical verification of all 1,505 articles or even all inherited secondary references in the Maze article.
