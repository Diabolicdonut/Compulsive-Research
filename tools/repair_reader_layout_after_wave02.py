#!/usr/bin/env python3
"""Repair reader-facing layout defects identified after Numbered Wave 02.

Scope:
- entries 001-100: move Strategic legacy after the opening introduction
- all active articles: remove duplicate in-article end navigation when a canonical
  continue-reading navigation already exists
- repair generic Design Echo headings
- normalize malformed source lists
- pin Arcane Signet comparison art to its original ELD printing
"""
from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]

DESIGN_TITLES = {
    "004-mox-pearl.html": "White acceleration after Mox Pearl",
    "005-mox-sapphire.html": "Blue acceleration after Mox Sapphire",
    "006-mox-jet.html": "Black acceleration after Mox Jet",
    "028-force-of-nature.html": "Green's colossal creatures after Force of Nature",
    "029-lord-of-the-pit.html": "Black's demons after Lord of the Pit",
    "030-vesuvan-doppelganger.html": "Magic's shapeshifters after Vesuvan Doppelganger",
    "051-juzam-djinn.html": "The monsters that inherited Juzám's risk",
    "055-city-of-brass.html": "What perfect mana cost after City of Brass",
}


def numbered_articles(limit: int = 100) -> list[Path]:
    out: list[Path] = []
    for n in range(1, limit + 1):
        matches = list(ROOT.glob(f"{n:03d}-*.html"))
        if len(matches) != 1:
            raise RuntimeError(f"Expected one article for entry {n:03d}, found {len(matches)}")
        out.append(matches[0])
    return out


def move_strategic_after_opening(soup: BeautifulSoup) -> bool:
    strategic = soup.find("section", id="strategic-legacy-brief")
    opening = soup.find("section", id="opening")
    if not strategic or not opening or strategic.parent is not opening.parent:
        return False
    if opening.find_next_sibling("section") is strategic:
        changed = False
    else:
        strategic.extract()
        opening.insert_after(strategic)
        changed = True

    toc = soup.find("nav", class_="toc")
    if toc:
        strategic_link = toc.find("a", href="#strategic-legacy-brief")
        opening_link = toc.find("a", href="#opening")
        if strategic_link and opening_link and opening_link.find_next_sibling("a") is not strategic_link:
            strategic_link.extract()
            opening_link.insert_after(strategic_link)
            changed = True
    return changed


def remove_duplicate_inner_nav(soup: BeautifulSoup) -> int:
    navs = soup.select(".end-nav")
    outside = [n for n in navs if n.find_parent("article") is None]
    removed = 0
    if outside:
        for nav in navs:
            if nav.find_parent("article") is not None:
                nav.decompose()
                removed += 1
    return removed


def fix_design_heading(soup: BeautifulSoup, filename: str) -> bool:
    title = DESIGN_TITLES.get(filename)
    if not title:
        return False
    sections = soup.select("section.design-echo-section")
    # Prefer the generic section; otherwise use the last design-echo section.
    target = None
    for sec in sections:
        h2 = sec.find("h2")
        if h2 and h2.get_text(" ", strip=True) in {
            "The descendants of the bargain",
            "The descendants",
            "Every Mox after the Moxen",
        }:
            target = sec
            break
    if target is None and sections:
        target = sections[-1]
    if target is None:
        return False
    h2 = target.find("h2")
    if not h2 or h2.get_text(" ", strip=True) == title:
        return False
    h2.string = title
    toc = soup.find("nav", class_="toc")
    if toc and target.get("id"):
        link = toc.find("a", href=f"#{target['id']}")
        if link:
            link.string = title
    return True


def normalize_source_grid(soup: BeautifulSoup) -> bool:
    changed = False
    for heading in soup.find_all(["h2", "h3"]):
        if heading.get_text(" ", strip=True).lower() != "sources":
            continue
        node = heading.find_next_sibling()
        if not isinstance(node, Tag) or node.name != "div" or "printings" not in (node.get("class") or []):
            continue
        ol = soup.new_tag("ol")
        ol["class"] = ["sources"]
        for anchor in node.find_all("a", recursive=False):
            li = soup.new_tag("li")
            new_a = soup.new_tag("a", href=anchor.get("href", "#"))
            bold = anchor.find("b")
            new_a.string = bold.get_text(" ", strip=True) if bold else anchor.get_text(" ", strip=True)
            li.append(new_a)
            desc = anchor.find("span")
            if desc:
                span = soup.new_tag("span")
                span.string = desc.get_text(" ", strip=True)
                li.append(span)
            ol.append(li)
        node.replace_with(ol)
        changed = True
    return changed


def pin_arcane_signet(soup: BeautifulSoup) -> bool:
    changed = False
    for img in soup.find_all("img", attrs={"data-card-name": "Arcane Signet"}):
        replacements = {
            "data-api-url": "https://api.scryfall.com/cards/named?exact=Arcane+Signet&set=eld",
            "data-fallback-art": "https://api.scryfall.com/cards/named?exact=Arcane+Signet&set=eld&format=image&version=art_crop",
            "data-fallback-normal": "https://api.scryfall.com/cards/named?exact=Arcane+Signet&set=eld&format=image&version=normal",
            "data-fallback-fuzzy": "https://api.scryfall.com/cards/named?exact=Arcane+Signet&set=eld&format=image&version=art_crop",
        }
        for key, value in replacements.items():
            if img.get(key) != value:
                img[key] = value
                changed = True
    return changed


def write_if_changed(path: Path, soup: BeautifulSoup, original: str, changed: bool) -> bool:
    if not changed:
        return False
    rendered = str(soup)
    if original.lstrip().lower().startswith("<!doctype html>") and not rendered.lstrip().lower().startswith("<!doctype html>"):
        rendered = "<!doctype html>\n" + rendered
    path.write_text(rendered, encoding="utf-8")
    return True


def main() -> int:
    touched: set[str] = set()
    strategic_moves = 0
    inner_nav_removed = 0
    design_fixed = 0
    sources_fixed = 0
    arcane_fixed = 0

    # Process entries 001-100 for placement and their other targeted repairs.
    numbered = numbered_articles(100)
    numbered_set = set(numbered)
    target_paths = numbered_set | {ROOT / "514-heart-of-kiran.html"}

    for path in sorted(target_paths):
        original = path.read_text(encoding="utf-8", errors="ignore")
        needs_parse = (
            path in numbered_set
            or 'class="end-nav"' in original
            or 'data-card-name="Arcane Signet"' in original
            or "<h3>Sources</h3><div class=\"printings\">" in original
        )
        if not needs_parse:
            continue
        soup = BeautifulSoup(original, "lxml")
        changed = False
        if path.name[:3].isdigit() and int(path.name[:3]) <= 100:
            if move_strategic_after_opening(soup):
                strategic_moves += 1; changed = True
            if fix_design_heading(soup, path.name):
                design_fixed += 1; changed = True
            if normalize_source_grid(soup):
                sources_fixed += 1; changed = True
        removed = remove_duplicate_inner_nav(soup)
        if removed:
            inner_nav_removed += removed; changed = True
        if pin_arcane_signet(soup):
            arcane_fixed += 1; changed = True
        if write_if_changed(path, soup, original, changed):
            touched.add(path.name)

    print(f"touched={len(touched)}")
    print(f"strategic_moves={strategic_moves}")
    print(f"inner_nav_removed={inner_nav_removed}")
    print(f"design_headings_fixed={design_fixed}")
    print(f"source_grids_fixed={sources_fixed}")
    print(f"arcane_signet_pages_fixed={arcane_fixed}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
