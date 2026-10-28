# Reader V3.1 articles 063–072 — candidate implementation (October 27, 2026)

## Recovery and boundaries

Starting accepted GitHub `main` was **fa6614c838664dcbf8dbd53b114893c91c3e80c2**. Reader V3.1's *last formally accepted ten-article checkpoint* remains **051–060**, even though 061 and 062 were separately source-audited and merged.

User requested the **next ten articles** after 062. The exact existing archive sequence is **063 Moat; 064 Nether Void; 065 The Abyss; 066 Land Tax; 067 Sylvan Library; 068 Concordant Crossroads; 069 Eureka; 070 Candelabra of Tawnos; 071 Transmute Artifact; 072 Power Artifact**. No other numbered or Honorable Mention HTML is authorized to change.

## Scope of completed candidate pass

Each page has its own differentiated first-person Reader V3.1 vignette after the canonical card introduction, exact named Deck Archive binding, era/matchup and reviewed mechanics. There are no claims of historical eyewitness accounts, tournament match transcripts, or named player quotations.

| Entry | Scene, evidence and governing nuance |
|---:|---|
| 063 Moat | Brian Weissman — The Deck; counter a Disenchant, then non-flying Apes cannot attack. Moat restricts attack declaration, not blocking, damage or existing attackers. |
| 064 Nether Void | Reid Duke — Mono-Black Pox; Bolt cast for {R} triggers a separate counter-unless-pay-{3} ability. Nether Void is not a tax on the casting cost or on Factory's activated ability. |
| 065 The Abyss | Reid Duke — Mono-Black Pox; active player chooses one nonartifact creature for the enchantment-controller's upkeep trigger. Destroy, not sacrifice; no wholesale wipe. |
| 066 Land Tax | Michael Loconto — PT New York 1996; one Plains versus two Islands, three basic lands searched into *hand*, one later normal land play, intervening-if checks. |
| 067 Sylvan Library | Henry Stern — Vice Age; normal draw + 2 Library draws, return one/pay four life for the other, 12→8 life, two of three kept. |
| 068 Concordant Crossroads | Mark's Little Deck; two Forests cast an Elf and Crossroads, haste allows the Elf to tap for mana that turn; haste applies to both players' creatures. |
| 069 Eureka | Groundhog Day curated Old School model; one player passing does not end the process, putting permanents into play is not casting them. |
| 070 Candelabra of Tawnos | Odd Anders Kjostvedt — U/G Control; Sol Ring pays {1} to untap Maze for two distinct creature targets; Candelabra does not produce mana. **Legacy banned June 29, 2026**. |
| 071 Transmute Artifact | Groundhog Day curated Old School model; Sol Ring (MV1) converts to Mana Vault (MV1), with artifact sacrificed **during spell resolution**, not as an additional cost to cast. |
| 072 Power Artifact | Original, clearly labeled **60-card curated demonstration**, not an event registration; two blue mana enchant Basalt Monolith; reduce {3} untap to {1}, net +2 colorless per cycle. |

Documentary source levels are deliberately distinguished. Original-printing identifiers and official rulings are source-checked; inherited tournament registration attributions still require individually verified original event sources. **The 072 article had no historical deck list at all**, so an explicitly invented 60-card 2000-era legal-card-pool teaching model was added without false organizer, opponent, date or finish. It is not classified as a verified tournament deck.

## Files and reproducibility

- `research-dossiers/reader-v31-063-072/editorial-candidates.json`: independent story, timeline, original-printing and mechanics decisions for all ten.
- `tools/prepare_reader_063_072.py --apply`: write story components into exactly these ten HTML pages, correct high-risk rules prose, refresh focused numbered research dossiers, generate word-count/reading-time metadata, source records and hashes.
- `tools/prepare_reader_063_072.py` (default check): verify vignette lengths, exact archive labels, source-bound dossier schemas, article SHA-256, reading-time and candidate status.
- `validation/reader-v3.1-063-072-candidate-metrics.json`: exact current article hashes, editorial words, reading times, and provenance-limited candidate status.
- `research-dossiers/reader-v31-063-072/NNN-story-candidate.json` and `NNN-review.json`: individual review of every scene and exact payment declaration.
- `audit/release-v2-validation-state.json` and dependent validation reports regenerated after article HTML changes, not bypassed.

## Actual passing candidate metrics and archive refresh

The isolated full refresh [GitHub Actions run 40614371151](https://github.com/Diabolicdonut/Compulsive-Research/actions/runs/40614371151) **completed successfully**, regenerating protected V2 fingerprints and detailed reports. The job ran the ten-page candidate generator, source/dossier validator, original 061/062 candidate validators, full Reader V3.1 experience checks, historical deck-archive check (exactly **1,505 numbered and canonical HM pages in corpus**), quick and V2 refresh suites, full release suite, internal navigation checks and preserved checkpoint verification. These tests passed as a candidate preparation run; permanent PR CI and desktop/mobile browser testing must still pass before merge.

Derived **editorial prose total for these ten articles: 27,697 words**, excluding deck archive/reference-only components:

| Entry | Card | Editorial words | Derived read time | Opening vignette words |
|---:|---|---:|---:|---:|
| 063 | Moat | 2,688 | 14 minutes | 92 |
| 064 | Nether Void | 2,766 | 14 minutes | 92 |
| 065 | The Abyss | 2,714 | 14 minutes | 93 |
| 066 | Land Tax | 2,847 | 15 minutes | 95 |
| 067 | Sylvan Library | 2,914 | 15 minutes | 109 |
| 068 | Concordant Crossroads | 2,721 | 14 minutes | 94 |
| 069 | Eureka | 2,680 | 14 minutes | 93 |
| 070 | Candelabra of Tawnos | 2,833 | 15 minutes | 94 |
| 071 | Transmute Artifact | 2,777 | 14 minutes | 100 |
| 072 | Power Artifact | 2,757 | 14 minutes | 99 |

Per-page SHA-256 hashes, word metrics and exact deck binding are stored in `validation/reader-v3.1-063-072-candidate-metrics.json`. Ten new story records and ten review files are stored beside the candidate editorial plan. The added Power Artifact deck passes all main-deck, group total, copy-buffer and provenance checks, explicitly labeled as a constructed study model. The temporary write-permitted Actions workflow is deleted from the PR after recording these artifacts.

**No new wave was promoted:** Reader acceptance remains 60/100 and weighted whole-product progress remains 51/100 pending formal 061–070 sign-off.

## Source leads for decisive claims

The individual card records at [mtg.wtf](https://mtg.wtf) identify the original 1994 printings and official Oracle/rulings. Independent high-impact checks are the [official June 29, 2026 Legacy ban](https://magic.wizards.com/en/news/announcements/banned-and-restricted-june-29-2026); [Wizards' 2006 Basalt Monolith errata correction](https://magic.wizards.com/en/news/feature/power-level-errata-b-gone-2006-07-14); [Wizards' 2003 Power Artifact combo retrospective](https://magic.wizards.com/en/news/feature/top-50-blue-cards-2003-08-15); [Transmute Artifact's 2011 sacrifice-on-resolution Oracle ruling](https://mtg.wtf/card/atq/14/Transmute-Artifact); and the [Eureka 2004 spell-resolution rules](https://mtg.wtf/card/leg/185/Eureka).

## Validation, preservation and acceptance

The release gate must pass Reader validation, dossier schema and source binding, exact archive counts, full V2 release refresh and fingerprint verification, archive navigation and desktop/mobile browser smoke tests. Report **specific run URLs and metrics only after GitHub Actions completes successfully**.

The batch in this report crosses an acceptance boundary: 063–070 completes the candidate draft set for 061–070; 071–072 begins the next batch. **Neither 061–070 nor 071–080 is thereby accepted.** To promote 061–070, inspect 061–070 in full, verify inherited secondary archival evidence, create the consolidated numbered migration ledger, preservation hashes and dated acceptance report, and rerun all release checks. Until that happens retain **60/100 Reader** and **51/100 whole-project weighted roadmap**.

Next individual article is **073 — Ali from Cairo**, but the recommended next milestone is **formal Reader 061–070 acceptance** before starting additional batches. Do not roll back previous 061 or 062 standalone work.
