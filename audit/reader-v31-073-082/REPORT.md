# Reader V3.1 candidates 073–082 — October 28, 2026

## Recovery and acceptance boundary

Source of truth was GitHub `main` `91a652760c12b753a80d226ffc79f355638d446e`, with successful archive and Pages workflows, 1,000 numbered articles plus 505 canonical Honorable Mentions, and last formally accepted Reader checkpoint **051–060**. Existing standalone 061–072 candidate work is preserved.

The user requested the next ten articles after 072. Exact scope: **073 Ali from Cairo, 074 Drop of Honey, 075 Old Man of the Sea, 076 Serendib Efreet, 077 Su-Chi, 078 Triskelion, 079 Tetravus, 080 Atog, 081 Ornithopter, 082 Feldon's Cane**. No other article HTML should change.

## Independently differentiated instructional scenes

| Article | Date-specified reference | Gameplay point |
|---|---|---|
| 073 Ali from Cairo | Explicitly authored 1994 casual red-control deck, **not** historical registration | Juggernaut deals five combat damage while Ali's replacement effect keeps 3-life controller at 1. Ali does not prevent damage or loss of life effects. |
| 074 Drop of Honey | Odd Anders Kjostvedt U/G Control (2023 Old School) | Kird Ape and Savannah Lions tie at power two, controller chooses one untargeted upkeep destruction; the other survives. |
| 075 Old Man of the Sea | Zak Dolan U/W/G Stasis archival 1994 card pool | Old Man taps to take 2-power Ape, optional not-untap retains control; increasing Ape's power or untapping Old Man ends it. |
| 076 Serendib Efreet | Brian Fisher American Weenie, 2015 Old School archive | One self-damage upkeep trigger then three flying damage in combat, with original blue identity separated from the green Revised printing error. |
| 077 Su-Chi | Curated Old School Workshop Prison list (not tournament) | Opponent uses **Disenchant** (not Terror, which cannot target artifact creatures) during active player's main phase; death trigger produces four colorless spent on Juggernaut, with pre-2009 mana-burn context. |
| 078 Triskelion | Antonino De Rosa Mono-Blue Tron archival 2005 deck | Three counters make Triskelion 4/4; removing two counters destroys two 1/1s and leaves 2/2. |
| 079 Tetravus | Curated Workshop Prison model | Remove two of three +1/+1 counters at upkeep, create two 1/1 flying tokens and leave a 2/2 flyer; no instant-speed reassembly. |
| 080 Atog | Kamiel Cornelissen 2004 Worlds archive | Sacrificing Frogmite and Seat of the Synod pumps 1/2 to 5/6 during combat for five lethal damage; no bonus land drop. |
| 081 Ornithopter | Ben Stark 2004 Pro Tour Kobe Affinity archive | Two artifact lands plus resolved zero-mana Ornithopter reduce Frogmite from {4} to {1}; tapping an artifact land does not stop its affinity count. |
| 082 Feldon's Cane | Matt Place 1996 Turbo Stasis archival list | Exile Cane as tap-activation cost, then shuffle controller's graveyard into library; no immediate bonus draw and Cane itself does not return. |

Each article uses an original **first-person representative reconstruction**, with an exact documentary Deck Archive title where available and a detailed no-false-attribution source review. The source check is scoped to original printing, artist, dated modern rulings and exact mechanics. Historical deck provenance inherited from the old V2 articles is **not automatically verified by a card's printing record**. Such deck-list URLs are explicitly marked as archive references with further event verification needed.

## Development artifacts

- `research-dossiers/reader-v31-073-082/editorial-candidates.json`: ten specific scenes, literal dates and era, exact deck reference, mechanics, source identities and manual payment review.
- `tools/prepare_reader_073_082.py`: generates only the ten specified pages plus source-scoped research/scene records, story-ledger candidates, reading times and hashes, and checks all ten.
- `validation/reader-v3.1-073-082-candidate-metrics.json`: derived exact editorial word counts, 200-wpm estimates, unique story lengths, source counts and SHA-256 checksums.
- Ten per-article `NNN-story-candidate.json` and `NNN-review.json`, retaining the full manuscript source.
- `audit/reader-v31-061-070/ACCEPTANCE-AUDIT.md`: separate structured review of the previously outstanding wave. Formal wave promotion is **blocked** by historically unbound source claims.

## Acceptance restrictions

The prepared articles cross wave boundaries: 073–080 belongs to the **071–080** acceptance unit, while 081–082 begins **081–090**. They cannot be accepted as a stand-alone mixed ten-page batch merely because the implementation is complete. In particular, the earlier 061–070 wave still has inherited historical claim/provenance blockers.

The full corpus must remain **1,505 active pages**. All existing 001–072 accepted and candidate HTML remains unchanged. Validate schema, Reader V3.1 stories, historic deck archive totals, navigation, fingerprinted full release and desktop/mobile browser appearance. Publication requires normal green PR CI; the special write-enabled workflow is removed before merge.

Current accepted status remains **60/100 initial Reader** and **51/100 weighted overall**. Next untouched article is **083 Millstone**. The highest-priority next *acceptance* milestone is completing the old 061–070 full historical source audit.
