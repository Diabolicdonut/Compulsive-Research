# Evidence and Claim Contract

## Claim records

Consequential historical, tournament, rules, lore, quotation, legality, and current
metagame statements are represented in the research dossier by a claim record:

```json
{
  "claimId": "stable-id",
  "summary": "What the article asserts",
  "sourceIds": ["source-id"],
  "confidence": "high",
  "asOf": "2026-08-02",
  "notes": "Optional conflict or limitation"
}
```

`asOf` is mandatory for current legality, current metagame position, prices,
availability, policy, and other time-sensitive statements.

## Source records

Each source has a stable ID, title, URL, source class, publication date when known,
access date, and a note describing its evidentiary role. A generic database listing
cannot by itself support a tournament placement, quotation, design-intent claim, or
story chronology.

## Primary-source preference

Prefer official tournament coverage, deck registrations, rules announcements,
set articles, card image galleries, published fiction, and interviews. Secondary
sources may provide synthesis, but they must not silently replace available primary
evidence for major claims.

## Uncertainty

Conflicting or incomplete records are disclosed. Use `medium` or `disputed`
confidence rather than manufacturing precision. Omission is preferable to invention.
