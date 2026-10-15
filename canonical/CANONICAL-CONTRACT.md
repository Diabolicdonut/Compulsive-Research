# Compulsive Research Canonical Article Contract

## Authority

`250-eternal-dragon.html` is the canonical published article. An immutable snapshot is stored as `canonical/250-eternal-dragon.canonical.html`; its SHA-256 digest is recorded in `canonical/250-eternal-dragon.sha256` and `canonical/canonical-lock.json`.

The canonical article is the structural authority for all numbered articles generated after this freeze. Visual and behavioral consistency takes priority over incidental redesign. Editorial specificity, evidence quality, and card-appropriate organization are governed separately by the Editorial V2 contract. A template change must be proposed and reviewed separately, then applied archive-wide as a deliberate migration.

## Locked systems

Future article generation must preserve the following systems and their component conventions:

1. **Header and hero** — `header.hero`, `.hero-grid`, `.hero-inner`, `.archive-link`, `.eyebrow`, `h1`, `.deckline`, `.byline`, and `.pill`. Every article uses the exact visible return label `← Back to Compulsive Research`; its href is the article-specific landing-page anchor supplied by `archive-manifest.json`. Every numbered article separately uses the exact eyebrow `Entry NNN · Wave XX · WAVE TITLE`. The wave title must match the landing page and manifest exactly; editorial lens labels such as “Historical Constructed,” “Constructed History,” “Modern Foundations,” or card-specific taglines are forbidden in the eyebrow.
2. **Numbered navigation** — `.rank-nav`, its centered archive position, and the canonical boundary behavior at entries 1 and 1000.
3. **Table of contents** — `.toc` links must use local fragments and every fragment must resolve to exactly one article section ID.
4. **Section formatting** — article chapters remain direct descendants of `article.article`, have unique IDs, use `.chapter-number`, and contain an `h2`.
5. **Card-reference links** — secondary card references use exactly `<span class="card-name" data-card="ORACLE CARD NAME" tabindex="0">DISPLAY NAME</span>`. The subject card is not repeatedly linked in ordinary prose. Every quantity-bearing deck row, including a subject-card row, is required to use this markup.
6. **Artwork spotlight** — every article contains exactly one `.art-break.artwork-spotlight` after the second substantive article section. It uses a full-viewport original-printing `art_crop` image in `.art-break-media`, `object-fit: cover`, the Eternal Dragon `center 25%` crop, desktop height `min(69vw, 720px)`, mobile height `72vh`, the canonical lower gradient, and `.art-caption` over the image. `[data-artwork-artist]` is mandatory static metadata verified for that exact printing. The visible `[data-artwork-credit]` line is exactly `ARTIST’S original SET artwork`. `.art-caption-excerpt` contains one or two sentences about visible imagery—subject/object/action/setting plus composition, framing, palette, light, shadow, motion, gesture, texture, scale, or atmosphere. Strategy, rules function, tournament/publication history, catalog/database notes, and generic “identity” boilerplate are forbidden.
7. **Design echo and inline image panels** — use the immutable `.inline-image.canonical-inline-image` component documented in `canonical/DESIGN-ECHO-CONTRACT.md`. It embeds a self-contained queued image resolver, never starts with a live API image URL, shows a readable final fallback, and uses Eternal Dragon’s edge-to-edge dark-green copy field with no black outer frame.
8. **Deck archive** — `section#decklists`, `.deck-archive`, `details.deck`, `summary`, `.deck-body`, `.deck-meta`, `button.copy[data-target]`, `.deck-columns`, `.deck-col`, `.group`, `.row`, `.qty`, and a matching hidden `pre` target. Row quantities are the sole total authority; all totals are integer sums and must agree across headings, prose, metadata, data attributes, and copy text. Significant sourced results receive `.tournament-impact`. Every article also contains a statically embedded `details.preconstructed-archive.official-mtg-decks[data-card]`; runtime product loading is forbidden. See `canonical/DECK-ARCHIVE-CONTRACT.md`.
9. Printing galleries obey `canonical/PRINTING-GALLERY-CONTRACT.md`: exact name plus Oracle-ID identity, up to twelve printings, unique artwork first, no `include:extras`, and Sources immediately afterward.
10. **Sources** — immediately after the printing gallery, every article uses exactly `<h3>Sources</h3>`, immediately followed by the source-record container. No prose or component may appear between the gallery, heading, and records. “Research Trail,” “Research sources,” omitted headings, duplicate headings, and other variants are noncanonical. See `canonical/SOURCES-CONTRACT.md`.
11. **Previous and next entries** — names, numbers, and landing-page anchors come only from `archive-manifest.json`.
12. **Landing-page return link** — every numbered article and Honorable Mention displays `← Back to Compulsive Research` and returns to its own landing-page row using the manifest-derived `index.html?focus=ENTRY_ANCHOR#ENTRY_ANCHOR`.
13. **JavaScript behavior** — card previews, mobile tap pinning, deck-copy buttons, TOC highlighting, and reading progress follow `assets/compulsive-research.js`.
14. **Mobile behavior** — the canonical `750px` responsive breakpoint and centered mobile card preview remain locked.
15. **Card-image and double-faced-card behavior** — `#preview .preview-track`, Scryfall `card_faces` resolution, distinct front/back images for physical double-faced cards, and one namesake rules panel per physical face are locked. Empty official-deck summaries display the numeral `0`.

## Editable content

Article generation may change only article-specific data and prose:

- Card, set, date, article title, deckline, and reading-time metadata. Entry number, wave number, wave title, and landing anchor are populated verbatim from `archive-manifest.json` and are not freeform editorial fields.
- Hero artwork URL or position; artwork-spotlight card, verified exact-printing artist, original set, image URL, and image-focused excerpt
- Chapter IDs, chapter labels, headings, and body content
- Card records and rules text
- Tournament deck records, sourced significant-result callouts, and official commercial preconstructed-deck catalogue configuration
- Printing records
- Source records
- Previous and next metadata supplied by `archive-manifest.json`

## Prohibited generation behavior

During article generation, do not:

- Rename canonical classes or introduce competing components
- Rewrite CSS or JavaScript
- Alter the artwork spotlight geometry, crop, placement, overlay structure, caption classes, exact artist/set credit format, or image-focused excerpt standard
- Move navigation, preview, footer, deck, printing, or source systems
- Guess previous/next entries
- invent links, quotations, tournament placements, decklists, dates, artists, or rules history
- link the subject card every time its name appears
- silently redesign an article because a different arrangement seems better

## Existing archive policy

The existing article files are preserved unless a reviewed migration explicitly changes them. Mechanical and editorial status are now separate. The legacy mechanical audit classifies them as:

- **A — Compliant:** no repair is needed under the mechanical contract.
- **B — Repairable:** prose is preserved; only flagged mechanical elements should be changed.
- **C — Rewrite required:** reserved for severe structural corruption or obviously incomplete content. Factual invention cannot be diagnosed reliably by a mechanical validator and requires editorial review.

The audit is evidence for a repair queue, not authorization to rewrite prose.
- Design Echo card references are discovered from final rendered prose using the Oracle-name catalog, postprocessed by `tools/canonicalize_card_links.py`, and independently rescanned by `tools/validate_card_links.py`; declarations are optional hints, not the authority. See `canonical/CARD-REFERENCE-CONTRACT.md`.


## Editorial V2 authority

This contract governs visual and mechanical behavior. It does not require every card
to use the same argumentative sequence. New and substantially revised prose must also
follow:

- `canonical/EDITORIAL-V2-CONTRACT.md`
- `canonical/EVIDENCE-CONTRACT.md`
- `canonical/CANONICAL-IDENTITY-V2-CONTRACT.md`
- `canonical/DECK-SEMANTICS-CONTRACT.md`

A mechanical pass is not an editorial approval.
