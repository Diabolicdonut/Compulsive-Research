# Headline Convention Validator Suite

**Result:** FAIL
**Suite version:** 3.0.0
**Numbered articles scanned:** 1000

## Results

- Canonical title-bank entries: 1000.
- Unique hero headlines: 1000 of 1,000.
- Duplicate headline groups: 0.
- Full card-name leaks: 0.
- Visible hero card-name labels: 0.
- Entries 001–400: 394 passed, 6 failed.
- Entries 401–1000: 592 passed, 8 failed.
- Generator contract failures: 0.

## Enforced convention

1. Every numbered article uses its canonical thematic essay title.
2. No two numbered articles share the same normalized hero headline.
3. The complete card name may not appear inside the thematic headline.
4. Generated pages may not display a separate card-name label above the headline.
5. Hero, browser title, headline metadata, opening chapter, and table of contents agree.
6. Headlines are limited to twelve words for the established mobile presentation.
7. The generator reads the canonical title bank and emits a plain thematic H1.

## Failed pages

- `215-nether-spirit.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `273-ichorid.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `327-umezawas-jitte.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `377-tarmogoyf.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `386-counterbalance.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `391-thoughtseize.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `401-noble-hierarch.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `403-bloodbraid-elf.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `417-stoneforge-mystic.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `429-splinter-twin.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `451-delver-of-secrets.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK|HEADLINE_META_MISMATCH
- `452-snapcaster-mage.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `468-deathrite-shaman.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK
- `484-treasure-cruise.html`: HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK|HEADLINE_META_MISMATCH|OPENING_TOC_MISMATCH
