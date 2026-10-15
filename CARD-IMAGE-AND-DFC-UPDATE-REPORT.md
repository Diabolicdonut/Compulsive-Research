# Card-image and double-faced-card rollout

**Release date:** August 1, 2026  
**Scope:** complete physical production archive

## Implemented standard

- Updated all **1,685 physical article files**.
- Every visible card row in every historical, editorial, and official-product decklist is a card-image preview link, including the article namesake card.
- The card preview runtime resolves a Scryfall card object rather than assuming that a reverse face is a separate named printing.
- When a card has separately imaged physical faces, the preview shows both face images from the same card object.
- Namesake lead panels automatically show both physical faces and one distinct rules panel for each face.
- Split and Adventure cards without separately imaged physical faces remain single-image previews.
- A collapsed Official Magic section with no matching product now displays the numeric summary label **0**; its explanatory empty-state sentence remains inside the section.

## Migration results

- Physical article files changed: **1,685**
- Previously unlinked visible deck rows repaired: **5,215**
- Empty official-product summaries converted to `0`: **545** during the automated pass, plus the already approved Delver prototype, for **546** total empty sections
- Card preview runtimes replaced: **1,685**
- Namesake lead panels annotated for automatic face handling: **1,685**

## Independent validation

### Card-image links and double-faced behavior

- Articles checked: **1,685**
- Visible deck rows checked: **537,913**
- Linked deck rows: **537,913**
- Article passes: **1,685**
- Failures: **0**

The validator also includes a Delver of Secrets regression fixture requiring two distinct face images, the reverse image from the same Scryfall card ID with `face=back`, and separate rules panels for Delver of Secrets and Insectile Aberration.

### Historical and editorial deck counts

- Articles checked: **1,685**
- Deck components checked: **6,794**
- Passes: **1,685**
- Warnings: **0**
- Failures: **0**

### Official-product deck counts

- Articles checked: **1,685**
- Expected product appearances: **8,595**
- Actual embedded product appearances: **8,595**
- Passes: **1,685**
- Failures: **0**

## Template and validation changes

The compact handoff package now includes:

- updated numbered and Honorable Mention templates;
- updated content schemas;
- an idempotent migration/check tool, `tools/canonicalize_card_image_links.py`;
- an independent validator, `tools/validate_card_image_links.py`;
- updated canonical card-reference, deck-archive, generation, and article contracts;
- updated GitHub validation workflow and validation-suite wrapper;
- a locked canonical Eternal Dragon snapshot containing the new runtime standard.
