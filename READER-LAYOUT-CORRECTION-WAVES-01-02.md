# Reader layout correction — Numbered Waves 01–02

Date: 2026-08-03

## User-reported defects corrected

1. **Strategic Legacy placement** — the section now follows `#opening` in every processed entry 001–100. The table of contents follows the same order. Readers encounter the featured card and its initial explanation before use or counterplay guidance.
2. **Duplicate previous/next navigation** — 37 embedded footer navigation blocks were removed. Every processed article now has exactly one previous/next block in the neutral Continue reading section outside article content.
3. **Design Echo titles** — eight inherited or generic headings were replaced with card-specific headings. “The descendants of the bargain,” “The descendants,” and “Every Mox after the Moxen” are prohibited by validation.
4. **Sol Ring and Timetwister sources** — malformed source grids were converted to ordinary source lists, restoring readable one-record-at-a-time formatting on mobile.
5. **Arcane Signet comparison art** — comparison panels now pin Arcane Signet to its original Throne of Eldraine Brawl printing instead of allowing the API to select a later crossover treatment.
6. **Official Magic product readability** — the official-product archive now uses a solid dark field, explicit light text, readable scope notes, and mobile-safe title/count wrapping.
7. **Packaging** — `preconstructed-decks.css` is included in the correction package and is now a required shared asset for all future wave packages.

## Template and validation updates

- `templates/article-shell.html` now places `{{STRATEGIC_LEGACY_HTML}}` after the opening section.
- Both article content schemas define the Strategic Legacy component.
- `canonical/READER-FACING-EDITORIAL-POLICY.md`, `canonical/DESIGN-ECHO-CONTRACT.md`, and `canonical/GENERATION-PROMPT.md` contain the new rules.
- `tools/validate_reader_layout_contract.py` is part of the quick and full bounded release suites.
- `tools/repair_reader_layout_after_wave02.py` records the deterministic repair.

## Validation

- Reader layout contract: PASS for entries 001–100.
- Duplicate embedded end navigation: 0 remaining in processed entries.
- Generic prohibited Design Echo titles: 0 remaining in processed entries.
- Malformed Sources printing grids: 0 remaining.
- Focused card-image links: 52,776 / 52,776.
- Focused deck archives: 424 / 424 components passed.
- Focused historical deck structure: 424 / 424 components passed.
- Focused official-product appearances: 876 / 876.
- Canonical identity, editorial quality, and deck semantics full-corpus validators: PASS.
- Bounded full release suite: PASS.

Current corpus fingerprint:

`a33366a6423130da730a0674944029622ad605b28fc94373235d68a34673e34f`
