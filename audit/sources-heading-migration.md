# Sources Heading Migration

Date: 2026-07-30

## Result

- Articles processed: **408**
- Articles changed: **407**
- Missing headings inserted: **343**
- Legacy `Research sources` headings renamed: **64**
- Already canonical: **1** (Eternal Dragon)
- Validation: **408/408 passed**
- Article prose and source records rewritten: **No**

## Canonical order

```html
<div class="printings">…card gallery…</div>
<h3>Sources</h3>
<ol class="sources">…source records…</ol>
```

Legacy source-record container classes were preserved during this targeted migration. The visible heading and its placement now match Eternal Dragon across the archive.

## Permanent enforcement

- Template: `templates/article-shell.html`
- Contract: `canonical/SOURCES-CONTRACT.md`
- Generation rules: `canonical/GENERATION-PROMPT.md`
- Canonicalizer/check: `tools/canonicalize_sources_heading.py --check`
- Mechanical audit: `tools/validate_archive.py`
- CI: `.github/workflows/validate-archive.yml`
