# Shared-asset migration policy

The shared files in `assets/` are established now, but the existing articles have not been mass-converted. This is deliberate: removing inline CSS or JavaScript from hundreds of pages in the same operation as an audit would create unnecessary risk.

## Future articles

New numbered articles should load:

```html
<link rel="stylesheet" href="assets/compulsive-research.css">
<script defer src="assets/compulsive-research.js"></script>
```

Article-specific art belongs in a small identity-only style block. It must not redefine canonical components.

## Existing articles

Migrate in controlled batches only after mechanical repairs stabilize:

1. Confirm that the article passes the component validator.
2. Compare its inline CSS and JavaScript with the canonical capabilities.
3. Preserve only article-specific art rules and genuinely required content-specific behavior.
4. Add the shared asset links.
5. Remove duplicated canonical CSS and JavaScript.
6. Test desktop and mobile card previews, deck copying, TOC highlighting, navigation, and printing galleries.
7. Rerun the validator and inspect the rendered page before committing.

The canonical snapshot must never be overwritten by a migration.
