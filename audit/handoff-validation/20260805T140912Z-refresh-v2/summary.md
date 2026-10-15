# Validation run — refresh-v2

- Status: **PASS**
- Passed: 9
- Failed: 0
- Skipped: 0

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `/opt/pyvenv/bin/python tools/validate_editorial_quality.py --output-dir audit/editorial-v2` |
| 2 | PASS | `/opt/pyvenv/bin/python tools/validate_canonical_identity.py --output-dir audit/canonical-identity-v2` |
| 3 | PASS | `/opt/pyvenv/bin/python tools/validate_deck_semantics.py --output-dir audit/deck-semantics` |
| 4 | PASS | `/opt/pyvenv/bin/python tools/validate_archive_core_v2.py --output-dir audit/archive-core-v2` |
| 5 | PASS | `/opt/pyvenv/bin/python tools/validate_historical_decks_only.py` |
| 6 | PASS | `/opt/pyvenv/bin/python tools/validate_deck_archives.py --jobs 4 --output-dir audit/deck-archives` |
| 7 | PASS | `/opt/pyvenv/bin/python tools/validate_official_mtg_decks.py --jobs 4 --output-dir audit/official-mtg-decks` |
| 8 | PASS | `/opt/pyvenv/bin/python tools/validate_card_image_links.py --jobs 4 --output-dir audit/card-image-links` |
| 9 | PASS | `/opt/pyvenv/bin/python tools/stamp_release_v2_state.py` |
