# Canonical Design Echo Contract

## Authority

The **Eternal Dragon / Timeless Dragon** section is the visual and structural
authority for every Design Echo image-plus-copy panel in Compulsive Research.

## Locked component

```html
<section id="…" class="design-echo-section">
  <div class="chapter-number">… · Design echo</div>
  <h2>…</h2>
  <p>Introductory comparison…</p>
  <div class="inline-image canonical-inline-image" data-image-card="CARD">
    <div class="image image-loading" data-card-label="CARD">
      <img class="inline-image-media"
           src="data:image/gif;base64,…"
           data-card-name="CARD"
           data-api-url="…"
           data-fallback-art="…"
           data-fallback-normal="…"
           data-fallback-fuzzy="…">
    </div>
    <div class="copy">
      <div class="eyebrow">SET · YEAR</div>
      <h3>Comparative thesis</h3>
      <p>What the later design kept, compressed, redirected, or restrained.</p>
    </div>
  </div>
  <p>Closing interpretation…</p>
</section>
```

## Image reliability

1. The image well contains a real `<img>`; CSS-only backgrounds are forbidden.
2. The initial `src` is a tiny local placeholder, not a live API image lookup.
3. A self-contained runtime waits until the panel nears the viewport, queues
   requests, resolves card JSON to direct static image URLs, caches the result,
   and retries transient failures.
4. Only after direct URLs fail may it try exact `art_crop`, exact `normal`, and
   fuzzy `art_crop` image endpoints, sequentially.
5. Final failure must hide the `<img>` and show a readable label. A blank black
   image well is forbidden.
6. Every article embeds the runtime inline for downloaded standalone use and
   also references `assets/design-echo.js` for the hosted archive.

## Geometry

Desktop uses Eternal Dragon's `1.4fr 1fr` image/copy split, 390px image
minimum, 980px component width, and zero internal gap. The copy field is the
canonical dark green `#20322f` with a restrained `#586963` border. Mobile uses
one column: the image and green copy field each reach the full component edge.
The outer component is transparent, so no black frame or inset can surround
its children.

## Prohibited variants

- `.descendant-panel` or any padded wrapper around the canonical panel
- an empty `.image` div
- card art assigned only through article-specific CSS
- `api.scryfall.com/cards/named?...format=image` as the initial `<img src>`
- green copy cards detached from the image, inset inside a black frame, or
  given bespoke margins, widths, radii, or mobile geometry

## Card-reference discovery

The final Design Echo prose is scanned after rendering by `tools/canonicalize_card_links.py`. Exact Oracle names are discovered from `canonical/card-name-catalog.json`; `cardReferences` is only an optional ambiguity hint. Shortened titles require `cardAliases`. Publication requires `tools/validate_card_links.py`, which removes existing links in memory and independently rescans visible prose so an incomplete declaration cannot hide a missed card name. See `canonical/CARD-REFERENCE-CONTRACT.md`.


## Card-specific heading and image identity

The Design Echo heading is written for the featured card and the specific lineage being discussed. Do not reuse generic headings such as **The descendants**, **The descendants of the bargain**, or a heading copied from another article.

The comparison image must represent the intended comparison, not whichever treatment an API currently returns first. When a card has crossover, showcase, or later promotional treatments that distort the comparison, pin the image resolver to the historically appropriate set or exact printing. Arcane Signet comparisons, for example, use its original Throne of Eldraine Brawl printing rather than a later Universes Beyond treatment.
