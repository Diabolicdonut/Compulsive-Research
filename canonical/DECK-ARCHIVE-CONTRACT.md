# Deck Archive Contract

## Authority

Card rows are the only authority for deck size. Every displayed total is a derived integer sum. A generator must never join quantity strings, copy an existing display total, assume 60/15, or silently normalize a historical registration.

## Required total pipeline

For every `details.deck`:

1. Parse each `.row .qty` as a positive integer.
2. Sum rows inside each `.group` and write the result to the group heading.
3. Track the zones separately: main deck, sideboard, commander, display commander, planar deck, and scheme deck.
4. Write the derived values to the corresponding `data-*` attributes, provenance sentence, `.deck-meta .small`, group headings, and hidden copy-decklist text.
5. Run `tools/canonicalize_copy_decklists.py` after changing any historical deck row.
6. Run both deck validators before release.

For tournament registrations and curated examples, groups other than Sideboard/Side board/Maybeboard are main-deck groups. For static official products, Commander, Display commander, Planar deck, and Scheme deck are supplemental zones and must not be added to `data-main-count`.

Unusual historical sizes are preserved when documentary evidence supports them. A published 61-card main deck, 16-card sideboard, or incomplete transcription is not forcibly converted to 60/15. Confirmed exceptions use `data-source-size-exception` and an explanatory provenance note. An unidentified card remains an explicit `Unknown Card` row rather than an invented identity.

## Deck kinds

Every deck declares one `data-deck-kind`:

- `tournament-registration` — sourced historical registration;
- `curated-example` — manually reviewed, format-legal example with an explicit legality date and non-tournament provenance;
- `official-digital-deck` — documented digital opponent or product list in the historical archive;
- `official-mtg-product` — statically embedded official Magic product deck from the committed catalogue snapshot.

Official products commonly have no sideboard. Zero is valid, must be displayed as `No sideboard`, and must never be padded to fifteen cards.


## Editorial V2 production rule

`editorial-study` is retired and forbidden in production. Existing synthetic study
shells must be removed rather than repaired. A card with no verified historical list
may show an empty documentary archive and a transparent research-pending note.

See `canonical/EDITORIAL-V2-CONTRACT.md` and
`canonical/DECK-SEMANTICS-CONTRACT.md`.

## Significant tournament impact

When a documentary tournament registration shows the article card in a winning list or at a major event—World Championship, Pro Tour, Players Championship, Mythic Championship, Invitational, Grand Prix, Nationals, or equivalent—the article includes a concise `.tournament-impact` callout.

Use conservative language such as “appeared in” or “was part of.” Identify the player, event, result, date, and copies when supported. Never claim the card alone caused the finish. Unsupported anecdotes are omitted or explicitly identified as unverified.

## Static Official Magic the Gathering decks section

Every article contains exactly one outer component:

```html
<!-- CR_OFFICIAL_MTG_DECKS_START -->
<details class="preconstructed-archive official-mtg-decks" ...>
  ...
</details>
<!-- CR_OFFICIAL_MTG_DECKS_END -->
```

Requirements:

- The visible label is exactly **Official Magic the Gathering decks**.
- The outer `details` element is collapsed by default.
- Every individual `details.deck.official-mtg-deck` is collapsed by default.
- Product decklists are written directly into the article HTML at build time; no browser fetch or `preconstructed-decks.js` loader is permitted.
- The committed source is `data/official-mtg-deck-catalogue.json`.
- Every qualifying catalogue product containing the article card is embedded once, in chronological order.
- Exact duplicate SKU variants with identical contents are deduplicated; the ordinary product name is preferred over Amazon or collector-finish variants.
- Products without sideboards remain without sideboards.
- If no qualifying product contains the card, the collapsed summary displays exactly `0`, while the opened section contains exactly: `No official Magic the Gathering products contained this particular card.`
- The article’s `data-official-deck-count` must equal the catalogue-derived product count.
- Every product ID, card row, quantity, zone count, subject-card copy count, and hidden copy list must match the snapshot.

Qualifying records are ready-to-play commercial, introductory, commemorative replica, or official digital decks, including theme, starter, Intro Pack, sample, Welcome, Duel, Commander, Planeswalker, Event, Challenger, World Championship replica, Jumpstart, Game Night, Planechase, Archenemy, Guild Kit, and comparable products. Named 20-card Beginner Box half-decks qualify. Redemption sets, ordinary Secret Lair drops, Deck Builder’s Toolkit modules, Welcome Boosters, land bundles, collector assortments, and other non-deck fixed contents do not.

## Card-image links and physical double-faced cards

Every quantity-bearing `.row` in every historical, editorial, digital, and official-product deck wraps the displayed card name in canonical card-reference markup:

```html
<span class="card-name" data-card="EXACT ORACLE NAME" tabindex="0">DISPLAY NAME</span>
```

This includes the article's namesake card. The ordinary prose rule against repeatedly linking the subject card does **not** apply inside decklists. An explicitly unidentified source slot uses `.source-unknown-card [data-card-unknown="true"]` and is not treated as a card identity.

The shared preview runtime resolves the Scryfall Card object. When `card_faces` supplies two independently imaged physical faces, both face images are displayed. It must never perform a second named-card image lookup for the reverse face, because that can return the front image again. The namesake `.card-lead` uses `data-dfc-mode="auto"`; physical double-faced cards display both face images and one separate rules panel per face. Split, aftermath, and Adventure cards remain a single printed-card image when their face objects do not carry separate image URIs.

Run `tools/canonicalize_card_image_links.py` after rendering deck rows and `tools/validate_card_image_links.py` before release.

## Known historical transcription resolutions

Run `tools/repair_known_historical_deck_anomalies.py` before final validation. Current resolutions include:

- Ben Rubin, Pro Tour New York 2000: use the sourced 15-card retrospective sideboard rather than the conflicting 16-card transcription.
- Justin Gary, Pro Tour Rome 1998: preserve the published 16-card sideboard and mark the source-size exception.
- Nicolas Olivieri, Pro Tour Osaka 2002: preserve the unidentified fifteenth slot as `Unknown Card`.
- Thought Invoker: classify the Shandalar list as `official-digital-deck`, not a tournament registration.

## Required commands

```bash
python tools/repair_known_historical_deck_anomalies.py --root PATH_TO_SITE --check
python tools/canonicalize_copy_decklists.py --root PATH_TO_SITE --check
python tools/render_official_mtg_deck_sections.py --root PATH_TO_SITE --check
python tools/validate_deck_archives.py --root PATH_TO_SITE --jobs 4
python tools/validate_official_mtg_decks.py --root PATH_TO_SITE --jobs 4
python tools/canonicalize_card_image_links.py PATH_TO_SITE --check
python tools/validate_card_image_links.py --root PATH_TO_SITE --jobs 4
```

`validate_deck_archives.py` verifies the 6,794 historical/static archive decks and tournament-impact rules. `validate_official_mtg_decks.py` independently compares every embedded official product section against the committed catalogue snapshot.
