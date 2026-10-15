# Accepted Reader V3.1 recovery — October 15, 2026

The feature branch starts at cleanup commit `26f8970c34d5ce9dbc427eb93ef1795b7a36668a`, reviewed with Issue #2. It imports all 2,376 files from the accepted Audit Checkpoint and retains the repository's `AGENTS.md` and `README.md`. No retired `honorable-NNN-*.html` pages are present. Generated Python caches are ignored.

## Recovery evidence

- Source ZIP SHA-256: `cb3d21844b00451ce9aabae7fe2003dffdf5ce4ce6b936b43bdf222bb43226d4`.
- Every `modified` and `added` record in `CHECKPOINT-01-MANIFEST.json` matches the source bytes.
- A later-uploaded correction-handoff ZIP was inspected (`ac342767df294e8324cf21b5037a34e874d2b585f51fad5766a7f32357ecac5b`). It is an older content snapshot: it reverts the 13 accepted article repairs and the improved validators. It was not substituted for the verified checkpoint. Upload time alone does not establish editorial precedence.
- All 1,505 article files and `index.html` match the accepted source byte-for-byte except the narrowly documented navigation repair below. The Eternal Dragon benchmark and all accepted September prose corrections are preserved.
- Hypnotic Specter's headline remains **The Creature That Made Every Hit a Gamble**, with its corrected turn sequence and regression guards.

## Navigation repair and validation

Entry 201, Rishadan Port, lacked its previous-entry control in the bottom navigation. The missing link to entry 200 was restored from the manifest without changing article prose or decks. `tools/validate_internal_navigation.py` detects that original failure and verifies the repaired corpus. It accepts both direct article links and landing-row navigation, while checking their destination against the manifest.

The final check covers 1,506 pages, **31,781 local links**, exactly 1,000 numbered articles, 505 canonical Honorable Mentions, and all 22 categories: **zero failures**. See `navigation.json`.

## Release validation

- Quick: **10/10 PASS**, `audit/handoff-validation/20261015T201316Z-quick/summary.md`.
- Refresh after the navigation repair: **9/9 PASS**, `audit/handoff-validation/20261015T201714Z-refresh-v2/summary.md`.
- Full release: **11/11 PASS**, `audit/handoff-validation/20261015T201920Z-full/summary.md`.
- Reader V3.1 corpus: **54 pages PASS**; regression and layout checks pass.
- GitHub Actions repeats the full release and complete navigation checks, then exercises article rendering and return-row visibility at 1440px and 390px. Browser dependency installation is performed on the runner because this workspace has no usable Chromium binary. External artwork is stubbed in that test; live image delivery is outside its claim.
- `lxml`, already required by the existing validators, is now explicitly declared alongside Beautiful Soup so a fresh Actions runner can reproduce validation.

## Known review queues retained

Deck semantics remain structurally passing with 1,440 cross-article deck-fingerprint warnings, 354 deck components lacking directly bound source URLs, and five monobasic-color warnings. The accepted audit's remaining legacy hero/title/artwork findings are retained. These have not been silently waived or described as corrected.

The accepted audit screened the 54 Reader V3.1 stories; it does not prove every historical assertion in the 1,505-page corpus. The prescribed next work remains entries **051–060**, followed by 061–070. Continue with manual rules/source review and small GitHub checkpoints.
