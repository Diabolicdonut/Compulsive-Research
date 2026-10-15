# Editorial V2 Wave 2 Validation

**Date:** 2026-08-02

## Full-corpus checks

| Validator | Result | Scope |
|---|---:|---:|
| Editorial quality, strict reviewed mode | PASS | 1,505 articles; 0 hard failures |
| Archive core V2 | PASS | 1,505 / 1,505 |
| Canonical identity | PASS | 1,000 / 1,000 numbered articles |
| Historical decks only | PASS | 1,505 articles; 1,572 documentary decks |
| Deck semantics | PASS with review warnings | 1,505 articles; 1,572 decks |
| Official Magic products | PASS | 8,252 expected and 8,252 embedded appearances |
| Local assets | PASS | 1,506 pages |
| Wave 2 research dossiers | PASS | 10 / 10 |

Deck-semantic warnings identify inherited cross-article fingerprints, unbound source metadata, and five monobasic-color review cases. They are migration-queue signals rather than failures in the ten reviewed Wave 2 pages.

## Changed-set checks

The ten Wave 2 articles plus the four structurally normalized Wave 1 pages passed the card-image and double-faced-card validator:

- 14 / 14 pages passed
- 7,395 / 7,395 deck rows linked to card previews
- 0 changed-set failures

The full 1,505-page card-image validator did not finish within the execution limit during this run. The changed set passed, and the unchanged corpus retained the previously validated Editorial V2 card-image implementation.

## Remaining archive findings

The editorial-quality audit still identifies 596 generic-dossier pages and substantial repeated prose elsewhere. These pages remain explicitly queued for reconstruction or audit and have not been promoted.
