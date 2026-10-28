# Reader V3.1 — 062 The Tabernacle at Pendrell Vale, individual candidate (October 27, 2026)

## Authority and scope

**Starting main:** `7cfcdccc60381e5579cad31e9731fc45c8ebfffd` (accepted Reader checkpoint through 060; independently reviewed Maze 061 candidate merged). This is a **single-article candidate for 062**, not an accepted ten-article 061–070 checkpoint. No previous Reader articles, honorable mentions or other game projects are within this change. Only `062-the-tabernacle-at-pendrell-vale.html` is changed among production article HTML; its landing/return/navigation and embedded existing deck archive remain intact.

**Completion accounting:** full-project **51/100 accepted weighted points** and Reader first 100 **60/100 accepted**. Neither changes merely because article 062 now has a sourced candidate. Next individual article **063 — Moat**, with 061/062 preserved for batch review.

## Original printing and exact card wording

- **First printed:** `Legends`, June 1, 1994, collector number 307, illustrator **Nicola Leonard**. [Original card and Oracle record](https://mtg.wtf/card/leg/307/The-Tabernacle-at-Pendrell-Vale).
- **Type:** legendary land, with no mana ability. Its Oracle text grants each creature its own **beginning-of-its-controller's-upkeep** triggered ability to be destroyed unless that creature's controller pays **{1}**.
- **Correct distinctions:** The Tabernacle does not tap to impose the upkeep tax. The creature's controller pays, not the opposing land's controller. Nonpayment **destroys** that creature rather than sacrificing it. Each separate creature trigger must resolve; players may use available mana and order their triggers accordingly. Already-triggered abilities are not erased by removing the land. These are rules consequences, not claims of a video-recorded tournament play. [Magic comprehensive rules](https://magic.wizards.com/en/rules).

## Dated deck evidence

- **2015 Grand Prix Seattle-Tacoma — Legacy Champion Jarvis Yu, Lands.** The historical registration had **one Tabernacle**, four `Crop Rotation`, four `Wasteland`, four `Rishadan Port`, four `Life from the Loam`, three `Maze of Ith`, and the `Dark Depths` + `Thespian's Stage` win package. [Event and complete deck](https://www.mtgtop8.com/event?e=10859&f=le).
- **2015-12-02 primary account:** Jarvis Yu's [Legacy Lands Primer](https://www.coolstuffinc.com/a/jarvisyu-120115-legacy-lands-primer) records his own strategic reasoning. Distinguish his proposed later list from the registered Grand Prix version rather than silently combining their card counts.
- **Contemporary final recap:** [Jarvis Yu Lands a Legacy Trophy](https://www.coolstuffinc.com/a/news-11082015-jarvis-yu-lands-a-legacy-trophy-at-grand-prix-seattle-tacoma/) reports Tabernacle mattered decisively in the first game of the final. The new story **does not purport to replay that game** or reproduce its exact board.

## Reader V3.1 conversion

The new opening includes the original-card artwork and rules introduction followed by a first-person representative **Lands-versus-Grixis Delver reconstruction**, with the **exact Deck Archive title** `Jarvis Yu — Lands` and an explicitly 2015-era card pool. The narrator taps `Forest` for {G} and sacrifices it to cast `Crop Rotation`, finds `The Tabernacle at Pendrell Vale`, then faces an opposing `Delver of Secrets`, `Young Pyromancer`, and two Elemental tokens. With two available mana-producing lands, the opponent can fund only two of the four creatures; their tokens are destroyed upon unpaid upkeep triggers.

The hidden mana ledger records precisely one `Crop Rotation` {G} payment from a `Forest`. **The Tabernacle is not incorrectly treated as an activated ability.** The visible story does not claim to quote Jarvis Yu or Christian Calcano, does not name an actual opponent, and does not attribute the imagined token count to tournament coverage. An individual review in `research-dossiers/reader-v31-061-070/062-review.json` documents the turn and payment arithmetic.

Editorial rewriting replaces inherited generic origin/history/format/technical/memory prose with 062-specific material, clarifies actual tournament evidence, and preserves the prior deck-archive body. The article receives Reader CSS, story placement, proper heading/TOC labels, and machine-derived read-time metadata.

## Validation and outstanding acceptance

`tools/validate_reader_062_candidate.py` is the focused read-only validation with a one-time `--apply` generator to derive the story JSON, editor words/read-time and SHA-256 record. The general Reader V3.1 validator, full V2 fingerprint refresh, full release/navigation and desktop/mobile browser checks remain required.

**Do not mark any suite successful until its GitHub Actions run has concluded.** Actual candidate metrics and successful workflow URLs are recorded after passing CI, not guessed.

Remaining gates: independently verify inherited secondary archival registrations and deeper article claims; convert 063–070 with story/dossier/sources; create and validate a single 061–070 checkpoint, update migration ledger and accepted Reader progress only after full signed-off QA. The inherited site-wide research warnings remain open.

## Verified production candidate metrics and release validation

The [October 27 successful full refresh run](https://github.com/Diabolicdonut/Compulsive-Research/actions/runs/40605584478) completed the individual 062 metadata derivation, both 061/062 candidate validators, roadmap consistency, quick suite, refreshed V2 report and release fingerprint, full release suite, internal navigation, and prior 051–060 checkpoint validation. Its temporary write-enabled workflow is removed before the PR is eligible for merge.

- **Article 062:** 3,391 derived editorial words; **17-minute read** at 200 words/minute.
- **First-person reconstructed scene:** 98 words, source-bound to exact Deck Archive title `Jarvis Yu — Lands`.
- **Source evidence:** five individually scoped claims with links.
- **Final article SHA-256:** `a5ce21e2ee1f88ee606c17131d35ca4663a35a3f070d7c4813b020dd14e37e74`.
- Generated records: `research-dossiers/reader-v31-061-070/062-story-candidate.json` and `validation/reader-v3.1-062-candidate-metrics.json`.

Normal PR CI must still pass the complete desktop/mobile browser and release checks before merge. These results are **single-page candidate evidence**, not ten-article batch acceptance; the accepted 051–060 Reader and project weights are unchanged.

## Exact next action

Begin **063 — Moat**, preserving the accepted 001–060 checkpoint and the individual 061/062 candidates. Keep the authoritative roadmap, current state and site-progress manifest in sync.
