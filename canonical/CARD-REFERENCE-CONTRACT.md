# Canonical Card-Reference Contract

## Authority

The final rendered prose and the checked-in Oracle-name catalog are the authority. `designEcho.cardReferences` is an optional editorial hint for ambiguous one-word names; it is never accepted as an exhaustive declaration.

## Required build sequence

1. Render every article component and all final Design Echo prose.
2. Run `python tools/canonicalize_card_links.py`.
3. Run `python tools/validate_card_links.py`.
4. Publish only when validation passes.

The canonicalizer scans eligible Design Echo prose longest-name-first, recognizes exact multiword Oracle names automatically, recognizes shortened names through article aliases, and recognizes one-word names such as **Persist** in high-confidence comma-separated card lists. It then writes canonical `.card-name` spans and regenerates `data-card-references` from what it actually discovered.

## Canonical markup

```html
<span class="card-name" data-card="EXACT ORACLE NAME" tabindex="0">DISPLAY TEXT</span>
```

The subject card is not repeatedly linked in ordinary article prose. Headings, navigation, Sources, printings, code, and existing anchors are excluded from automatic prose linking. **Deck records are a separate mandatory scope:** every quantity-bearing deck row, including rows for the article subject, must use the canonical markup.

## Catalog maintenance

`canonical/card-name-catalog.json` is the committed offline snapshot. Run `python tools/refresh_card_name_catalog.py` when network access is available to refresh it from Scryfall's complete card-name catalog. CI runs `python tools/refresh_card_name_catalog.py --check` and never requires live network access.

## Validation

Validation independently rescans prose after temporarily removing existing links. It fails when a recognized occurrence is unlinked, partially linked, linked to the wrong Oracle name, omitted from `data-card-references`, or when the declaration contains a name not present in the prose. This prevents an incomplete declaration from allowing an omitted card name to pass.

## Deck previews and double-faced cards

Deck card names are interactive image references, not ordinary anchors. `tools/canonicalize_card_image_links.py` ensures every deck quantity row carries canonical markup and installs the shared card-face runtime. The runtime reads Scryfall `card_faces` data; a true physical double-faced card displays two distinct face images. The namesake lead likewise shows both physical faces and a separate rules panel for each. Validate with `tools/validate_card_image_links.py`.
