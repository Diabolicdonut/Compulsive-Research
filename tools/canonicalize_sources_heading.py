#!/usr/bin/env python3
"""Canonicalize the final Sources heading in every article.

The canonical order is:

    printing gallery
    <h3>Sources</h3>
    source records

This migration changes only the source heading: legacy heading variants are
renamed and missing headings are inserted immediately before the existing
source-record container. Article prose, source records, galleries, and other
components are preserved.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

SECTION_RE = re.compile(
    r"<section\b[^>]*\bid=(?P<q>['\"])(?:printings|sources)(?P=q)[^>]*>.*?</section>",
    re.IGNORECASE | re.DOTALL,
)
SOURCE_HEADING_RE = re.compile(
    r"<h(?P<level>[34])\b[^>]*>\s*(?:Research\s+sources|Research\s+trail|Sources)\s*</h(?P=level)>",
    re.IGNORECASE | re.DOTALL,
)
SOURCE_LIST_RE = re.compile(
    r"<(?:ol|ul|div)\b[^>]*\bclass=(?P<q>['\"])[^'\"]*(?:\bsources\b|\bsource-list\b)[^'\"]*(?P=q)[^>]*>",
    re.IGNORECASE | re.DOTALL,
)


def article_files(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*.html") if path.name != "index.html")


def canonicalize_section(section_html: str) -> tuple[str, str | None]:
    """Return updated section HTML and action (renamed/inserted/None)."""
    headings = list(SOURCE_HEADING_RE.finditer(section_html))
    if headings:
        # The archive should have one final source heading. Normalize the first
        # one and remove duplicate legacy source headings if any exist.
        first = headings[0]
        updated = section_html[: first.start()] + "<h3>Sources</h3>" + section_html[first.end() :]
        # Remove any later duplicate source-heading variants without touching
        # the section's h2 (“Printings … sources”).
        offset = first.start() + len("<h3>Sources</h3>")
        tail = SOURCE_HEADING_RE.sub("", updated[offset:])
        updated = updated[:offset] + tail
        return updated, "renamed" if first.group(0) != "<h3>Sources</h3>" or len(headings) > 1 else None

    source_list = SOURCE_LIST_RE.search(section_html)
    if not source_list:
        return section_html, "ERROR:no identifiable source-record container"

    updated = section_html[: source_list.start()] + "<h3>Sources</h3>" + section_html[source_list.start() :]
    return updated, "inserted"


def migrate_raw(raw: str) -> tuple[str, str | None]:
    match = SECTION_RE.search(raw)
    if not match:
        return raw, "ERROR:no #printings/#sources section"
    section = match.group(0)
    updated_section, action = canonicalize_section(section)
    if action and action.startswith("ERROR:"):
        return raw, action
    updated = raw[: match.start()] + updated_section + raw[match.end() :]
    return updated, action


def source_record_container(section: Tag, heading: Tag) -> Tag | None:
    canonical = section.select_one(".sources")
    if canonical:
        return canonical
    legacy = section.select_one(".source-list")
    if legacy:
        return legacy
    # A few early articles use a second .printings div as the source record
    # container. In those files, the record container is the first tag sibling
    # after the Sources heading that contains outbound links.
    sibling = heading.find_next_sibling()
    while isinstance(sibling, Tag):
        if sibling.find("a", href=True) or (sibling.name == "a" and sibling.get("href")):
            return sibling
        sibling = sibling.find_next_sibling()
    return None


def validate_path(path: Path) -> list[str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    article = soup.select_one("article.article")
    section = article.select_one("#printings, #sources") if article else None
    if not section:
        return ["missing #printings/#sources section"]

    headings = [
        h for h in section.find_all(["h3", "h4"], recursive=True)
        if h.get_text(" ", strip=True).casefold() in {"sources", "research sources", "research trail"}
    ]
    canonical = [h for h in headings if h.name == "h3" and h.get_text(" ", strip=True) == "Sources"]
    errors: list[str] = []
    if len(canonical) != 1:
        errors.append(f"expected exactly one h3 Sources heading; found {len(canonical)}")
        return errors
    if len(headings) != 1:
        variants = ", ".join(h.get_text(" ", strip=True) for h in headings)
        errors.append(f"legacy or duplicate source headings remain: {variants}")

    heading = canonical[0]
    records = source_record_container(section, heading)
    if not records:
        errors.append("could not identify source-record container after Sources heading")
        return errors

    previous = records.find_previous_sibling()
    if previous is not heading:
        errors.append("Sources heading is not immediately before the source-record container")

    # The card gallery must precede the heading. Accept either canonical
    # .printings or the dynamic #printing-grid component.
    galleries = section.select("#printing-grid, .printings")
    galleries_before = [g for g in galleries if g is not records and g.sourceline is not None]
    # BeautifulSoup sourceline is not dependable for minified HTML, so use the
    # source order of descendants instead.
    descendants = [node for node in section.descendants if isinstance(node, Tag)]
    try:
        heading_index = descendants.index(heading)
        record_index = descendants.index(records)
    except ValueError:
        errors.append("unable to establish source-heading document order")
        return errors
    gallery_nodes = [g for g in galleries if g is not records and g in descendants]
    if not gallery_nodes:
        errors.append("no printing gallery found before Sources heading")
    elif not any(descendants.index(g) < heading_index for g in gallery_nodes):
        errors.append("Sources heading does not follow the printing gallery")
    if heading_index >= record_index:
        errors.append("Sources heading does not precede source records")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Report drift without changing files.")
    args = parser.parse_args()

    root = args.root.resolve()
    changed: list[tuple[str, str]] = []
    errors: list[str] = []

    for path in article_files(root):
        raw = path.read_text(encoding="utf-8")
        updated, action = migrate_raw(raw)
        if action and action.startswith("ERROR:"):
            errors.append(f"{path.name}: {action[6:]}")
            continue
        if updated != raw:
            changed.append((path.name, action or "updated"))
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    if not args.check:
        for path in article_files(root):
            for error in validate_path(path):
                errors.append(f"{path.name}: {error}")

    if errors:
        print("SOURCES HEADING ERRORS")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.check and changed:
        print("SOURCES HEADING DRIFT")
        for filename, action in changed:
            print(f"- {filename}: {action}")
        return 1

    if args.check:
        # Check placement, not only whether the migration would alter bytes.
        placement_errors: list[str] = []
        for path in article_files(root):
            for error in validate_path(path):
                placement_errors.append(f"{path.name}: {error}")
        if placement_errors:
            print("SOURCES HEADING ERRORS")
            for error in placement_errors:
                print(f"- {error}")
            return 1

    counts: dict[str, int] = {}
    for _, action in changed:
        counts[action] = counts.get(action, 0) + 1
    verb = "Would update" if args.check else "Updated"
    print(f"{verb} {len(changed)} article(s).")
    for action, count in sorted(counts.items()):
        print(f"- {action}: {count}")
    if not changed:
        print("All article source headings already match the canonical gallery → Sources → records order.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
