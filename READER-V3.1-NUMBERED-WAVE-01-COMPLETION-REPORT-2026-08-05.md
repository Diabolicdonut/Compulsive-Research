# Compulsive Research — Reader V3.1 Numbered Wave 1 Completion Report

**Date:** August 5, 2026  
**Completed range:** Entries 011–050, Lightning Bolt through Stasis  
**Resulting Reader V3.1 numbered range:** Entries 001–050

## Work completed

Forty existing long-form articles were retrofitted to Reader V3.1 without replacing the project, rebuilding from an older package, or shortening their established editorial bodies. Their genuine tournament Deck Archives and official Wizards product records were preserved.

Each page now places its card image, rules identity, original printing context, and framing before a single first-person vignette labeled exactly **A story from the table**. Strategic Legacy immediately follows the completed opening. Visible era, matchup, source-deck, and reconstruction captions remain suppressed; those facts are retained as hidden metadata and in the editorial story ledger.

## Story research and presentation

- 40 individually written stories
- 40 unique normalized six-word openings
- 0 stock memory-cue openings in entries 011–050
- 40 exact hidden Deck Archive references found in the corresponding source pages
- All stories presented as representative recollections rather than attributed quotations or claimed documentary play-by-play
- Story titles, game states, card names, mana, sequencing, attacks, and stack interactions reviewed individually

The exact story records are in `research-dossiers/READER-V3.1-NUMBERED-WAVE-01-STORY-LEDGER.json`.

## Read-time and structure

The forty articles contain 135,275 words of continuous editorial prose. Derived read times range from 15 to 21 minutes at 200 words per minute. Deck rows, printing records, Sources, hidden metadata, scripts, styles, and interface controls are excluded.

Entry 022, Serra Angel, lacked the required Strategic Legacy section in its inherited structure. A card-specific section was added after the opening so the page now follows the Reader V3.1 order. No other article was shortened to satisfy the retrofit.

## Review files

- `READER-V3.1-ENTRIES-011-050-REVIEW-INDEX.html`
- `READER-V3.1-MIGRATION-LEDGER.json`
- `validation/reader-v3.1-entries-011-050-metrics.json`
- `validation/reader-v3.1-entries-011-050-metrics.md`

## Validation

Final Reader V3.1 experience and layout validators pass the completed corpus. The archive-wide `--refresh-v2` run passed all 9 stages, and the bounded `--full` release run passed all 10 stages against corpus SHA-256 `15f0b1c2a39d8010f320bfa6b5742e7db5698b8cdfab688826b7a18ef916cc0b`.

The retained deck-semantics warning queue is unchanged from the uploaded source project and is documented in `validation/reader-v3.1-unresolved-warnings.md`. None of those warnings is a Reader V3.1 structural failure, and none of the five monobasic-color warnings occurs in entries 011–050.

## Next task

Retrofit entries 051–100, Juzám Djinn through Ivory Tower, in five internal ten-card checkpoints and return one merged fifty-article package.

## Post-delivery correction — Hypnotic Specter

Reader review identified an inaccurate draw-related headline and an impossible two-land early-game sequence in entry 024. Both were replaced, generation sources were corrected, and regression validation was added. The corrected release corpus is `d874a46b242050c684a1ed42ae46813f7a3029b12da40a7f036bd4b8db59a68f`.
