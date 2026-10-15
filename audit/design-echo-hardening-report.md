# Design Echo hardening report

## Scope

- Articles updated: **408**
- Canonical Design Echo/image-plus-copy panels updated: **420**
- Canonical authority: `250-eternal-dragon.html#descendant`

## Image-loading correction

The previous panels began with a live `api.scryfall.com/...format=image` URL in each `<img src>`. When that request failed, every fallback reused the same API host and the empty image well remained visible as a black rectangle.

The new component now:

1. Starts with a local one-pixel placeholder instead of a network request.
2. Waits until the panel approaches the viewport.
3. Queues panels rather than sending requests in a page-load burst.
4. Resolves exact-card JSON and uses the returned direct static artwork URL.
5. Caches successful direct URLs when browser storage is available.
6. Retries transient JSON failures with backoff.
7. Tries exact art crop, exact normal image, and fuzzy art crop only as sequential last-resort paths.
8. Hides the `<img>` and displays a readable failure label if every source fails, so the component cannot end as an unexplained blank black well.
9. Embeds the runtime in every article so downloaded `content://`/standalone HTML files do not depend on a neighboring JavaScript asset. The hosted site also retains `assets/design-echo.js`.

## Geometry correction

All panels now use the Eternal Dragon geometry:

- Desktop: `1.4fr / 1fr` image-copy split, zero gap, 390px minimum image height.
- Mobile: one column, with image and copy field each reaching the full component width.
- Outer component: transparent, zero padding, zero border, and no black inset frame.
- Copy field: canonical dark green `#20322f`, restrained `#586963` border, and edge-to-edge alignment with the image.
- Failed images are forcibly removed from layout with `display:none!important` before the failure label is shown.

## Future enforcement

Updated:

- `templates/article-shell.html`
- `templates/article-content.schema.json`
- `canonical/DESIGN-ECHO-CONTRACT.md`
- `canonical/CANONICAL-CONTRACT.md`
- `canonical/GENERATION-PROMPT.md`
- `tools/canonicalize_design_echo.py`
- `tools/complete_design_echo_sections.py`
- `tools/validate_design_echo.py`
- `assets/design-echo.js`
- shared canonical CSS assets
- Eternal Dragon canonical snapshot and SHA-256 lock

## Validation

- Canonicalizer idempotence: **passed**
- Design Echo validator: **408 articles / 420 panels / 0 failures**
- Canonical Eternal Dragon lock: **passed**
- Initial live API image URLs remaining in Design Echo `<img src>`: **0**
- Panels using local initial placeholders: **420**
- Articles containing self-contained runtime: **408**
- Full archive audit: **A=1, B=407**, unchanged from the prior classification
- New mechanical issue signatures: **0**

The execution environment could not open local pages in Chromium or make live external image requests, so network rendering was not falsely claimed as tested. Static validation, JavaScript syntax validation, canonical lock verification, and archive-regression checks all passed.
