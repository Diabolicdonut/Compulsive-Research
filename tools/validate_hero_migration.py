#!/usr/bin/env python3
"""Hero and headline migration validator suite for Compulsive Research."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from headline_identity import (
    GENERIC_HEADLINES,
    editorial_headline,
    headline_contains_card_name,
    normalize as normalize_headline,
)
from hero_identity import (
    NUMBERED_RE,
    article_card,
    canonical_art_urls,
    header_css_urls,
    identity,
    identity_matches,
    metadata_map,
    normalize_name,
    numbered_files,
)

SUITE_VERSION = "2.0.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_card_data(root: Path) -> dict[int, dict]:
    payload = json.loads((root / "data" / "remaining-entry-card-data.json").read_text(encoding="utf-8"))
    return {int(card["entry"]): card for card in payload["cards"]}


def headline_text(hero) -> str:
    if not hero:
        return ""
    h1 = hero.find("h1")
    if not h1:
        return ""
    return normalize_headline(h1.get_text(" ", strip=True))


def append_finding(row: dict, finding: str) -> None:
    findings = [value for value in row.get("findings", "").split("|") if value]
    if finding not in findings:
        findings.append(finding)
    row["findings"] = "|".join(findings)
    row["finding_count"] = len(findings)
    row["status"] = "FAIL" if findings else "PASS"


def validate_page(path: Path, card: str, card_data: dict) -> dict:
    entry = int(NUMBERED_RE.match(path.name).group(1))
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    art_url, normal_url = canonical_art_urls(soup, card)
    hero = soup.select_one("header.hero")
    findings: list[str] = []
    actual_src = ""
    actual_identity = ""
    mode = "missing"
    headline = headline_text(hero)
    expected_headline = editorial_headline(card_data, path.parent)

    if not hero:
        findings.append("MISSING_HERO")
    else:
        hero_img = hero.select_one("img.hero-media")
        if hero_img and hero_img.get("src"):
            mode = "image"
            actual_src = hero_img.get("src")
            actual_identity = str(identity(actual_src) or "")
            if not identity_matches(actual_src, art_url, card):
                findings.append("HERO_IMAGE_IDENTITY_MISMATCH")
            fallback = hero_img.get("onerror") or ""
            urls = re.findall(r"https://api\.scryfall\.com/cards/[^'\";]+", fallback)
            if not urls or not identity_matches(urls[-1], normal_url, card):
                findings.append("HERO_FALLBACK_IDENTITY_MISMATCH")
            if entry >= 401 and normalize_name(hero_img.get("data-hero-card") or "") != normalize_name(card):
                findings.append("HERO_IMAGE_DATA_CARD_MISMATCH")
            if entry >= 401 and normalize_name(hero.get("data-hero-card") or "") != normalize_name(card):
                findings.append("HERO_HEADER_DATA_CARD_MISMATCH")
        else:
            mode = "css-legacy"
            css_urls = header_css_urls(text, hero.get("class") if hero else [])
            matching = [url for url in css_urls if identity_matches(url, art_url, card)]
            if not matching:
                findings.append("CSS_HERO_IDENTITY_MISMATCH")
            elif matching:
                actual_src = matching[-1]
                actual_identity = str(identity(actual_src) or "")

        if entry >= 401:
            lock = soup.find("style", id="hero-identity-contract")
            if not lock:
                findings.append("MISSING_HERO_IDENTITY_CONTRACT")
            else:
                lock_urls = re.findall(r"https://api\.scryfall\.com/cards/[^\"'\)\s;]+", lock.get_text(" ", strip=True))
                if not lock_urls or not all(identity_matches(url, art_url, card) for url in lock_urls):
                    findings.append("HERO_CONTRACT_IDENTITY_MISMATCH")
            h1 = hero.find("h1")
            if not h1:
                findings.append("HERO_HEADING_STRUCTURE_MISMATCH")
            else:
                if h1.select_one(".hero-card-name"):
                    findings.append("VISIBLE_CARD_NAME_LABEL_PRESENT")
                if h1.select_one(".hero-title"):
                    findings.append("LEGACY_HERO_TITLE_WRAPPER_PRESENT")

            body_card = normalize_name(soup.body.get("data-article-card") if soup.body else "")
            if body_card != normalize_name(card):
                findings.append("BODY_ARTICLE_CARD_MISMATCH")
            h1_node = hero.find("h1")
            for node, code in [
                (hero, "HERO_HEADLINE_CARD_MISMATCH"),
                (h1_node, "H1_HEADLINE_CARD_MISMATCH"),
            ]:
                if not node or normalize_name(node.get("data-headline-card") or "") != normalize_name(card):
                    findings.append(code)

    if not headline:
        findings.append("MISSING_HERO_HEADLINE")
    if headline in GENERIC_HEADLINES:
        findings.append("SHARED_GENERIC_HEADLINE")
    if expected_headline and headline != expected_headline:
        findings.append("GENERATED_HEADLINE_DOES_NOT_MATCH_TEMPLATE")
    if headline_contains_card_name(headline, card):
        findings.append("HEADLINE_CONTAINS_FULL_CARD_NAME")
    if expected_headline:
        meta = soup.find("meta", attrs={"name": "article-headline"})
        if entry >= 401:
            if not meta or normalize_headline(meta.get("content") or "") != headline:
                findings.append("HEADLINE_META_MISMATCH")
            opening = soup.select_one("#opening h2")
            if not opening or normalize_headline(opening.get_text(" ", strip=True)) != headline:
                findings.append("OPENING_HEADING_MISMATCH")
            toc = soup.select_one('nav.toc a[href="#opening"]')
            if not toc or normalize_headline(toc.get_text(" ", strip=True)) != headline:
                findings.append("OPENING_TOC_MISMATCH")
        elif meta and normalize_headline(meta.get("content") or "") != headline:
            findings.append("HEADLINE_META_MISMATCH")
    if soup.title and headline not in soup.title.get_text(" ", strip=True):
        findings.append("DOCUMENT_TITLE_HEADLINE_MISMATCH")

    return {
        "file": path.name,
        "entry": entry,
        "card": card,
        "range": "001-400" if entry <= 400 else "401-1000",
        "hero_mode": mode,
        "expected_art": art_url,
        "actual_hero": actual_src,
        "actual_identity": actual_identity,
        "headline": headline,
        "expected_headline": expected_headline,
        "status": "PASS" if not findings else "FAIL",
        "finding_count": len(findings),
        "findings": "|".join(findings),
        "sha256": sha256(path),
    }


def validate_generator(root: Path) -> list[str]:
    path = root / "tools" / "generate_remaining_entries.py"
    text = path.read_text(encoding="utf-8")
    failures = []
    required = [
        "hero_header['data-hero-card']",
        "hero_media['data-hero-card']",
        "hero_media['src'] = art_url",
        "hero_media['onerror']",
        "id='hero-identity-contract'",
        "from headline_identity import editorial_headline",
        "return editorial_headline(card)",
        "soup.body['data-article-card'] = card['articleName']",
        "headline_meta['content'] = title",
        "hero_header['data-headline-card'] = card['articleName']",
        "h1['data-headline-card'] = card['articleName']",
        "h1.string = title",
    ]
    for token in required:
        if token not in text:
            failures.append(f"GENERATOR_MISSING:{token}")
    for token in ["hero-card-name", "card_name_span", "editorial_span"]:
        if token in text:
            failures.append(f"GENERATOR_FORBIDDEN_VISIBLE_CARD_LABEL:{token}")
    if "Garruk%20Wildspeaker" in text or "Garruk Wildspeaker" in text:
        failures.append("GENERATOR_CONTAINS_GARRUK_HERO_LITERAL")
    if re.search(r"return\s+ROLE_TITLES", text):
        failures.append("GENERATOR_STILL_RETURNS_SHARED_ROLE_TITLE")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or (root / "audit" / "hero-migration")).resolve()
    output.mkdir(parents=True, exist_ok=True)

    known = metadata_map(root)
    cards = load_card_data(root)
    files = numbered_files(root)
    rows = []
    for path in files:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        card = article_card(path, soup, known)
        entry = int(NUMBERED_RE.match(path.name).group(1))
        rows.append(validate_page(path, card, cards[entry]))

    duplicate_map: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["actual_identity"]:
            duplicate_map[row["actual_identity"]].append(row)
    duplicate_failures = []
    for ident, group in duplicate_map.items():
        cards_in_group = {normalize_name(r["card"]) for r in group}
        if len(group) > 1 and len(cards_in_group) > 1:
            duplicate_failures.append({"identity": ident, "files": [r["file"] for r in group], "cards": [r["card"] for r in group]})
            for row in group:
                append_finding(row, "CROSS_CARD_DUPLICATE_HERO")

    headline_map: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["headline"]:
            headline_map[normalize_headline(row["headline"]).casefold()].append(row)
    headline_duplicate_failures = []
    for key, group in headline_map.items():
        if key and len(group) > 1:
            headline_duplicate_failures.append({
                "headline": group[0]["headline"],
                "files": [r["file"] for r in group],
                "cards": [r["card"] for r in group],
            })
            for row in group:
                append_finding(row, "DUPLICATE_HERO_HEADLINE")

    generator_failures = validate_generator(root)
    counts = {
        "numbered_files": len(rows),
        "passed": sum(r["status"] == "PASS" for r in rows),
        "failed": sum(r["status"] == "FAIL" for r in rows),
        "entries_001_400_passed": sum(r["status"] == "PASS" and r["entry"] <= 400 for r in rows),
        "entries_001_400_failed": sum(r["status"] == "FAIL" and r["entry"] <= 400 for r in rows),
        "entries_401_1000_passed": sum(r["status"] == "PASS" and r["entry"] >= 401 for r in rows),
        "entries_401_1000_failed": sum(r["status"] == "FAIL" and r["entry"] >= 401 for r in rows),
        "image_heroes": sum(r["hero_mode"] == "image" for r in rows),
        "legacy_css_heroes": sum(r["hero_mode"] == "css-legacy" for r in rows),
        "cross_card_duplicate_groups": len(duplicate_failures),
        "unique_headlines": len(headline_map),
        "duplicate_headline_groups": len(headline_duplicate_failures),
        "generator_failures": len(generator_failures),
    }
    passed = (
        counts["failed"] == 0
        and not duplicate_failures
        and not headline_duplicate_failures
        and not generator_failures
        and len(rows) == 1000
        and counts["unique_headlines"] == 1000
    )

    csv_path = output / "hero-migration-validation.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "suite": "Compulsive Research Hero and Headline Migration Validator Suite",
        "suite_version": SUITE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if passed else "FAIL",
        "counts": counts,
        "generator_failures": generator_failures,
        "duplicate_failures": duplicate_failures,
        "headline_duplicate_failures": headline_duplicate_failures,
        "failed_pages": [r for r in rows if r["status"] == "FAIL"],
    }
    json_path = output / "hero-migration-validation.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = [
        "# Hero and Headline Migration Validator Suite",
        "",
        f"**Result:** {payload['result']}",
        f"**Suite version:** {SUITE_VERSION}",
        f"**Numbered articles scanned:** {counts['numbered_files']}",
        "",
        "## Results",
        "",
        f"- Entries 001–400: {counts['entries_001_400_passed']} passed, {counts['entries_001_400_failed']} failed.",
        f"- Entries 401–1000: {counts['entries_401_1000_passed']} passed, {counts['entries_401_1000_failed']} failed.",
        f"- Explicit image heroes: {counts['image_heroes']}.",
        f"- Valid legacy CSS-only heroes: {counts['legacy_css_heroes']}.",
        f"- Cross-card duplicate hero groups: {counts['cross_card_duplicate_groups']}.",
        f"- Unique hero headlines: {counts['unique_headlines']} of 1,000.",
        f"- Duplicate headline groups: {counts['duplicate_headline_groups']}.",
        f"- Generator contract failures: {counts['generator_failures']}.",
        "",
        "## Enforced contract",
        "",
        "1. The visible hero image must identify the article card.",
        "2. The image-error fallback and final CSS fallback must identify the same card.",
        "3. Entries 401–1000 must display the card name in the hero heading.",
        "4. Different cards may not share the same resolved hero identity.",
        "5. Every numbered article must have a unique, card-relevant editorial headline.",
        "6. Shared role/category headlines from the former generator are forbidden.",
        "7. Generated headlines must match the deterministic headline template and all headline metadata must agree.",
        "8. The generation template must write card-specific hero media and card-specific headlines.",
    ]
    if generator_failures:
        md.extend(["", "## Generator failures", ""] + [f"- {x}" for x in generator_failures])
    if payload["failed_pages"]:
        md.extend(["", "## Failed pages", ""] + [f"- `{r['file']}`: {r['findings']}" for r in payload["failed_pages"]])
    (output / "HERO-MIGRATION-VALIDATION-REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(payload["counts"], indent=2))
    print(f"Hero and Headline Migration Validator Suite: {payload['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
