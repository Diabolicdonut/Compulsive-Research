#!/usr/bin/env python3
"""Regression tests for reader-facing mechanics and vignette chronology guards."""
from __future__ import annotations

from bs4 import BeautifulSoup

from validate_reader_experience_v3 import (
    article_subject_integrity_errors,
    primary_mechanics_claim_errors,
    vignette_chronology_errors,
)


def mechanics_fixture(headline: str, oracle: str) -> BeautifulSoup:
    return BeautifulSoup(
        f"""<!doctype html><html><head><title>Hypnotic Specter: {headline}</title></head>
        <body><div class='hero'><h1>{headline}</h1></div>
        <section id='opening'><h2>{headline}</h2><div class='card-lead'><div class='oracle'>{oracle}</div></div></section>
        </body></html>""",
        "lxml",
    )


def vignette_fixture(story: str, ledger: str = ""):
    soup = BeautifulSoup(
        f"""<aside class='play-vignette'><p>{story}</p>{ledger}</aside>""",
        "lxml",
    )
    vignette = soup.select_one(".play-vignette")
    return vignette, vignette.find("p").get_text(" ", strip=True)


def main() -> int:
    failures: list[str] = []

    old_heading = mechanics_fixture(
        "The Creature That Stole the Next Draw",
        "Flying. Whenever Hypnotic Specter deals damage to an opponent, that player discards a card at random.",
    )
    if not any("unsupported 'draw'" in item for item in primary_mechanics_claim_errors(old_heading)):
        failures.append("unsupported draw-mechanics headline was not rejected")

    corrected_heading = mechanics_fixture(
        "The Creature That Made Every Hit a Gamble",
        "Flying. Whenever Hypnotic Specter deals damage to an opponent, that player discards a card at random.",
    )
    if primary_mechanics_claim_errors(corrected_heading):
        failures.append("corrected Hypnotic Specter headline was rejected")

    impossible_story = (
        "Black Lotus put Hypnotic Specter into play before my opponent's first turn. "
        "He developed two lands. The Specter attacked on turn two."
    )
    vignette, text = vignette_fixture(impossible_story)
    findings = vignette_chronology_errors(vignette, text)
    if not any("2 lands before the speaker's second turn" in item for item in findings):
        failures.append("impossible two-land chronology was not rejected")
    if not any("lacks hidden .vignette-sequence-data" in item for item in findings):
        failures.append("compressed multi-turn story without a sequence ledger was not rejected")

    valid_ledger = """
    <script class='vignette-sequence-data' type='application/json'>
    {
      "schema_version": 1,
      "on_the_play": "speaker",
      "turns": [
        {"active_player":"speaker","turn":1,"land_drops":["Underground Sea"],"actions":["cast Hypnotic Specter"]},
        {"active_player":"opponent","turn":1,"land_drops":["Tundra"],"actions":["passed"]},
        {"active_player":"speaker","turn":2,"land_drops":["Island"],"actions":["attacked with Hypnotic Specter"]}
      ]
    }
    </script>
    """
    valid_story = (
        "Black Lotus put Hypnotic Specter into play beside Underground Sea before my opponent's first turn. "
        "He played Tundra and passed. On my second turn I played Island and attacked with Hypnotic Specter."
    )
    marked_story = (
        "Black Lotus put Hypnotic Specter into play beside "
        "<span class='card-name' data-card='Underground Sea'>Underground Sea</span> before my opponent's first turn. "
        "He played <span class='card-name' data-card='Tundra'>Tundra</span> and passed. On my second turn I played "
        "<span class='card-name' data-card='Island'>Island</span> and attacked with Hypnotic Specter."
    )
    vignette, text = vignette_fixture(marked_story, valid_ledger)
    valid_findings = vignette_chronology_errors(vignette, text)
    if valid_findings:
        failures.append("valid compressed chronology was rejected: " + "; ".join(valid_findings))

    wrong_card = BeautifulSoup("""
        <header class="hero"><img class="hero-media"
          src="https://api.scryfall.com/cards/named?exact=Timetwister&amp;set=lea"/></header>
        <section id="opening"><div class="card-lead"><img data-article-card-image=""
          src="https://api.scryfall.com/cards/named?exact=Wheel%20of%20Fortune&amp;set=lea"/>
          <div class="stats"><div class="stat"><b>Illustrated by</b>Mark Tedin</div></div>
        </div></section>
        <figure class="artwork-spotlight" data-artwork-artist="Daniel Gelon"></figure>
        <details class="official-mtg-decks" data-card="Timetwister"></details>
    """, "lxml")
    subject_errors = article_subject_integrity_errors(wrong_card, "Wheel of Fortune")
    if not all(any(fragment in error for error in subject_errors) for fragment in
               ("hero image", "official-product section", "lead artist")):
        failures.append("cross-card hero/product identity or original artist leak was not rejected")
    wrong_card.select_one("header.hero img")["src"] = "https://api.scryfall.com/cards/named?exact=Wheel%20of%20Fortune&set=lea"
    wrong_card.select_one("details.official-mtg-decks")["data-card"] = "Wheel of Fortune"
    wrong_card.select_one(".card-lead .stat b").next_sibling.replace_with("Daniel Gelon")
    if article_subject_integrity_errors(wrong_card, "Wheel of Fortune"):
        failures.append("corrected subject images, product data, and artist were rejected")

    if failures:
        print(f"Reader Experience V3 regression tests: FAIL ({len(failures)} finding(s))")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Reader Experience V3 regression tests: PASS (mechanics, chronology, and article subject identity)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
