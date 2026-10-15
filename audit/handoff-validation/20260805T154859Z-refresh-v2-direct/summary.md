# Validation run — refresh-v2-direct

- Status: **PASS**
- Passed: **9/9**
- Failed: **0**

The suite runner repeatedly stalled while launching its final subprocess in this container. Each constituent command was therefore executed directly, in the same order, and passed. This is an execution-environment runner issue, not a validator or corpus failure.

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `python tools/validate_editorial_quality.py --output-dir audit/editorial-v2` |
| 2 | PASS | `python tools/validate_canonical_identity.py --output-dir audit/canonical-identity-v2` |
| 3 | PASS | `python tools/validate_deck_semantics.py --output-dir audit/deck-semantics` |
| 4 | PASS | `python tools/validate_archive_core_v2.py --output-dir audit/archive-core-v2` |
| 5 | PASS | `python tools/validate_historical_decks_only.py` |
| 6 | PASS | `python tools/validate_deck_archives.py --jobs 4 --output-dir audit/deck-archives` |
| 7 | PASS | `python tools/validate_official_mtg_decks.py --jobs 4 --output-dir audit/official-mtg-decks` |
| 8 | PASS | `python tools/validate_card_image_links.py --jobs 4 --output-dir audit/card-image-links` |
| 9 | PASS | `python tools/stamp_release_v2_state.py` |
