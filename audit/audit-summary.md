# Compulsive Research archive audit

## Scope

The validator inspected **408 article files**: 401 numbered articles and 7 honorable mentions.
The landing page contains 1,000 numbered records, but this project package currently contains numbered articles 001–400 plus entry 605. The 401–604 gap is therefore a publication-state fact, not automatically an article defect.

This is a mechanical audit. It does not certify historical claims, quotations, deck provenance, or source reliability.

## Classification

- **A — Compliant:** 264
- **B — Repairable:** 144
- **C — Rewrite required/candidate:** 0

Category C is reserved for severe structural failure or obviously incomplete length. A factual rewrite should never be ordered solely from this validator.

## Most common repair signals

- `LOW_CARD_LINK_COVERAGE` — 85 article(s)
- `END_NAV` — 51 article(s)
- `DECK_MAIN_TOTAL` — 23 article(s)
- `TOP_NAV` — 13 article(s)
- `DECK_SIDE_TOTAL` — 11 article(s)
- `NONCANONICAL_SOURCE_LIST` — 8 article(s)
- `SUBJECT_CARD_LINKED` — 6 article(s)
- `MISSING_PREVIEW` — 1 article(s)
- `NONCANONICAL_DECK_ID` — 1 article(s)
- `NONCANONICAL_PRINTINGS_ID` — 1 article(s)

## Canonical status

`250-eternal-dragon.html` is forced to Category A unless a severe structural failure is detected, because it is the frozen authority. Its exact snapshot and SHA-256 digest are stored in `canonical/`.

## Shared-asset migration

- Articles already using `assets/compulsive-research.css`: 0
- Articles already using `assets/compulsive-research.js`: 0
- Existing pages remain inline and unchanged in this freeze. Shared assets are established for future generation and controlled batch migration.

## Category C candidates

No article met the validator’s severe automatic rewrite threshold.

## Files

- `audit-report.csv` — sortable repair queue
- `audit-report.json` — complete machine-readable findings
- `representative-sample.md` — stratified 20-article mechanical sample

Run the audit again with:

```bash
python tools/build_manifest.py
python tools/validate_archive.py
```
