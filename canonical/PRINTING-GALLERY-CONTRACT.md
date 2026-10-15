# Canonical printing-gallery contract

The visual structure remains governed by `250-eternal-dragon.html`, while identity and selection are enforced by the gallery runtime and validators.

## Identity contract

1. Resolve the article subject through Scryfall's exact-name endpoint.
2. Follow that exact card object's `prints_search_uri`.
3. Accept a candidate only when its `oracle_id` equals the resolved card's Oracle ID **and** its normalized name equals the resolved exact name.
4. Require English, paper, nondigital card objects with a usable card image.
5. Never use `include:extras` for printing galleries or printing-catalog source links.
6. Cached records are rejected unless every record has the exact card name, one shared Oracle ID, a unique Scryfall printing ID, and an image.

## Selection contract

1. Display no more than **12** printings.
2. If fewer than 12 legitimate printings exist, display all of them.
3. Keep the original printing first chronologically.
4. Prioritize one representative from each distinct `illustration_id` before filling remaining slots with same-art reprints.
5. After artwork diversity, favor historically distinctive products, frames, promos, and chronological coverage.

## Published structure

```html
<div class="printings canonical-printing-gallery"
     id="printing-grid"
     data-card="CARD NAME"
     data-original-set="set"
     data-gallery-mode="hydrate"
     data-gallery-max="12"
     data-identity-policy="exact-name-and-oracle-id"
     data-selection-policy="unique-artwork-first">
  <!-- one to twelve verified static fallback figures -->
</div>
<h3>Sources</h3>
```

The verified runtime replaces the fallback only after all records pass identity validation. On failure, the existing exact original-printing fallback remains. Visible loading and failure boxes are forbidden.

## Validation

```bash
node tools/test_printing_gallery_identity.js
python tools/canonicalize_printing_galleries.py --check
python tools/validate_archive.py --jobs 4 --output-dir audit/current
```
