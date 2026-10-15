# Validation run — quick-direct

- Status: **PASS**
- Passed: **10/10**
- Failed: **0**

The suite runner repeatedly stalled while launching its final subprocess in this container. Each constituent command was therefore executed directly, in the same order, and passed. This is an execution-environment runner issue, not a validator or corpus failure.

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `python tools/check_canonical_lock.py` |
| 2 | PASS | `python tools/build_manifest.py` |
| 3 | PASS | `python tools/validate_local_assets.py` |
| 4 | PASS | `python tools/validate_no_reader_facing_editorial_labels.py` |
| 5 | PASS | `python tools/validate_reader_layout_contract.py` |
| 6 | PASS | `python tools/test_reader_experience_v3_regressions.py` |
| 7 | PASS | `python tools/validate_reader_experience_v3.py` |
| 8 | PASS | `python tools/remove_editorial_study_decks.py --check` |
| 9 | PASS | `python tools/validate_honorable_template.py` |
| 10 | PASS | `python tools/validate_honorable_categories.py` |
