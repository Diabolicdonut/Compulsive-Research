#!/usr/bin/env python3
"""Discover and canonicalize Design Echo card references archive-wide.

Unlike the legacy declaration-driven pass, this tool scans the finished prose
against the checked-in Oracle-name catalog. ``data-card-references`` is an
output manifest, not the authority. Run this tool after every transformation
that can alter Design Echo prose, then run ``validate_card_links.py``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from card_reference_engine import (
    clean_name,
    display_map_from_catalog,
    discover_section_matches,
    link_matches,
    load_json_list_attribute,
    load_json_map_attribute,
    norm_key,
    unique_names,
    unwrap_card_spans,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "canonical" / "card-name-catalog.json"
SUPPLEMENT_PATH = ROOT / "canonical" / "card-link-supplement.json"
REPORT_PATH = ROOT / "audit" / "card-reference-discovery-migration.json"
ARTICLE_GLOBS = ("[0-9][0-9][0-9]-*.html", "[0-9][0-9][0-9][0-9]-*.html", "honorable-*.html")
NON_CARD_LABELS = {"The Deck"}

CARD_LINK_STYLE = """
/* CR_CARD_LINK_DESIGN_ECHO_STYLES */
.design-echo-section .card-name,
.inline-image.canonical-inline-image .copy .card-name{
  color:inherit;border-bottom:2px dotted #d8b878;cursor:help;outline:none;
  text-decoration:none;font-weight:inherit
}
.design-echo-section .card-name:hover,
.design-echo-section .card-name:focus,
.inline-image.canonical-inline-image .copy .card-name:hover,
.inline-image.canonical-inline-image .copy .card-name:focus{
  color:#d8b878;border-color:#d8b878
}
"""


def article_paths() -> list[Path]:
    found: set[Path] = set()
    for pattern in ARTICLE_GLOBS:
        found.update(ROOT.glob(pattern))
    return sorted(found)


def manifest_subjects() -> dict[str, str]:
    data = json.loads((ROOT / "archive-manifest.json").read_text(encoding="utf-8"))
    return {
        item["file"]: item["card"]
        for group in (data.get("entries", []), data.get("honorable_mentions", []))
        for item in group
        if item.get("file") and item.get("card")
    }


def load_supplement() -> tuple[list[str], dict[str, dict[str, str]]]:
    if not SUPPLEMENT_PATH.exists():
        return [], {}
    data = json.loads(SUPPLEMENT_PATH.read_text(encoding="utf-8"))
    names = unique_names(x for x in data.get("names", []) if isinstance(x, str))
    aliases: dict[str, dict[str, str]] = {}
    for filename, mapping in data.get("article_aliases", {}).items():
        if isinstance(mapping, dict):
            aliases[filename] = {
                str(display): str(canonical)
                for display, canonical in mapping.items()
                if str(display).strip() and str(canonical).strip()
            }
    return names, aliases


def load_catalog(paths: Iterable[Path]) -> dict[str, str]:
    """Merge the committed snapshot with confirmed project metadata.

    The committed catalog is never rebuilt from article prose. The refresh
    utility is the only tool allowed to replace it with an authoritative full
    snapshot.
    """
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names: list[str] = list(data.get("names", []))
    supplement, _ = load_supplement()
    names.extend(supplement)
    names.extend(manifest_subjects().values())
    # Existing explicit metadata is trusted as project-local evidence. This
    # preserves names introduced after the last catalog refresh.
    for path in paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for attribute in ("data-card", "data-card-name", "data-image-card"):
            for element in soup.select(f"[{attribute}]"):
                value = clean_name(element.get(attribute))
                if value and value not in NON_CARD_LABELS:
                    names.append(value)
    catalog: dict[str, str] = {}
    for name in unique_names(names):
        if name not in NON_CARD_LABELS:
            catalog.setdefault(norm_key(name), name)
    return catalog


def section_image_card(section: Tag) -> str | None:
    holder = section.select_one("[data-image-card]")
    return clean_name(holder.get("data-image-card")) if holder else None


def image_prefix_alias(section: Tag, subject: str) -> dict[str, str]:
    image_name = section_image_card(section)
    if not image_name or "," not in image_name:
        return {}
    alias = image_name.split(",", 1)[0].strip()
    if len(alias) < 4 or norm_key(alias) == norm_key(subject):
        return {}
    if alias in section.get_text(" ", strip=True):
        return {alias: image_name}
    return {}


def ensure_styles(soup: BeautifulSoup) -> bool:
    if "CR_CARD_LINK_DESIGN_ECHO_STYLES" in str(soup):
        return False
    style = soup.find("style")
    if not style:
        return False
    style.append(CARD_LINK_STYLE)
    return True


def ensure_runtime(soup: BeautifulSoup) -> bool:
    if "CR_CARD_PREVIEW_RUNTIME_START" in str(soup):
        return False
    runtime_path = ROOT / "assets" / "compulsive-research.js"
    if not runtime_path.exists() or not soup.body:
        return False
    script = soup.new_tag("script")
    script.string = runtime_path.read_text(encoding="utf-8")
    soup.body.append(script)
    return True


def canonicalize_section(
    section: Tag,
    catalog: dict[str, str],
    subject: str,
    supplemental_aliases: dict[str, str],
) -> dict[str, object]:
    prior_declared = load_json_list_attribute(section, "data-card-references")
    prior_aliases = load_json_map_attribute(section, "data-card-aliases")
    prior_links = [clean_name(el.get("data-card")) for el in section.select(".card-name[data-card]")]
    prior_links = [name for name in prior_links if name]

    aliases = dict(prior_aliases)
    aliases.update(supplemental_aliases)
    aliases.update(image_prefix_alias(section, subject))
    # Aliases must point to known canonical names; add their targets to the
    # runtime catalog so project-specific shorthand works before a refresh.
    for canonical in aliases.values():
        cleaned = clean_name(canonical)
        if cleaned:
            catalog.setdefault(norm_key(cleaned), cleaned)

    explicit_names = unique_names(prior_declared + prior_links + list(aliases.values()))
    image_card = section_image_card(section)
    if image_card:
        explicit_names.append(image_card)

    unwrapped = unwrap_card_spans(section)
    display_map = display_map_from_catalog(catalog, aliases)
    matches_by_node = discover_section_matches(
        section,
        display_map,
        subject,
        explicit_names=explicit_names,
        aliases=aliases,
    )
    linked_occurrences = 0
    discovered_names: list[str] = []
    for node, matches in matches_by_node:
        discovered_names.extend(match.canonical for match in matches)
        linked_occurrences += link_matches(node, matches)

    references = sorted(unique_names(discovered_names), key=lambda value: value.casefold())
    section["data-card-references"] = json.dumps(references, ensure_ascii=False, separators=(",", ":"))
    used_keys = {norm_key(name) for name in references}
    used_aliases = {
        display: canonical
        for display, canonical in aliases.items()
        if norm_key(canonical) in used_keys
    }
    section["data-card-aliases"] = json.dumps(used_aliases, ensure_ascii=False, separators=(",", ":"))
    section["data-card-discovery"] = "oracle-catalog-v2"
    return {
        "unwrapped_occurrences": len(unwrapped),
        "linked_occurrences": linked_occurrences,
        "references": references,
        "aliases": used_aliases,
        "new_references": sorted(set(references) - set(prior_declared), key=str.casefold),
        "removed_references": sorted(set(prior_declared) - set(references), key=str.casefold),
    }



def section_signature(section: Tag) -> dict[str, object]:
    return {
        "references": load_json_list_attribute(section, "data-card-references"),
        "aliases": load_json_map_attribute(section, "data-card-aliases"),
        "discovery": section.get("data-card-discovery"),
        "links": [
            (clean_name(element.get_text(" ", strip=True)) or "", clean_name(element.get("data-card")) or "", element.get("tabindex"))
            for element in section.select(".card-name")
        ],
    }

def process_file(
    path: Path,
    catalog: dict[str, str],
    subject: str,
    supplemental_aliases: dict[str, str],
    check: bool,
) -> dict[str, object]:
    original = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(original, "html.parser")
    section = soup.select_one(".design-echo-section")
    if not section:
        return {"file": path.name, "changed": False, "error": "Design Echo section missing"}
    before_signature = section_signature(section)
    details = canonicalize_section(section, catalog, subject, supplemental_aliases)
    after_signature = section_signature(section)
    style_added = ensure_styles(soup)
    runtime_added = ensure_runtime(soup)
    changed = before_signature != after_signature or style_added or runtime_added
    if changed and not check:
        path.write_text(str(soup), encoding="utf-8")
        # Reapply the locked Design Echo panel formatter after BeautifulSoup
        # edits so this postprocessor never creates a conflict with the
        # independent Design Echo validator. This calls only the per-file
        # migration, not that tool's contract/template writers.
        from canonicalize_design_echo import migrate_file as normalize_design_echo_file
        normalize_design_echo_file(path, check=False)
    return {
        "file": path.name,
        "changed": changed,
        "style_added": style_added,
        "runtime_added": runtime_added,
        **details,
    }


def update_schema() -> None:
    path = ROOT / "templates" / "article-content.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    design = data.get("properties", {}).get("designEcho", {})
    required = design.get("required", [])
    if "cardReferences" in required:
        required.remove("cardReferences")
    properties = design.get("properties", {})
    if "cardReferences" in properties:
        properties["cardReferences"]["description"] = (
            "Optional editorial hints for ambiguous card names. The final exhaustive list is discovered from rendered prose by tools/canonicalize_card_links.py and written to data-card-references."
        )
    if "cardAliases" in properties:
        properties["cardAliases"]["description"] = (
            "Optional shortened display text mapped to exact Oracle names. Use only when prose intentionally abbreviates a card title; automatic exact-name discovery remains authoritative."
        )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_template() -> None:
    path = ROOT / "templates" / "article-shell.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    section = soup.select_one(".design-echo-section")
    if section:
        section["data-card-references"] = "[]"
        section["data-card-aliases"] = "{{DESIGN_ECHO_CARD_ALIASES_JSON}}"
        section["data-card-discovery"] = "oracle-catalog-v2"
        comment_text = (
            " CARD REFERENCE BUILD STEP: cardReferences are optional hints. After all prose is rendered, run "
            "tools/canonicalize_card_links.py; it discovers exact Oracle names, writes data-card-references, and must be followed by tools/validate_card_links.py. "
        )
        existing = soup.find(string=lambda value: value and "CARD REFERENCE BUILD STEP" in value)
        if existing:
            existing.replace_with(comment_text)
        else:
            section.insert_before(soup.new_string("\n<!--" + comment_text + "-->\n"))
    ensure_styles(soup)
    ensure_runtime(soup)
    path.write_text(str(soup), encoding="utf-8")


def update_contracts() -> None:
    contract = ROOT / "canonical" / "CARD-REFERENCE-CONTRACT.md"
    contract.write_text("""# Canonical Card-Reference Contract

## Authority

The final rendered prose and the checked-in Oracle-name catalog are the authority. `designEcho.cardReferences` is an optional editorial hint for ambiguous one-word names; it is never accepted as an exhaustive declaration.

## Required build sequence

1. Render every article component and all final Design Echo prose.
2. Run `python tools/canonicalize_card_links.py`.
3. Run `python tools/validate_card_links.py`.
4. Publish only when validation passes.

The canonicalizer scans eligible Design Echo prose longest-name-first, recognizes exact multiword Oracle names automatically, recognizes shortened names through article aliases, and recognizes one-word names such as **Persist** in high-confidence comma-separated card lists. It then writes canonical `.card-name` spans and regenerates `data-card-references` from what it actually discovered.

## Canonical markup

```html
<span class="card-name" data-card="EXACT ORACLE NAME" tabindex="0">DISPLAY TEXT</span>
```

The subject card is not repeatedly linked in ordinary article prose. Headings, navigation, deck records, Sources, printings, code, and existing anchors are excluded from automatic prose linking.

## Catalog maintenance

`canonical/card-name-catalog.json` is the committed offline snapshot. Run `python tools/refresh_card_name_catalog.py` when network access is available to refresh it from Scryfall's complete card-name catalog. CI runs `python tools/refresh_card_name_catalog.py --check` and never requires live network access.

## Validation

Validation independently rescans prose after temporarily removing existing links. It fails when a recognized occurrence is unlinked, partially linked, linked to the wrong Oracle name, omitted from `data-card-references`, or when the declaration contains a name not present in the prose. This prevents an incomplete declaration from allowing an omitted card name to pass.
""", encoding="utf-8")

    canonical = ROOT / "canonical" / "CANONICAL-CONTRACT.md"
    text = canonical.read_text(encoding="utf-8")
    old = "- Design Echo card references are declared in structured data, postprocessed by `tools/canonicalize_card_links.py`, and validated by `tools/validate_card_links.py`."
    new = "- Design Echo card references are discovered from final rendered prose using the Oracle-name catalog, postprocessed by `tools/canonicalize_card_links.py`, and independently rescanned by `tools/validate_card_links.py`; declarations are optional hints, not the authority. See `canonical/CARD-REFERENCE-CONTRACT.md`."
    text = text.replace(old, new)
    canonical.write_text(text, encoding="utf-8")

    prompt = ROOT / "canonical" / "GENERATION-PROMPT.md"
    text = prompt.read_text(encoding="utf-8")
    old_prompt = "4a. Supply `designEcho.cardReferences` as an exhaustive list of exact Oracle names for every card named in the Design Echo. After all HTML fields are assembled, run `python tools/canonicalize_card_links.py`, then `python tools/validate_card_links.py`. Use `designEcho.cardAliases` whenever prose shortens an Oracle name. A missing declaration or an unlinked declared name is a publication failure."
    new_prompt = "4a. `designEcho.cardReferences` may contain editorial hints for ambiguous one-word names, but it is not the authority. After every HTML field and prose transformation is complete, run `python tools/canonicalize_card_links.py`, then `python tools/validate_card_links.py`. The canonicalizer discovers exact Oracle names from the final prose, regenerates the exhaustive `data-card-references` list, and links them. Use `designEcho.cardAliases` whenever prose intentionally shortens an Oracle name. Any recognized but unlinked name, partial link, wrong Oracle target, or declaration mismatch is a publication failure."
    text = text.replace(old_prompt, new_prompt)
    prompt.write_text(text, encoding="utf-8")


def update_workflow() -> None:
    path = ROOT / ".github" / "workflows" / "validate-archive.yml"
    text = path.read_text(encoding="utf-8")
    catalog_step = "      - name: Verify committed card-name catalog\n        run: python tools/refresh_card_name_catalog.py --check\n"
    if "Verify committed card-name catalog" not in text:
        text = text.replace("      - name: Verify canonical card references\n", catalog_step + "      - name: Verify canonical card references\n")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when any article would change")
    args = parser.parse_args()

    paths = article_paths()
    subjects = manifest_subjects()
    catalog = load_catalog(paths)
    _, supplement_aliases = load_supplement()
    results = [
        process_file(path, dict(catalog), subjects.get(path.name, ""), supplement_aliases.get(path.name, {}), args.check)
        for path in paths
    ]
    changed = sum(bool(row.get("changed")) for row in results)
    errors = [row for row in results if row.get("error")]

    if args.check:
        print(json.dumps({"articles": len(results), "would_change": changed, "errors": len(errors)}, indent=2))
        if changed or errors:
            for row in results:
                if row.get("changed") or row.get("error"):
                    print(f"- {row['file']}: " + (row.get("error") or "card references are not canonical"))
            return 1
        return 0

    update_schema()
    update_template()
    update_contracts()
    update_workflow()
    summary = {
        "articles": len(results),
        "changed_articles": changed,
        "errors": len(errors),
        "catalog_names_available": len(catalog),
        "linked_occurrences": sum(int(row.get("linked_occurrences", 0)) for row in results),
        "new_reference_names": sorted({name for row in results for name in row.get("new_references", [])}, key=str.casefold),
        "removed_reference_names": sorted({name for row in results for name in row.get("removed_references", [])}, key=str.casefold),
        "files": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "files"}, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
