#!/usr/bin/env python3
"""Independently validate discovered Design Echo card references."""
from __future__ import annotations

from collections import Counter
import argparse
import csv
import json
from pathlib import Path

from bs4 import BeautifulSoup

from card_reference_engine import (
    clone_without_links,
    clean_name,
    display_map_from_catalog,
    discover_section_matches,
    load_json_list_attribute,
    load_json_map_attribute,
    match_counter,
    norm_key,
    unique_names,
)
from canonicalize_card_links import article_paths, load_catalog, load_supplement, manifest_subjects, section_image_card

ROOT = Path(__file__).resolve().parents[1]


def counter_difference(left: Counter[str], right: Counter[str]) -> list[str]:
    output: list[str] = []
    for name, count in sorted((left - right).items(), key=lambda item: item[0].casefold()):
        output.append(f"{name}" + (f" ×{count}" if count > 1 else ""))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--article', type=Path, action='append', help='Limit validation to a canonical article (repeatable)')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'audit')
    args = parser.parse_args()
    paths = sorted({(ROOT / path).resolve() for path in args.article}) if args.article else article_paths()
    if args.article and not set(paths).issubset(set(article_paths())):
        parser.error('--article must name an existing canonical production article')
    subjects = manifest_subjects()
    catalog = load_catalog([])
    _, supplement_aliases = load_supplement()
    rows: list[dict[str, object]] = []
    failures = 0

    for path in paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        issues: list[str] = []
        subject = subjects.get(path.name, "")

        for element in soup.select(".card-name"):
            if not clean_name(element.get("data-card")):
                issues.append("card-name missing data-card")
            if element.get("tabindex") != "0":
                issues.append("card-name missing tabindex=0")

        section = soup.select_one(".design-echo-section")
        expected: Counter[str] = Counter()
        actual: Counter[str] = Counter()
        declared: list[str] = []
        if not section:
            issues.append("Design Echo section missing")
        else:
            declared = load_json_list_attribute(section, "data-card-references")
            raw_declaration = section.get("data-card-references")
            if raw_declaration is None:
                issues.append("data-card-references missing")
            else:
                try:
                    parsed = json.loads(raw_declaration)
                    if not isinstance(parsed, list) or not all(isinstance(item, str) and item.strip() for item in parsed):
                        issues.append("data-card-references must be a string array")
                    elif len({norm_key(item) for item in parsed}) != len(parsed):
                        issues.append("data-card-references contains duplicates")
                except json.JSONDecodeError:
                    issues.append("data-card-references is not valid JSON")

            aliases = load_json_map_attribute(section, "data-card-aliases")
            aliases.update(supplement_aliases.get(path.name, {}))
            for canonical in aliases.values():
                cleaned = clean_name(canonical)
                if cleaned:
                    catalog.setdefault(norm_key(cleaned), cleaned)

            clone = clone_without_links(section)
            display_map = display_map_from_catalog(catalog, aliases)
            # Declarations are supplied only as single-word ambiguity hints.
            # The scan itself derives expected references from visible prose.
            image_card = section_image_card(section)
            explicit_hints = declared + list(aliases.values()) + ([image_card] if image_card else [])
            expected_matches = discover_section_matches(
                clone,
                display_map,
                subject,
                explicit_names=explicit_hints,
                aliases=aliases,
            )
            expected = match_counter(expected_matches)

            for element in section.select(".card-name[data-card]"):
                canonical = clean_name(element.get("data-card"))
                if not canonical:
                    continue
                actual[canonical] += 1
                display = clean_name(element.get_text(" ", strip=True)) or ""
                target_key = norm_key(canonical)
                valid_display = norm_key(display) == target_key
                alias_target = aliases.get(display)
                if alias_target and norm_key(alias_target) == target_key:
                    valid_display = True
                if not valid_display:
                    issues.append(f"card link display/target mismatch: {display} → {canonical}")
                if target_key == norm_key(subject):
                    issues.append(f"subject card linked in Design Echo prose: {canonical}")
                if target_key not in catalog:
                    issues.append(f"card link target absent from catalog: {canonical}")

            missing = counter_difference(expected, actual)
            extra = counter_difference(actual, expected)
            if missing:
                issues.append("recognized but unlinked card occurrences: " + "; ".join(missing))
            if extra:
                issues.append("unexpected or partial card links: " + "; ".join(extra))

            expected_unique = sorted(unique_names(expected.keys()), key=str.casefold)
            declared_unique = sorted(unique_names(declared), key=str.casefold)
            if {norm_key(x) for x in expected_unique} != {norm_key(x) for x in declared_unique}:
                missing_declared = sorted(
                    [x for x in expected_unique if norm_key(x) not in {norm_key(y) for y in declared_unique}],
                    key=str.casefold,
                )
                stale_declared = sorted(
                    [x for x in declared_unique if norm_key(x) not in {norm_key(y) for y in expected_unique}],
                    key=str.casefold,
                )
                if missing_declared:
                    issues.append("data-card-references omits discovered cards: " + "; ".join(missing_declared))
                if stale_declared:
                    issues.append("data-card-references contains cards absent from prose: " + "; ".join(stale_declared))

            alias_targets = {norm_key(value) for value in aliases.values()}
            expected_keys = {norm_key(name) for name in expected}
            unused_aliases = [display for display, target in aliases.items() if norm_key(target) not in expected_keys]
            if unused_aliases:
                issues.append("unused card aliases: " + "; ".join(sorted(unused_aliases, key=str.casefold)))
            if section.get("data-card-discovery") != "oracle-catalog-v2":
                issues.append("data-card-discovery marker missing or obsolete")

        html_text = str(soup)
        if "CR_CARD_PREVIEW_RUNTIME_START" not in html_text:
            issues.append("delegated card preview runtime missing")
        if "querySelectorAll('.card-name')" in html_text or 'querySelectorAll(".card-name")' in html_text:
            issues.append("legacy per-element card listener remains")
        if "CR_CARD_LINK_DESIGN_ECHO_STYLES" not in html_text:
            issues.append("Design Echo card-link styles missing")

        issues = list(dict.fromkeys(issues))
        status = "PASS" if not issues else "FAIL"
        failures += bool(issues)
        rows.append({
            "file": path.name,
            "status": status,
            "issues": " | ".join(issues),
            "discovered_unique": len(expected),
            "discovered_occurrences": sum(expected.values()),
            "linked_occurrences": sum(actual.values()),
            "declared_unique": len(declared),
        })

    audit = args.output_dir
    audit.mkdir(parents=True, exist_ok=True)
    fields = ["file", "status", "issues", "discovered_unique", "discovered_occurrences", "linked_occurrences", "declared_unique"]
    with (audit / "card-link-validation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    payload = {"articles": len(rows), "passes": len(rows) - failures, "failures": failures, "rows": rows}
    (audit / "card-link-validation.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "rows"}, indent=2))
    if failures:
        for row in rows:
            if row["status"] == "FAIL":
                print(f"- {row['file']}: {row['issues']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
