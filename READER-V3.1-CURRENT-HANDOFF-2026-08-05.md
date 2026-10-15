# Compulsive Research — Reader V3.1 Current Handoff

## September 24, 2026 audit checkpoint

The September checkpoint supersedes the August validation and work-status claims below. The archive-wide structural and editorial audit is in `audit.md`. Ten numbered Reader V3.1 stories (003, 007, 013, 014, 019, 027, 032, 033, 038, and 042) and the Stoneforge Mystic supplemental story (417) received targeted gameplay corrections. Wheel of Fortune (016) also had a wrong-card image and artist-credit repair. Decklists, navigation, and the other long-form text were preserved. The forty-entry migration ledger, story ledger, review index, and reading times were refreshed.

The next content checkpoint is **entries 051–060**, then 061–070, 071–080, 081–090, and 091–100. See the newest `audit.md` for validation status and the ordered editorial backlog.

**Authoritative as of:** August 5, 2026  
**Project root:** `Compulsive-Research-main/`  
**Landing page:** `index.html`  
**Canonical structural article:** `250-eternal-dragon.html`

## Current archive

- 1,000 numbered articles
- 505 active Honorable Mentions
- 22 Honorable Mention categories
- 1,505 active article pages total
- Honorable Mention navigation remains category-local
- Reader-facing editorial workflow labels are prohibited

This project folder is the sole source of truth. Do not rebuild it from older ZIPs or overwrite it with earlier Wave 1, Wave 2, Editorial V2, Reader V3, or pre-V3.1 packages.

## Reader V3.1 status

### Numbered Wave 1 complete

Entries **001–050** are now under Reader V3.1. Entries 001–010 remain the approved pilot; entries 011–050, Lightning Bolt through Stasis, complete the first numbered wave.

The forty newly migrated pages preserve their existing long-form articles and documentary Deck Archives while adding:

- A card-specific first-person vignette at the end of the opening
- Hidden era, matchup, exact Deck Archive registration, reconstruction status, and opening-mode metadata
- Strategic Legacy immediately after the completed opening
- Read time calculated from editorial prose at 200 words per minute
- Reader V3.1 styling and inline Official Magic product contrast

Review and audit files:

- `READER-V3.1-ENTRIES-011-050-REVIEW-INDEX.html`
- `READER-V3.1-MIGRATION-LEDGER.json`
- `research-dossiers/READER-V3.1-NUMBERED-WAVE-01-STORY-LEDGER.json`
- `validation/reader-v3.1-entries-011-050-metrics.md`

### Supplementary examples

The project also retains these updated samples:

- `248-astral-slide.html`
- `250-eternal-dragon.html`
- `417-stoneforge-mystic.html`
- `425-emrakul-the-aeons-torn.html`

## Final validation for Numbered Wave 1

- Reader Experience V3: **PASS** — 54 migrated pages
- Reader layout contract: **PASS** — 100 numbered pages checked
- Reader-facing editorial labels: **PASS** — 1,505 pages checked
- Archive-wide `--refresh-v2`: **PASS** — 9/9 stages
- Bounded `--full`: **PASS** — 10/10 stages
- Release corpus SHA-256: `15f0b1c2a39d8010f320bfa6b5742e7db5698b8cdfab688826b7a18ef916cc0b`

The pre-existing deck-semantics warning queue remains unchanged. Read `validation/reader-v3.1-unresolved-warnings.md` before treating warning counts as new defects.

## Exact next task

Retrofit Reader V3.1 for numbered entries **051–100**, from **Juzám Djinn** through **Ivory Tower**.

Work internally in five groups of ten:

- 051–060
- 061–070
- 071–080
- 081–090
- 091–100

Return one merged fifty-article package. After entries 051–100, produce Honorable Mention Wave 1, then continue numbered entries in fifty-card waves using internal ten-card checkpoints.

## Reader-facing article order

1. Article title and opening thesis
2. Card image
3. Rules text and original identity
4. Brief article framing
5. **A story from the table**
6. **Strategic Legacy**
7. Remaining history, mechanics, tournament, play, counterplay, art, products, decks, printings, and sources

Strategic Legacy must not appear before the card image, rules, and original identity. Do not place a highlighted sentence immediately before Strategic Legacy that merely repeats its lead.

## “A story from the table” standard

The visible vignette contains only:

- The label **A story from the table**
- A card-specific title
- The raw story

Do not show a year, matchup caption, source-deck caption, reconstruction notice, or interpretive explanation in the visible story panel. Preserve those facts in hidden metadata.

Each story must use first-person singular voice, describe one speaker and one opponent in one concrete game, name exact cards and game actions, show the featured card doing its characteristic work, and end on the decisive play, reaction, reversal, punchline, or resulting board state. It should usually run 70–170 words and must be written individually rather than produced from a shared prose skeleton.

Within each fifty-card wave, do not repeat the normalized first six words and use no more than one stock memory cue such as “I remember,” “I still remember,” or “There I was.” Do not append an explanation of what the story meant.

## Historical grounding

Ground tournament-card vignettes in an exact historical Deck Archive registration whenever possible. Verify period legality, mana, timing, archetype, and matchup. A representative recollection must not be presented as a quotation from a named real player or as documented match play unless a source proves that sequence.

When no suitable tournament registration exists, use a period-appropriate kitchen-table game, official preconstructed deck, Limited environment, Commander table, or famous rules interaction, while remaining concrete and plausible.

## Read-time standard

Read time is derived from continuous editorial prose at **200 words per minute**. Exclude decklist rows, printing-gallery records, source-list records, hidden metadata and copy buffers, scripts, styles, controls, and collapsed interface material. Never hard-code “20 minute read.” Do not pad articles to reach a target length.

## Layout and archive rules

- Official Magic product text requires shared CSS plus inline critical contrast.
- Sources remain ordinary readable lists, never printing-gallery grids.
- Each page gets one Continue Reading block outside article content, notes, and Sources.
- Design Echo headings and comparison art must be card-specific and correct.
- Preserve genuine tournament registrations and official Wizards product decks.
- Never invent tournament registrations.
- Label representative and curated constructions clearly.
- Do not shorten strong existing articles or expose internal editorial workflow labels.

## Important files

Read these before editing:

1. `READER-V3.1-CURRENT-HANDOFF-2026-08-05.md`
2. `READER-V3.1-START-HERE-2026-08-05.md`
3. `CURRENT-STATE.json`
4. `canonical/READER-FACING-EDITORIAL-POLICY.md`
5. `canonical/EDITORIAL-V2-CONTRACT.md`
6. `canonical/GENERATION-PROMPT.md`
7. `canonical/DECK-ARCHIVE-CONTRACT.md`
8. `templates/article-shell.html`
9. `templates/honorable-article-shell.html`
10. `tools/validate_reader_experience_v3.py`
11. `tools/validate_reader_layout_contract.py`
12. `tools/apply_reader_v31_entries_011_050.py` as an implementation record, not a generic story generator

Use entries 001–010 as the primary pilot, entries 011–050 as the completed first-wave corpus, and the four supplementary articles as additional structural examples.

## Validation commands

After every internal ten-card group:

```bash
python tools/validate_reader_experience_v3.py
python tools/validate_reader_layout_contract.py
python tools/run_validation_suite.py --quick
```

Before final packaging:

```bash
python tools/run_validation_suite.py --refresh-v2
python tools/run_validation_suite.py --full
```

Do not claim a pass that did not complete. Structural validation is not a substitute for reading every new story for repetition, rules errors, historical implausibility, or generic phrasing.

## Post-wave correction — Hypnotic Specter

`024-hypnotic-specter.html` was corrected after reader review. Its headline now describes random discard rather than a nonexistent draw-step effect, and its story now uses a legal, explicitly ledgered 1994 turn sequence. Reader V3.1 validation now rejects unsupported primary mechanics claims and validates accelerated-opening land chronology. See `READER-V3.1-HYPNOTIC-SPECTER-CORRECTION-REPORT-2026-08-05.md`.
