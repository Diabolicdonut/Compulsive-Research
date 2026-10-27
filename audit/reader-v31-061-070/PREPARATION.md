# Reader V3.1 061–070 — mechanical integrity preparation (not an accepted Reader wave)

**Prepared:** October 27, 2026.  
**Starting accepted GitHub main:** `ebb25ec9d3230d4df297918da0e758b9b10b287b`.  
**Scope:** only numbered articles 061–070, project roadmap/status, this preparation report and narrowly targeted validation.  
**Status:** candidate rules/case-study corrections; **NOT** a completed ten-article Reader V3.1 checkpoint. `CURRENT-STATE.json` remains at accepted 051–060 with next article 061. Both published counters intentionally stay at **51/100 weighted overall** and **60/100 initial Reader**.

## Changes by card

| Entry | Review and newly installed teaching case | Source/rules focus |
|---:|---|---|
| 061 Maze of Ith | An untapped Serra Angel remains attacking and deals no damage after Maze; second Kird Ape still deals two; Maze cannot make mana | [Official Dominaria Remastered notes](https://magic.wizards.com/en/news/feature/dominaria-remastered-release-notes), and current [The Dark card](https://mtg.wtf/card/drk/117/Maze-of-Ith) |
| 062 The Tabernacle at Pendrell Vale | Four creatures, two lands, per-creature upkeep triggers, two paid and two destroyed | [Legends original wording](https://mtg.wtf/card?q=%21The+Tabernacle+At+Pendrell+Vale); not a tapped, activated, sacrifice or mana ability |
| 063 Moat | Kird Ape swarm cannot be declared as ground attackers; flying Serra Angel can attack; blocks aren't prohibited | Oracle attack restriction / documented flying exception |
| 064 Nether Void | A cast one-red-mana Bolt is countered by a subsequent {3}-payment trigger | [Legends ruling](https://mtg.wtf/card/leg/113/Nether-Void): not an additional casting cost, symmetric trigger |
| 065 The Abyss | Only one nonartifact creature is targeted and destroyed on the active player's upkeep | [Legends rulings](https://mtg.wtf/card/leg/120/The-Abyss): active player's choice, destruction, world supertype |
| 066 Land Tax | One Plains versus two Islands yields up to three basic lands in hand; no extra land drop | [Legends card and intervening-if ruling](https://m.mtg.wtf/card/leg/26/Land-Tax) |
| 067 Sylvan Library | Three cards drawn including normal draw; one returned and one kept by paying four life | [Legends card and drawn-this-turn rulings](https://mtg.wtf/card/leg/207/Sylvan-Library) |
| 068 Concordant Crossroads | Newly cast Llanowar Elves can tap for mana after haste is granted, but opposing creatures gain haste too | Legends card wording; symmetrical haste |
| 069 Eureka | Alternating passes do not end the spell until all players pass in sequence; entering isn't casting; triggers wait | [Legends original and rulings](https://mtg.wtf/card/leg/185/Eureka) |
| 070 Candelabra of Tawnos | Detailed High Tide {2} activation and six-blue-mana demonstration; explicitly historical Legacy scenario | [Antiquities card/rulings](https://www.mtg.wtf/card/atq/43/Candelabra-of-Tawnos) and [June 29, 2026 official Legacy ban](https://magic.wizards.com/en/news/announcements/banned-and-restricted-june-29-2026) |

All ten generic “Imagine a game in which neither player is dramatically ahead” case-study sections were replaced with differing card-specific sequences and explicit reconstruction disclaimers. The changes do not claim these hypothetical scenarios occurred in the real-world deck registrations appearing elsewhere on the pages. Existing deck archive content, images, sources, article navigation targets and the accepted prior waves were left intact.

## Integrity and progress accounting

- Source facts were checked against exact official/card rules where cited. Focused regression tests in `tools/validate_reader_061_070_mechanics.py` check the ten examples, high-risk misconceptions, and the 2026 legality update. Passing these tests would not validate all historical claims in the rest of the articles.
- The 1,505-article canonical count and 22 HM category structure are unchanged; the source archive should still be validated using the full navigation and release suites.
- **Gate:** `reader-061-100` is now **partial** in both `ROADMAP-COVERAGE.md` and `site-progress.json`. Partial gates contribute zero weighted points. This is not promotion of Reader acceptance: 061–070 still require official page conversion, meaningful first-person stories tied to matching cited deck lists, research-dossier schemas, complete article-level source review, editorial/read-time metrics and sign-off.
- **Prior accepted Reader:** 051–060, ten articles. **Next content work:** begin complete Reader V3.1 conversion of **061 Maze of Ith**, then the rest of 061–070, preserving these rules repairs.

## Remaining requirements before accepting 061–070

1. Complete research dossiers, exact original printing/artist/format checks, factual review of all article sections, dated tournaments, and sources that support each meaningful claim. Prior source lists containing generic archive homepages must be replaced with specific references when they support claims.
2. Create distinctive, representative **first-person** table stories in the opening of each article, using documented card pools and deck titles, with explicit era, matchup, scenario, paid mana and turn/board-state checks. The current case studies are an additional mechanical teaching section, **not a substitute** for the Reader V3.1 story contract.
3. Apply the Reader V3.1 layout and byline metadata; regenerate editorial word count/read times and 061–070 article/story ledgers, producing deterministic SHA-256 preservation records.
4. Run `python tools/run_validation_suite.py --quick`, refresh `--refresh-v2` after article content changes to regenerate reports and corpus fingerprint, then `--full`, full navigation, Reader checkpoint and desktop/mobile browser checks. CI must show actual results; **do not treat this preparation note as proof of release success**.
5. Only after full validated PR acceptance on main should `CURRENT-STATE.json`, `READER-V3.1-MIGRATION-LEDGER.json` and the published Reader count advance to **70/100** and the immediate next article become **071**. Overall weighted roadmap completion remains 51% until an accepted 12-point 061–100 gate (or explicitly approved subdivisions) qualifies it for an increase.

## Scope boundaries

No inherited deck warning queue is claimed resolved. No article outside 061–070 should change. Do not silently rewrite historical registrations, erase prior research, or update accepted publication revision while this remains a preparatory pass.
