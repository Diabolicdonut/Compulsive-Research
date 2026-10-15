# Compulsive Research — Reader V3.1 Current Handoff

**Authoritative as of:** August 5, 2026  
**Project root:** `Compulsive-Research-main/`  
**Landing page:** `index.html`  
**Canonical structural article:** `250-eternal-dragon.html`

## Current archive

- 1,000 numbered articles
- 505 active Honorable Mentions
- 22 Honorable Mention categories
- 1,505 active article pages total
- Honorable Mention navigation remains category-local
- Reader-facing editorial workflow labels are prohibited

This project folder is the source of truth. Do not rebuild it from older ZIPs or overwrite it with earlier Wave 1, Wave 2, Editorial V2, or Reader V3 packages.

## Reader V3.1 status

### Fully validated pilot

Entries 001–010 are the approved Reader V3.1 pilot:

1. Black Lotus
2. Ancestral Recall
3. Time Walk
4. Mox Pearl
5. Mox Sapphire
6. Mox Jet
7. Mox Ruby
8. Mox Emerald
9. Timetwister
10. Sol Ring

These ten establish the required story presentation, story-opening diversity, read-time calculation, layout order, product contrast, and validation rules.

### Additional updated sample articles

The following out-of-sequence articles were also updated and are included as supplementary examples:

- `248-astral-slide.html`
- `250-eternal-dragon.html`
- `417-stoneforge-mystic.html`
- `425-emrakul-the-aeons-torn.html`

They demonstrate the Reader V3.1 treatment across a cycling engine, a canonical long-form benchmark, an equipment tutor, and a giant game-ending threat. They do not change the next sequential production range.

## Exact next task

Complete Reader V3.1 for numbered entries **011–050**, from **Lightning Bolt** through **Stasis**.

Work internally in four groups of ten:

- 011–020
- 021–030
- 031–040
- 041–050

Return one merged forty-article package that completes Numbered Wave 1 under Reader V3.1.

After entries 011–050:

1. Retrofit entries 051–100 to Reader V3.1.
2. Produce Honorable Mention Wave 1, the first 50 active HMs in landing-page category order.
3. Continue numbered entries in fifty-card waves, using internal ten-card checkpoints.

## Reader-facing article order

The reader must encounter the card before being told how to use it.

Required opening order:

1. Article title and opening thesis
2. Card image
3. Rules text and original identity
4. Brief article framing
5. **A story from the table**
6. **Strategic Legacy**
7. Remaining history, mechanics, tournament, play, counterplay, art, products, decks, printings, and sources

Strategic Legacy must not appear before the card image, rules, and original identity. Do not place a highlighted sentence immediately before Strategic Legacy that repeats its lead.

## “A story from the table” standard

The visible vignette contains only:

- The label **A story from the table**
- A card-specific title
- The story

Do not show a year, matchup caption, source-deck caption, reconstruction notice, or interpretive explanation in the visible story panel. Preserve those facts in hidden metadata.

Each story must:

- Use first-person singular voice.
- Describe one speaker, one opponent, and one concrete game.
- Be grounded in a plausible historical or contemporary card pool.
- Name exact cards, mana, turns, phases, attacks, stack interactions, or board states.
- Show the featured card doing the thing that made it memorable.
- End on the play, reaction, reversal, punchline, or resulting board state.
- Usually run 70–170 words.
- Be written individually, not generated from a shared prose skeleton.

Do not repeatedly begin stories with “I remember,” “I still remember,” “There I was,” or equivalent stock cues. Within each fifty-card wave:

- No repeated normalized first six words.
- No more than one stock memory-cue opening.
- Vary openings among dialogue, an opponent’s play, an opening hand, a revealed card, life total, board state, combat, a spell on the stack, a mistake, or the punchline already taking shape.

Do not add a final paragraph explaining why the story mattered. Avoid phrases such as:

- “What I remember most”
- “Looking back”
- “By modern standards”
- “This demonstrates”
- “The lesson was”

The story itself should carry the meaning.

## Historical grounding

For tournament cards, ground the vignette in an exact historical deck already in the Deck Archive whenever possible. Verify:

- The year and format
- Card legality and printing availability
- Exact mana requirements
- The archetype and likely opponent
- Rules and timing as they existed in that period

The visible story may be a representative recollection, but it must not be presented as a quotation from a named real person or as a documented match sequence unless a source proves that exact sequence.

For cards without a suitable tournament deck, use a period-appropriate kitchen-table game, official preconstructed deck, Limited environment, Commander table, or famous rules interaction. Keep it specific and plausible.

## Read-time standard

Read time is derived from actual continuous editorial prose at **200 words per minute**.

Exclude:

- Decklist rows
- Printing-gallery records
- Source-list records
- Hidden copy buffers and metadata
- Scripts and styles
- Collapsed controls and interface labels

Never hard-code “20 minute read.” Recalculate after every substantive edit.

Articles may grow beyond 4,000 words when the card’s design history, tournament record, lore, artwork, rules history, official products, or cultural importance supports it. Do not pad articles to reach a target.

## Global layout and presentation rules

- Official Magic product text must remain high-contrast in normal browsers and Android local-file viewers.
- Use both shared CSS and inline critical contrast.
- Sources must be ordinary readable source lists, never printing-gallery grids.
- Each page gets one Continue Reading previous/next block outside the article, sources, and notes.
- Design Echo headings must be card-specific. Do not reuse “Descendants of the Bargain” or another article’s private joke globally.
- Comparison art must depict the named comparison card and use a stable intended printing when crossovers or alternate treatments could create an irrelevant image.
- Reader-facing pages must not display Editorial V2, review status, approval status, migration status, wave labels, or internal QA notes.

## Deck Archive rules

- Preserve genuine historical tournament registrations.
- Preserve official Wizards commercial decks.
- Never invent a tournament deck.
- Clearly label representative or curated examples as `curated-example`.
- A documentary deck may appear in multiple card articles when it genuinely contains each featured card.
- Deck totals, sideboards, namesake-card presence, and card-image links must validate.

## Important files

Read these before editing:

1. `READER-V3.1-CURRENT-HANDOFF-2026-08-05.md`
2. `READER-V3.1-START-HERE-2026-08-05.md`
3. `canonical/READER-FACING-EDITORIAL-POLICY.md`
4. `canonical/EDITORIAL-V2-CONTRACT.md`
5. `canonical/GENERATION-PROMPT.md`
6. `canonical/DECK-ARCHIVE-CONTRACT.md`
7. `templates/article-shell.html`
8. `templates/honorable-article-shell.html`
9. `tools/validate_reader_experience_v3.py`
10. `tools/validate_reader_layout_contract.py`

Use entries 001–010 as the primary sequential pilot and the four additional sample articles as supplementary examples.

## Validation commands

After each internal ten-card batch:

```bash
python tools/validate_reader_experience_v3.py
python tools/validate_reader_layout_contract.py
python tools/run_validation_suite.py --quick
```

Before final packaging:

```bash
python tools/run_validation_suite.py --refresh-v2
python tools/run_validation_suite.py --full
```

If a long validator exceeds one execution window, run the project’s staged validators and resume from the failed stage. Do not claim a pass that was not actually completed.

## Delivery format for entries 011–050

Return:

- The forty updated article HTML files
- Updated project infrastructure, templates, and validators
- Any new or revised research dossiers
- A review index linking all forty pages
- Validation reports and metrics
- Updated project state and migration ledger
- Package manifest and SHA-256 checksums
- Preferably one full current-project ZIP when file size is allowed

Do not call the work complete merely because structural validation passes. Read the stories and major new prose for repetition, historical implausibility, and generic phrasing.
