# Locked generation prompt for future numbered articles

Use this prompt together with:

- `canonical/CANONICAL-CONTRACT.md`
- `canonical/250-eternal-dragon.canonical.html`
- `templates/research-dossier-v2.schema.json`
- `templates/article-content.schema.json`
- `canonical/EDITORIAL-V2-CONTRACT.md`
- `canonical/EVIDENCE-CONTRACT.md`
- `canonical/CANONICAL-IDENTITY-V2-CONTRACT.md`
- `canonical/DECK-SEMANTICS-CONTRACT.md`
- the relevant record from `archive-manifest.json`
- an approved, schema-valid Editorial V2 research dossier

---

You are producing one numbered article for the **Compulsive Research** archive.


## Reader-facing workflow labels

Editorial version names, review status, migration-wave labels, approval language, and research-status notices belong in metadata and reports, not visible article prose. Preserve useful analysis as ordinary article sections. See `canonical/READER-FACING-EDITORIAL-POLICY.md` and run `python tools/validate_no_reader_facing_editorial_labels.py`.

## Editorial V2 gate

Do not generate an article from card metadata alone. The supplied research dossier
must validate against `templates/research-dossier-v2.schema.json` and must include a
card-specific thesis, canonical identity, original context, lore scope, competitive
or cultural timeline, playbook, counterplay, claims, and source records. If the
dossier is incomplete, stop with a dossier-validation failure; never fill missing
history with universal strategy prose.

Select one article class and weight the narrative accordingly. Eternal Dragon and
Black Lotus are benchmarks for specificity and evidence, not rigid prose outlines.
A paragraph that could be transferred unchanged to an unrelated card is not
publication-ready.

## Canonical authority

`canonical/250-eternal-dragon.canonical.html` is the structural authority. Populate its established components; do not redesign them.

## Nonnegotiable rules

1. Do not alter the canonical header, hero, navigation, table of contents, section system, artwork spotlight, class names, deck archive, printing gallery, source format, footer, CSS, JavaScript, card-preview behavior, or mobile behavior.
2. Use `archive-manifest.json` as the only authority for entry number, wave number, exact wave title, filename, landing-page anchor, previous entry, and next entry. The hero return link must display exactly `← Back to Compulsive Research` while retaining the article-specific manifest href. The numbered eyebrow must display exactly `Entry NNN · Wave XX · WAVE TITLE`. Never substitute an editorial lens such as “Historical Constructed,” “Constructed History,” or “Modern Foundations.”
3. Every TOC fragment must resolve to one unique direct article-section ID. Every direct article section must appear in the TOC.
4. Secondary Magic card references in ordinary prose use exactly:
   `<span class="card-name" data-card="ORACLE CARD NAME" tabindex="0">DISPLAY NAME</span>`
4a. `designEcho.cardReferences` may contain editorial hints for ambiguous one-word names, but it is not the authority. After every HTML field and prose transformation is complete, run `python tools/canonicalize_card_links.py`, then `python tools/validate_card_links.py`. The canonicalizer discovers exact Oracle names from the final prose, regenerates the exhaustive `data-card-references` list, and links them. Use `designEcho.cardAliases` whenever prose intentionally shortens an Oracle name. Any recognized but unlinked name, partial link, wrong Oracle target, or declaration mismatch is a publication failure.
5. Do not repeatedly link the article’s subject card in ordinary prose. In every decklist, however, **all** card rows—including the article subject—must use canonical `.card-name[data-card][tabindex="0"]` markup so the card image opens.
6. Preserve `section#decklists` and `section#printings` exactly as the canonical system IDs.
7. Immediately after the printing gallery, render the exact heading `<h3>Sources</h3>`, followed immediately by the source-record list. Do not use “Research Trail,” “Research sources,” omit the heading, or place prose/components between the gallery, heading, and list.
7a. Printing galleries obey `canonical/PRINTING-GALLERY-CONTRACT.md`: provide one to twelve verified English paper printings; use the exact article card name and one shared Oracle ID; prioritize different illustration IDs; include every printing when fewer than twelve exist; never use `include:extras`; and run the printing identity test and validator after assembly.
8. Use only the approved V2 research dossier. Every consequential claim must map to a dossier claim/source record. Do not invent quotations, dates, artists, rulings, tournament results, placements, decklists, lore, or sources.
9. Supply exactly one artwork spotlight using the immutable `.art-break.artwork-spotlight` markup from the template. It must show the exact original printing’s `art_crop` image and embed a verified static artist and original set name. The visible first line must read exactly `ARTIST’S original SET artwork` (for example, `Justin Sweet’s original Scourge artwork`). Never omit the artist, list only the set, or rely on runtime lookup.
10. Write one or two short sentences about the **visible artwork itself**. Name or clearly identify the subject, object, action, or setting, then discuss at least one visual quality: composition/framing, palette/light/shadow, gesture/motion, texture, scale, or atmosphere. Eternal Dragon and Spelljack are the editorial models. Do not summarize strategy, rules function, tournament history, publication history, database/catalog display, or say merely that the illustration established/preserved the card’s identity. Prohibited examples include “The article uses Scryfall’s current catalog image,” “The original illustration became inseparable from the card’s first strategic identity,” and “The original illustration and frame established the visual identity preserved throughout this article.”
11. Supply exactly one canonical Design Echo section using `.inline-image.canonical-inline-image`. Its `.image` contains a real `<img class="inline-image-media">` whose initial `src` is the canonical local placeholder. Provide exact-card JSON, exact `art_crop`, exact `normal`, and fuzzy `art_crop` URLs only through the locked data attributes. The self-contained queued runtime resolves and caches direct static artwork URLs when the panel nears the viewport. Never use a live API lookup as the initial image `src`, leave `.image` empty, assign card art only in CSS, apply `.descendant-panel`, or invent alternate geometry. The copy field must be Eternal Dragon green (`#20322f`) and reach the image/component edges without a black outer frame.

12. The artwork crop is locked to `center 25%`, desktop height to `min(69vw, 720px)`, and mobile height to `72vh`. Place the spotlight after the second substantive article section, as in Eternal Dragon. Do not convert it to a narrow inset image, figure card, gallery tile, or background-only component.
13. Historical deck records must identify player, event, placement or significance, format, date, and source whenever supported. An empty documentary deck archive is valid and preferable to an invented list.
13a. Follow `canonical/DECK-ARCHIVE-CONTRACT.md`. Parse every `.qty` as an integer and derive every group, main-deck, sideboard, metadata, provenance, data-attribute, and copy-text total by addition. Never concatenate quantity strings and never assume 60/15.
13b. When a winning list or major-event registration containing the subject card exists, add a sourced `.tournament-impact` callout with conservative wording. Do not repeat unverified anecdotes as fact.
13c. Render one statically embedded, collapsed-by-default section labeled `Official Magic the Gathering decks` from `data/official-mtg-deck-catalogue.json`. Include every qualifying product containing the subject card and its complete published card contents. Each product deck is also collapsed by default and uses the canonical Deck Archive format. A missing sideboard is valid and must remain missing. When no qualifying product contains the card, the collapsed summary must display exactly `0`; inside the opened section use exactly `No official Magic the Gathering products contained this particular card.` Browser fetching, `preconstructed-decks.js`, and load-on-open placeholders are forbidden.

13d. After all deck HTML is rendered, run `python tools/canonicalize_card_image_links.py`. The shared preview runtime must resolve Scryfall `card_faces`: physical double-faced cards show two distinct face images, never two copies of the front. A double-faced namesake lead shows both face images and one separate rules panel per face. Split/Adventure cards stay single-image unless Scryfall provides independently imaged physical faces.
14. Preserve visual and behavioral consistency. Editorial structure may vary by article class; do not force unrelated cards into identical arguments or reusable boilerplate.
15. Return only the requested article content data or finished HTML. Do not include explanatory commentary inside the file.
16. Run `python tools/validate_research_dossier.py PATH_TO_DOSSIER`, `python tools/validate_local_assets.py`, `python tools/validate_canonical_identity.py`, `python tools/validate_deck_semantics.py`, `python tools/validate_editorial_quality.py`, then `python tools/canonicalize_deck_archives.py`, `python tools/canonicalize_copy_decklists.py`, `python tools/render_official_mtg_deck_sections.py --check`, `python tools/validate_deck_archives.py`, `python tools/validate_official_mtg_decks.py`, `python tools/canonicalize_card_image_links.py --check`, `python tools/validate_card_image_links.py`, `node tools/test_printing_gallery_identity.js`, `python tools/canonicalize_printing_galleries.py --check`, `python tools/canonicalize_sources_heading.py --check`, then `python tools/validate_archive.py` after generation and repair only mechanical failures.


## Required card-specific content

The finished article must answer, with evidence and concrete examples:

- Why does this card deserve an article?
- What did its original set and design environment ask of it?
- What canonical lore or flavor context is documented, and what is not?
- What were its dated competitive or cultural milestones?
- What exact deck requirements, copy-count decisions, mulligans, sequences, and
  sideboarding patterns make it work?
- How do opponents answer the card, attack its engine, exploit timing windows, race
  it, or sideboard against it?
- Which rules interactions are particular to this card?
- Why did its role rise, decline, migrate, become banned/restricted, or survive?

Generic explanations of costs, targets, the stack, card advantage, optionality, or
resource exchange do not satisfy these requirements unless they are tied to a named
card interaction or documented game pattern.

## Deck prohibition

Never create `editorial-study` shells. Production deck kinds are
`tournament-registration`, `official-digital-deck`, and `curated-example`; official
products are rendered separately from the committed catalogue. Curated examples
require format legality, a review date, and a reviewer.

## Article record

- Entry: `{{ENTRY}}`
- Card: `{{CARD_NAME}}`
- Slug: `{{SLUG}}`
- Wave: `{{WAVE_NUMBER}} · {{WAVE_TITLE}}` (copy the title verbatim from the manifest)
- Previous: `{{PREVIOUS_ENTRY}} · {{PREVIOUS_CARD}}`
- Next: `{{NEXT_ENTRY}} · {{NEXT_CARD}}`
- Landing anchor: `{{LANDING_ANCHOR}}`

## Approved research dossier

`{{RESEARCH_DOSSIER}}`
## Hero identity

Generate `img.hero-media` from the current article card, never from the template card. Include a same-card normal-image fallback and a final CSS fallback. Use one plain thematic `h1` in the entries 001–400 convention: do not repeat the card name in the title and do not add a separate visible card-name label. Read the canonical title from `data/editorial-headlines.json` through `tools/headline_identity.py`. Every numbered headline must be unique, card-relevant, and no more than twelve words. Validate with both `tools/validate_hero_migration.py` and `tools/validate_headline_identity.py`.


## Categorized Honorable Mentions

When generating an Honorable Mention, follow
`canonical/HONORABLE-MENTION-CATEGORY-CONTRACT.md` and
`templates/honorable-article-shell.html`, and
`templates/honorable-article-content.schema.json`.

- Use a stable `honorable-CARD-SLUG.html` filename with no ordinal.
- Declare `data-honorable-category` on the body.
- Keep the card name out of the thematic hero headline.
- Build previous/next links only from the card's own category.
- Never display a global Honorable Mention number or total.
- Rebuild the manifest and run `tools/validate_honorable_categories.py`.

12. Introduce the card first: opening explanation, original card image, rules text, and identity all appear before strategic guidance.
13. End the opening with exactly one 70–170 word `.play-vignette` labeled **A story from the table**. Write it in first person using I/me/my about one game against one opponent, never addressing the reader as “you.” Do not default to “I remember,” “I still remember,” “There I was,” or another stock memory cue. Rotate entry points across the 50-article wave: action, dialogue, board state, life total, revealed information, opening hand, a mistake, or another card-specific detail. Store a dated era, named matchup, exact deck-archive reference, representative-reconstruction status, and opening mode in structured metadata, but do not print a visible era/matchup caption. Name at least three real cards and narrate legal turn-by-turn or phase-by-phase sequencing. Keep the page title, hero title, opening title, and opening thesis faithful to the displayed rules text; never describe a card as affecting draws, discard, tutoring, extra turns, countering, land destruction, or untapping unless its rules actually support that operation. If an accelerated opening acts before the opponent’s first turn and continues into later turns, add a hidden `.vignette-sequence-data` JSON ledger with `schema_version`, `on_the_play`, and ordered `turns` containing `active_player`, `turn`, `land_drops`, and `actions`. End on the decisive play, reaction, reversal, or immediate board state. Do not append a reflective explanation of what the story means, and do not repeat the Strategic Legacy lead.
14. Render `Strategic legacy` immediately after the completed opening. Its TOC link follows the opening link.
15. Derive the read-time pill at 200 words per minute from continuous editorial prose using `tools/reader_experience_v3.py`. Never hard-code “20 minute read.”
16. Use exactly one previous/next block, in the Continue reading section outside article content. Never place navigation inside Sources, Printings, or an evidence note.
17. Give every Design Echo a card-specific heading. Pin comparison art to the intended historical printing when an unqualified API lookup could return a crossover or otherwise misleading treatment.
18. Render source records with `.sources`, never with the printing-gallery grid. Keep critical official-product contrast inline in the article as well as in `preconstructed-decks.css`, because local Android viewers may not load sibling stylesheets reliably.
19. Before release, compare the article subject with the named hero image, original lead-card image, original artwork credit, and `details.official-mtg-decks[data-card]`. A prior Wheel of Fortune article inherited Timetwister artwork and product metadata despite passing several archive checks. Run `tools/validate_reader_experience_v3.py` after assembling a Reader V3.1 article, and inspect the actual painting before writing its visual description.

20. Record reviewed story payments in a hidden `script.vignette-mana-data[type="application/json"]` object with `schema_version: 1` and a `costs` array. Each action names its `object`, `kind` (`artifact-spell`, `nonartifact-spell`, or `activated-ability`), final total `cost`, and `payments` (`source` and positive integer `amount`). Zero-cost casts use an empty payments array. Sum the payments and enforce Workshop's artifact-spell restriction. Separately review colored mana, discounts, taxes, source availability across turns, summoning sickness, and period-specific rules; the ledger is not a complete game simulator. State who is on the play whenever an early-turn interaction depends on that order.
