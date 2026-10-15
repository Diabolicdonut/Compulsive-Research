# Hero Identity Contract

Every numbered article must identify its own card in the top-page hero artwork while presenting only the thematic editorial title as visible heading text.

## Required behavior

- The visible `img.hero-media`, when present, must resolve to the article card.
- Its `onerror` fallback must resolve to the same card.
- The final CSS hero fallback must resolve to the same card.
- Entries 401–1000 use a plain thematic `h1`; `.hero-card-name` and `.hero-title` wrappers are forbidden.
- The card identity remains available in `body[data-article-card]`, `header.hero[data-hero-card]`, `header.hero[data-headline-card]`, `img.hero-media[data-hero-card]`, and `h1[data-headline-card]`.
- Different article cards may not share one resolved hero identity.
- The generator may not contain a fixed card-name or fixed hero-image literal.

Legacy entries that intentionally use a CSS-only hero remain valid when the effective CSS image resolves to the article card. The frozen Eternal Dragon authority remains byte-identical.

## Enforcement

Run:

```bash
python tools/validate_hero_migration.py --output-dir audit/hero-migration
```

The validator writes CSV, JSON, and Markdown reports and exits nonzero on any mismatch.

## Headline extension

Hero validation also enforces `canonical/HEADLINE-IDENTITY-CONTRACT.md`: all 1,000 numbered articles must use unique thematic titles without full card-name leakage. The combined suite remains `tools/validate_hero_migration.py`.
