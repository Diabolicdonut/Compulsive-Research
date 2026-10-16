# Validation run — refresh-v2

- Status: **FAIL**
- Passed: 4
- Failed: 1
- Skipped: 0

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/validate_editorial_quality.py --output-dir audit/editorial-v2` |
| 2 | PASS | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/validate_canonical_identity.py --output-dir audit/canonical-identity-v2` |
| 3 | PASS | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/validate_deck_semantics.py --output-dir audit/deck-semantics` |
| 4 | PASS | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/validate_archive_core_v2.py --output-dir audit/archive-core-v2` |
| 5 | FAIL | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/validate_historical_decks_only.py` |
