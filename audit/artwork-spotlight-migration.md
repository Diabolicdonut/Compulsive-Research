# Artwork spotlight canonicalization

## Migration scope

- Articles inspected and updated: **408**
- Existing artwork spotlights normalized and repositioned: **360**
- Articles that previously lacked a spotlight and received one: **48**
- Existing card-specific excerpts preserved: **266**
- Generic or missing excerpts replaced with card-specific text: **142**
- Artist credits embedded directly from existing or verified metadata: **115**
- Legacy artist credits resolved from the exact original Scryfall printing at page load: **293**

## Canonical result

Every numbered and Honorable Mention article now has exactly one artwork spotlight after the second substantive article section. The component uses the Eternal Dragon convention: full viewport width, `art_crop`, `object-fit: cover`, `center 25%`, desktop height `min(69vw, 720px)`, mobile height `72vh`, a lower readability gradient, and the credit plus excerpt over the image.

The old narrow inset override was superseded archive-wide. The prohibited generic sentence, “The original illustration became inseparable from the card’s first strategic identity,” no longer appears as a spotlight excerpt.

## Future enforcement

The canonical article snapshot, shared CSS, artwork metadata script, article template, JSON schema, generation prompt, canonical contract, lock file, migration utility, and validator now define the same artwork component. Future articles must provide a verified artist and card-specific excerpt before publication.

## Validation

A full structural pass found **0 artwork-spotlight failures across 408 articles**: one spotlight per article, correct placement, nonempty original-set metadata, `art_crop` image, caption credit, excerpt, canonical CSS lock, and metadata script.
