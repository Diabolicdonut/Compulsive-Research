# Compulsive Research — Editorial V2 Implementation Report

**Release:** `2026-08-02-editorial-v2-foundation`  
**Production corpus:** 1,000 numbered articles + 505 active Honorable Mentions  
**Canonical visual authority:** `250-eternal-dragon.html`

## Purpose

This release implements the project-level changes required to begin bringing the archive toward the historical specificity, cultural breadth, practical play guidance, and evidentiary standards demonstrated by **Eternal Dragon** and **Black Lotus**.

It does not claim that 1,505 articles have already been individually researched and rewritten. Instead, it removes known misleading generated material, corrects canonical data, introduces an enforceable Editorial V2 system, and records every remaining article’s research status.

## Archive-wide production changes

### Synthetic deck removal

- Removed **4,681** production components marked `editorial-study`.
- Production schemas no longer permit `editorial-study` as a deck kind.
- Decklists are now optional when no verified list is available.
- Articles without documentary lists receive a transparent open-research notice.
- Removed three additional study/comparator components that did not contain their article’s subject card.

### Canonical debut identity

- Repaired **78** false debut records caused by recurring promotional containers.
- Normalized **21** correct-set records from showcase/borderless treatments to the regular base printing.
- Corrected visible identity mismatches including Memory Lapse, Wildfire, Sakura-Tribe Elder, and Elvish Champion.
- Added a committed override file for legitimate promotional debuts.
- Canonical-identity validation now maps numbered articles by archive entry rather than assuming card names are unique.

### Asset and structural cleanup

- Removed **4,515** obsolete references to three absent JavaScript files.
- Preserved the canonical inline Artwork Spotlight, Design Echo, and Printing Gallery runtimes.
- Added the canonical Design Echo class to **172** legacy Honorable Mention sections.
- Normalized Rishadan Port’s legacy `#decks` and `#sources` IDs to `#decklists` and `#printings`.
- Excluded all 180 retired numbered Honorable Mention duplicates from the active release root.

### Editorial status

Every active page now carries separate machine-readable fields for:

- editorial contract;
- editorial status;
- research status.

Current queue:

| Status | Articles |
|---|---:|
| Benchmark | 3 |
| Reviewed | 0 |
| Audit required | 903 |
| Rewrite required | 599 |

The 599 continuation-generator pages remain explicitly identified as substantive rewrite work rather than being classified as complete merely because their HTML passes.

## New Editorial V2 contracts and schemas

Added:

- `canonical/EDITORIAL-V2-CONTRACT.md`
- `canonical/EVIDENCE-CONTRACT.md`
- `canonical/CANONICAL-IDENTITY-V2-CONTRACT.md`
- `canonical/DECK-SEMANTICS-CONTRACT.md`
- `templates/research-dossier-v2.schema.json`

Updated:

- `canonical/CANONICAL-CONTRACT.md`
- `canonical/GENERATION-PROMPT.md`
- `canonical/DECK-ARCHIVE-CONTRACT.md`
- numbered and Honorable Mention article schemas;
- numbered and Honorable Mention shell templates;
- the Eternal Dragon canonical snapshot and lock.

Editorial V2 explicitly models:

- article class;
- central thesis;
- canonical identity;
- original set and design context;
- lore scope and chronology;
- competitive timeline;
- card-specific playbook;
- card-specific counterplay;
- claim-to-source relationships;
- current-information review dates;
- research and editorial status.

## Generator policy

The metadata-only continuation generator is retired by default. It now refuses to generate production articles unless the legacy unsafe override is explicitly supplied.

Future generation requires a validated research dossier. The system may render reviewed research; it may not manufacture tournament history, quotations, deck provenance, lore, or strategic conclusions from card metadata alone.

## New and revised validators

Added or substantially revised:

- `validate_research_dossier.py`
- `validate_local_assets.py`
- `validate_canonical_identity.py`
- `normalize_canonical_debut_printings.py`
- `validate_deck_semantics.py`
- `validate_editorial_quality.py`
- `validate_archive_core_v2.py`
- `release_fingerprint.py`
- `stamp_release_v2_state.py`
- `verify_release_v2_state.py`

The validation model now separates:

1. visual and structural conformity;
2. canonical card identity;
3. deck arithmetic and provenance;
4. editorial specificity and duplication;
5. evidence signals;
6. research completeness;
7. exact release/report parity.

## Current validation results

| Validation | Result |
|---|---:|
| Canonical numbered identity | 1,000 PASS |
| Fast archive core | 1,505 PASS |
| Documentary deck archive | 1,135 article pages / 1,557 decks PASS |
| Official Wizards product decks | 1,505 pages / 8,252 appearances PASS |
| Card-image deck rows | 438,171 of 438,171 linked |
| Local asset resolution | PASS |
| Synthetic study decks remaining | 0 |
| Editorial audit hard failures | 0 |

The editorial audit intentionally retains warnings:

- 599 pages contain recognized generic dossier language;
- 1,230 pages exceed the exact-duplication warning threshold;
- 431 tournament registrations lack a machine-bound source URL;
- 333 deck fingerprints recur across unrelated article subjects and require later provenance review;
- five mono-basic mana configurations receive non-blocking review warnings.

These warnings are the rewrite and verification queue, not hidden failures.

## Release validation model

After changing article content or relevant schemas:

```bash
python tools/run_validation_suite.py --refresh-v2
```

This regenerates the V2 reports and binds them to the current corpus.

Before packaging or deploying:

```bash
python tools/run_validation_suite.py --full
```

The full release check verifies the quick structural suite and confirms that all passing reports match the exact corpus fingerprint.

Current fingerprint:

```text
d4ecaa3ec8a3af7f61e7bc46507bb969b8e25b279ca586a4fbdd77992387d5dc
```

## What remains

The system is now capable of preventing another metadata-dossier cohort, but the existing editorial debt still requires research.

Recommended migration order:

1. Rewrite the 599 `rewrite-required` pages in reviewed batches of 10–20.
2. Audit the 903 `audit-required` pages for missing lore, tournament chronology, play guidance, counterplay, and source quality.
3. Bind exact source URLs to the 431 unbound tournament components.
4. Investigate repeated documentary deck fingerprints rather than deleting them automatically; some repetition is historically legitimate when one deck demonstrates several cards.
5. Promote articles to `reviewed` only after human source and prose review.

The infrastructure migration is complete. The card-by-card scholarship remains a controlled editorial program rather than an automated bulk-generation task.
