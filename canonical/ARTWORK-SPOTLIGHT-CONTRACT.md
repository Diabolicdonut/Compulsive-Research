# Canonical artwork spotlight contract

Eternal Dragon and Spelljack are the editorial references for every Compulsive Research artwork spotlight.

## Locked presentation

- Exactly one `.art-break.artwork-spotlight` appears after the second substantive article section.
- The exact original printing is shown through an `art_crop` image.
- The image remains full viewport width with `object-fit: cover`, `object-position: center 25%`, desktop height `min(69vw, 720px)`, and mobile height `72vh`.
- `.art-caption` remains over the lower portion of the image with the canonical gradient.

## Required credit line

The first line always follows this exact pattern:

```text
ARTIST’S original SET artwork
```

Example:

```text
Justin Sweet’s original Scourge artwork
```

`data-artwork-artist`, `data-artwork-set`, and `data-artwork-set-name` are required static metadata for the exact printing shown. A missing artist may not be replaced by a set-only heading or deferred to a runtime lookup.

## Required excerpt

The second line contains one or two short sentences about the visible image itself. It must:

1. Identify or clearly evoke a visible subject, object, action, or setting.
2. Discuss at least one visual quality: composition or framing; palette, light, or shadow; motion or gesture; texture; scale; or atmosphere.
3. Be specific to that card’s illustration rather than reusable boilerplate.

Good model:

> A blue-robed mage clings to a tree while physically pulling a green spell away from its path. The image makes the card’s joke literal: this is less a formal counter than magical highway robbery.

Forbidden approaches include:

- Strategic or rules summaries
- Tournament or publication history
- Scryfall, database, or catalog-display notes
- Statements that the art merely established, preserved, or embodied the card’s strategic or visual identity
- Generic claims that could be pasted under an unrelated image

## Enforcement

- `templates/article-shell.html` fixes the markup.
- `templates/article-content.schema.json` requires static artist, set, image, and excerpt fields.
- `canonical/GENERATION-PROMPT.md` governs future article generation.
- `tools/canonicalize_artwork_spotlight.py --check` verifies layout, static credit format, and excerpt quality.
- `tools/validate_archive.py` reports violations during every archive audit.
- `tools/refine_artwork_captions.py` is the controlled migration utility for legacy captions when verified card metadata is supplied.
