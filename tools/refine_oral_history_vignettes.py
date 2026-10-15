#!/usr/bin/env python3
"""Rewrite Reader Experience V3 vignettes as unframed first-person table stories.

The visible vignette contains only a neutral label, a title, and the story itself.
Historical grounding remains in data attributes for research and validation, but no
visible era/matchup caption or explanatory coda is printed in the article.
"""
from __future__ import annotations

from pathlib import Path
import json
from bs4 import BeautifulSoup, NavigableString
import re

from reader_experience_v3 import editorial_word_count, reading_time_minutes, WORDS_PER_MINUTE

ROOT = Path(__file__).resolve().parents[1]

VIGNETTES = {
    1: {
        "title": "The game ended before his first land",
        "era": "1994 Type I",
        "matchup": "Weissman control against Zoo",
        "deck": "Brian Weissman — The Deck",
        "opening_mode": "opponent-before-first-turn",
        "body": "My opponent had not even played his first land when I put down [[Tundra]], [[Mox Jet]], and [[Black Lotus]]. The Lotus became three black mana, and [[Mind Twist]] took four cards from the Zoo hand he had been so pleased to keep: [[Kird Ape]], [[Channel]], [[Fireball]], and [[Taiga]]. He stared at the three cards left in his hand for a moment, drew for turn, played a land, and passed. The game had technically begun, but most of his plan was already in the graveyard.",
    },
    2: {
        "title": "Three cards that rebuilt the whole game",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "board-state",
        "body": "By the end of his turn, [[Whirling Dervish]] and [[Argothian Pixies]] were still coming at me, my hand was a land and [[Serra Angel]], and one more attack plus a burn spell would finish the game. I had already spent [[Swords to Plowshares]] on [[Kird Ape]] and [[Mana Drain]] on [[Channel]]. At his end step I tapped [[Mox Sapphire]] for [[Ancestral Recall]]. The three cards were [[Wrath of God]], [[Tundra]], and [[Time Walk]]. I untapped, played Tundra, swept both creatures away, and followed with Serra Angel. Time Walk gave the Angel two attacks before my opponent could untap again.",
    },
    3: {
        "title": "He paid four mana for a turn he never received",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "life-total",
        "body": "Eight life looked safe to my opponent. He tapped four mana for [[Control Magic]], stole my [[Old Man of the Sea]], and finally put a blocker in front of [[Serra Angel]]. Another draw from [[Sylvan Library]] might even have found [[Psionic Blast]] or [[Fireball]]. I untapped, cast [[Time Walk]], and sent Serra Angel over for four. Then the extra turn began. I untapped again, drew, and attacked for the last four before he ever received another main phase. He had paid four mana for a creature he never got to untap with.",
    },
    4: {
        "title": "I answered the Ape and developed anyway",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "table-dialogue",
        "body": "“[[Taiga]], [[Kird Ape]], go.” My opponent pushed the Ape forward as though the first attack was already owed to him. I played [[Island]] and [[Mox Pearl]]. The Pearl made white for [[Swords to Plowshares]], so the Ape disappeared before combat ever arrived, and the Island cast [[Ivory Tower]]. He looked at the empty space where his creature had been, then at the Tower, and passed his second turn with [[Lightning Bolt]] and [[Chain Lightning]] still in hand. I untapped with Island, Mox Pearl, Ivory Tower, and a full grip.",
    },
    5: {
        "title": "His Black Lotus ran straight into two blue mana",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Channel–Fireball Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "sudden-threat",
        "body": "The [[Black Lotus]] hit the table before I had settled into the game. My opponent played [[Taiga]], cracked the Lotus for green, cast [[Channel]], and began counting life toward [[Fireball]]. I had only [[Tundra]] and [[Mox Sapphire]] in play, but together they made two blue mana on turn one. I cast [[Mana Drain]]. Channel went to the graveyard after his Lotus had already vanished, and Fireball stayed stranded in his hand. On my turn the Drain mana, Tundra, and a new [[Savannah]] cast [[Icy Manipulator]]. He drew, looked at the Fireball again, and passed.",
    },
    6: {
        "title": "The black Mox took away his protection",
        "era": "2007 Vintage Championship era",
        "matchup": "Gro-A-Tog against Flash combo",
        "deck": "Stephen Menendian — Gro-A-Tog",
        "opening_mode": "revealed-information",
        "body": "The first card [[Duress]] showed me was [[Flash]]. Beside it sat [[Force of Will]], [[Summoner's Pact]], and enough mana to make the whole hand dangerous. I had opened on [[Underground Sea]] and [[Mox Jet]], so the discard spell resolved before my opponent had taken a turn. I took his Force, then used Underground Sea for [[Ancestral Recall]]. The three cards included [[Gush]], [[Quirion Dryad]], and another blue card for my own Force of Will. I passed with a full hand, his protection gone, and the Flash he intended to hide now sitting faceup in my mind.",
    },
    7: {
        "title": "The prison and its mechanic arrived together",
        "era": "2005 Vintage Championship",
        "matchup": "5-Color Stax against blue Gifts control",
        "deck": "Roland Chang — 5-Color Stax",
        "opening_mode": "opening-hand",
        "body": "My opening seven contained [[Mishra's Workshop]], [[Mox Ruby]], [[Trinisphere]], and [[Goblin Welder]]. Workshop cast Trinisphere before my opponent had played anything; Mox Ruby then cast the Welder. He looked down at the [[Brainstorm]], [[Ancestral Recall]], and artifact mana in the hand he had kept. Every one-mana spell now cost three, and the Welder was already waiting to recycle [[Tangle Wire]] or [[Smokestack]]. He played a land and passed without casting a spell.",
    },
    8: {
        "title": "I sacrificed the Workshop and somehow kept it",
        "era": "2005 Vintage Championship",
        "matchup": "5-Color Stax against blue control",
        "deck": "Roland Chang — 5-Color Stax",
        "opening_mode": "counterintuitive-play",
        "body": "Sacrificing [[Mishra's Workshop]] after using it once felt completely wrong, which was exactly why the play worked. Workshop cast [[Crucible of Worlds]]. [[Mox Emerald]] paid for [[Crop Rotation]], and I traded the Workshop for [[Tolarian Academy]]. Academy tapped for two blue from Crucible and the Mox, letting me cast [[Sphere of Resistance]] before my opponent's first turn. I passed with Crucible, Sphere, Academy, and Emerald in play. On turn two I played the sacrificed Workshop from my graveyard as my land for the turn.",
        "sequence": {"schema_version": 1, "on_the_play": "speaker", "turns": [{"active_player": "speaker", "turn": 1, "land_drops": ["Mishra's Workshop"], "actions": ["cast Crucible of Worlds", "played Mox Emerald", "cast Crop Rotation using Mox Emerald", "sacrificed Mishra's Workshop and found Tolarian Academy", "cast Sphere of Resistance"]}, {"active_player": "opponent", "turn": 1, "land_drops": [], "actions": ["no relevant action stated"]}, {"active_player": "speaker", "turn": 2, "land_drops": ["Mishra's Workshop"], "actions": ["played Mishra's Workshop from the graveyard using Crucible of Worlds"]}]},
    },
    9: {
        "title": "We both drew seven, but only I had a battlefield",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "battlefield-asymmetry",
        "body": "Four permanents reached my side of the table before my opponent had played one: [[Tundra]], [[Mox Pearl]], [[Mox Sapphire]], and [[Sol Ring]]. Sapphire and the Ring then cast [[Timetwister]]. The hand he had kept around [[Channel]] and [[Fireball]] disappeared into his library, and we each drew seven new cards. He had no battlefield and had not made a land drop. I still had Tundra, two Moxen, and Sol Ring. He counted my mana, looked at his new seven, and shook his head.",
    },
    10: {
        "title": "The turn-two Wrath nobody expected",
        "era": "1994 World Championship era",
        "matchup": "U/W/G control against Zoo",
        "deck": "Zak Dolan — U/W/G Stasis Control",
        "opening_mode": "opponent-curve",
        "body": "[[Kird Ape]] on turn one, [[Argothian Pixies]] on turn two. My opponent had curved out exactly the way those old Zoo decks were supposed to, and I had taken the first attack while holding [[Wrath of God]]. My own opening was [[Tundra]] into [[Sol Ring]]. I untapped, played [[Savannah]], tapped both lands for white, used Sol Ring for the other two mana, and cast Wrath on turn two. He had not seen it coming. Both creatures went to the graveyard before he had played a third land. He drew, made that third land drop, and passed. I untapped with Sol Ring still in play and [[Serra Angel]] in hand.",
    },
}

CARD_TOKEN = re.compile(r"\[\[([^\]]+)\]\]")


def append_card_markup(soup: BeautifulSoup, parent, text: str) -> None:
    pos = 0
    for match in CARD_TOKEN.finditer(text):
        if match.start() > pos:
            parent.append(NavigableString(text[pos:match.start()]))
        card = match.group(1)
        span = soup.new_tag("span", attrs={"class": "card-name", "data-card": card, "tabindex": "0"})
        span.string = card
        parent.append(span)
        pos = match.end()
    if pos < len(text):
        parent.append(NavigableString(text[pos:]))


def update_read_time(soup: BeautifulSoup) -> None:
    count = editorial_word_count(soup)
    minutes = reading_time_minutes(count)
    pill = soup.select_one(".byline .pill[data-reading-word-count][data-reading-time-wpm]")
    if pill is None:
        return
    pill["data-reading-word-count"] = str(count)
    pill["data-reading-time-wpm"] = str(WORDS_PER_MINUTE)
    pill.string = f"Approximately {minutes} minute read"


def rewrite(path: Path, entry: int) -> None:
    d = VIGNETTES[entry]
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    body = soup.body
    card = body.get("data-article-card") if body else None
    opening = soup.find("section", id="opening")
    if body is None or opening is None or not card:
        raise RuntimeError(f"{path.name}: missing article structure")

    old = opening.select_one(":scope > .play-vignette")
    if old:
        old.decompose()

    vignette = soup.new_tag(
        "aside",
        attrs={
            "class": "play-vignette",
            "data-featured-card": card,
            "aria-label": f"First-person table story for {card}",
            "data-vignette-scenario": "representative-recollection",
            "data-vignette-voice": "first-person-recollection",
            "data-vignette-era": d["era"],
            "data-vignette-matchup": d["matchup"],
            "data-vignette-deck-reference": d["deck"],
            "data-vignette-opening": d["opening_mode"],
        },
    )
    label = soup.new_tag("div", attrs={"class": "vignette-label"})
    label.string = "A story from the table"
    heading = soup.new_tag("h3")
    heading.string = d["title"]
    paragraph = soup.new_tag("p")
    append_card_markup(soup, paragraph, d["body"])
    vignette.extend([label, heading, paragraph])
    if d.get("sequence"):
        sequence = soup.new_tag("script", attrs={"class": "vignette-sequence-data", "type": "application/json"})
        sequence.string = "\n" + json.dumps(d["sequence"], indent=2, ensure_ascii=False) + "\n"
        vignette.append(sequence)
    opening.append(vignette)

    body["data-vignette-specificity"] = "period-grounded-oral-history"
    update_read_time(soup)
    path.write_text(str(soup), encoding="utf-8")


def main() -> int:
    for entry in range(1, 11):
        matches = list(ROOT.glob(f"{entry:03d}-*.html"))
        if len(matches) != 1:
            raise RuntimeError(f"entry {entry:03d}: expected one article, found {len(matches)}")
        rewrite(matches[0], entry)
        print(f"Updated {matches[0].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
