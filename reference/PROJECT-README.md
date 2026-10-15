# Compulsive Research

**Compulsive Research** is a long-form static website about the history, strategy, artwork, tournament use, and cultural legacy of individual *Magic: The Gathering* cards.

## Archive inventory

- **1,000 numbered articles**
- **505 categorized Honorable Mention articles**
- **22 Honorable Mention categories**
- **1,505 article pages total**
- Landing page: [`index.html`](index.html)

The site is self-contained and can be published directly through GitHub Pages from the repository root.

## Continue the project

Read these files before making changes:

1. [`START-HERE.md`](START-HERE.md)
2. [`PROJECT-HANDOFF.md`](PROJECT-HANDOFF.md)
3. [`NEW-CONVERSATION-PROMPT.txt`](NEW-CONVERSATION-PROMPT.txt)
4. [`VALIDATION-SUITE.md`](VALIDATION-SUITE.md)
5. [`canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md`](canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md)
6. [`canonical/CANONICAL-CONTRACT.md`](canonical/CANONICAL-CONTRACT.md)

The canonical numbered article is [`250-eternal-dragon.html`](250-eternal-dragon.html). The reusable Honorable Mention template is [`templates/honorable-article-shell.html`](templates/honorable-article-shell.html).

## Honorable Mention architecture

- Honorable Mentions are **not globally numbered**.
- Filenames use stable card slugs: `honorable-card-name.html`.
- Articles are grouped into category shelves on the landing page.
- Previous/next navigation remains inside the article’s category.
- A normal insertion changes only the new article, its immediate category neighbors, `index.html`, and rebuilt manifests.

## Validation

Install the Python dependency:

```bash
python -m pip install -r requirements.txt
```

Run the focused continuation suite:

```bash
python tools/run_validation_suite.py --quick
```

Run the complete release suite:

```bash
python tools/run_validation_suite.py --full
```

GitHub Actions runs the archive validation workflow on pushes and pull requests through [`.github/workflows/validate-archive.yml`](.github/workflows/validate-archive.yml).

## GitHub Pages

After committing the extracted repository contents:

1. Open **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select the primary branch and the **`/ (root)`** folder.
4. Save the setting.

Keep `index.html` in the repository root. The included `.nojekyll` file tells GitHub Pages to serve the static project without Jekyll processing.

## Important qualification

The mechanical validation suite checks templates, identities, navigation, galleries, manifests, and other structural rules. A mechanical pass does not independently prove every historical claim, quotation, deck provenance, or source interpretation in the editorial archive.
