# Reader-Facing Editorial Workflow Policy

Editorial workflow belongs in project metadata, dossiers, reports, and validation—not in the published article prose.

## Published article rule

Article pages must not display internal production labels such as:

- Editorial V2
- reviewed under Editorial V2
- reviewed wave labels
- editorial status or research status notices
- migration-completion dates

The underlying `data-editorial-*` and `data-research-*` attributes may remain because validators and migration tooling use them. Research dossiers, status ledgers, audit reports, and handoff documents may also retain workflow terminology.

## Substantive material

Do not delete useful card-specific analysis merely because it was added during a review wave. Present it as ordinary editorial content. The Numbered Wave 01 synthesis panels are therefore titled **Strategic legacy**, with sections for the card's thesis, use, counterplay, and tournament or cultural record.

## Evidence notes

A reader-facing evidence note is allowed when it explains source treatment, uncertainty, or the difference between documentary and curated material. It must not describe the page as reviewed, approved, migrated, or compliant with an internal editorial version.

## Article order

The opening section must introduce the featured card before the **Strategic legacy** synthesis appears. The required reader order is:

1. Opening explanation of what the card is
2. Card identity, original printing, and rules text
3. A short **classic-play vignette** showing the namesake card at its historical best
4. Strategic legacy: thesis, use, counterplay, and record
5. The remaining historical narrative

The table of contents must use the same order. Strategic guidance must never be the first article chapter.

## Footer navigation

Exactly one previous/next navigation block appears in the neutral **Continue reading** section outside `<article>`. Source or evidence notes remain part of the relevant Deck Archive or Sources section and must never contain or directly wrap previous/next buttons.

## Official-product readability

The official Magic product archive uses a solid dark field with high-contrast light text. Its title, count, scope note, and expanded deck descriptions must remain readable in mobile and offline viewers.

## Validation

Run:

```bash
python tools/validate_no_reader_facing_editorial_labels.py
```

This check is part of the quick continuation suite.


## Classic-play vignette

Every newly generated or migrated article includes one short narrative scene inside the opening section, after the card image/rules introduction and before **Strategic legacy**. The scene is a first-person table recollection: one player remembering one opponent and one concrete sequence. Historical grounding remains in structured metadata and the research dossier, but the visible article shows only the story. It must:

- use the visible label **A story from the table**;
- use a first-person singular speaker (I, me, my), but do not force a stock memory cue at the beginning;
- depict that speaker against one opponent, never an unspecified multiplayer table or generalized second-person “you”;
- store a specific year or tournament era, opposing archetypes, and an exact Deck Archive reference in structured attributes without printing a visible era/matchup caption;
- name at least three exact cards, including the featured card, and describe legal turn-by-turn or phase-by-phase sequencing;
- keep primary headlines and opening framing faithful to the displayed rules text; do not attribute drawing, discarding, tutoring, extra turns, countering, land destruction, or untap denial to a card that does not perform that operation;
- when an accelerated opening acts before the opponent’s first turn and the story continues into later turns, include a hidden `.vignette-sequence-data` JSON ledger recording active-player turns, land drops, and actions so chronology and one-land-per-turn limits can be validated;
- remain concise and direct (normally 70–170 words);
- end on the decisive play, reaction, reversal, or immediate board state;
- avoid an explanatory coda telling the reader what the story means, why the card matters, or how modern players should interpret it;
- avoid repeating the Strategic Legacy lead.

The vignette is a representative reconstruction, not a quotation or claim that a recorded match unfolded word for word. That status is retained in machine-readable metadata rather than inserted into the prose.

## Derived reading time

The read-time pill is calculated at **200 words per minute** from continuous editorial prose. Expandable decklists, printing galleries, source records, hidden copy buffers, scripts, and styles are excluded. The pill stores the derived word count and WPM as data attributes so validation can confirm that the displayed estimate is current. Read time is never hard-coded to twenty minutes.
