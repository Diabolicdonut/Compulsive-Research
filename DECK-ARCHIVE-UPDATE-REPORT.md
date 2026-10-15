# Compulsive Research — Deck Archive and Official Product Rollout

**Update date:** August 1, 2026  
**Scope:** all 1,685 physical article HTML files in the supplied production archive, plus the canonical article, contracts, templates, schemas, renderer, migration tools, workflow, and validators.

## Final production result

- Physical article files scanned: **1,685**
- Active landing-page article links: **1,505**
- Retained unlinked legacy physical files also checked: **180**
- Historical, editorial, and documented digital deck components checked: **6,794**
- Static official-product deck appearances checked: **8,595**
- Total validated deck components: **15,389**
- Articles passing historical deck validation: **1,685**
- Articles passing official-product catalogue validation: **1,685**
- Failures in either deck validator: **0**
- Articles containing at least one qualifying official product deck: **1,139**
- Articles using the required no-product statement: **546**
- Qualifying unique official deck records in the committed catalogue: **1,739**
- Articles with a documentary significant-tournament-impact callout: **320**
- Malformed concatenated totals remaining: **0**

## Static Official Magic the Gathering decks standard

Every article contains one collapsible section labeled exactly **Official Magic the Gathering decks**. The outer section and every product deck are collapsed by default.

For cards appearing in qualifying official products, the article statically embeds every matching complete published decklist from the committed catalogue snapshot. The deck is formatted like the other Deck Archive entries and includes calculated totals, card groups, copy text, product metadata, and all applicable zones. A product that has no sideboard remains without a sideboard.

For cards that do not appear in a qualifying official product, the section remains present and contains exactly:

> No official Magic the Gathering products contained this particular card.

The implementation is deliberately offline. Browser fetching, `preconstructed-decks.js`, and placeholder text such as “Open this section to load” are forbidden.

## Catalogue scope

The committed snapshot includes ready-to-play commercial, introductory, commemorative replica, and official digital deck products, including theme decks, starter and sample decks, Intro Packs, Duel Decks, Event and Challenger Decks, Commander products, Planeswalker Decks, Game Night, Welcome Decks, Jumpstart half-decks, World Championship Deck replicas, and comparable published products.

Non-deck distributions are excluded, including redemption sets, randomized or fixed card assortments, Deck Builder’s Toolkit modules, ordinary Secret Lair drops, land packs, and collector sets. Exact duplicate SKU variants with identical contents are deduplicated.

Authority:

- `data/official-mtg-deck-catalogue.json`
- `canonical/DECK-ARCHIVE-CONTRACT.md`
- `tools/render_official_mtg_deck_sections.py`

## Count correction

Visible card rows are the sole numerical authority. Every quantity is parsed as an integer and added. The calculated results are synchronized across group headings, main-deck and sideboard metadata, provenance prose, HTML data attributes, and copy-decklist text.

Neither validator assumes a 60-card main deck or a 15-card sideboard. Documented historical exceptions and official products without sideboards are preserved instead of normalized away.

## Validation rules

The historical validator independently recalculates the existing tournament/editorial deck components while excluding the new official-product entries from double counting.

The official-product validator independently compares every article against the committed catalogue and fails on:

- Missing or duplicated official sections
- Wrong section label or default-open state
- Missing, extra, or mismatched product IDs
- A product that does not contain the article card
- Incorrect card contents or subject-card copy count
- Incorrect main, sideboard, commander, display-commander, plane, or scheme totals
- Incorrect group headings, data attributes, or copy text
- Missing required empty-state text
- Remaining runtime-loader scripts or network-fetch placeholders

## Validation evidence

- `historical-deck-validation/deck-validation.json`
- `historical-deck-validation/deck-validation.md`
- `official-mtg-deck-validation/official-mtg-deck-validation.json`
- `official-mtg-deck-validation/official-mtg-deck-validation.md`
- `OFFICIAL-MTG-DECK-IMPLEMENTATION-REPORT.md`

The two independent deck validators completed successfully. A separate broader legacy suite attempt that timed out is documented independently and is not treated as a completed full-suite pass.
