# Design Echo permanent fix

## Authority

`250-eternal-dragon.html#descendant` remains the canonical visual and structural authority.

## Root cause

The blank panels were not ordinary broken `<img>` elements. Many articles used an empty `.image` div and supplied the artwork only through article-specific CSS. A failed CSS background request cannot run an image `onerror` recovery chain, so the component remained as a large black image well. The archive also contained legacy `.descendant-panel` rules that added alternate padding, borders, heights, and mobile geometry.

## Migration

- 408 articles checked; all 408 now contain a canonical Design Echo panel.
- 420 canonical image-plus-copy panels are present.
- 298 pre-existing inline panels were migrated.
- 138 legacy `.descendant-panel` elements were eliminated, including 97 standalone legacy boxes.
- 25 text-only Design Echo sections received a canonical visual panel.
- Every panel now uses `section.design-echo-section > .inline-image.canonical-inline-image`.
- Every copy field now uses the Eternal Dragon sequence: `.eyebrow`, `h3`, and explanatory paragraph copy.
- No `.descendant-panel` element or CSS rule remains.

## Image recovery

Each panel now contains a real `img.inline-image-media` and uses this recovery order:

1. exact-card `art_crop`;
2. exact-card `normal`;
3. fuzzy-name `art_crop`;
4. readable in-panel failure label.

The inline recovery handler keeps downloaded standalone HTML functional; `assets/design-echo.js` supplies the shared runtime behavior.

## Future enforcement

The canonical template, structured-content schema, generation prompt, Design Echo contract, shared CSS and JavaScript, migration tools, validator, canonical SHA lock, and GitHub Actions workflow now enforce the Eternal Dragon component.

## Validation

- Design Echo validation: 408/408 articles, 420/420 panels, 0 failures.
- Canonical wave and return-link check: passed.
- Artwork spotlight structure and caption checks: passed.
- Mechanical audit: A=1, B=407; no new issue signatures introduced.
