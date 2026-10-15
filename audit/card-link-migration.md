# Canonical card-reference migration

## Scope

This migration standardized Magic card references in the **Design Echo** portions of all existing Compulsive Research articles. Existing canonical card links elsewhere in the articles were preserved. Article prose was not rewritten.

## Canonical system

Every Design Echo section now declares its exact card targets:

```html
<section class="design-echo-section"
         data-card-references='["Remand","Hinder","Spell Queller","Subtlety"]'
         data-card-aliases='{}'>
```

Visible occurrences use the Eternal Dragon markup:

```html
<span class="card-name" data-card="Remand" tabindex="0">Remand</span>
```

Shortened display names are explicit rather than guessed. For example:

```html
data-card-references='["Eiganjo, Seat of the Empire"]'
data-card-aliases='{"Eiganjo":"Eiganjo, Seat of the Empire"}'
```

The postprocessor runs after all content transformations:

```bash
python tools/canonicalize_card_links.py
python tools/validate_card_links.py
```

Preview behavior now uses document-level event delegation. A card span inserted by a later migration therefore works without adding a new per-element JavaScript listener.

## Migration results

- **408** articles processed and updated
- **543** canonical card-reference spans added
- **140** articles received at least one new Design Echo link
- **407** Design Echo sections now carry one or more declared card targets
- **1** Design Echo contains only generic categories and correctly declares no named card target
- **3,365** verified or editorially confirmed names are available to the local linker
- **1** known non-card preview link (`The Deck`, an archetype label) was removed
- No article prose, decklist, source record, artwork, or navigation text was rewritten

## Representative corrections

- **Necropotence:** Yawgmoth’s Bargain, Ad Nauseam, and Bolas’s Citadel
- **Memory Lapse:** Remand, Hinder, Spell Queller, and Subtlety
- **Ophidian:** Shadowmage Infiltrator, Ninja of the Deep Hours, Ohran Viper, and Curiosity
- **Mahamoti Djinn:** shortened “Zahid” resolves to Zahid, Djinn of the Lamp
- **Karakas:** shortened “Eiganjo” resolves to Eiganjo, Seat of the Empire
- **Maro:** shortened Multani, Soramaro, and Masumaro names resolve to their exact Oracle names

## Template and automation changes

Updated:

- `templates/article-shell.html`
- `templates/article-content.schema.json`
- `canonical/DESIGN-ECHO-CONTRACT.md`
- `canonical/GENERATION-PROMPT.md`
- `canonical/CANONICAL-CONTRACT.md`
- `canonical/card-name-catalog.json`
- `canonical/card-link-supplement.json`
- `tools/canonicalize_card_links.py`
- `tools/validate_card_links.py`
- `tools/validate_archive.py` (parallel `--jobs` support and delegated-runtime recognition)
- `.github/workflows/validate-archive.yml`

Future structured article data must provide `designEcho.cardReferences`; shortened names use `designEcho.cardAliases`.

## Validation

- Card-reference validator: **408/408 passed**
- Design Echo validator: **408 articles / 420 panels / 0 failures**
- Canonical Eternal Dragon lock: **passed**
- Archive regression check: **no new mechanical issue signatures**

The general archive audit remains **A: 1, B: 407, C: 0** because previously queued mechanical repairs—especially source-heading variants and older navigation/card-coverage issues—remain outside this focused migration.
