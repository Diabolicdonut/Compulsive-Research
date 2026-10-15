# Card-reference discovery migration

## Scope

- Articles processed: **408**
- Articles whose Design Echo reference set or occurrence count changed: **25**
- Net newly linked occurrences: **+13**
- Independent validation: **408/408 passed**

## Newly discovered exact Oracle names

- Basalt Monolith
- Deadly Dispute
- Doomsday
- Edgar Markov
- Grand Abolisher
- Isamaru, Hound of Konda
- Jaheira, Friend of the Forest
- Juzám Djinn
- Kroxa, Titan of Death's Hunger
- Lotus Cobra
- Make Disappear
- Mystic Snake
- Nykthos, Shrine to Nyx
- Persist
- Phyrexian Altar
- Plunge into Darkness
- Unmoored Ego
- Uro, Titan of Nature's Wrath

## Removed stale or partial reference names

- Forest
- Ghalta, Primal Hunger
- Mirari

## Permanent system changes

- `data-card-references` is now generated from final rendered prose instead of trusted as an exhaustive input.
- Exact multiword names use longest-name-first matching.
- High-confidence comma-separated lists recognize one-word card names such as **Persist**.
- `data-card-aliases` resolves intentional shorthand such as **Kroxa**, **Uro**, and **Nykthos**.
- The validator removes existing links in memory and independently rescans prose, so an omitted declaration cannot conceal a missed card.
- The refresh utility can replace the checked-in offline snapshot with Scryfall’s complete card-name catalog when network access is available. CI validates the committed snapshot without making live requests.

## Regression fixtures

The automated fixtures cover Persist, Plunge into Darkness, Jaheira/Forest longest-name matching, Kroxa/Uro aliases, hyphen-suffixed Deadly Dispute-style prose, and ambiguous ordinary words.

## Archive-wide validation

- Wave identity and return links: passed.
- Artwork spotlight validation: 408/408 passed.
- Design Echo structure and image validation: 408 articles / 420 panels passed.
- Printing-gallery identity test: passed.
- Sources heading and placement: passed.
- Canonical Eternal Dragon lock: passed.
- Mechanical audit: A = 265, B = 143, C = 0.
- Regression comparison: no new mechanical issue signatures.

## Environment note

This migration used the checked-in offline catalog snapshot plus confirmed editorial overrides because the execution environment could not reach the live catalog endpoint. The project now includes `tools/refresh_card_name_catalog.py`; running it in a connected environment refreshes the snapshot from the complete official catalog without changing the linking or validation rules.
