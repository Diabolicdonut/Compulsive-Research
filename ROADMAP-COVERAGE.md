# Compulsive Research — Authoritative Development Roadmap

**Roadmap revision:** 1.7 (October 28, 2026)  
**Authority:** This document governs the finite current Compulsive Research archive program. `site-progress.json` is the machine-readable mirror of its weighted acceptance gates; `CURRENT-STATE.json` is authoritative for the latest accepted editorial checkpoint. See [`AGENTS.md`](AGENTS.md) for mandatory worker procedure.  
**Recovered baseline:** GitHub `main` commit `40bdf22c8f61959da4284663be1fe0b7198f4a7d`; the October 27 status-widget implementation at `b20f944769372d5129f5261ce0f5dfd5566e58f9` is retained, not replaced.

## 1. North-star vision and scope

**Compulsive Research is a lasting, historically grounded, readable Magic: The Gathering card-history encyclopedia:** the story of why individual cards mattered, from design and first printing through tournament adoption, changing formats, characteristic interactions, art and presentation, memorable play experiences and their continuing legacy. Every entry should be recognizable as an independently researched feature rather than generated template prose. The site should let readers find, browse, compare and return to individual features reliably, on desktop or mobile.

The **current finite approved release** comprises **1,000 numbered features**, **505 canonical unnumbered Honorable Mentions**, **22 Honorable Mention categories**, and **1,505 active article pages** plus the landing page. It does **not** purport to include every Magic card ever printed. The roadmap encompasses both the already working archive and **all remaining editorial, evidence, user-experience and release-quality work** necessary to bring this corpus to publication quality—not merely the next 10 or 100 Reader V3.1 articles.

Future card additions, new editorial collections, translations, interactive features, or a different total article count are potential extensions, **not silently included in the present 100-point denominator**. Approve such scope explicitly, record the decision here, and revise the weights and status manifest transparently before claiming a new percentage.

## 2. Recovery, preservation and source of truth

Before any work, fetch the latest GitHub `main`, its recent commits, open PRs, Issues and Actions. Inspect `CURRENT-STATE.json`, the newest `audit.md` entry, `READER-V3.1-MIGRATION-LEDGER.json`, `audit/reader-v31-051-060/REPORT.md`, `canonical/`, `research/`, `tools/`, `validation/` and `AGENTS.md`. An accepted newer checkpoint always supersedes any older instructions or ZIP snapshot; dated handoffs remain historical evidence, not a reason to roll back.

Preserve **exactly 1,000 numbered pages and 505 active `honorable-<slug>.html` pages** during the current program, with category-local HM navigation and one live link per canonical page. Do not recreate retired `honorable-NNN-*.html` duplicates. `250-eternal-dragon.html` remains a structural Reader benchmark. Accepted repairs—including Hypnotic Specter chronology, Wheel of Fortune identity, validated gameplay scenes and Reader 051–060—are protected. Changes to a document outside the approved work range need an explicit source-backed justification and a preservation report.

The last accepted Reader V3.1 checkpoint is **051–060** (October 16, 2026); the next source-reviewed item is **061 — Maze of Ith**. Accepted 051–060 work preserved **1,495 articles byte-identically** outside its ten-entry batch; navigation checked **31,781 local links with zero failures**. These structural checks do **not** prove every historical claim in all 1,505 articles.

## 3. Milestone sequence and completion definition

The full program is not complete merely because the articles exist. Milestones may overlap in implementation but cannot be **accepted** until their stated evidence and quality criteria are met. Work proceeds in small, reviewable, independently validated waves.

| Milestone | Objective and remaining acceptance work | Completion evidence |
|---|---|---|
| M0 — Archive preservation | Maintain the complete 1,505-page canonical corpus and all 22 HM categories; eliminate broken canonical identities, navigation and return links | Archive manifest, canonical identity, link validation, CI and browser checks |
| M1 — Reader V3.1 initial conversion | Retain accepted 001–060; convert **061–070**, **071–080**, **081–090**, **091–100** as four distinct reviewed checkpoints | Each wave: source dossier, legal gameplay scene, corrected page, revised ledger, diff-based preservation proof, release tests |
| M2 — Archive-wide historical/editorial review | Review remaining numbered features **101–1000**, while respecting previously modernized exceptions; then review all **505 HMs**. Prioritize the 590 rewrite-required and 792 audit-required records, accounting for overlap instead of adding counts; use research-backed waves | Per-page claim audit and signoff, updated warnings/defect ledger, accepted category- and range-scoped batches |
| M3 — Deck provenance and gameplay truth | Reconcile deck fingerprints, unbound source URLs and monobasic-color anomalies; check lists, dates, format legality and tournament attribution | Bound primary sources or explicitly labeled curated examples; resolved or justified warning ledger |
| M4 — Artwork, rights and media | Verify subject, original illustrator, first printing, image identity, accessibility, rights/link notices and resilient image failure states | Media audit and targeted negative tests; no invented provenance or copyrighted asset scraping |
| M5 — Reader/site experience | Preserve browse/search/filter, wave and HM collapsibles, per-article table-of-contents links, return-to-entry behavior, responsive typography and accessible controls | Desktop and 390px browser smoke tests, keyboard checks, readable fallback/error states |
| M6 — Release and archival durability | Complete full-corpus evidence review, release fingerprints, correct repair histories, no regressions, stable Pages deployment, reproducible documentation and contributor instructions | Accepted full/refresh/quick suites, release stamp, GitHub Actions and reviewed release note |

### Editorial contract for every article

An article should establish the card's actual printed identity and first release, essential rules and interactions **in the correct historical rules context**, the design or strategic reason it mattered, format/tournament and deck-history evidence with dates, illustrative play, art/artist identity, and lasting influence. A representative first-person table scene must be explicitly identifiable as reconstruction rather than a real quotation or exact match transcript. The scene's game state must be legal: one land play per turn absent an effect, sufficient colored and generic mana, correct timing, stack, priority, summoning sickness, targeting, combat math, board state and period card availability. Claims and named decks must distinguish documented registrations from editorial examples.

Honor the existing `canonical/` contracts and don't regenerate accepted prose from generic templates. Defects in card identity, sources, deck records or historical claims outrank cosmetics. Preserve source citations and changes to the migration ledger and audit alongside the article itself.

### Next authorized editorial batches

1. **061–070** beginning with Maze of Ith; accept only after ten researched features, story/source checks and CI/browser gates.
2. **071–080**, **081–090**, **091–100**, each as a separate accepted checkpoint.
3. Continue **101–1000** in rational, independently reviewable waves, prioritized by editorial defects and card prominence rather than presumed numerical completeness.
4. Complete **all 505 HM articles** with the same historical/mechanical standards, maintaining category navigation.
5. Reconcile archive-wide deck, source, art, accessibility and residual validator warnings; complete a final full-corpus acceptance sweep.

Work on M2–M6 can proceed in parallel if a change is safely isolated and reported; a worker may not declare an entire milestone accepted from an isolated success.

**October 28 explicit reader editorial approval:** The user reviewed and **accepted the published 073–082 articles**. Preserve this editorial sign-off in `CURRENT-STATE.json` and `audit.md`. This does not by itself satisfy independent event-deck provenance, contiguous Reader 071–080/081–090 migration ledger, or the still-blocked 061–070 source-audit requirements; therefore the formally accepted Reader counter remains **60/100**, with weighted roadmap **51/100**.

**October 28 Reader 083–092 ten-article implementation:** Produce period-anchored first-person Reader V3.1 scenes, corrected origin/rules/tournament explanations, independent dossier reviews and derived metrics for **083 Millstone; 084 Ivory Tower; 085 Zuran Orb; 086 Hymn to Tourach; 087 Order of Leitbur; 088 Order of the Ebon Hand; 089 Icatian Javelineers; 090 Aeolipile; 091 Goblin Grenade; 092 High Tide**. The 091 article had no documented historical deck, so its 60-card original 1994 red-Goblin model must be labeled a **curated example**, never a tournament registration. Rules-critical checks: mill ≠ discard or automatic decking loss, Ivory Tower counts hand before draw, Orb sacrifices lands as activation costs, Hymn random discard, first-strike pump sequencing, Javelineers tap and javelin activation costs, Aeolipile's sacrifice before response, Goblin Grenade's **additional casting-cost sacrifice**, and High Tide's symmetrical Island mana triggers. See `audit/reader-v31-083-092/REPORT.md`, `research-dossiers/reader-v31-083-092/editorial-candidates.json` and `tools/prepare_reader_083_092.py`.

**Wave boundaries:** 083–090 finishes candidate drafts of 081–090; 091–092 are advance drafts in 091–100. User editorial sign-off is recorded separately and no formal wave acceptance or weighted milestone is awarded solely for completing drafts. Next untouched article **093 — Merchant Scroll**. Before advancing any Reader count, resolve source evidence and cumulative wave acceptance blockers with repeatable preservation tests.

**October 28 Reader 061–070 evidence-based wave acceptance review:** The ten page candidates pass existing structural/gameplay and release tests but have retained inherited deck registrations without event-specific source binding and deeper historical claims that were never independently signed off. The new `tools/audit_reader_061_070_acceptance.py` produces reproducible page hashes, source classification, unresolved deck-entry counts and explicit acceptance gates in `audit/reader-v31-061-070/ACCEPTANCE-AUDIT.md`. **Acceptance is blocked, not granted.** The latest authoritative accepted checkpoint therefore remains **051–060** (60/100). Publication-quality provenance cannot be replaced by a clean build or an automatic source-count metric.

**October 28 Reader 073–082 ten-article continuation:** Prepare focused Reader V3.1 source/rules and distinct first-person vignette candidates for **073 Ali from Cairo, 074 Drop of Honey, 075 Old Man of the Sea, 076 Serendib Efreet, 077 Su-Chi, 078 Triskelion, 079 Tetravus, 080 Atog, 081 Ornithopter and 082 Feldon's Cane**. For 073, an explicitly curated 60-card 1994 red-defense study replaces no historical registration; the sole purpose is a truthful Reader archive example. 073–080 complete the candidate set for 071–080 and 081–082 begin 081–090. A ten-article manuscript report, detailed per-page hash and source-scoped research records are required; do not invent historical matches, dates or event decks. Next untouched 083 Millstone. **Neither wave's accepted progress advances.** Overall roadmap remains **51/100** under the unchanged weights.

**October 27 Reader 063–072 ten-article candidate production:** Implement a ten-article Reader V3.1 opening-story, mechanics and research-evidence pass on articles **063 Moat** through **072 Power Artifact**, continuing the prior source-backed 061/062 candidates. Each receives a distinctive first-person illustrative scene anchored in an exact Deck Archive title; 072 gains an explicitly curated, non-tournament Power Artifact/Basalt Monolith demonstration (there is no verified tournament deck in its inherited article). Correct high-risk historical/rules errors, especially **Transmute Artifact sacrifice during resolution, not as an additional casting cost**, and document the **June 29, 2026 Legacy ban of Candelabra of Tawnos**. Generate exact per-page word counts, article hashes, story reviews and a separate ten-article report. See `audit/reader-v31-063-072/REPORT.md`, `research-dossiers/reader-v31-063-072/editorial-candidates.json` and `tools/prepare_reader_063_072.py`.

**Acceptance accounting:** completion of 063–072 as *candidate pages* means **061–070 has ten candidate articles**, not an accepted checkpoint. The 061–070 batch still needs research dossier provenance clearance, original-document validation, preservation reports, and a wave-level acceptance ledger. 071–072 belong to the following 071–080 wave. **Do not** report 70/100 accepted until the batch review passes. Both current published counters remain **Reader 60/100**, **weighted project 51/100**. The next individual article is **073 — Ali from Cairo**, while the most urgent acceptance work is 061–070 consolidated review.

**October 27 Reader 062 individual modernization candidate:** The Tabernacle at Pendrell Vale has a Reader V3.1 story grounded in Jarvis Yu's November 2015 Legacy Lands winning card pool, a carefully labeled hypothetical Grixis Delver upkeep, correct independent creature triggers and {1} payments, verified Legends/Nicola Leonard identity and source-specific evidence. See `audit/reader-v31-061-070/062-CANDIDATE.md`, `research-dossiers/reader-v31-061-070/062-review.json` and `tools/validate_reader_062_candidate.py`. Both 061 and 062 remain **individual migration candidates**, not a signed-off ten-article batch. The exact next authoring entry is **063 — Moat**. Full Reader remains **60/100 accepted** and whole-product **51/100 weighted**.

**October 27 Reader 061 single-article modernization candidate:** Maze of Ith now has a source-grounded opening and first-person reconstruction using Mark Arce's 2015 published Mono Black registration, original The Dark artist/set identity, corrected official combat rules, a reviewable zero-mana activation ledger, and a tightened article-specific research dossier. See `audit/reader-v31-061-070/061-CANDIDATE.md` and `tools/validate_reader_061_candidate.py`. **This does not promote the ten-article 061–070 checkpoint**: articles 062–070 still require individual migrations, and archived secondary lists/history remain review queues. Accepted Reader metric stays **60/100** and overall weighted acceptance **51/100**. The exact next production article is **062 — The Tabernacle at Pendrell Vale**, with 061 reopened if its source review uncovers defects.

**October 27 Reader 061–070 mechanics preparation:** Ten inherited interchangeable case studies have been replaced with card-specific, mechanically auditable examples. Confirmed material corrections include Maze not removing attackers from combat, Tabernacle using controller-upkeep destruction triggers rather than activation or sacrifice, Nether Void's triggered counter rather than a casting-cost increase, The Abyss's targeted one-at-a-time destruction, and Candelabra's **June 29, 2026 Legacy ban**. See `audit/reader-v31-061-070/PREPARATION.md` and `tools/validate_reader_061_070_mechanics.py`. **This is only a partial preparatory pass:** none of articles 061–070 is yet accepted as a complete Reader V3.1 migration; full story dossiers, first-person reconstructions, source/deck audits, reading-time updates, release fingerprint refresh and batch acceptance remain. The accepted Reader indicator therefore remains **60/100**, and the overall weighted roadmap remains **51/100**.


## 4. Weighted total-project acceptance gates

These weights reflect **current approved delivery scope**, including the substantial preserved and functional foundation. The existing percentages are deliberately held stable pending a reviewed rebaseline. A full gate earns its weight only on acceptance; a **partial** gate earns **zero** overall points, but can report detailed evidence and subprogress in audit records. This is a conservative *delivery milestone* measure, not a percentage of fact-checked sentences or a simple number of HTML files. The machine-readable mirror must contain the exact same gates, weights and status.

| Current finite approved delivery gate | Weight | Status | Authority |
|---|---:|---|---|
| Preserve exactly 1,000 numbered and 505 active Honorable Mention pages | 16 | accepted | `CURRENT-STATE.json; README.md` |
| Full navigation/link and canonical page identity validation | 10 | accepted | `audit.md; audit/reader-v31-051-060/REPORT.md` |
| Canonical 22 Honorable Mention categories and safe navigation | 8 | accepted | `CURRENT-STATE.json` |
| Source-reviewed Reader V3.1 migrations through article 060 | 10 | accepted | `audit/reader-v31-051-060/REPORT.md; READER-V3.1-MIGRATION-LEDGER.json` |
| Modernize Reader V3.1 articles 061–100 without restarting 001–060 | 12 | partial | `CURRENT-STATE.json immediateNextTask` |
| Evidence-check and normalize remaining numbered/HM article histories | 17 | partial | `canonical/; research/; audit.md` |
| Resolve documented deck evidence, attribution and migration warnings | 8 | partial | `CURRENT-STATE.json; audit.md` |
| Maintain legally sourced art links, rights notices and accessible embeds | 6 | partial | `audit.md; README.md` |
| Desktop/mobile archive browse, filter and UX acceptance coverage | 7 | accepted | `README.md; .github/workflows/validate-archive.yml` |
| Full archive editorial acceptance with negative regression protections | 6 | partial | `audit.md; validation/` |

**Overall accepted: 51/100 = 51%**. **Reader V3.1 initial hundred: 60/100 = 60%**, after articles 001–060. The overall number may stay constant across a successful intermediate editorial wave until one of the explicitly approved weighted gates has been fully accepted. The separate Reader progress is intended to show the incremental 061–100 work.

**Do not equate 51% weighted acceptance with 51% of research or factual claims independently verified.** A displayed 100% will mean **all stated current release gates have accepted evidence**, not that future Magic publications and optional enhancements are finished.

## 5. Worker governance and mandatory roadmap maintenance

Every AI development worker must treat this file as the governing *future scope and sequence*, `CURRENT-STATE.json` as the **current accepted checkpoint**, `site-progress.json` as the **published structured progress**, and `audit.md` plus wave-specific reports as acceptance evidence. On conflict with older handoffs, use newest accepted GitHub state and update stale references rather than restarting work. Do not let parallel workers overwrite each other's branch changes.

**For every implementation, scope change, newly accepted batch or milestone:**

1. Recover GitHub head and confirm the requested work appears in this roadmap; if not, first document the scope decision, affected gates and acceptance evidence here.
2. Implement on a fresh feature branch in a minimal diff; preserve accepted articles outside the authorized batch and document any necessary exception.
3. Run quick validation during work, refresh-V2 after content changes, full suite and navigation before release, plus Reader checkpoint and browser validations as applicable.
4. Update `CURRENT-STATE.json`, the relevant migration ledger, `audit.md`, reports and metrics **to reflect only work actually accepted**. Record the next exact resumable task and known unresolved warnings.
5. Review and update **this roadmap** (revision, milestone status, acceptance evidence, open issues, and next steps). Synchronize the matching weights/statuses, review date, revision fallback and phase counts in `site-progress.json`. Keep the real checkpoint data authoritative: the widget reads `CURRENT-STATE.json` when possible.
6. Run `python tools/validate_site_progress.py` and all applicable existing checks. Confirm the site shows correct revision, overall weighted percent, explanatory basis and the separate Reader phase. Do not mark gates accepted merely because code was authored or a PR was opened.
7. Open a PR describing changes, evidence, preservation checks, effect on the overall percentage, new risks and exact next task. Merge only after review and successful Actions; then verify the accepted branch and Pages result.

An editorial change that leaves overall weighted points unchanged **still requires a checkpoint, roadmap/status review, and an updated phase metric where applicable**. Similarly, changes to the long-term vision must not be hidden in a local chat prompt; amend this file and record the decision. If a milestone is split for finer progress reporting, preserve its parent's weight so the total stays exactly 100 unless the user approves a new baseline.

## 6. Open backlog and evidence limitations

- The currently inherited review queues include approximately **590 rewrite-required** and **792 audit-required** pages (potentially overlapping), **1,440 reused deck-fingerprint warnings**, **349 unbound-source warnings** and **5 monobasic-color warnings**, as reported at accepted checkpoint 051–060. These are not failures in all cases; investigate individually.
- Earlier exhaustive legacy hero/title/artwork validators yielded unresolved or outdated contract findings; those *do not* automatically prove current pages are wrong. Triage with original source evidence before changing images, headlines or metadata.
- Browser tests exercise desktop/mobile rendering with stubbed external artwork. They do not prove live third-party image delivery or correctness of every historical assertion.
- Continuously improve negative regression fixtures for the actual errors previously found (mana, land drops, story chronology, identity, deck attributions, nav/TOC). Maintain per-article source review instead of treating green CI as historical verification.

## 7. Published revision and progress architecture

`index.html` loads the **read-only** `site-progress.js` status widget. The script fetches `site-progress.json`, resolves the latest editorial revision via `CURRENT-STATE.json`, calculates accepted gate weights (100 total), shows a separate Reader 001–100 progress bar, and links back to this roadmap. The same manifest can be read by future tools; do not hard-code percentages into the HTML. The mount is isolated from article content and site navigation to preserve the accepted archive/release fingerprint.

**Current public display:** `Rev Reader V3.1 051-060`, `Roadmap 51%`; inside the disclosure: 60/100 Reader V3.1 initial features. GitHub Actions checks the manifest's agreement with this roadmap and the canonical state. An unavailable source must not lead to a fabricated completion figure. Changes to layout/style should preserve keyboard accessibility, mobile readability and the canonical landing-page content.

## 8. Acceptance record and next action

- **Accepted editorial content baseline:** Reader V3.1 **051–060**, October 16, 2026; `40bdf22c8f61959da4284663be1fe0b7198f4a7d`.
- **Roadmap + live status baseline:** `b20f944769372d5129f5261ce0f5dfd5566e58f9`, October 27, 2026; Actions passed.
- **This governance revision:** formalizes long-range completion conditions and routine roadmap/status updates without modifying article prose, the accepted article corpus or gate weighting.
- **Next acceptance task:** clear **061–070 event provenance and inherited historical claims** and formally sign off that wave; **next untouched article:** **093 Merchant Scroll**, following independently revised 083–092. User has editorially accepted 073–082; formal Reader accepted remains 60/100.
- **Required handoff:** state the exact accepted main commit and checkpoint, validations actually run, accepted vs pending work, warning changes and next isolated task.

See `README.md`, `AGENTS.md`, `CURRENT-STATE.json`, `audit.md` and the relevant checkpoint dossier for the complete working context.
