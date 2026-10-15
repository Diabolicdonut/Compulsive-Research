#!/usr/bin/env python3
"""Validate reader-facing article layout conventions introduced after Wave 02."""
from __future__ import annotations

import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BANNED_DESIGN_HEADINGS = {
    "The descendants of the bargain",
    "The descendants",
    "Every Mox after the Moxen",
}


def numbered(limit: int = 100) -> list[Path]:
    out: list[Path] = []
    for n in range(1, limit + 1):
        matches = list(ROOT.glob(f"{n:03d}-*.html"))
        if len(matches) != 1:
            raise RuntimeError(f"entry {n:03d}: expected one article, found {len(matches)}")
        out.append(matches[0])
    return out


def main() -> int:
    errors: list[str] = []
    checked = 0

    for path in numbered(100):
        checked += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(text, "lxml")

        strategic = soup.find("section", id="strategic-legacy-brief")
        opening = soup.find("section", id="opening")
        if strategic:
            if not opening:
                errors.append(f"{path.name}: Strategic legacy exists without #opening")
            elif opening.find_next_sibling("section") is not strategic:
                errors.append(f"{path.name}: Strategic legacy must follow the opening introduction")
            toc = soup.find("nav", class_="toc")
            if toc:
                opening_link = toc.find("a", href="#opening")
                strategic_link = toc.find("a", href="#strategic-legacy-brief")
                if not opening_link or not strategic_link or opening_link.find_next_sibling("a") is not strategic_link:
                    errors.append(f"{path.name}: TOC order does not match opening → Strategic legacy")

        for section in soup.select("section.design-echo-section"):
            h2 = section.find("h2")
            if h2 and h2.get_text(" ", strip=True) in BANNED_DESIGN_HEADINGS:
                errors.append(f"{path.name}: generic Design Echo heading: {h2.get_text(' ', strip=True)!r}")

        for nav in soup.select(".end-nav"):
            if nav.find_parent("article") is not None:
                errors.append(f"{path.name}: end navigation is embedded inside article content")
        if len(soup.select(".end-nav")) != 1:
            errors.append(f"{path.name}: expected exactly one end navigation, found {len(soup.select('.end-nav'))}")

        for heading in soup.find_all(["h2", "h3"]):
            if heading.get_text(" ", strip=True).lower() != "sources":
                continue
            nxt = heading.find_next_sibling()
            if nxt and nxt.name == "div" and "printings" in (nxt.get("class") or []):
                errors.append(f"{path.name}: Sources is incorrectly rendered with printing-gallery layout")

    # The comparison image must not drift to the newest crossover treatment.
    for path in ROOT.glob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if 'data-card-name="Arcane Signet"' not in text:
            continue
        soup = BeautifulSoup(text, "lxml")
        for img in soup.find_all("img", attrs={"data-card-name": "Arcane Signet"}):
            for attr in ("data-api-url", "data-fallback-art", "data-fallback-normal", "data-fallback-fuzzy"):
                value = img.get(attr, "")
                if "set=eld" not in value:
                    errors.append(f"{path.name}: Arcane Signet {attr} is not pinned to the original ELD printing")

    css_path = ROOT / "preconstructed-decks.css"
    css = css_path.read_text(encoding="utf-8", errors="ignore") if css_path.exists() else ""
    required_css = [
        ".preconstructed-archive.official-mtg-decks",
        "background:#192b28",
        "color:#e7eeeb!important",
        ">summary strong",
        ">summary small",
    ]
    for token in required_css:
        if token not in css:
            errors.append(f"preconstructed-decks.css: missing contrast rule {token!r}")

    if errors:
        print(f"Reader layout contract: FAIL ({len(errors)} finding(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Reader layout contract: PASS ({checked} processed numbered articles; global Arcane Signet and product-contrast checks passed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
