# Start Here — Compulsive Research Continuation Package

This folder is the authoritative continuation copy of the **Compulsive Research** Magic: The Gathering article website as of **August 1, 2026**.

## Current state

- **1,000 numbered articles** (`001-...html` through `1000-...html`)
- **505 unnumbered Honorable Mention articles** (`honorable-card-slug.html`)
- **22 Honorable Mention categories**
- **1,505 article pages total**
- Landing page: `index.html`
- Canonical numbered article: `250-eternal-dragon.html`
- Canonical Honorable Mention template: `templates/honorable-article-shell.html`

The latest additions are:

- Five Onslaught Zombies articles: Festering Goblin, Putrid Raptor, Soulless One, Unholy Grotto, and Withered Wretch
- Sleight of Mind, filed under **Archive Favorites**

## How to continue in a new ChatGPT conversation

1. Upload the complete ZIP without extracting or rearranging it.
2. Paste the contents of `NEW-CONVERSATION-PROMPT.txt` into the new conversation.
3. Add the next request at the marked line.
4. Tell the new conversation to treat the uploaded ZIP—not conversation memory or an older build—as the source of truth.

## Read these files first

1. `PROJECT-HANDOFF.md`
2. `NEW-CONVERSATION-PROMPT.txt`
3. `VALIDATION-SUITE.md`
4. `canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md`
5. `canonical/CANONICAL-CONTRACT.md`
6. `archive-manifest.json`
7. `data/honorable-categories.json`
8. `templates/honorable-article-shell.html`
9. `templates/honorable-article-content.schema.json`

## Important operating rules

- Do not restore global numbering to Honorable Mentions.
- Honorable Mention filenames are stable card slugs.
- Previous/next links stay inside the article's category.
- A normal Honorable Mention insertion should modify only the new article, its immediate category neighbors, `index.html`, and rebuilt manifests/data.
- Preserve the card-type filter and landing-page focus anchors.
- Do not invent historical deck registrations, placements, quotations, sources, artists, printings, or design credits.
- Keep `index.html` named exactly `index.html`.

## Validation

Run the focused continuation check:

```bash
python tools/run_validation_suite.py --quick
```

Run the complete suite before a release:

```bash
python tools/run_validation_suite.py --full
```

The GitHub Actions equivalent is in `.github/workflows/validate-archive.yml`.
