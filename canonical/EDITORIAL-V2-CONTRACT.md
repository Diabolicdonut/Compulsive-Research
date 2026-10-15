# Compulsive Research Editorial V2 Contract

## Purpose

The visual template is shared across the archive. The editorial argument is not.
Every article must explain why its particular card mattered, what evidence supports
that account, how the card is used, and how opponents respond. Mechanical template
compliance is necessary but is never treated as proof of editorial quality.

## Article classes

Every new or substantially revised article declares exactly one primary class:

- `tournament-pillar`
- `character-or-story-object`
- `combo-or-engine-piece`
- `design-landmark`
- `casual-icon`
- `banned-or-restricted-card`
- `collector-object`

A secondary class may be recorded, but it does not replace the primary research
question.

## Mandatory editorial pillars

Every V2 article contains evidence-backed material for:

1. **Thesis** — one concise claim explaining why the card belongs in the archive.
2. **Canonical identity** — Oracle identity, true debut printing, release date,
   original artist, original printed wording when available, and current Oracle text.
3. **Original context** — set environment, design purpose, contemporary reception,
   and the constraints under which the card was first evaluated.
4. **Lore or flavor context** — full canonical chronology when documented; otherwise
   an explicitly limited flavor-context discussion. Never invent lore to fill a slot.
5. **Competitive or cultural biography** — dated milestones, archetype movement,
   metagame reaction, decline, replacement, or cultural afterlife as applicable.
6. **Playbook** — role, deck requirements, copy count, mulligan implications,
   sequencing, sideboarding, and common mistakes.
7. **Counterplay** — direct answers, engine disruption, timing windows, racing,
   resource attacks, and sideboarding where applicable.
8. **Rules texture** — card-specific interactions and misconceptions, not generic
   descriptions of how the stack or costs work.
9. **Artwork and material history** — exact original artwork plus meaningful changes
   in later printings.
10. **Evidence** — claims map to identifiable sources and current claims carry an
    `as of` date.
11. **Classic-play vignette** — a concise first-person table story placed after the card has been introduced. It uses the visible label **A story from the table**, depicts one opponent, binds through hidden metadata to a dated era, matchup, exact Deck Archive record, and opening mode, and uses at least three named cards in legal sequencing. Primary framing must match the displayed rules text. An accelerated story that acts before the opponent’s first turn and continues into later turns also carries a hidden machine-readable turn ledger so land drops and turn order can be checked. Its opening must vary naturally within the production wave rather than repeatedly beginning with “I remember” or an equivalent cue. The visible prose contains only the scene and ends on the play, reaction, reversal, or board state without an explanatory coda.
12. **Derived read time** — the displayed estimate is computed from continuous editorial prose at 200 words per minute, not copied from a template. Reference lists, galleries, and expandable decklists do not inflate the estimate.

## Specificity standard

A paragraph fails editorial review when it can be moved unchanged to an unrelated
card article. Replacing the article subject with another card name must make the
paragraph false, incomplete, or obviously mismatched.

At minimum, strategic paragraphs should contain concrete card-specific material such
as named interactions, actual timing windows, archetype requirements, copy-count
logic, matchup consequences, dated events, or format-specific constraints.

## Lore standard

Lore fields use one of three scopes:

- `full` — documented character, object, location, faction, or story chronology;
- `flavor-only` — setting, flavor text, art direction, name, or mechanical expression;
- `none-documented` — no reliable lore beyond the physical card object.

Canonical story facts, artist interpretation, player recollection, and editorial
interpretation must remain distinguishable.

## Competitive-history standard

A card with meaningful tournament influence should normally record:

- initial reception;
- first documented breakthrough;
- competitive peak;
- metagame reaction;
- movement between relevant formats;
- decline, rotation, ban, restriction, replacement, or transformation;
- present historical afterlife, dated when current status is discussed.

Do not fabricate a complete timeline when evidence is sparse. Record the gap.

## Deck policy

Public production articles may include only:

- `tournament-registration` — a sourced historical registration;
- `official-digital-deck` — a documented official digital product/opponent list;
- `curated-example` — a manually reviewed, legal and coherent example with a stated
  format and `as of` date;
- `official-mtg-product` — rendered from the committed official catalogue.

`editorial-study` is forbidden in production. A missing documentary deck archive is
valid and preferable to an invented list. Article-content schemas therefore allow an
empty `decklists` array.

## Evidence classes

Sources declare one of:

- `primary`
- `contemporary-secondary`
- `retrospective-secondary`
- `database`
- `player-recollection`

Direct quotations require an identifiable speaker and source. Composite player
memory is paraphrased without quotation marks.

## Status fields

Mechanical and editorial status are separate:

- `mechanicalStatus`: `pass`, `warning`, or `fail`
- `editorialStatus`: `benchmark`, `reviewed`, `audit-required`, `rewrite-required`
- `researchStatus`: `scaffold`, `in-research`, `draft`, `fact-checked`, `complete`
- `releaseStatus`: `draft`, `staging`, `production`

Only `researchStatus: complete` plus an approved editorial review may be represented
as fully researched.
