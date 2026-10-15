# Numbered article wave-eyebrow migration

## Current canonical rule

Every article now uses the same visible landing-page return label, while every numbered article renders its wave identity from the corresponding landing-page record:

```html
<a class="archive-link" href="index.html?focus=entry-NNN#entry-NNN">← Back to Compulsive Research</a>
<div class="eyebrow">Entry NNN · Wave XX · EXACT WAVE TITLE</div>
```

The exact wave title comes from `index.html` through `archive-manifest.json`. Editorial labels such as **Historical Constructed**, **Constructed History**, **Modern Foundations**, **Eternal & Combo**, and card-specific taglines are not permitted in the numbered eyebrow.

## Original wave-eyebrow migration result

- Present numbered articles checked: **401**
- Numbered articles whose wave identity was corrected: **384**
- Numbered articles already matching the exact manifest-derived wave identity: **17**
- Honorable Mentions changed by the original wave migration: **0**
- Article prose, sections, decklists, printings, sources, CSS, and JavaScript changed by that migration: **0**

A normalized comparison against the pre-migration package confirmed that the original 384 article changes were limited to the hero `.archive-link` and `.eyebrow` elements. A later archive-wide migration standardized the visible `.archive-link` text to `← Back to Compulsive Research` on all numbered and Honorable Mention articles while retaining each article-specific landing anchor.

## Examples

- Entry 205: `Entry 205 · Wave 05 · Masques, Invasion, Odyssey, and Onslaught`
- Entry 250: `Entry 250 · Wave 05 · Masques, Invasion, Odyssey, and Onslaught`
- Entry 605: `Entry 605 · Wave 13 · Kaldheim, Strixhaven, Midnight Hunt, and Modern Horizons 2`

## Future enforcement

- `tools/canonicalize_wave_identity.py` repairs the canonical return link on every article and the manifest-derived eyebrow on numbered articles.
- `python tools/canonicalize_wave_identity.py --check` fails when either system drifts.
- `tools/validate_archive.py` reports `HERO_RETURN_LINK_TEXT`, `HERO_WAVE_EYEBROW`, or `LANDING_RETURN` for mismatches.
- `.github/workflows/validate-archive.yml` runs the identity check on every push and pull request.
- `canonical/GENERATION-PROMPT.md` and `templates/article-shell.html` require the same format for future articles.

## Canonical snapshot

The Eternal Dragon snapshot and SHA-256 lock were deliberately refreshed after each approved archive-wide canonical migration. Article prose was not changed by either identity migration.
