# Hero and Headline Migration Validator Suite

**Result:** FAIL
**Suite version:** 2.0.0
**Numbered articles scanned:** 1000

## Results

- Entries 001–400: 394 passed, 6 failed.
- Entries 401–1000: 516 passed, 84 failed.
- Explicit image heroes: 985.
- Valid legacy CSS-only heroes: 15.
- Cross-card duplicate hero groups: 0.
- Unique hero headlines: 1000 of 1,000.
- Duplicate headline groups: 0.
- Generator contract failures: 0.

## Enforced contract

1. The visible hero image must identify the article card.
2. The image-error fallback and final CSS fallback must identify the same card.
3. Entries 401–1000 must display the card name in the hero heading.
4. Different cards may not share the same resolved hero identity.
5. Every numbered article must have a unique, card-relevant editorial headline.
6. Shared role/category headlines from the former generator are forbidden.
7. Generated headlines must match the deterministic headline template and all headline metadata must agree.
8. The generation template must write card-specific hero media and card-specific headlines.

## Failed pages

- `215-nether-spirit.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `273-ichorid.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `327-umezawas-jitte.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `377-tarmogoyf.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `386-counterbalance.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `391-thoughtseize.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `401-noble-hierarch.html`: HERO_CONTRACT_IDENTITY_MISMATCH|GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `403-bloodbraid-elf.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `406-path-to-exile.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `407-maelstrom-pulse.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `410-progenitus.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `417-stoneforge-mystic.html`: HERO_CONTRACT_IDENTITY_MISMATCH|GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `418-lotus-cobra.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `420-goblin-guide.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `422-vampire-nighthawk.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `424-primeval-titan.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `425-emrakul-the-aeons-torn.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `429-splinter-twin.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `433-batterskull.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `434-sword-of-feast-and-famine.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `440-phyrexian-metamorph.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `444-wurmcoil-engine.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `446-tempered-steel.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `451-delver-of-secrets.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE|HEADLINE_META_MISMATCH
- `452-snapcaster-mage.html`: HERO_CONTRACT_IDENTITY_MISMATCH|GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `453-liliana-of-the-veil.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `458-griselbrand.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `468-deathrite-shaman.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE
- `477-nykthos-shrine-to-nyx.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `479-sylvan-caryatid.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `484-treasure-cruise.html`: GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE|HEADLINE_META_MISMATCH|OPENING_TOC_MISMATCH
- `488-goblin-rabblemaster.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `539-teferi-hero-of-dominaria.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `561-uro-titan-of-nature-s-wrath.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `570-brazen-borrower.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `581-thassa-s-oracle.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `582-underworld-breach.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `583-heliod-sun-crowned.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `584-dryad-of-the-ilysian-grove.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `585-kroxa-titan-of-death-s-hunger.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `586-shark-typhoon.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `590-muxus-goblin-grandee.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `593-hullbreacher.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `595-fierce-guardianship.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `596-deflecting-swat.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `603-dragon-s-rage-channeler.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `604-murktide-regent.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `606-fury.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `607-solitude.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `608-endurance.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `609-subtlety.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `611-dauthi-voidwalker.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `612-ignoble-hierarch.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `613-yavimaya-cradle-of-growth.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `618-persist.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `619-prismatic-ending.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `621-academy-manufactor.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `622-alrund-s-epiphany.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `623-goldspan-dragon.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `624-esika-s-chariot.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `626-koma-cosmos-serpent.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `631-expressive-iteration.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `633-professor-onyx.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `641-wedding-announcement.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `642-ledger-shredder.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `643-unlicensed-hearse.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `648-the-wandering-emperor.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `659-psychic-frog.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `661-ocelot-pride.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `662-guide-of-souls.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `664-tamiyo-inquisitive-student.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `671-haughty-djinn.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `677-elesh-norn-mother-of-machines.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `679-skrelv-defector-mite.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `680-sunfall.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `683-beseech-the-mirror.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `688-deep-cavern-bat.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `692-slickshot-show-off.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `709-surgical-extraction.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `733-crop-rotation.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `737-crucible-of-worlds.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `751-command-tower.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `785-jeska-s-will.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `835-elvish-champion.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `842-thorn-elemental.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `876-gravecrawler.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `898-giada-font-of-hope.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `900-youthful-valkyrie.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `929-blacker-lotus.html`: HERO_CONTRACT_IDENTITY_MISMATCH
- `938-booster-tutor.html`: HERO_CONTRACT_IDENTITY_MISMATCH
