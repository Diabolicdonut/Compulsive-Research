#!/usr/bin/env python3
"""Validate static Official Magic the Gathering deck sections against a snapshot."""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, OrderedDict, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

SECTION_LABEL = "Official Magic the Gathering decks"
CATEGORY_ORDER = ["Creatures", "Planeswalkers", "Instants", "Sorceries", "Artifacts", "Enchantments", "Battles", "Lands", "Other cards"]
ZONE_KEYS = ("mainBoard", "sideBoard", "commander", "displayCommander", "planes", "schemes")
ZONE_LABELS = {
    "mainBoard": "Main deck",
    "sideBoard": "Sideboard",
    "commander": "Commander",
    "displayCommander": "Display commander",
    "planes": "Planar deck",
    "schemes": "Scheme deck",
}

_CATALOGUE: dict[str, Any] | None = None
_PRODUCTS: dict[str, dict] = {}
_INVERTED: dict[str, set[str]] = defaultdict(set)
_NAME_INDEX: dict[str, set[str]] = defaultdict(set)


def normalize(value: Any) -> str:
    text = str(value or "").replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "", text)


def classify(type_line: str) -> str:
    t = str(type_line or "")
    if "Creature" in t: return "Creatures"
    if "Planeswalker" in t: return "Planeswalkers"
    if "Battle" in t: return "Battles"
    if "Instant" in t: return "Instants"
    if "Sorcery" in t: return "Sorceries"
    if "Artifact" in t: return "Artifacts"
    if "Enchantment" in t: return "Enchantments"
    if "Land" in t: return "Lands"
    return "Other cards"


def init_worker(catalogue_path: str) -> None:
    global _CATALOGUE, _PRODUCTS, _INVERTED, _NAME_INDEX
    _CATALOGUE = json.loads(Path(catalogue_path).read_text(encoding="utf-8"))
    _PRODUCTS = {p["id"]: p for p in _CATALOGUE["products"]}
    _INVERTED = defaultdict(set)
    for p in _CATALOGUE["products"]:
        for zone in p["zones"].values():
            for uuid, count in zone:
                if int(count) > 0:
                    _INVERTED[str(uuid)].add(p["id"])
    _NAME_INDEX = defaultdict(set)
    for uuid, card in _CATALOGUE["cards"].items():
        for name in (card.get("name"), card.get("faceName")):
            if name:
                _NAME_INDEX[normalize(name)].add(uuid)


def add(issues: list[dict], code: str, message: str, product: str | None = None) -> None:
    row = {"code": code, "message": message}
    if product:
        row["product"] = product
    issues.append(row)


def subject_from_soup(soup: BeautifulSoup, path: Path) -> str:
    body = soup.find("body")
    if not body or not body.get("data-article-card"):
        raise ValueError(f"{path.name}: missing data-article-card")
    return str(body["data-article-card"]).strip()


def aggregate(zone: list[list[Any]]) -> list[tuple[str, int, str]]:
    assert _CATALOGUE is not None
    cards = _CATALOGUE["cards"]
    by_name: OrderedDict[str, list[Any]] = OrderedDict()
    for uuid, count in zone:
        card = cards[str(uuid)]
        name = card["name"]
        if name not in by_name:
            by_name[name] = [0, card.get("type") or ""]
        by_name[name][0] += int(count)
    return [(name, int(value[0]), str(value[1])) for name, value in by_name.items()]


def expected_groups(product: dict) -> list[tuple[str, list[tuple[str, int]]]]:
    categories = {label: [] for label in CATEGORY_ORDER}
    for name, count, type_line in aggregate(product["zones"]["mainBoard"]):
        categories[classify(type_line)].append((name, count))
    groups = [(label, values) for label in CATEGORY_ORDER if (values := categories[label])]
    for key in ("sideBoard", "commander", "displayCommander", "planes", "schemes"):
        values = [(name, count) for name, count, _ in aggregate(product["zones"][key])]
        if values:
            groups.append((ZONE_LABELS[key], values))
    return groups


def actual_groups(deck: Tag) -> list[tuple[str, list[tuple[str, int]]]]:
    out = []
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        label_text = heading.get_text(" ", strip=True) if heading else "Cards"
        label = re.split(r"\s*[·|—-]\s*\d+\s*$", label_text, maxsplit=1)[0].strip()
        rows = []
        for row in group.select(".row"):
            qty = row.select_one(".qty")
            card = row.select_one(".card-name")
            if qty is None or card is None:
                continue
            qtext = qty.get_text(" ", strip=True)
            if not qtext.isdigit():
                rows.append((card.get_text(" ", strip=True), -1))
            else:
                rows.append((card.get("data-card") or card.get_text(" ", strip=True), int(qtext)))
        out.append((label, rows))
    return out


def zone_total(product: dict, key: str) -> int:
    return sum(int(count) for _, count in product["zones"][key])


def inspect(path: Path) -> dict:
    assert _CATALOGUE is not None
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    subject = subject_from_soup(soup, path)
    issues: list[dict] = []
    hosts = soup.select("details.official-mtg-decks")
    if len(hosts) != 1:
        add(issues, "SECTION_COUNT", f"Expected exactly one official section; found {len(hosts)}.")
        return {"file": path.name, "card": subject, "expected": 0, "actual": 0, "issues": issues, "status": "FAIL"}
    host = hosts[0]
    if host.has_attr("open"):
        add(issues, "SECTION_OPEN", "Official section must be collapsed by default.")
    summary_label = host.select_one(":scope > summary strong")
    if summary_label is None or summary_label.get_text(" ", strip=True) != SECTION_LABEL:
        add(issues, "SECTION_LABEL", f"Section label must be {SECTION_LABEL!r}.")
    if host.get("data-loaded") != "true":
        add(issues, "STATIC_MARKER", "Section must be marked data-loaded=true.")
    if host.get("data-catalogue-snapshot") != str(_CATALOGUE["snapshotDate"]):
        add(issues, "SNAPSHOT", "Article snapshot does not match the catalogue snapshot.")
    if raw.count("CR_OFFICIAL_MTG_DECKS_START") != 1 or raw.count("CR_OFFICIAL_MTG_DECKS_END") != 1:
        add(issues, "BUILD_MARKERS", "Static section build markers are missing or duplicated.")
    if "preconstructed-decks.js" in raw or "Open this section to load" in raw or "Loading the official" in raw:
        add(issues, "RUNTIME_PLACEHOLDER", "Legacy runtime-loader text or script remains.")

    subject_uuids = _NAME_INDEX.get(normalize(subject), set())
    expected_ids: set[str] = set()
    for uuid in subject_uuids:
        expected_ids.update(_INVERTED.get(uuid, set()))
    expected_products = sorted(
        (_PRODUCTS[pid] for pid in expected_ids),
        key=lambda p: (p.get("releaseDate") or "9999", p.get("type") or "", p.get("name") or "", p.get("setCode") or "", p["id"]),
    )
    expected_order = [p["id"] for p in expected_products]
    decks = host.select("details.official-mtg-deck")
    actual_order = [str(deck.get("data-product-id") or "") for deck in decks]
    if actual_order != expected_order:
        missing = [pid for pid in expected_order if pid not in actual_order]
        extras = [pid for pid in actual_order if pid not in expected_order]
        add(issues, "PRODUCT_SET", f"Embedded product IDs differ from catalogue. Missing={missing[:8]}, extras={extras[:8]}.")
    if host.get("data-official-deck-count") != str(len(expected_products)):
        add(issues, "SECTION_COUNT_ATTRIBUTE", f"data-official-deck-count should be {len(expected_products)}.")

    summary_small = host.select_one(":scope > summary small")
    shown_small = summary_small.get_text(" ", strip=True) if summary_small else ""
    if not expected_products and shown_small != "0":
        add(issues, "ZERO_SUMMARY", f"A zero-result section must show exactly '0'; found {shown_small!r}.")
    if expected_products and shown_small == "0":
        add(issues, "NONZERO_SUMMARY", "A nonempty section incorrectly displays a zero count.")

    if not expected_products:
        empty = host.select_one(".official-mtg-empty")
        if empty is None or empty.get_text(" ", strip=True) != _CATALOGUE["emptyState"]:
            add(issues, "EMPTY_STATE", "Required no-product comment is missing or altered.")
        if decks:
            add(issues, "EMPTY_HAS_DECKS", "Zero-result section contains deck entries.")
    else:
        if host.select_one(".official-mtg-empty"):
            add(issues, "NONEMPTY_HAS_EMPTY_STATE", "A nonempty section displays the empty-state comment.")

    for deck, product in zip(decks, expected_products):
        pid = product["id"]
        if deck.has_attr("open"):
            add(issues, "PRODUCT_OPEN", "Individual official deck must be collapsed by default.", pid)
        if deck.get("data-deck-kind") != "official-mtg-product":
            add(issues, "PRODUCT_KIND", "Official deck has the wrong data-deck-kind.", pid)
        expected_counts = {
            "data-main-count": zone_total(product, "mainBoard"),
            "data-sideboard-count": zone_total(product, "sideBoard"),
            "data-commander-count": zone_total(product, "commander"),
            "data-display-commander-count": zone_total(product, "displayCommander"),
            "data-plane-count": zone_total(product, "planes"),
            "data-scheme-count": zone_total(product, "schemes"),
        }
        for attr, value in expected_counts.items():
            if deck.get(attr) != str(value):
                add(issues, "PRODUCT_ZONE_COUNT", f"{attr} should be {value}, found {deck.get(attr)!r}.", pid)
        copies = sum(int(count) for key in ZONE_KEYS for uuid, count in product["zones"][key] if str(uuid) in subject_uuids)
        if deck.get("data-subject-copies") != str(copies):
            add(issues, "SUBJECT_COPIES", f"data-subject-copies should be {copies}.", pid)
        strong = deck.select_one(":scope > summary strong")
        if strong is None or strong.get_text(" ", strip=True) != product["name"]:
            add(issues, "PRODUCT_NAME", "Displayed product name does not match the catalogue.", pid)
        expected = expected_groups(product)
        actual = actual_groups(deck)
        if actual != expected:
            add(issues, "PRODUCT_CONTENTS", f"Rendered card groups do not match catalogue contents. Expected {expected[:2]!r}; found {actual[:2]!r}.", pid)

    status = "PASS" if not issues else "FAIL"
    return {"file": path.name, "card": subject, "expected": len(expected_products), "actual": len(decks), "issues": issues, "status": status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--catalogue", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    root = args.root.resolve()
    catalogue = (args.catalogue or (root / "official-mtg-deck-catalogue.json")).resolve()
    out = (args.output_dir or (root / "official-mtg-deck-validation")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(set(list(root.glob("[0-9][0-9][0-9]-*.html")) + list(root.glob("[0-9][0-9][0-9][0-9]-*.html")) + list(root.glob("honorable-*.html"))))
    with ProcessPoolExecutor(max_workers=max(1, args.jobs), initializer=init_worker, initargs=(str(catalogue),)) as pool:
        results = list(pool.map(inspect, files, chunksize=4))
    statuses = Counter(r["status"] for r in results)
    codes = Counter(i["code"] for r in results for i in r["issues"])
    payload = {
        "root": str(root),
        "catalogue": str(catalogue),
        "articles": len(results),
        "expectedDeckAppearances": sum(r["expected"] for r in results),
        "actualDeckAppearances": sum(r["actual"] for r in results),
        "statusCounts": dict(statuses),
        "issueCodeCounts": dict(codes),
        "results": results,
    }
    (out / "official-mtg-deck-validation.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Official Magic deck validation", "",
        f"- Articles: **{payload['articles']}**",
        f"- Expected embedded product appearances: **{payload['expectedDeckAppearances']}**",
        f"- Actual embedded product appearances: **{payload['actualDeckAppearances']}**",
        f"- Pass: **{statuses.get('PASS', 0)}**",
        f"- Fail: **{statuses.get('FAIL', 0)}**", "", "## Issue counts", "",
    ]
    lines.extend([f"- `{code}`: {count}" for code, count in codes.most_common()] or ["No issues found."])
    (out / "official-mtg-deck-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("articles", "expectedDeckAppearances", "actualDeckAppearances", "statusCounts", "issueCodeCounts")}, indent=2))
    return 1 if statuses.get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
