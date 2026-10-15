# Reader V3.1 — Hypnotic Specter correction

**Date:** August 5, 2026  
**Article:** `024-hypnotic-specter.html`

## Reader-facing correction

- Replaced the inaccurate headline **“The Creature That Stole the Next Draw”** with **“The Creature That Made Every Hit a Gamble.”** Hypnotic Specter does not affect the draw step; combat damage causes a random discard from the opponent’s existing hand.
- Rewrote **A story from the table** from scratch. The new story uses a legal turn sequence grounded in `Bo Bell — Mind Twist Control`:
  - speaker turn one: Underground Sea, Mox Sapphire, Black Lotus, Hypnotic Specter;
  - opponent turn one: Tundra;
  - speaker turn two: Island, Specter combat trigger discards Wrath of God, Mox Sapphire casts The Rack;
  - opponent turn two: Plains and Swords to Plowshares; Underground Sea plus Island cast Counterspell;
  - speaker turn three: Hypnotic Specter attacks again.
- The story title is now **“The die found Wrath.”**
- Read time remains **approximately 19 minutes**, derived from 3,692 editorial words.

## Validation changes

- `tools/validate_reader_experience_v3.py` now rejects direct headline mechanics claims unsupported by the displayed rules text.
- Accelerated stories that act before the opponent’s first turn and continue into later turns must include hidden `.vignette-sequence-data` JSON.
- The sequence validator checks active-player turn order, one land drop per turn unless an allowance is declared, visible land-name binding, and agreement with explicit turn references.
- `tools/test_reader_experience_v3_regressions.py` proves that both rejected Hypnotic Specter versions fail and that the corrected sequence passes.
- The generation prompt, Reader-facing policy, Editorial V2 contract, and repeatable article-generation scripts were updated so rerunning production cannot restore the bad headline or story.

## Validation result

- Reader Experience V3 regression tests: **PASS**
- Reader Experience V3 corpus: **54/54 PASS**
- Reader layout contract: **PASS**
- Quick constituent checks: **10/10 PASS**
- Refresh-V2 constituent checks: **9/9 PASS**
- Full bounded constituent checks: **11/11 PASS**
- Release corpus SHA-256: `d874a46b242050c684a1ed42ae46813f7a3029b12da40a7f036bd4b8db59a68f`

The Python suite wrapper repeatedly stalled while launching its final subprocess in this container. Every constituent command was run directly in the required order and passed; the direct-run summaries are retained under `audit/handoff-validation/20260805T154859Z-*-direct/`.
