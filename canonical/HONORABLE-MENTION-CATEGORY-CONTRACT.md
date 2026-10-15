# Honorable Mention category and navigation contract

## Purpose

Honorable Mentions are an open-ended supplemental archive. They do **not** use a
global sequence number. Stable card-based filenames and category-local navigation
allow one shelf to change without renumbering or rebuilding every other article.

## Stable filename

Every article uses:

```text
honorable-CARD-SLUG.html
```

Examples:

```text
honorable-goblin-bombardment.html
honorable-the-ur-dragon.html
honorable-fire-ice.html
```

A filename beginning `honorable-001-`, `honorable-094-`, or any other ordinal is
invalid. Existing numbered URLs are tracked in the migration deletion manifest,
not retained as canonical article filenames.

## Landing-page shelf

Every article appears exactly once inside:

```html
<details class="honorable-category-panel"
         data-honorable-category="CATEGORY">
  ...
  <a class="honorable-entry"
     id="honorable-CARD-SLUG"
     href="honorable-CARD-SLUG.html">...</a>
</details>
```

The card-type filter continues to use `data-card-types`. Search and filter logic
must hide empty shelves and open only shelves containing matching entries.

## Article identity

The body declares both identities:

```html
<body data-article-card="CARD NAME"
      data-honorable-category="CATEGORY">
```

The hero badge names the category, never an ordinal. The article return link is:

```text
index.html?focus=honorable-CARD-SLUG#honorable-CARD-SLUG
```

## Navigation boundary

Both `.rank-nav` and `.end-nav` link only to the immediate previous and next
articles in the same landing-page category. The first and last articles use a
`.nav-placeholder` on the missing side. Cross-category previous/next links are
forbidden.

No visible text may use `Honorable 017`, `Honorable Mention 94 of 180`, or any
other global position. A category name may be shown in the center of the nav.

## Insertion workflow

1. Add the new stable article file.
2. Insert its landing card inside the appropriate category.
3. Update only the new article and its immediate category neighbors.
4. Rebuild `archive-manifest.json`.
5. Run `python tools/validate_honorable_categories.py`.

No unrelated Honorable Mention article should change during a normal insertion.
