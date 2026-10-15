#!/usr/bin/env python3
"""Canonicalize and validate Compulsive Research printing galleries.

The published gallery is identity-safe and artwork-first:
- the requested card is resolved by Scryfall's exact-name endpoint;
- all results are restricted to the resolved card's oracle_id and exact name;
- up to twelve English paper printings are shown;
- distinct illustration_id values are selected before same-art reprints;
- cards with fewer than twelve legitimate printings show all of them;
- existing HTML figures remain as an offline fallback while the verified gallery loads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

RUNTIME_START = "/* CR_PRINTING_GALLERY_RUNTIME_START */"
RUNTIME_END = "/* CR_PRINTING_GALLERY_RUNTIME_END */"
STYLE_ID = "cr-printing-gallery-style"
RUNTIME_ID = "cr-printing-gallery-runtime"
ASSET_PATH = "assets/printing-gallery.js"
MAX_PRINTINGS = 12
RUNTIME_VERSION = 'VERSION="5"'

STYLE = f'''<style id="{STYLE_ID}">
/* Canonical printings: verified exact-card hydration with a clean offline fallback. */
.printing-status{{display:none!important}}
.canonical-printing-gallery[aria-busy="true"]{{min-height:0}}
</style>'''

INTRO_REPLACEMENTS = [
    (re.compile(r"Cards with fewer than four legitimate paper printings show every available version instead\.", re.I),
     "Cards with fewer than twelve legitimate paper printings show every available version instead."),
    (re.compile(r"Cards with fewer than four legitimate printings show every available version instead\.", re.I),
     "Cards with fewer than twelve legitimate printings show every available version instead."),
    (re.compile(r"presents at least four historically distinctive paper releases when the card has that many; cards with fewer than four show every available version\.", re.I),
     "presents up to twelve legitimate paper printings, prioritizing distinct artwork; cards with fewer than twelve show every available version."),
]


def load_metadata(root: Path) -> dict[str, dict]:
    path = root / "canonical" / "artwork-card-metadata.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["file"]: item for item in data["cards"]}


def article_files(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*.html") if p.name != "index.html")


def find_gallery_section(soup: BeautifulSoup) -> tuple[Tag | None, Tag | None]:
    article = soup.select_one("article.article") or soup.find("article")
    scope = article or soup
    section = scope.find("section", id="printings")
    if section:
        gallery = section.select_one(".printings")
        if gallery:
            return section, gallery
    for candidate in scope.find_all("section"):
        gallery = candidate.select_one(".printings")
        if gallery:
            return candidate, gallery
    return None, None


def make_original_figure(fragment: BeautifulSoup, meta: dict) -> Tag:
    card = meta["articleCard"]
    set_code = meta["setCode"]
    set_name = meta["setName"]
    src = (
        "https://api.scryfall.com/cards/named?exact="
        + quote(card, safe="")
        + "&set="
        + quote(set_code, safe="")
        + "&format=image&version=normal"
    )
    figure = fragment.new_tag("figure")
    figure["class"] = ["printing", "original-printing"]
    figure["data-card-name"] = card
    figure["data-set"] = set_code
    figure["data-identity-status"] = "exact-name-set-fallback"
    image = fragment.new_tag("img")
    image["alt"] = f"{card} original printing"
    image["loading"] = "lazy"
    image["decoding"] = "async"
    image["src"] = src
    caption = fragment.new_tag("figcaption")
    strong = fragment.new_tag("b")
    strong.string = set_name
    caption.append(strong)
    caption.append(fragment.new_tag("br"))
    caption.append("Original printing")
    figure.append(image)
    figure.append(caption)
    return figure


def runtime_text(root: Path) -> str:
    return (root / ASSET_PATH).read_text(encoding="utf-8").strip()


def remove_runtime(text: str) -> str:
    text = re.sub(
        rf'<script[^>]*id=["\']{re.escape(RUNTIME_ID)}["\'][^>]*>.*?</script>',
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'<script[^>]*>\s*/\* CR_PRINTING_GALLERY_RUNTIME_START \*/.*?/\* CR_PRINTING_GALLERY_RUNTIME_END \*/\s*</script>',
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        rf'<script[^>]*src=["\']{re.escape(ASSET_PATH)}["\'][^>]*>\s*</script>',
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        rf'<style[^>]*id=["\']{re.escape(STYLE_ID)}["\'][^>]*>.*?</style>',
        "",
        text,
        flags=re.I | re.S,
    )
    return re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)


def add_runtime(text: str, runtime: str) -> str:
    text = remove_runtime(text)
    if "</head>" in text:
        text = text.replace("</head>", STYLE + "\n</head>", 1)
    else:
        text = STYLE + "\n" + text
    block = f'<script id="{RUNTIME_ID}">\n{runtime}\n</script>\n<script defer="" src="{ASSET_PATH}"></script>\n'
    if "</body>" in text:
        return text.replace("</body>", block + "</body>", 1)
    return text + "\n" + block


def normalize_printing_copy(section: Tag) -> None:
    for node in section.find_all(string=True):
        if not node.strip():
            continue
        updated = str(node)
        for pattern, replacement in INTRO_REPLACEMENTS:
            updated = pattern.sub(replacement, updated)
        if updated != str(node):
            node.replace_with(updated)


def remove_include_extras(text: str) -> str:
    replacements = [
        (r"%20include%3Aextras", ""),
        (r"\+include%3Aextras", ""),
        (r"%20include:extras", ""),
        (r"\s+include:extras", ""),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return text


def annotate_fallback_figure(figure: Tag, meta: dict, index: int) -> None:
    figure["data-card-name"] = meta["articleCard"]
    if not figure.get("data-identity-status"):
        figure["data-identity-status"] = "canonical-static-fallback"
    if index == 0:
        classes = list(figure.get("class", []))
        if "original-printing" not in classes:
            classes.append("original-printing")
        figure["class"] = classes
        if not figure.get("data-set"):
            figure["data-set"] = meta["setCode"]


def canonicalize_file(path: Path, meta: dict, runtime: str) -> tuple[bool, list[str]]:
    original = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(original, "html.parser")
    section, gallery = find_gallery_section(soup)
    if not gallery or not section:
        return False, ["missing printing gallery"]

    notes: list[str] = []
    classes = [c for c in gallery.get("class", []) if c != "static-printing-gallery"]
    for required in ["printings", "canonical-printing-gallery"]:
        if required not in classes:
            classes.append(required)
    gallery["class"] = classes
    gallery["id"] = "printing-grid"
    gallery["data-card"] = meta["articleCard"]
    gallery["data-original-set"] = meta["setCode"]
    gallery["data-gallery-mode"] = "hydrate"
    gallery["data-gallery-max"] = str(MAX_PRINTINGS)
    gallery["data-identity-policy"] = "exact-name-and-oracle-id"
    gallery["data-selection-policy"] = "unique-artwork-first"
    gallery.attrs.pop("data-oracle-id", None)
    gallery.attrs.pop("data-gallery-state", None)
    gallery.attrs.pop("data-cr-printing-queued", None)

    for status in list(gallery.select(".printing-status")):
        status.decompose()

    figures = gallery.select("figure.printing")
    if not figures:
        gallery.append(make_original_figure(soup, meta))
        figures = gallery.select("figure.printing")
        notes.append("created exact original fallback")
    elif len(figures) == 1:
        # Rebuild legacy one-card placeholders so the fallback itself is exact.
        for child in list(gallery.children):
            if isinstance(child, Tag):
                child.decompose()
            elif str(child).strip():
                child.extract()
        gallery.append(make_original_figure(soup, meta))
        figures = gallery.select("figure.printing")
        notes.append("rebuilt exact original fallback")
    elif len(figures) > MAX_PRINTINGS:
        for figure in figures[MAX_PRINTINGS:]:
            figure.decompose()
        figures = gallery.select("figure.printing")
        notes.append(f"trimmed fallback to {MAX_PRINTINGS}")

    for index, figure in enumerate(figures):
        annotate_fallback_figure(figure, meta, index)
    gallery["data-gallery-fallback-count"] = str(len(figures))

    normalize_printing_copy(section)

    section_id = section.get("id", "")
    old_match = None
    if section_id:
        pattern = re.compile(
            r'<section\b(?=[^>]*\bid=["\']' + re.escape(section_id) + r'["\'])[^>]*>.*?</section>',
            re.I | re.S,
        )
        old_match = pattern.search(original)
    if old_match:
        updated = original[: old_match.start()] + str(section) + original[old_match.end() :]
    else:
        updated = str(soup)

    updated = remove_include_extras(updated)
    updated = add_runtime(updated, runtime)
    changed = updated != original
    if changed:
        path.write_text(updated, encoding="utf-8")
    notes.append(f"verified hydrate policy; fallback figures={len(figures)}; max={MAX_PRINTINGS}")
    return changed, notes


def validate_file(path: Path, meta: dict) -> list[str]:
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    section, gallery = find_gallery_section(soup)
    errors: list[str] = []
    if not gallery or not section:
        return ["missing .printings gallery"]

    classes = gallery.get("class", [])
    if "canonical-printing-gallery" not in classes:
        errors.append("gallery lacks canonical-printing-gallery")
    if gallery.get("data-card") != meta["articleCard"]:
        errors.append("gallery data-card is missing or incorrect")
    if gallery.get("data-original-set") != meta["setCode"]:
        errors.append("gallery data-original-set is missing or incorrect")
    if gallery.get("data-gallery-mode") != "hydrate":
        errors.append("existing archive gallery must use verified hydrate mode")
    if gallery.get("data-gallery-max") != str(MAX_PRINTINGS):
        errors.append("gallery maximum is not 12")
    if gallery.get("data-identity-policy") != "exact-name-and-oracle-id":
        errors.append("exact identity policy is missing")
    if gallery.get("data-selection-policy") != "unique-artwork-first":
        errors.append("unique-artwork-first policy is missing")
    if gallery.get("id") != "printing-grid":
        errors.append("hydrate gallery lacks id=printing-grid")

    if gallery.select_one(".printing-status"):
        errors.append("visible/legacy .printing-status remains")
    if re.search(r"loading (?:the |at least |distinct-art|iconic)|could not load", gallery.get_text(" ", strip=True), re.I):
        errors.append("loading/failure copy remains in gallery")

    figures = gallery.select("figure.printing")
    if not 1 <= len(figures) <= MAX_PRINTINGS:
        errors.append(f"fallback figure count must be between 1 and {MAX_PRINTINGS}")
    for index, figure in enumerate(figures, 1):
        image = figure.find("img")
        caption = figure.find("figcaption")
        if figure.get("data-card-name") != meta["articleCard"]:
            errors.append(f"printing {index} lacks exact data-card-name")
        if not image or not image.get("src", "").strip():
            errors.append(f"printing {index} lacks image src")
        if not caption or not caption.get_text(" ", strip=True):
            errors.append(f"printing {index} lacks caption")

    if "include:extras" in text.lower() or "include%3aextras" in text.lower():
        errors.append("include:extras remains and can admit non-card extras")
    if RUNTIME_START not in text or RUNTIME_END not in text:
        errors.append("embedded canonical runtime is missing")
    if RUNTIME_VERSION not in text:
        errors.append("printing runtime is not version 5")
    for token in ["canonical.prints_search_uri", "card.oracle_id===canonical.oracle_id", "MAX_PRINTINGS=12", "unique-artwork-first"]:
        if token not in text:
            errors.append(f"runtime identity/selection token missing: {token}")
    if f'id="{STYLE_ID}"' not in text and f"id='{STYLE_ID}'" not in text:
        errors.append("canonical no-status style is missing")
    if f'src="{ASSET_PATH}"' not in text and f"src='{ASSET_PATH}'" not in text:
        errors.append("shared printing-gallery asset is missing")

    sources = section.find(["h3", "h4"], string=lambda value: value and value.strip() == "Sources")
    if not sources:
        errors.append("Sources heading is missing")
    else:
        cursor = gallery.find_next_sibling()
        while cursor is not None and not isinstance(cursor, Tag):
            cursor = cursor.next_sibling
        if cursor is not sources:
            errors.append("Sources heading does not immediately follow gallery")

    section_text = section.get_text(" ", strip=True).lower()
    if "fewer than four" in section_text or "at least four" in section_text:
        errors.append("obsolete four-printing copy remains")
    return errors


def update_template(root: Path, runtime: str) -> None:
    path = root / "templates" / "article-shell.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<div class="printings canonical-printing-gallery[^>]*>\{\{PRINTING_FIGURES_HTML\}\}</div>',
        '<div class="printings canonical-printing-gallery" id="printing-grid" data-card="{{CARD_NAME}}" data-original-set="{{ORIGINAL_SET_CODE}}" data-gallery-mode="hydrate" data-gallery-max="12" data-identity-policy="exact-name-and-oracle-id" data-selection-policy="unique-artwork-first">{{PRINTING_FIGURES_HTML}}</div>',
        text,
        count=1,
    )
    text = remove_include_extras(text)
    text = add_runtime(text, runtime)
    path.write_text(text, encoding="utf-8")


def update_schema(root: Path) -> None:
    path = root / "templates" / "article-content.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    prop = data["properties"]["printings"]
    prop["minItems"] = 1
    prop["maxItems"] = MAX_PRINTINGS
    item = prop["items"]
    item["required"] = [
        "cardName", "oracleId", "scryfallId", "illustrationId", "setCode",
        "collectorNumber", "caption", "imageUrl"
    ]
    item["properties"] = {
        "cardName": {"type": "string", "minLength": 1, "description": "Must exactly equal the article subject card name."},
        "oracleId": {"type": "string", "minLength": 1, "description": "All gallery records must share this exact Scryfall Oracle ID."},
        "scryfallId": {"type": "string", "minLength": 1, "description": "Unique Scryfall printing ID; duplicates are forbidden."},
        "illustrationId": {"type": "string", "description": "Used to prioritize different artworks before same-art reprints."},
        "setCode": {"type": "string", "minLength": 1},
        "collectorNumber": {"type": "string", "minLength": 1},
        "caption": {"type": "string", "minLength": 1},
        "imageUrl": {"type": "string", "format": "uri"},
    }
    prop["description"] = (
        "One to twelve verified English paper printings rendered before Sources. "
        "Every record must have the exact article card name and the same Oracle ID. "
        "Choose distinct illustration IDs first, then fill remaining slots with other legitimate printings. "
        "If fewer than twelve printings exist, include all of them."
    )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_docs(root: Path) -> None:
    contract = root / "canonical" / "PRINTING-GALLERY-CONTRACT.md"
    contract.write_text(f"""# Canonical printing-gallery contract

The visual structure remains governed by `250-eternal-dragon.html`, while identity and selection are enforced by the gallery runtime and validators.

## Identity contract

1. Resolve the article subject through Scryfall's exact-name endpoint.
2. Follow that exact card object's `prints_search_uri`.
3. Accept a candidate only when its `oracle_id` equals the resolved card's Oracle ID **and** its normalized name equals the resolved exact name.
4. Require English, paper, nondigital card objects with a usable card image.
5. Never use `include:extras` for printing galleries or printing-catalog source links.
6. Cached records are rejected unless every record has the exact card name, one shared Oracle ID, a unique Scryfall printing ID, and an image.

## Selection contract

1. Display no more than **{MAX_PRINTINGS}** printings.
2. If fewer than {MAX_PRINTINGS} legitimate printings exist, display all of them.
3. Keep the original printing first chronologically.
4. Prioritize one representative from each distinct `illustration_id` before filling remaining slots with same-art reprints.
5. After artwork diversity, favor historically distinctive products, frames, promos, and chronological coverage.

## Published structure

```html
<div class="printings canonical-printing-gallery"
     id="printing-grid"
     data-card="CARD NAME"
     data-original-set="set"
     data-gallery-mode="hydrate"
     data-gallery-max="12"
     data-identity-policy="exact-name-and-oracle-id"
     data-selection-policy="unique-artwork-first">
  <!-- one to twelve verified static fallback figures -->
</div>
<h3>Sources</h3>
```

The verified runtime replaces the fallback only after all records pass identity validation. On failure, the existing exact original-printing fallback remains. Visible loading and failure boxes are forbidden.

## Validation

```bash
node tools/test_printing_gallery_identity.js
python tools/canonicalize_printing_galleries.py --check
python tools/validate_archive.py --jobs 4 --output-dir audit/current
```
""", encoding="utf-8")

    prompt = root / "canonical" / "GENERATION-PROMPT.md"
    text = prompt.read_text(encoding="utf-8")
    text = re.sub(
        r"(?m)^7a\. .*?$",
        "7a. Printing galleries obey `canonical/PRINTING-GALLERY-CONTRACT.md`: provide one to twelve verified English paper printings; use the exact article card name and one shared Oracle ID; prioritize different illustration IDs; include every printing when fewer than twelve exist; never use `include:extras`; and run the printing identity test and validator after assembly.",
        text,
    )
    text = text.replace(
        "16. Run `python tools/canonicalize_printing_galleries.py --check`,",
        "16. Run `node tools/test_printing_gallery_identity.js`, `python tools/canonicalize_printing_galleries.py --check`,",
    )
    prompt.write_text(text, encoding="utf-8")

    canonical = root / "canonical" / "CANONICAL-CONTRACT.md"
    ctext = canonical.read_text(encoding="utf-8")
    ctext = re.sub(
        r"(?m)^9\. .*printings.*$",
        "9. Printing galleries obey `canonical/PRINTING-GALLERY-CONTRACT.md`: exact name plus Oracle-ID identity, up to twelve printings, unique artwork first, no `include:extras`, and Sources immediately afterward.",
        ctext,
    )
    canonical.write_text(ctext, encoding="utf-8")


def update_workflow(root: Path) -> None:
    path = root / ".github" / "workflows" / "validate-archive.yml"
    text = path.read_text(encoding="utf-8")
    step = "      - name: Test printing-gallery identity and artwork selection\n        run: node tools/test_printing_gallery_identity.js\n"
    marker = "      - name: Verify canonical printing galleries\n"
    if step not in text:
        text = text.replace(marker, step + marker, 1)
    path.write_text(text, encoding="utf-8")


def update_general_validator(root: Path) -> None:
    path = root / "tools" / "validate_archive.py"
    text = path.read_text(encoding="utf-8")
    # Replace the current printing-component validation block through its next outer else.
    start = text.find('        printing_component = source_container.select_one(".printings")')
    end_marker = '        else:\n            add(issues, "FAIL", "MISSING_PRINTINGS_COMPONENT", "Missing .printings component.")'
    end = text.find(end_marker, start)
    if start >= 0 and end >= 0:
        end += len(end_marker)
        block = '''        printing_component = source_container.select_one(".printings")
        if printing_component:
            printing_text = printing_component.get_text(" ", strip=True)
            printing_classes = printing_component.get("class", [])
            printing_figures = printing_component.select("figure.printing")
            if printing_component.select_one(".printing-status") or re.search(r"loading (?:the |at least |distinct-art|iconic)|could not load", printing_text, re.I):
                add(issues, "FAIL", "PRINTING_LOADING_COPY", "Printing gallery exposes loading/failure status copy.")
            if "canonical-printing-gallery" not in printing_classes:
                add(issues, "FAIL", "PRINTING_COMPONENT_CLASS", "Printing gallery lacks .canonical-printing-gallery.")
            if printing_component.get("data-gallery-mode") != "hydrate":
                add(issues, "FAIL", "PRINTING_MODE", "Printing gallery does not use verified hydrate mode.")
            if printing_component.get("data-gallery-max") != "12":
                add(issues, "FAIL", "PRINTING_MAX", "Printing gallery maximum is not twelve.")
            if printing_component.get("data-identity-policy") != "exact-name-and-oracle-id":
                add(issues, "FAIL", "PRINTING_IDENTITY_POLICY", "Printing gallery lacks exact name plus Oracle-ID policy.")
            if printing_component.get("data-selection-policy") != "unique-artwork-first":
                add(issues, "FAIL", "PRINTING_ART_POLICY", "Printing gallery lacks unique-artwork-first policy.")
            if not 1 <= len(printing_figures) <= 12:
                add(issues, "FAIL", "PRINTING_FIGURES", "Printing fallback must contain one to twelve figures.")
            expected_card = printing_component.get("data-card")
            if not expected_card or not printing_component.get("data-original-set"):
                add(issues, "FAIL", "PRINTING_METADATA", "Printing gallery lacks data-card or data-original-set.")
            seen_fallback_ids = set()
            fallback_oracle_ids = set()
            for printing_figure in printing_figures:
                if printing_figure.get("data-card-name") != expected_card:
                    add(issues, "FAIL", "PRINTING_CARD_IDENTITY", "A printing fallback lacks the exact article card name.")
                    break
                scryfall_id = printing_figure.get("data-scryfall-id")
                if scryfall_id:
                    if scryfall_id in seen_fallback_ids:
                        add(issues, "FAIL", "PRINTING_DUPLICATE_ID", "Printing fallback repeats a Scryfall printing ID.")
                        break
                    seen_fallback_ids.add(scryfall_id)
                oracle_id = printing_figure.get("data-oracle-id")
                if oracle_id:
                    fallback_oracle_ids.add(oracle_id)
                image = printing_figure.find("img")
                caption = printing_figure.find("figcaption")
                if not image or not image.get("src", "").strip():
                    add(issues, "FAIL", "PRINTING_IMAGE", "A printing fallback lacks an image URL.")
                    break
                if not caption or not caption.get_text(" ", strip=True):
                    add(issues, "FAIL", "PRINTING_CAPTION", "A printing fallback lacks a caption.")
                    break
            if len(fallback_oracle_ids) > 1:
                add(issues, "FAIL", "PRINTING_MIXED_ORACLE", "Printing fallback contains multiple Oracle IDs.")
            if re.search(r"include(?::|%3A)extras", raw, re.I):
                add(issues, "FAIL", "PRINTING_INCLUDE_EXTRAS", "include:extras may admit unrelated extra cards.")
            if "CR_PRINTING_GALLERY_RUNTIME_START" not in raw:
                add(issues, "FAIL", "PRINTING_RUNTIME", "Printing gallery lacks the embedded canonical runtime.")
            for token, code in [
                ("canonical.prints_search_uri", "PRINTING_SEARCH_URI"),
                ("card.oracle_id===canonical.oracle_id", "PRINTING_ORACLE_FILTER"),
                ("MAX_PRINTINGS=12", "PRINTING_MAX_RUNTIME"),
                ("unique-artwork-first", "PRINTING_ART_RUNTIME"),
            ]:
                if token not in raw:
                    add(issues, "FAIL", code, f"Printing runtime lacks required token: {token}")
        else:
            add(issues, "FAIL", "MISSING_PRINTINGS_COMPONENT", "Missing .printings component.")'''
        text = text[:start] + block + text[end:]
    path.write_text(text, encoding="utf-8")


def update_lock(root: Path) -> None:
    published = root / "250-eternal-dragon.html"
    snapshot = root / "canonical" / "250-eternal-dragon.canonical.html"
    snapshot.write_bytes(published.read_bytes())
    digest = hashlib.sha256(published.read_bytes()).hexdigest()
    (root / "canonical" / "250-eternal-dragon.sha256").write_text(digest + "\n", encoding="utf-8")
    lock_path = root / "canonical" / "canonical-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["sha256"] = digest
    lock["canonical_sha256"] = digest
    lock["canonical_article_sha256"] = digest
    lock["last_canonical_migration"] = "2026-07-30"
    lock["canonical_printing_gallery"] = {
        "authority": "250-eternal-dragon.html#printings",
        "contract": "canonical/PRINTING-GALLERY-CONTRACT.md",
        "maximum": MAX_PRINTINGS,
        "identity": "exact normalized name plus one shared Scryfall oracle_id",
        "selection": "distinct illustration_id first, then legitimate same-art printings",
        "fewer_than_max": "show every available English paper printing",
        "include_extras": "forbidden",
        "runtime_version": 5,
        "validator": "tools/canonicalize_printing_galleries.py --check",
        "unit_test": "node tools/test_printing_gallery_identity.js",
    }
    lock_path.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_report(root: Path, changed: int, notes: list[str]) -> None:
    report = root / "audit" / "printing-gallery-identity-migration.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "# Printing gallery identity and twelve-printing migration\n\n"
        f"- Articles processed: {len(article_files(root))}\n"
        f"- Article files changed: {changed}\n"
        f"- Maximum printings: {MAX_PRINTINGS}\n"
        "- Identity rule: exact normalized card name plus one shared Scryfall Oracle ID\n"
        "- Selection rule: distinct artwork first, then other legitimate printings\n"
        "- `include:extras`: removed and forbidden\n\n"
        "## Root cause\n\n"
        "The previous runtime searched by text with `include:extras`. That search could return extra or composite card objects that referenced the subject without being the subject card itself. The old renderer did not compare Oracle IDs before displaying a result.\n\n"
        "## Permanent fix\n\n"
        "The runtime now resolves the exact card, follows its own `prints_search_uri`, rejects every result with a different `oracle_id` or name, invalidates old caches, and renders at most twelve unique Scryfall printing IDs. Distinct illustration IDs are selected before same-art reprints.\n\n"
        "## Validation\n\n"
        "The Node fixture test includes an unrelated Grave Researcher object beside Reanimate printings and proves that the unrelated object is rejected. Archive validation also checks the runtime tokens, twelve-card maximum, exact-card metadata, no `include:extras`, and Sources placement.\n\n"
        + ("## Notes\n\n" + "\n".join(f"- {note}" for note in notes[:30]) + "\n" if notes else ""),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate without modifying files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    metadata = load_metadata(root)

    if args.check:
        failures: list[tuple[str, list[str]]] = []
        for path in article_files(root):
            meta = metadata.get(path.name)
            if not meta:
                failures.append((path.name, ["missing canonical artwork/card metadata"]))
                continue
            errors = validate_file(path, meta)
            if errors:
                failures.append((path.name, errors))
        if failures:
            print(f"PRINTING GALLERY VALIDATION FAILED: {len(failures)} article(s)")
            for name, errors in failures[:60]:
                print(name)
                for error in errors:
                    print(f"  - {error}")
            return 1
        print(f"Identity-safe printing galleries verified: {len(article_files(root))}/{len(article_files(root))} articles")
        return 0

    runtime = runtime_text(root)
    changed = 0
    notes: list[str] = []
    for path in article_files(root):
        meta = metadata.get(path.name)
        if not meta:
            notes.append(f"{path.name}: missing metadata")
            continue
        did_change, file_notes = canonicalize_file(path, meta, runtime)
        changed += int(did_change)
        notes.extend(f"{path.name}: {note}" for note in file_notes)

    update_template(root, runtime)
    update_schema(root)
    update_docs(root)
    update_workflow(root)
    update_general_validator(root)
    update_lock(root)
    write_report(root, changed, notes)

    failures = []
    for path in article_files(root):
        meta = metadata.get(path.name)
        if meta:
            errors = validate_file(path, meta)
            if errors:
                failures.append((path.name, errors))
    if failures:
        print(f"Migration completed but {len(failures)} article(s) failed validation")
        for name, errors in failures[:50]:
            print(name, "; ".join(errors))
        return 1
    print(f"Updated {changed} articles with exact-card identity and up to {MAX_PRINTINGS} artwork-first printings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
