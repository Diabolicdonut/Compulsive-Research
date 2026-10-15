# Headline Convention Contract

Every numbered article uses a unique thematic editorial title in the established entries 001–400 convention: the title describes the card without repeating the card's full name.

## Required behavior

- The visible hero headline must be nonempty, card-relevant, and editorial rather than a shared category label.
- No two numbered articles may share the same normalized hero headline.
- The complete normalized card name may not appear inside the thematic headline.
- Generated pages may not display a separate card-name line above the hero headline.
- The canonical authority is `data/editorial-headlines.json`, read through `tools/headline_identity.py`.
- The former shared generator titles, including “The Mana Base as Strategy” and “A Body With Immediate Consequences,” are forbidden.
- The hero headline, document `<title>`, `meta[name="article-headline"]`, opening-section heading, and opening table-of-contents label must agree on generated pages.
- Generated pages identify the subject in metadata and data attributes—`body[data-article-card]`, `header.hero[data-headline-card]`, and `h1[data-headline-card]`—without adding the card name to the visible title.
- Headlines are limited to twelve words for the established mobile presentation.

## Enforcement

Run:

```bash
python tools/validate_headline_identity.py --output-dir audit/headline-convention
```

The validator writes CSV, JSON, and Markdown reports and exits nonzero on duplicate, generic, card-name-bearing, overlong, mismatched, or stale-template headlines.
