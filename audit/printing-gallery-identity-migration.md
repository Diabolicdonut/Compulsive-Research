# Printing gallery identity and twelve-printing migration

- Articles processed: 408
- Article files changed: 408
- Maximum printings: 12
- Identity rule: exact normalized card name plus one shared Scryfall Oracle ID
- Selection rule: distinct artwork first, then other legitimate printings
- `include:extras`: removed and forbidden

## Root cause

The previous runtime searched by text with `include:extras`. That search could return extra or composite card objects that referenced the subject without being the subject card itself. The old renderer did not compare Oracle IDs before displaying a result.

## Permanent fix

The runtime now resolves the exact card, follows its own `prints_search_uri`, rejects every result with a different `oracle_id` or name, invalidates old caches, and renders at most twelve unique Scryfall printing IDs. Distinct illustration IDs are selected before same-art reprints.

## Validation

The Node fixture test includes an unrelated Grave Researcher object beside Reanimate printings and proves that the unrelated object is rejected. Archive validation also checks the runtime tokens, twelve-card maximum, exact-card metadata, no `include:extras`, and Sources placement.

## Notes

- 001-black-lotus.html: rebuilt exact original fallback
- 001-black-lotus.html: verified hydrate policy; fallback figures=1; max=12
- 002-ancestral-recall.html: rebuilt exact original fallback
- 002-ancestral-recall.html: verified hydrate policy; fallback figures=1; max=12
- 003-time-walk.html: rebuilt exact original fallback
- 003-time-walk.html: verified hydrate policy; fallback figures=1; max=12
- 004-mox-pearl.html: rebuilt exact original fallback
- 004-mox-pearl.html: verified hydrate policy; fallback figures=1; max=12
- 005-mox-sapphire.html: rebuilt exact original fallback
- 005-mox-sapphire.html: verified hydrate policy; fallback figures=1; max=12
- 006-mox-jet.html: rebuilt exact original fallback
- 006-mox-jet.html: verified hydrate policy; fallback figures=1; max=12
- 007-mox-ruby.html: rebuilt exact original fallback
- 007-mox-ruby.html: verified hydrate policy; fallback figures=1; max=12
- 008-mox-emerald.html: rebuilt exact original fallback
- 008-mox-emerald.html: verified hydrate policy; fallback figures=1; max=12
- 009-timetwister.html: rebuilt exact original fallback
- 009-timetwister.html: verified hydrate policy; fallback figures=1; max=12
- 010-sol-ring.html: rebuilt exact original fallback
- 010-sol-ring.html: verified hydrate policy; fallback figures=1; max=12
- 011-lightning-bolt.html: rebuilt exact original fallback
- 011-lightning-bolt.html: verified hydrate policy; fallback figures=1; max=12
- 012-counterspell.html: rebuilt exact original fallback
- 012-counterspell.html: verified hydrate policy; fallback figures=1; max=12
- 013-dark-ritual.html: rebuilt exact original fallback
- 013-dark-ritual.html: verified hydrate policy; fallback figures=1; max=12
- 014-swords-to-plowshares.html: rebuilt exact original fallback
- 014-swords-to-plowshares.html: verified hydrate policy; fallback figures=1; max=12
- 015-demonic-tutor.html: rebuilt exact original fallback
- 015-demonic-tutor.html: verified hydrate policy; fallback figures=1; max=12

## Final verification

- Node identity/artwork-selection fixture: PASS
- Canonical gallery check: 408/408 PASS
- Per-article identity validation: 408/408 PASS
- Sources-heading validation: PASS
- Card-reference validation: 408/408 PASS
- Design Echo validation: 408 articles / 420 panels / 0 failures
- Canonical Eternal Dragon lock: PASS
- Full mechanical audit: A=264, B=144, C=0
- Audit regression comparison: no new mechanical issue signatures

The test environment could not perform a dependable live browser fetch of every external Scryfall image. The runtime logic, cache rejection, exact-identity filtering, pagination, selection algorithm, generated markup, JavaScript syntax, and archive validations were tested locally. Existing exact original-printing fallbacks remain visible if a remote catalog request fails.
