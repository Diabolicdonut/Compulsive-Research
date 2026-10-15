# Reader V3.1 exact ten-card checkpoint replay

These reports were reproduced from the untouched uploaded Reader V3.1 source ZIP. The final migration tool was applied cumulatively in the required ranges, and after each range the exact three requested commands were run:

1. `python tools/validate_reader_experience_v3.py`
2. `python tools/validate_reader_layout_contract.py`
3. `python tools/run_validation_suite.py --quick`

The replay isolates the 011–020, 021–030, 031–040, and 041–050 project states. It does not replace the final archive-wide `--refresh-v2` and `--full` release runs.
