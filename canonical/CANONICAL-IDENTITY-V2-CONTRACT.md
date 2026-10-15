# Canonical Card Identity V2 Contract

Each article consumes one committed canonical identity record. Runtime search order
or the first row returned by an external export is never the authority for a card's
debut.

Required identity fields:

- exact article and Oracle names;
- Oracle ID;
- physical card faces;
- true first playable paper printing;
- set code and set name;
- card-specific release date;
- Scryfall printing ID and illustration ID;
- original artist;
- original printed wording when available;
- current Oracle wording;
- promotional/reprint classification.

Recurring promotional sets often carry a set-level date that predates the actual
card. Records from Pro Tour Promos, Grand Prix Promos, Judge Gift Cards, Secret Lair,
Store Championships, The List, oversized products, and similar collections must not
be selected as a debut merely because their container date sorts first.

Known exceptions in which a promotional product genuinely was the card's first
playable printing must be committed explicitly in
`data/canonical-first-printing-overrides.json`.
