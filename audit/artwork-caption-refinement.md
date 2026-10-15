# Artwork spotlight credit and caption migration

## Canonical standard

Every artwork spotlight now follows the Eternal Dragon / Spelljack convention:

- The first line is exactly **Artist’s original Set artwork**.
- Artist metadata is embedded statically for the exact original printing shown.
- The excerpt discusses the visible subject, object, action, setting, composition, palette/light, motion/gesture, texture, scale, or atmosphere.
- Strategy summaries, rules text, tournament/publication history, Scryfall/catalog notes, and generic “visual identity” boilerplate are rejected.

## Migration result

- Articles inspected: **408**
- Static artist + set credits: **408/408**
- Image-focused excerpts passing the canonical checks: **408/408**
- Original-printing `art_crop` images: **408/408**
- Duplicate excerpt text: **0**
- Validation failures: **0**

## Curated corrections

The migration includes hand-authored spotlight text for Eternal Dragon, Spelljack, Feldon’s Cane, Tarmogoyf, Akroma, Angel of Wrath, and Exalted Angel. All remaining articles now carry a unique, card-named image-focused excerpt or preserved specific visual commentary.

## Future enforcement

The standard is locked in:

- `canonical/ARTWORK-SPOTLIGHT-CONTRACT.md`
- `canonical/GENERATION-PROMPT.md`
- `canonical/CANONICAL-CONTRACT.md`
- `templates/article-shell.html`
- `templates/article-content.schema.json`
- `canonical/artwork-card-metadata.json`
- `tools/canonicalize_artwork_spotlight.py --check`
- `tools/refine_artwork_captions.py --check`
- `tools/validate_archive.py`
- `.github/workflows/validate-archive.yml`
