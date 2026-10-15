#!/usr/bin/env python3
"""Normalize canonical debut records to the regular base printing.

This pass fixes a subtle data issue left by the promo-container repair: when a card
had multiple treatments in its true debut set, lexicographic collector-number sorting
could select a showcase/borderless treatment (for example 311 before 87). The regular
base printing is selected by numeric collector order, while preserving split suffixes
such as 32a/32b.

The pass also repairs article pages whose visible original-printing metadata differs
from the committed snapshot.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]


def collector_key(value: Any) -> tuple[int, str]:
    text = str(value or "").strip()
    match = re.match(r"(\d+)", text)
    return (int(match.group(1)) if match else 10**9, text.casefold())


def choose_base_printing(card: dict[str, Any]) -> dict[str, Any] | None:
    same = [
        p for p in card.get("printings", [])
        if p.get("setCode") == card.get("setCode")
        and p.get("releaseDate") == card.get("releaseDate")
    ]
    if not same:
        return None
    return min(same, key=lambda p: collector_key(p.get("collectorNumber")))


def replace_text(node, old: str, new: str) -> None:
    if not node or not old or old == new:
        return
    for text in list(node.find_all(string=True)):
        raw = str(text)
        if old in raw:
            text.replace_with(NavigableString(raw.replace(old, new)))


def make_caption(soup: BeautifulSoup, record: dict[str, Any]) -> Any:
    cap = soup.new_tag("figcaption")
    bold = soup.new_tag("b")
    year = str(record.get("releaseDate", ""))[:4]
    bold.string = record.get("setName", "Printing") + (f" · {year}" if year else "")
    cap.append(bold)
    cap.append(soup.new_tag("br"))
    tail = f"Original printing · {record.get('artist') or 'Artist not listed'}"
    if record.get("collectorNumber"):
        tail += f" · {record['collectorNumber']}"
    cap.append(NavigableString(tail))
    return cap


def current_page_identity(soup: BeautifulSoup) -> dict[str, str]:
    spot = soup.select_one(".artwork-spotlight")
    return {
        "setCode": (spot.get("data-artwork-set") if spot else "") or "",
        "setName": (spot.get("data-artwork-set-name") if spot else "") or "",
        "artist": (spot.get("data-artwork-artist") if spot else "") or "",
    }


def update_page(path: Path, record: dict[str, Any]) -> bool:
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    before = current_page_identity(soup)
    changed = False

    set_code = record.get("setCode", "")
    set_name = record.get("setName", "")
    release_year = str(record.get("releaseDate", ""))[:4]
    artist = record.get("artist", "")

    # Head metadata and selected historical-context blocks.
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        content = meta["content"]
        for old, new in [
            (before["setName"], set_name),
            (before["artist"], artist),
        ]:
            if old and old != new:
                content = content.replace(old, new)
        if content != meta["content"]:
            meta["content"] = content
            changed = True

    for selector in [
        "header.hero .deckline", "header.hero .byline", "#opening", "#origin",
        "#memory", "#mechanics", "#history"
    ]:
        node = soup.select_one(selector)
        if not node:
            continue
        original = str(node)
        replace_text(node, before["setName"], set_name)
        replace_text(node, before["artist"], artist)
        if str(node) != original:
            changed = True

    # Hero image.
    hero_img = soup.select_one("header.hero img.hero-media")
    if hero_img:
        if record.get("artUrl") and hero_img.get("src") != record["artUrl"]:
            hero_img["src"] = record["artUrl"]
            changed = True
        fallback = record.get("imageUrl")
        if fallback:
            onerror = f"this.onerror=null;this.src='{fallback}';"
            if hero_img.get("onerror") != onerror:
                hero_img["onerror"] = onerror
                changed = True

    # Lead card object where present.
    lead = soup.select_one(".card-lead")
    if lead:
        if record.get("scryfallId") and lead.get("data-scryfall-id") != record["scryfallId"]:
            lead["data-scryfall-id"] = record["scryfallId"]
            changed = True
        image = lead.find("img")
        if image and record.get("imageUrl") and image.get("src") != record["imageUrl"]:
            image["src"] = record["imageUrl"]
            changed = True
        eyebrow = lead.select_one(".oracle .eyebrow")
        if eyebrow and set_name and eyebrow.get_text(strip=True) != set_name:
            eyebrow.string = set_name
            changed = True
        for stat in lead.select(".stat"):
            label_node = stat.find("b")
            label = label_node.get_text(" ", strip=True).lower() if label_node else ""
            if not label_node:
                continue
            if any(key in label for key in ["original set", "first release", "first printed"]):
                desired = f"{set_name} · {release_year}" if release_year else set_name
                existing = stat.get_text(" ", strip=True)
                if desired not in existing:
                    stat.clear(); stat.append(label_node); stat.append(NavigableString(desired)); changed = True
            elif "illustrated by" in label:
                existing = stat.get_text(" ", strip=True)
                if artist and artist not in existing:
                    stat.clear(); stat.append(label_node); stat.append(NavigableString(artist)); changed = True

    # Artwork Spotlight.
    spot = soup.select_one(".artwork-spotlight")
    if spot:
        desired_attrs = {
            "data-artwork-artist": artist,
            "data-artwork-set": set_code,
            "data-artwork-set-name": set_name,
        }
        for key, value in desired_attrs.items():
            if value and spot.get(key) != value:
                spot[key] = value; changed = True
        art_img = spot.select_one(".art-break-media")
        if art_img:
            if record.get("artUrl") and art_img.get("src") != record["artUrl"]:
                art_img["src"] = record["artUrl"]; changed = True
            if record.get("imageUrl") and art_img.get("data-fallback-src") != record["imageUrl"]:
                art_img["data-fallback-src"] = record["imageUrl"]; changed = True
        credit = spot.select_one("[data-artwork-credit]")
        desired_credit = f"{artist}’s original {set_name} artwork"
        if credit and credit.get_text(" ", strip=True) != desired_credit:
            credit.string = desired_credit; changed = True

    # Printing gallery: repurpose the existing original figure when necessary.
    grid = soup.select_one(".canonical-printing-gallery")
    if grid:
        if grid.get("data-original-set") != set_code:
            grid["data-original-set"] = set_code; changed = True
        figures = grid.find_all("figure", recursive=False)
        target = next((f for f in figures if f.get("data-scryfall-id") == record.get("scryfallId")), None)
        if target is None:
            target = next((f for f in figures if "original-printing" in f.get("class", [])), None)
        if target is None:
            target = soup.new_tag("figure")
            grid.insert(0, target)
            changed = True
        for fig in figures:
            classes = [c for c in fig.get("class", []) if c != "original-printing"]
            if not classes:
                classes = ["printing"]
            if fig.get("class", []) != classes:
                fig["class"] = classes
                changed = True
        target_classes = ["printing", "original-printing"] + [
            c for c in target.get("class", []) if c not in {"printing", "original-printing"}
        ]
        target["class"] = list(dict.fromkeys(target_classes))
        attrs = {
            "data-card-name": record.get("cardName") or record.get("articleName") or "",
            "data-scryfall-id": record.get("scryfallId", ""),
            "data-set": set_code,
            "data-collector-number": str(record.get("collectorNumber") or ""),
            "data-identity-status": "verified-editorial-v2-snapshot",
        }
        for key, value in attrs.items():
            if value and target.get(key) != value:
                target[key] = value; changed = True
        image = target.find("img")
        if image is None:
            image = soup.new_tag("img"); target.insert(0, image); changed = True
        desired_image = record.get("imageUrl", "")
        if desired_image and image.get("src") != desired_image:
            image["src"] = desired_image; changed = True
        desired_alt = f"{record.get('cardName') or record.get('articleName')} — {set_name}"
        if image.get("alt") != desired_alt:
            image["alt"] = desired_alt; changed = True
        image["loading"] = "lazy"; image["decoding"] = "async"
        caption = target.find("figcaption")
        replacement = make_caption(soup, record)
        if caption:
            if caption.get_text(" ", strip=True) != replacement.get_text(" ", strip=True):
                caption.replace_with(replacement); changed = True
        else:
            target.append(replacement); changed = True
        if target is not grid.find("figure", recursive=False):
            target.extract(); grid.insert(0, target); changed = True
        count = str(len(grid.find_all("figure", recursive=False)))
        if grid.get("data-gallery-fallback-count") != count:
            grid["data-gallery-fallback-count"] = count; changed = True

    if changed:
        path.write_text(str(soup), encoding="utf-8")
    return changed


def update_artwork_metadata(path: Path, records: dict[str, dict[str, Any]]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for row in data.get("cards", []):
        record = records.get(row.get("articleCard"))
        if not record:
            continue
        for key, value in {
            "setCode": record.get("setCode"),
            "setName": record.get("setName"),
            "artist": record.get("artist"),
        }.items():
            if value and row.get(key) != value:
                row[key] = value; changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    data_path = root / "data/remaining-entry-card-data.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    cards = payload["cards"]

    changes: list[dict[str, Any]] = []
    records_for_metadata: dict[str, dict[str, Any]] = {}
    for card in cards:
        target = choose_base_printing(card)
        if not target or target.get("scryfallId") == card.get("scryfallId"):
            continue
        old_id = card.get("scryfallId")
        old_collector = next((p.get("collectorNumber") for p in card.get("printings", []) if p.get("scryfallId") == old_id), None)
        row = {
            "entry": card.get("entry"),
            "cardName": card.get("articleName"),
            "setCode": card.get("setCode"),
            "oldCollectorNumber": old_collector,
            "newCollectorNumber": target.get("collectorNumber"),
            "oldScryfallId": old_id,
            "newScryfallId": target.get("scryfallId"),
            "pageUpdated": False,
        }
        changes.append(row)
        if args.check:
            continue
        for printing in card.get("printings", []):
            printing["original"] = printing.get("scryfallId") == target.get("scryfallId")
        card.update({
            "artist": target.get("artist", card.get("artist")),
            "scryfallId": target.get("scryfallId", card.get("scryfallId")),
            "illustrationId": target.get("illustrationId", ""),
        })
        records_for_metadata[card["articleName"]] = target
        matches = sorted(root.glob(f"{int(card['entry']):03d}-*.html"))
        if matches:
            row["pageUpdated"] = update_page(matches[0], target)

    # Repair known visible/snapshot mismatches which are not alternate-treatment issues.
    if not args.check:
        by_entry = {int(c["entry"]): c for c in cards}
        for entry in (131, 293, 330):
            card = by_entry[entry]
            target = choose_base_printing(card) or next(
                (p for p in card.get("printings", []) if p.get("scryfallId") == card.get("scryfallId")), None
            )
            if target:
                matches = sorted(root.glob(f"{entry:03d}-*.html"))
                if matches:
                    updated = update_page(matches[0], target)
                    changes.append({
                        "entry": entry,
                        "cardName": card["articleName"],
                        "setCode": card["setCode"],
                        "visibleIdentityRepair": True,
                        "pageUpdated": updated,
                    })
                records_for_metadata[card["articleName"]] = target

        data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        update_artwork_metadata(root / "canonical/artwork-card-metadata.json", records_for_metadata)

    report = {
        "mode": "check" if args.check else "apply",
        "alternateTreatmentCorrections": sum(1 for c in changes if "oldScryfallId" in c),
        "visibleIdentityRepairs": sum(1 for c in changes if c.get("visibleIdentityRepair")),
        "pagesUpdated": sum(1 for c in changes if c.get("pageUpdated")),
        "status": "FAIL" if args.check and changes else "PASS",
        "changes": changes,
    }
    report_path = root / "audit/canonical-debut-normalization.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["mode", "alternateTreatmentCorrections", "visibleIdentityRepairs", "pagesUpdated", "status"]}, indent=2))
    return 1 if args.check and changes else 0


if __name__ == "__main__":
    raise SystemExit(main())
