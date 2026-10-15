COMPULSIVE RESEARCH — EDITORIAL V2 FOUNDATION — AUGUST 2, 2026

Extract all three release ZIPs into the same folder and merge their contents. Keep index.html at the project root. The deploy root contains 1,000 numbered articles and 505 active Honorable Mentions; retired numbered Honorable Mention duplicates are no longer included.

This release preserves the Eternal Dragon visual/component authority while adding separate Editorial V2 research, evidence, canonical-identity, and deck-semantics contracts. It removes 4,681 synthetic editorial-study decks, repairs false promotional debut records, normalizes regular debut printings, removes obsolete missing-script references, and adds corpus-fingerprinted validation.

Validation:
  python tools/run_validation_suite.py --quick
  python tools/run_validation_suite.py --refresh-v2   (after article-content changes)
  python tools/run_validation_suite.py --full

The full command verifies that the committed passing reports match the exact current corpus.

Important: this is an infrastructure and truthfulness migration, not a claim that all articles have already received bespoke research rewrites. data/editorial-status.json records 3 benchmarks, 903 audit-required pages, and 599 rewrite-required pages.

Read PROJECT-HANDOFF.md, VALIDATION-SUITE.md, and the contracts under canonical/ before editing.
