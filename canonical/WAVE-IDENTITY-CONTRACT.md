# Canonical article return link and numbered wave identity

Every article uses the landing page and `archive-manifest.json` as the single source of truth for its return-link destination. Every numbered article also uses the manifest as the authority for its Entry · Wave · Wave Title eyebrow.

## Required numbered-article rendering

```html
<a class="archive-link" href="index.html?focus=entry-NNN#entry-NNN">← Back to Compulsive Research</a>
<div class="eyebrow">Entry NNN · Wave XX · EXACT WAVE TITLE</div>
```

## Required Honorable Mention rendering

```html
<a class="archive-link" href="index.html?focus=HONORABLE-ANCHOR#HONORABLE-ANCHOR">← Back to Compulsive Research</a>
```

- The visible return-link text is identical on every article.
- The href remains article-specific so the landing page reopens at the correct numbered entry or Honorable Mention.
- Entry numbers are zero-padded to three digits for entries 001–999.
- Wave numbers are zero-padded to two digits.
- The numbered wave title is copied verbatim from the corresponding landing-page wave heading.
- Labels such as `Historical Constructed`, `Constructed History`, `Modern Foundations`, `Eternal & Combo`, and card-specific taglines are not valid substitutes for the numbered eyebrow.
- Honorable Mentions remain a separate sequence and are not assigned numbered waves.

## Enforcement

- Repair existing pages: `python tools/canonicalize_wave_identity.py`
- Check without changing files: `python tools/canonicalize_wave_identity.py --check`
- The archive validator reports `HERO_RETURN_LINK_TEXT`, `HERO_WAVE_EYEBROW`, or `LANDING_RETURN` for future drift.
