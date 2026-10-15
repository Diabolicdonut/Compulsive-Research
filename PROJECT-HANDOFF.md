# CURRENT AUTHORITATIVE READER V3.1 STATE — SEPTEMBER 24, 2026

This section supersedes older continuation instructions below.

- Source of truth: this complete `Compulsive-Research-main` folder, updated from the August 5 Hypnotic Specter corrected package
- Reader V3.1 numbered Wave 1: entries 001–050 complete
- Supplementary updated samples: entries 248, 250, 417, and 425
- September gameplay review corrected 10 numbered scenes and the Stoneforge Mystic supplementary scene; Wheel of Fortune's wrong-card images and credit were also repaired; see `audit.md`
- Nether Spirit's duplicated headline was corrected; the updated headline scan finds 1,000 unique titles, with 14 older title-bank mismatches remaining for review
- Exact next content task: entries 051–060, the first independently validated checkpoint of the 051–100 retrofit
- Current handoff: `READER-V3.1-CURRENT-HANDOFF-2026-08-05.md`
- Fresh prompt: `READER-V3.1-FRESH-CONVERSATION-PROMPT-2026-08-05.txt`

Read the current Reader V3.1 handoff before using any historical notes below.

---

# CURRENT AUTHORITATIVE CONTINUATION STATE — READER V3

**As of August 4, 2026; this section supersedes older status counts and continuation instructions later in this document.**

- Release: `2026-08-04-reader-v3-raw-table-stories-pilot-approved`
- Active articles: 1,505 (1,000 numbered + 505 active Honorable Mentions)
- Editorial V2/reader-layout processed: numbered entries 001–100, plus selected later benchmark rewrites
- Reader V3 approved: entries 001–010
- Immediate next task: entries 011–050, completing Numbered Wave 1 under Reader V3
- Then: retrofit entries 051–100 to Reader V3
- Then: Honorable Mention Wave 1, first 50 active HMs in category order
- Reader V3 source: `READER-V3-PROJECT-HANDOFF.md`
- Fresh-conversation prompt: `READER-V3-FRESH-CONVERSATION-PROMPT.txt`

Read the Reader V3 handoff before the historical project notes below.

---

# Compulsive Research — Project Handoff

**Project version:** `2026-08-01-card-images-and-double-faced-cards`

**Source of truth:** this complete project folder and the ZIP that contains it.

**Canonical numbered article:** `250-eternal-dragon.html`

**Canonical snapshot and lock:**

- `canonical/250-eternal-dragon.canonical.html`
- `canonical/250-eternal-dragon.sha256`
- `canonical/canonical-lock.json`

## Card-image and double-faced-card standard

The August 1, 2026 card-image rollout is complete across all **1,685 physical article files**. Every visible card row in every historical, editorial, and official-product decklist is now a card-image link, including the article namesake card. The validator checked **537,913 visible deck rows** and found **537,913 linked rows**.

For physical double-faced cards, the preview runtime resolves one Scryfall card object and renders each face from its own `card_faces[].image_uris` record. Namesake lead panels show both physical faces and a separate rules panel for each face. The collapsed empty Official Magic section uses the numeric label **0**.

The historical and official deck-count validators were rerun after the migration: **6,794 historical/editorial decks** and **8,595 official-product appearances** passed with no count failures.

## Current authoritative archive state

- Numbered landing-page records: **1,000**
- Numbered article files: **1,000**
- Numbered range: **001–1000**
- Honorable Mention articles: **505**
- Honorable Mention categories: **22**
- Total article pages: **1,505**
- Honorable Mention numbering: **retired**
- Honorable Mention navigation: **category-local only**
- Landing page: `index.html`
- Card-type filter: active and must be preserved

The 505 Honorable Mentions comprise the 180 pre-categorization articles, the 319-card typal expansion, five Onslaught Zombies additions, and Sleight of Mind.

## Latest completed changes

### Categorized Honorable Mentions

Honorable Mentions use stable filenames of the form:

```text
honorable-card-slug.html
```

They are grouped into shelves on the landing page. Previous/next links never cross category boundaries. Do not restore old files named `honorable-NNN-card-slug.html`.

Category authority:

- `data/honorable-categories.json`
- `honorable_category_manifest.json`
- `archive-manifest.json`
- `canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md`

### Onslaught Zombies additions

The Zombies shelf now includes articles for:

- Festering Goblin
- Putrid Raptor
- Soulless One
- Unholy Grotto
- Withered Wretch

The project also retains `Compulsive-Research-Onslaught-Zombies-EVALUATION.md` and its supporting validation/manifest files.

### Sleight of Mind

`honorable-sleight-of-mind.html` is filed in **Archive Favorites**, between Nimble Mongoose and Spelljack. The reusable Honorable Mention template and validators were updated in the same release.

## Required startup procedure

Before editing:

1. Extract the complete ZIP and work only from that extracted copy.
2. Read `README-FIRST.md` and this handoff.
3. Read every contract in `canonical/`, especially:
   - `CANONICAL-CONTRACT.md`
   - `GENERATION-PROMPT.md`
   - `HONORABLE-MENTION-CATEGORY-CONTRACT.md`
   - `HERO-IDENTITY-CONTRACT.md`
   - `HEADLINE-IDENTITY-CONTRACT.md`
   - `ARTWORK-SPOTLIGHT-CONTRACT.md`
   - `DESIGN-ECHO-CONTRACT.md`
   - `CARD-REFERENCE-CONTRACT.md`
   - `PRINTING-GALLERY-CONTRACT.md`
   - `SOURCES-CONTRACT.md`
4. Inspect the templates and schemas in `templates/`.
5. Read `archive-manifest.json` and `data/honorable-categories.json` before deciding whether a requested card already has an article.
6. Verify the canonical lock:

   ```bash
   pip install -r requirements.txt
   python tools/check_canonical_lock.py
   ```

7. Run `python tools/run_validation_suite.py --quick` to establish a baseline.
8. Preserve existing prose and research unless the user explicitly requests a rewrite.
9. Make surgical changes rather than regenerating compliant pages.

## Canonical design authority

`250-eternal-dragon.html` controls the approved numbered-article structure and behavior, including:

- Header and hero
- Return link
- Entry and wave identity
- Previous/next navigation
- Table of contents
- Article sections
- Card-reference previews
- Artwork Spotlight
- Design Echo
- Deck Archive
- Printing Gallery
- Sources
- Footer and mobile behavior

Routine work must not redesign or simplify these systems.

For Honorable Mentions, use:

- `templates/honorable-article-shell.html`
- `templates/honorable-article-content.schema.json`
- `canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md`

## Adding an Honorable Mention

1. Search `archive-manifest.json` for the exact normalized card name.
2. Confirm the card is absent from both numbered entries and Honorable Mentions.
3. Choose the most appropriate existing category. Create a new category only when the current taxonomy is clearly inadequate.
4. Create `honorable-card-slug.html` from the canonical Honorable Mention template.
5. Insert the card alphabetically inside its category unless the user specifies a different editorial order.
6. Update only:
   - The new article
   - Its immediate previous neighbor, when present
   - Its immediate next neighbor, when present
   - `index.html`
   - `data/honorable-categories.json`
   - `honorable_category_manifest.json`
   - `archive-manifest.json`
7. Preserve category-local navigation and landing anchors.
8. Run the quick suite, then the full suite before packaging.

## Research and editorial rules

- Do not invent tournament players, events, placements, dates, decklists, quotations, artists, printings, or design credits.
- Do not publish reconstructed or editorial deck shells; use documentary lists or omit the decklist.
- Preserve verified historical lists.
- Sources must be article-specific and substantive; generic card databases alone do not establish historical claims.
- New long-form articles should normally approximate a 20-minute read unless the user requests otherwise.
- Card names in prose use the canonical `span.card-name` markup and shared preview runtime.
- The subject card should not be linked repeatedly inside its own article.
- Printing galleries may show up to 12 exact-identity printings and should prefer distinct artwork.

## Approved template-change procedure

A site-wide template change is not complete until all applicable layers are updated:

1. Canonical article/snapshot and lock
2. Relevant contract files
3. Templates and schemas
4. Shared CSS and any approved JavaScript; the official-deck component uses CSS only
5. Migration/canonicalization tools
6. Independent validators and fixtures
7. GitHub Actions workflow
8. Every affected article
9. Migration report and article-by-article validation output

Do not change only the visible HTML.

## Validation and release

Read `VALIDATION-SUITE.md`. The standard commands are wrapped by:

```bash
python tools/run_validation_suite.py --quick
python tools/run_validation_suite.py --full
```

After approved work, deliver:

- A complete updated project ZIP
- The updated `index.html`
- A smaller incremental update ZIP when useful
- A release report
- Validation output
- An honest note about any test that could not be completed

## Static Official Magic deck rollout — August 1, 2026

The supplied production site was updated across all **1,685 physical article files**. Every article now contains one collapsed-by-default section labeled **Official Magic the Gathering decks**. Matching product decklists and their full contents are compiled directly into the HTML from `data/official-mtg-deck-catalogue.json`; each product deck is also collapsed by default. Cards with no qualifying product retain the section with the exact required no-product statement.

The runtime loader has been retired. `preconstructed-decks.js`, browser fetching, and “Open this section to load” placeholders are publication failures.

The count contract remains strict: visible quantity rows are added as integers, all visible and copyable totals agree, products without sideboards remain without sideboards, and documented historical exceptions are preserved. Read `DECK-ARCHIVE-UPDATE-REPORT.md` and `canonical/DECK-ARCHIVE-CONTRACT.md` before changing deck HTML.

Completed deck validation baseline:

- **6,794** historical/editorial deck components
- **8,595** official-product deck appearances
- **15,389** total validated deck components
- **1,685 PASS, 0 FAIL** in the historical validator
- **1,685 PASS, 0 FAIL** in the official-product validator

Required order after a deck, article, template, or catalogue change:

```bash
python tools/repair_known_historical_deck_anomalies.py --root PATH_TO_SITE --check
python tools/canonicalize_copy_decklists.py --root PATH_TO_SITE --check
python tools/render_official_mtg_deck_sections.py --root PATH_TO_SITE --check
python tools/validate_deck_archives.py --root PATH_TO_SITE --jobs 4 --output-dir PATH_TO_SITE/historical-deck-validation
python tools/validate_official_mtg_decks.py --root PATH_TO_SITE --jobs 4 --output-dir PATH_TO_SITE/official-mtg-deck-validation
```

## Editorial V2 reviewed-wave status — August 2, 2026

The universal metadata-dossier generator is retired for publication work. New or rewritten articles must be based on an article-specific research dossier, documentary deck evidence, and the Editorial V2 contracts.

Current reviewed set:

- `451-delver-of-secrets.html` — user approved Editorial V2 benchmark
- `386-counterbalance.html` — Editorial V2 Wave 1 review
- `391-thoughtseize.html` — Editorial V2 Wave 1 review
- `484-treasure-cruise.html` — Editorial V2 Wave 1 review

Production deck policy:

- Do not publish `editorial-study` or mechanically filled deck shells.
- Use verified tournament registrations, verified official products, or omit the decklist.
- A documentary list may appear in more than one article when it genuinely contains multiple featured cards; cross-article reuse is a warning for review, not automatically a failure.

See `EDITORIAL-V2-WAVE-1-REPORT.md` and the dossiers under `research-dossiers/editorial-v2-wave-1/`.

## Editorial V2 Wave 2 and full-archive migration ledger — August 2, 2026

Wave 2 advances ten additional high-priority articles under the approved Delver standard. Four pages received substantive card-specific reconstruction and six already-bespoke pages received evidence, deck-archive, and Editorial V2 review without unnecessary prose replacement.

Substantive rewrites:

- `101-necropotence.html`
- `159-survival-of-the-fittest.html`
- `177-tolarian-academy.html`
- `416-jace-the-mind-sculptor.html`

Reviewed and promoted bespoke pages:

- `022-serra-angel.html`
- `102-force-of-will.html`
- `103-brainstorm.html`
- `303-skullclamp.html`
- `328-senseis-divining-top.html`
- `351-dark-confidant.html`

Current full-archive migration ledger:

- **17** benchmark or reviewed-v2 articles
- **252** automated V2 candidates awaiting human approval
- **640** articles requiring deeper editorial/evidence audit
- **596** articles requiring substantive card-specific rewrite

The candidate label is not approval. It identifies pages whose existing prose and sources appear strong enough for focused human review rather than presumptive reconstruction. The full queue is stored in `data/full-editorial-migration-queue.json`.

See `EDITORIAL-V2-WAVE-2-REPORT.md`, `EDITORIAL-V2-WAVE-2-VALIDATION.md`, and `research-dossiers/editorial-v2-wave-2/`.


## Editorial V2 Wave 3 — August 2, 2026

Wave 3 completes four additional substantive rewrites from the continuation-generator cohort:

- `401-noble-hierarch.html`
- `403-bloodbraid-elf.html`
- `417-stoneforge-mystic.html`
- `452-snapcaster-mage.html`

Each page now contains a card-specific thesis, original-set context, rules and sequencing analysis, tournament chronology, practical playbook, counterplay, artwork/flavor discussion, four documentary tournament registrations, preserved official-product archive, article-specific sources, and a validated Editorial V2 research dossier.

Migration ledger after Wave 3:

- **21** benchmark or reviewed-v2 articles
- **252** automated V2 candidates awaiting human approval
- **640** articles requiring deeper editorial/evidence audit
- **592** articles requiring substantive card-specific rewrite

Wave 3 validation baseline:

- Archive core: **1,505 PASS, 0 FAIL**
- Canonical numbered identities: **1,000 PASS, 0 FAIL**
- Historical deck structure: **1,505 PASS, 0 FAIL** across **1,588** documentary components
- Official product archives: **1,505 PASS, 0 FAIL** and **8,252 / 8,252** expected appearances
- Changed-page card previews: **1,110 / 1,110** deck rows linked
- Editorial V2 strict mode: **0 hard failures**; all four Wave 3 pages have zero article-level findings
- Research dossiers: **4 PASS, 0 FAIL**

Cross-article deck fingerprint warnings are expected when one authentic tournament registration documents several featured cards. They remain review signals rather than failures.

See `EDITORIAL-V2-WAVE-3-REPORT.md`, `EDITORIAL-V2-WAVE-3-VALIDATION.md`, and `research-dossiers/editorial-v2-wave-3/`.

## Editorial V2 Wave 4 — August 2, 2026

Wave 4 completes four additional card-specific Editorial V2 reconstructions:

- `327-umezawas-jitte.html`
- `377-tarmogoyf.html`
- `429-splinter-twin.html`
- `468-deathrite-shaman.html`

Each page now contains a distinct historical thesis, original-set and rules context, tournament chronology, practical play and counterplay, artwork/flavor analysis, four documentary tournament registrations, preserved official-product records, article-specific sources, and a validated research dossier.

Umezawa's Jitte includes the May 18, 2026 Modern unban and is current through August 2, 2026. Deathrite Shaman distinguishes its Modern and Legacy policy histories and its legal but structurally weaker Pioneer role. Tarmogoyf is treated as a tournament and design landmark whose decline resulted primarily from creature-quality inflation rather than a ban. Splinter Twin separates the rules of the infinite-creature loop from the strategic "Twin tax" that shaped Modern play.

Migration ledger after Wave 4:

- **25** benchmark or reviewed-v2 articles
- **250** automated V2 candidates awaiting human approval
- **640** articles requiring deeper editorial/evidence audit
- **590** articles requiring substantive card-specific rewrite

Wave 4 validation baseline:

- Archive core: **1,505 PASS, 0 FAIL**
- Canonical numbered identities: **1,000 PASS, 0 FAIL**
- Historical deck structure: **1,505 PASS, 0 FAIL** across **1,594** documentary components
- Official product archives: **1,505 PASS, 0 FAIL** and **8,252 / 8,252** expected appearances
- Changed-page card previews: **571 / 571** deck rows linked
- Focused Editorial V2 strict mode: **0 hard failures**, **186 / 186** substantive paragraphs unique
- Research dossiers: **4 PASS, 0 FAIL**

The deck-semantic suite passes with archive-level warnings retained as review signals. Cross-article fingerprints are expected when one authentic registration documents multiple featured cards; older source-binding and monobasic warnings remain migration work rather than Wave 4 failures.

See `EDITORIAL-V2-WAVE-4-REPORT.md`, `EDITORIAL-V2-WAVE-4-VALIDATION.md`, and `research-dossiers/editorial-v2-wave-4/`.


## Numbered Wave 01 (entries 001–050)

- Review date: 2026-08-02
- Scope: all numbered entries 001 through 050.
- Forty-eight articles received a new card-specific Editorial V2 strategic and tournament brief. Black Lotus remains the benchmark, and Serra Angel retains its previously approved V2 article.
- Fifty research dossiers were added and validated.
- Representative, style-based, novelty, and community reconstructions are labeled `curated-example` rather than `tournament-registration`.
- Mox Ruby and Demonic Tutor received additional documentary lists from already validated project records.
- Lord of the Pit and Shahrazad now state the limits of their tournament evidence instead of manufacturing sanctioned results.


## Reader-facing editorial-label cleanup — August 2, 2026

The user approved the Editorial V2 workflow but does not want internal review/version language displayed inside the articles. All reader-facing `Editorial V2`, reviewed-wave, editorial-status, and research-status notices have been removed. The substantive Numbered Wave 01 synthesis remains in each applicable article as a neutral `Strategic legacy` section. Hidden body metadata, research dossiers, migration ledgers, and audit reports retain workflow status for tooling.

Future waves must follow `canonical/READER-FACING-EDITORIAL-POLICY.md` and pass `tools/validate_no_reader_facing_editorial_labels.py`. Full-size single-project handoffs are acceptable; splitting below 25 MB is no longer required unless specifically requested.

## Numbered Wave 02 (entries 051–100) — August 3, 2026

Numbered Wave 02 processes every article from `051-juzam-djinn.html` through `100-karakas.html`. All fifty pages now carry a reader-facing Strategic legacy chapter with a distinct thesis, practical use, counterplay, and tournament/cultural record. Strong bespoke prose was preserved; the scaffolded cohort also had the most visible repeated opening, origin, technical, format, counterplay, migration, evaluation, and memory language replaced with card-specific material.

Deck provenance was corrected throughout the wave: 157 components remain documentary tournament registrations, while 31 representative, style-based, novelty, archetype, or community constructions are transparently labeled `curated-example`. The wave retains 152 official Wizards product deck records. Fifty article-specific research dossiers were created and validated.

Reader-facing workflow language remains prohibited. Older “Editorial note” labels in the first six pages of the wave were converted to neutral “Source note” labels. Internal workflow state remains in metadata, dossiers, and reports.

Wave 02 validation baseline:

- Archive core: **1,505 PASS, 0 FAIL**
- Canonical numbered identities: **1,000 PASS, 0 FAIL**
- Historical deck structure: **1,505 PASS, 0 FAIL** across **1,600** components
- Deck archive totals: **1,140 article pages PASS**
- Official product archives: **1,505 PASS, 0 FAIL**, **8,252 / 8,252** appearances
- Card-image links: **439,618 / 439,618** deck rows linked
- Research dossiers: **50 PASS, 0 FAIL**
- Reader-facing workflow labels: **0 findings**
- Full bounded release suite: **PASS** at `audit/handoff-validation/20260803T060840Z-full/summary.md`
- Release fingerprint: `6441f73222d64cb0c319afda0c55167a55df46e519b7f1f1d37c5e6f693c2dfd`

The next scheduled task is **Honorable Mention Wave 01**, followed by Numbered Wave 03 (entries 101–150).

## Reader layout correction after Numbered Wave 02

The user reviewed mobile screenshots and established the following binding rules:

- Introduce the featured card before Strategic legacy; the synthesis now follows `#opening` in entries 001–100.
- Previous/next navigation appears once, outside article content. Duplicate footer navigation embedded below source notes was removed.
- Design Echo headings must be card-specific; inherited headings such as “The descendants of the bargain” are prohibited.
- Comparison art is pinned when a current default image is misleading. Arcane Signet uses its original ELD printing instead of a later Captain America treatment.
- Sources use the source-list component, not the printing grid. Sol Ring and Timetwister were repaired.
- Official-product archives use explicit high-contrast mobile/offline colors, and `preconstructed-decks.css` must be included in every wave package.

Run `python tools/validate_reader_layout_contract.py` before packaging every subsequent wave.
