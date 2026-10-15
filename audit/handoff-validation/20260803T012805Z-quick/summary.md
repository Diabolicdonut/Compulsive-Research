# Validation run — quick

- Status: **PASS**
- Passed: 7
- Failed: 0
- Skipped: 0

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `/opt/pyvenv/bin/python tools/check_canonical_lock.py` |
| 2 | PASS | `/opt/pyvenv/bin/python tools/build_manifest.py` |
| 3 | PASS | `/opt/pyvenv/bin/python tools/validate_local_assets.py` |
| 4 | PASS | `/opt/pyvenv/bin/python tools/validate_no_reader_facing_editorial_labels.py` |
| 5 | PASS | `/opt/pyvenv/bin/python tools/remove_editorial_study_decks.py --check` |
| 6 | PASS | `/opt/pyvenv/bin/python tools/validate_honorable_template.py` |
| 7 | PASS | `/opt/pyvenv/bin/python tools/validate_honorable_categories.py` |
