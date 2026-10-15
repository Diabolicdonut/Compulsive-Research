# Reader V3.1 entries 011–050 — unresolved warnings

The requested Reader V3.1 experience, layout, archive-core, historical-deck, Deck Archive, official-product, card-image-link, local-asset, canonical-lock, and release-state checks all pass. There are no unresolved Reader V3.1 structural failures in entries 011–050.

The archive-wide deck-semantics report retains the same warning queue that existed in the uploaded source project:

- **1,440 `CROSS_ARTICLE_DECK_FINGERPRINT` warnings.** The same documentary or curated decklist appears in multiple card articles. This is frequently legitimate because one historically important registration can contain many featured cards, but the validator keeps the reuse visible for editorial review. Entries 011–050 account for 174 of these appearances.
- **354 `DECK_SOURCE_NOT_BOUND` warnings.** These deck components do not yet have a machine-readable source URL bound directly to the component. Entries 011–050 account for 76. The retrofit preserved the existing registrations and did not invent source bindings.
- **5 `MONOBASIC_COLOR_WARNING` warnings elsewhere in the archive.** They occur in entries 138, 168, 169, 215, and 271. None occurs in entries 011–050.

These counts are unchanged from the uploaded Reader V3.1 source ZIP. The deck-semantics validator therefore remains `PASS` with warnings rather than treating them as release-blocking failures.

The story metadata identifies exact Deck Archive titles already present in each of the forty articles. It does not claim that the narrated game sequence is a documented match transcript; every new vignette is explicitly marked as a representative recollection.
