#!/usr/bin/env python3
"""Review candidate Reader V3.1 article 062 without promoting 061-070 as accepted.

--apply updates derived read time, generated candidate metadata, and source-bound
story record. Default --check is read-only and fails on stale artifacts.
The accepted checkpoint in CURRENT-STATE.json MUST remain at 051-060; 061 is a distinct already-reviewed candidate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator, FormatChecker
from reader_experience_v3 import editorial_word_count, reading_time_minutes

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "062-the-tabernacle-at-pendrell-vale.html"
REVIEW = ROOT / "research-dossiers/reader-v31-061-070/062-review.json"
STORY = ROOT / "research-dossiers/reader-v31-061-070/062-story-candidate.json"
METRICS = ROOT / "validation/reader-v3.1-062-candidate-metrics.json"
DOSSIER = ROOT / "research-dossiers/numbered-wave-02/062-the-tabernacle-at-pendrell-vale.json"
SCHEMA = ROOT / "templates/research-dossier-v2.schema.json"
SOURCE_VERIFICATION = ROOT / "research-dossiers/reader-v31-061-070/062-source-verification.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write derived article/readtime/story artifacts")
    args = parser.parse_args()
    errors = []
    page = ARTICLE.read_text(encoding="utf-8")
    soup = BeautifulSoup(page, "lxml")
    review = load(REVIEW)
    state = load(ROOT / "CURRENT-STATE.json")
    if state.get("readerV31LatestCheckpoint", {}).get("nextArticle") != 61:
        errors.append("062 candidate must not override a newer accepted Reader checkpoint")
    if soup.body.get("data-reader-experience") != "v3":
        errors.append("062 must explicitly use Reader V3.1")
    if soup.body.get("data-vignette-specificity") != "period-grounded-oral-history":
        errors.append("062 lacks full vignette specificity tag")
    if "id=\"cr-reader-experience-v3\"" not in page:
        errors.append("062 missing required inline styles")
    dossier = load(DOSSIER)
    schema = load(SCHEMA)
    errors.extend("dossier: " + problem.message for problem in Draft202012Validator(
        schema, format_checker=FormatChecker()).iter_errors(dossier))
    claimed_sources = {s["sourceId"] for s in dossier.get("sources", [])}
    for record in dossier.get("claims", []):
        if not set(record.get("sourceIds", [])).issubset(claimed_sources):
            errors.append("dossier claim has a sourceId not in verified sources")
    source_data = load(SOURCE_VERIFICATION)
    if len(source_data.get("claims", [])) < 3:
        errors.append("062 requires at least three source-specific evidence records")
    vignette = soup.select_one("#opening > aside.play-vignette")
    if vignette is None:
        errors.append("opening has no direct Reader story")
        story_record = {}
    else:
        title = vignette.select_one("h3").get_text(" ", strip=True)
        story = vignette.select_one("p").get_text(" ", strip=True)
        raw_payments = vignette.select_one("script.vignette-mana-data")
        raw_review = vignette.select_one("script.vignette-review-data")
        story_record = {
            "entry":62, "card":"The Tabernacle at Pendrell Vale", "file":ARTICLE.name, "title":title,
            "story":story, "storyWords":len(re.findall(r"\b[\w’'-]+\b", story)),
            "deckReference":vignette.get("data-vignette-deck-reference"),
            "era":vignette.get("data-vignette-era"),
            "matchup":vignette.get("data-vignette-matchup"),
            "openingMode":vignette.get("data-vignette-opening"),
            "scenario":vignette.get("data-vignette-scenario"),
            "payments":json.loads(raw_payments.string) if raw_payments else None,
            "review":json.loads(raw_review.string) if raw_review else None,
            "manualReview":review["manualReview"],
            "basis":"Documented winning 2015 Lands pool; hypothetical opposing board and upkeep sequence",
            "status":"candidate within unaccepted 061-070 wave"
        }
        if not 70 <= story_record["storyWords"] <= 170:
            errors.append(f"Story has {story_record['storyWords']} words; expected 70..170")
        if story_record["deckReference"] != "Jarvis Yu — Lands":
            errors.append("Story must bind to exact Mark Arce Deck Archive title")
        archive_decks = {x.get_text(" ", strip=True) for x in soup.select("details.deck summary strong")}
        if story_record["deckReference"] not in archive_decks:
            errors.append("Story deck is not a published article archive item")
        if story_record["payments"] != {
            "schema_version":1,
            "costs":[{"object":"Crop Rotation","kind":"nonartifact-spell","cost":1,"payments":[{"source":"Forest","amount":1}]}]
        }:
            errors.append("Tabernacle story must show Crop Rotation paid with Forest; the upkeep trigger is not activated")
        if "not a tournament match transcript" not in story_record["review"].get("scenario",""):
            errors.append("Story must disclaim a recorded match")
    words = editorial_word_count(soup)
    minutes = reading_time_minutes(words)
    pill = soup.select_one(".byline .pill")
    if pill is None:
        errors.append("byline reading-time pill absent")
    elif args.apply:
        expected = (f'<span class="pill" data-reading-word-count="{words}" '
                    f'data-reading-time-wpm="200">Approximately {minutes} minute read</span>')
        page, count = re.subn(r'<span class="pill"(?:[^>]*)>Approximately \d+ minute read</span>',
                              lambda _:expected, page, count=1)
        if count != 1:
            errors.append("unable to replace reader pill once")
        page, n = re.subn(r'(<article class="article" data-expanded-word-count=")\d+(")',
                          lambda match:f"{match[1]}{words}{match[2]}", page, count=1)
        if n != 1:
            errors.append("unable to replace existing expanded word count once")
    else:
        if pill.get("data-reading-word-count") != str(words) or pill.get("data-reading-time-wpm") != "200":
            errors.append("byline derived read-time metadata is stale")
        if pill.get_text(" ", strip=True) != f"Approximately {minutes} minute read":
            errors.append("byline displayed reading time is stale")
    if errors:
        print("FAIL Reader 062 candidate:")
        for problem in errors: print(" - " + problem)
        return 1
    if args.apply:
        ARTICLE.write_text(page, encoding="utf-8")
    metrics = {
        "checkpoint":"reader-v31-062-candidate-2026-10-27",
        "acceptance":"single-page candidate; wave 061-070 NOT accepted",
        "file":ARTICLE.name, "card":"The Tabernacle at Pendrell Vale",
        "articleEditorialWords":words, "readTimeMinutes":minutes,
        "sha256":hashlib.sha256((page if args.apply else ARTICLE.read_text(encoding="utf-8")).encode("utf-8")).hexdigest(),
        "storyTitle":story_record["title"],"storyWords":story_record["storyWords"],
        "deckReference":story_record["deckReference"],
        "sourceEvidence":len(source_data["claims"]),
        "nextAcceptanceAction":"complete independently sourced 063-070 then validate batch"
    }
    if args.apply:
        write(STORY, story_record)
        write(METRICS, metrics)
    else:
        if not STORY.exists() or load(STORY) != story_record:
            errors.append("candidate story record missing or out of sync")
        if not METRICS.exists() or load(METRICS) != metrics:
            errors.append("candidate article metrics/hash missing or stale")
    if errors:
        for problem in errors: print("FAIL:", problem)
        return 1
    print(f"PASS 062 {'refreshed' if args.apply else 'verified'}: {words} words, {minutes} min, "
          f"{story_record['storyWords']} vignette words; accepted Reader still 60/100")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
