# Validation run — quick

- Status: **FAIL**
- Passed: 5
- Failed: 1
- Skipped: 0

| # | Status | Command |
|---:|:---:|---|
| 1 | PASS | `/opt/pyvenv/bin/python tools/check_canonical_lock.py` |
| 2 | PASS | `/opt/pyvenv/bin/python tools/build_manifest.py` |
| 3 | PASS | `/opt/pyvenv/bin/python tools/validate_local_assets.py` |
| 4 | PASS | `/opt/pyvenv/bin/python tools/validate_no_reader_facing_editorial_labels.py` |
| 5 | PASS | `/opt/pyvenv/bin/python tools/validate_reader_layout_contract.py` |
| 6 | FAIL | `/opt/pyvenv/bin/python tools/validate_reader_experience_v3.py` |
