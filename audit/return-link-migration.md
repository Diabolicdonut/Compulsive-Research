# Canonical “Back to Compulsive Research” return-link migration

## Canonical rule

Every article now uses the same visible hero return label:

```html
<a class="archive-link" href="ARTICLE-SPECIFIC-LANDING-ANCHOR">← Back to Compulsive Research</a>
```

The visible text is universal. The href remains specific to each article so returning to the landing page reopens at the correct numbered entry or Honorable Mention.

Numbered articles continue to display their manifest-derived identity separately:

```html
<div class="eyebrow">Entry NNN · Wave XX · EXACT WAVE TITLE</div>
```

## Migration result

- Total existing article files updated: **408**
- Numbered articles updated: **401**
- Honorable Mention articles updated: **7**
- Landing-page destinations changed: **0**
- Article prose, sections, decklists, printings, sources, CSS, and JavaScript changed: **0**

A byte-level comparison against the preceding canonicalized package confirmed that every article difference was confined to its hero `.archive-link` element.

## Canonical infrastructure updated

- `250-eternal-dragon.html`
- `canonical/250-eternal-dragon.canonical.html`
- `canonical/250-eternal-dragon.sha256`
- `canonical/canonical-lock.json`
- `canonical/CANONICAL-CONTRACT.md`
- `canonical/GENERATION-PROMPT.md`
- `canonical/WAVE-IDENTITY-CONTRACT.md`
- `templates/article-shell.html`
- `tools/canonicalize_wave_identity.py`
- `tools/validate_archive.py`
- `.github/workflows/validate-archive.yml`

## Verification

The following checks pass:

```text
python tools/canonicalize_wave_identity.py --check
python tools/check_canonical_lock.py
python tools/build_manifest.py
python tools/validate_archive.py --output-dir audit/current-return-link
python tools/check_audit_regression.py audit/baseline-2026-07-29.json audit/current-return-link/audit-report.json
```

Results:

- Canonical hero identity drift: **0 articles**
- Canonical Eternal Dragon lock: **verified**
- Manifest navigation drift: **none**
- New mechanical regression signatures: **none**
- Existing audit classification: **A = 1, B = 407, C = 0**

The remaining Category B repair queue is unchanged and was not broadened by this migration.
