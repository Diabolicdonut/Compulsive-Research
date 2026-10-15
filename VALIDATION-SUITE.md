# Compulsive Research Validation Suite — Editorial V2

The release now separates fast release verification, report regeneration, and retained legacy migration audits.

## Runtime requirements

- Python 3.12 or later
- Python packages from `requirements.txt`
- Node.js only for retained printing-gallery regression tests in the legacy-exhaustive mode

```bash
pip install -r requirements.txt
```

## Standard commands

### Focused structural check

```bash
python tools/run_validation_suite.py --quick
```

Checks the Eternal Dragon lock, rebuilds the manifests, resolves local assets, confirms that no synthetic `editorial-study` decks remain, and validates the active Honorable Mention architecture.

### Regenerate Editorial V2 reports

Run this after changing article HTML, canonical card data, editorial statuses, or the V2 schemas:

```bash
python tools/run_validation_suite.py --refresh-v2
```

This regenerates:

1. Editorial specificity and duplication audit
2. Canonical first-printing identity validation
3. Deck-semantic and provenance validation
4. Fast archive-core validation
5. Documentary-deck validation
6. Official Wizards product-deck validation
7. Deck-row card-image validation
8. Corpus fingerprint and report hashes

The resulting state is stored in:

```text
audit/release-v2-validation-state.json
```

### Complete release verification

```bash
python tools/run_validation_suite.py --full
```

The full release command runs the quick checks and verifies that every committed passing V2 report is bound to the exact current article corpus. Any article or schema change invalidates the fingerprint until `--refresh-v2` is run again.

### Retained legacy migration audits

```bash
python tools/run_validation_suite.py --legacy-exhaustive
```

This additionally invokes older migration-era hero, headline, artwork, Design Echo, printing-gallery, card-reference, and all-purpose archive checks. These tools are retained for targeted regression investigation, but some encode superseded assumptions—such as obsolete external JavaScript shims—and are not the primary Editorial V2 release gate.

### Bounded audit stages

When a long command exceeds the execution window, run consecutive inclusive stage ranges and preserve every summary. For example:

```bash
python tools/run_validation_suite.py --legacy-exhaustive --stage-start 10 --stage-end 14
python tools/run_validation_suite.py --legacy-exhaustive --stage-start 15 --stage-end 19
```

The JSON summary records the original stage numbers, total planned stages, and `partialRun: true`; a successful subset is labeled `PARTIAL_PASS`, never a full-suite pass. Do not rerun report stamping or claim full release verification from a selected range. The full release gate remains `--refresh-v2` followed by `--full` on the final corpus.

## Primary V2 validators

```bash
python tools/validate_editorial_quality.py --output-dir audit/editorial-v2
python tools/validate_canonical_identity.py --output-dir audit/canonical-identity-v2
python tools/validate_deck_semantics.py --output-dir audit/deck-semantics
python tools/validate_archive_core_v2.py --output-dir audit/archive-core-v2
python tools/validate_historical_decks_only.py
python tools/validate_deck_archives.py --jobs 4 --output-dir audit/deck-archives
python tools/validate_official_mtg_decks.py --jobs 4 --output-dir audit/official-mtg-decks
python tools/validate_card_image_links.py --jobs 4 --output-dir audit/card-image-links
python tools/stamp_release_v2_state.py
python tools/verify_release_v2_state.py
```

## What a passing result means

A pass establishes that:

- The release package is structurally coherent.
- Canonical numbered-card identity matches the committed snapshot.
- No synthetic study decks remain in production.
- Documentary deck totals and official-product records are internally consistent.
- Every visible deck row is connected to the card-preview system.
- Editorial warnings and rewrite statuses are recorded rather than hidden.
- The validation reports match the exact current corpus.

A pass does **not** mean every historical claim has already received human review. The editorial audit intentionally preserves warnings for duplicated prose, thin source lists, unbound deck sources, and other research debt. Consult `data/editorial-status.json` and `audit/editorial-v2/` before promoting an article to `reviewed`.

## Current release baseline

The August 2, 2026 Editorial V2 foundation release records:

- 1,000 numbered articles passing canonical-identity validation
- 1,505 active articles passing archive-core validation
- 1,557 documentary deck components passing deck-archive validation
- 8,252 official-product deck appearances matching the committed catalogue
- 438,171 visible deck rows linked to card previews
- 0 production `editorial-study` deck components
- 0 unresolved local asset references
- corpus fingerprint `d4ecaa3ec8a3af7f61e7bc46507bb969b8e25b279ca586a4fbdd77992387d5dc`

### Reader layout contract

```bash
python tools/validate_reader_layout_contract.py
```

This verifies opening-before-strategy order for processed waves, one end-navigation block outside article content, card-specific Design Echo headings, proper source-list geometry, historically pinned Arcane Signet comparison art, and high-contrast official-product CSS. It is part of the quick suite.

### Reader Experience V3 staged migration

```bash
python tools/validate_reader_experience_v3.py
```

This validator checks only pages declaring `data-reader-experience="v3"`, allowing the archive to migrate in approved batches. It verifies a card-first opening, one classic-play vignette, Strategic Legacy placement, nonduplicative opening/strategy language, derived read time at 200 words per minute, and inline critical contrast for official Magic product sections. It is part of the quick suite.
