#!/usr/bin/env python3
"""Validate the staged Reader Experience V3 migration.

Only pages declaring data-reader-experience="v3" are required to satisfy the
new contract, allowing the archive to migrate in approved batches.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qs, unquote_plus, urlparse
from bs4 import BeautifulSoup, Tag

from reader_experience_v3 import WORDS_PER_MINUTE, editorial_word_count, reading_time_minutes, normalized_text

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_STYLE_TOKENS = (
    ".play-vignette",
    "details.preconstructed-archive.official-mtg-decks",
    "color:#edf3f0!important",
    "display:block!important",
)
BANNED_THESIS_SELECTORS = (
    ".thesis-band",
    ".argument-in-one-sentence",
    ".one-sentence-argument",
)
STOCK_MEMORY_OPENING = re.compile(
    r"^(?:i (?:still )?remember|i can still picture|there i was|i recall|i once remember)",
    re.I,
)


def card_name_key(name: str) -> str:
    """Allow typographic apostrophes in inherited display metadata."""
    return name.replace("’", "'").casefold()


def article_subject_integrity_errors(soup: BeautifulSoup, card: str) -> list[str]:
    """Check subject-bearing components that can inherit a previous article's card."""
    findings = []
    for label, selector in (
        ("hero image", "header.hero img.hero-media"),
        ("lead card image", "#opening .card-lead img[data-article-card-image]"),
    ):
        image = soup.select_one(selector)
        if image is None:
            continue
        exact = parse_qs(urlparse(image.get("src", "")).query).get("exact", [""])[0]
        if exact and card_name_key(unquote_plus(exact)) != card_name_key(card):
            findings.append(f"{label} resolves {exact!r} rather than {card!r}")
    official = soup.select_one("details.official-mtg-decks")
    if official is not None and card_name_key(official.get("data-card", "")) != card_name_key(card):
        findings.append(f"official-product section declares {official.get('data-card')!r} rather than {card!r}")
    spotlight = soup.select_one(".artwork-spotlight[data-artwork-artist]")
    if spotlight is not None:
        original_artist = (spotlight.get("data-artwork-artist") or "").strip().casefold()
        for stat in soup.select("#opening .card-lead .stat"):
            heading = stat.find("b")
            if heading and heading.get_text(" ", strip=True).casefold() == "illustrated by":
                lead_artist = stat.get_text(" ", strip=True).removeprefix(heading.get_text(" ", strip=True)).strip()
                if original_artist and lead_artist and original_artist != lead_artist.casefold():
                    findings.append(f"lead artist {lead_artist!r} disagrees with original spotlight artist")
                break
    return findings


PRIMARY_MECHANICS_CLAIMS = {
    "draw": (
        re.compile(r"\b(?:draw|draws|drawing|drew|topdeck(?:ed|ing|s)?)\b", re.I),
        re.compile(r"\b(?:draw|library|top card|put [^.]{0,80} into [^.]{0,40} hand)\b", re.I),
    ),
    "discard": (
        re.compile(r"\bdiscard(?:s|ed|ing)?\b", re.I),
        re.compile(r"\bdiscard(?:s|ed|ing)?\b", re.I),
    ),
    "extra turn": (
        re.compile(r"\b(?:extra|additional) turn\b", re.I),
        re.compile(r"\b(?:extra|additional) turn\b", re.I),
    ),
    "counter a spell": (
        re.compile(r"\bcounter(?:ed|s|ing)? (?:a |the |every )?spell\b", re.I),
        re.compile(r"\bcounter [^.]{0,80}spell\b", re.I),
    ),
    "destroy land": (
        re.compile(r"\bdestroy(?:ed|s|ing)? (?:a |the |every |all )?lands?\b|\blands? (?:was|were|is|are) (?:destroyed|gone)\b", re.I),
        re.compile(r"\bdestroy [^.]{0,80}lands?\b", re.I),
    ),
    "search a library": (
        re.compile(r"\bsearch(?:ed|es|ing)? (?:the |your |a )?library\b|\btutor(?:ed|s|ing)?\b", re.I),
        re.compile(r"\bsearch [^.]{0,100}library\b", re.I),
    ),
    "prevent untapping": (
        re.compile(r"\b(?:does not|doesn't|did not|didn't|never|cannot|can't) untap\b|\bonly one land (?:came back|untapped)\b", re.I),
        re.compile(r"\buntap\b", re.I),
    ),
}

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
COMPRESSED_OPENING_RE = re.compile(
    r"\bbefore (?:my |the )?opponent[’']s first turn\b|\bbefore (?:his|her|their) first turn\b",
    re.I,
)
LATER_TURN_RE = re.compile(
    r"\b(?:on (?:my |his |her |their )?(?:second|third|fourth|fifth) turn|on turn (?:two|three|four|five|2|3|4|5))\b",
    re.I,
)
EXTRA_LAND_EXCEPTION_RE = re.compile(
    r"\b(?:extra turn|additional turn|additional land|extra land|Fastbond|Exploration|Burgeoning|Explore|Summer Bloom|Azusa|Time Walk)\b",
    re.I,
)


def primary_mechanics_claim_errors(soup: BeautifulSoup) -> list[str]:
    """Reject direct headline mechanics claims that the printed rules do not support."""
    oracle = soup.select_one("#opening .card-lead .oracle")
    if oracle is None:
        return []
    oracle_text = oracle.get_text(" ", strip=True)
    framing_nodes = [
        soup.title,
        soup.select_one(".hero h1"),
        soup.select_one("#opening > h2"),
    ]
    framing = " | ".join(
        node.get_text(" ", strip=True) for node in framing_nodes if node is not None
    )
    findings: list[str] = []
    for family, (claim_re, support_re) in PRIMARY_MECHANICS_CLAIMS.items():
        if claim_re.search(framing) and not support_re.search(oracle_text):
            findings.append(
                f"primary title/opening makes an unsupported {family!r} mechanics claim; "
                "the card's displayed rules text does not contain that operation"
            )
    return findings


def _turn_number(word: str) -> int:
    lowered = word.lower()
    if lowered.isdigit():
        return int(lowered)
    ordinals = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
    return ordinals.get(lowered, NUMBER_WORDS.get(lowered, 0))


def vignette_chronology_errors(vignette: Tag, paragraph_text: str) -> list[str]:
    """Validate high-risk early-turn prose and an optional hidden turn ledger.

    A compressed opening that acts before the opponent's first turn and then
    continues into later turns must carry a machine-readable ledger. This makes
    land-drop order reviewable instead of trusting fluent prose.
    """
    findings: list[str] = []
    normalized_apostrophes = paragraph_text.replace("’", "'")
    compressed = bool(COMPRESSED_OPENING_RE.search(normalized_apostrophes))
    continues = bool(LATER_TURN_RE.search(normalized_apostrophes))

    # Conservative prose-level regression guard for the exact class of error in
    # which an opponent somehow has multiple normal land drops before the
    # speaker's second turn.
    turn_two = re.search(
        r"\b(?:on my second turn|on turn two|attacked on turn two|attack(?:ed|s|ing)? on turn two)\b",
        normalized_apostrophes,
        re.I,
    )
    if compressed and turn_two:
        before_turn_two = normalized_apostrophes[:turn_two.start()]
        land_claims = re.finditer(
            r"\b(?:my opponent|the opponent|he|she|they)\b[^.!?]{0,100}\b(?:developed|had|controlled|with)\s+"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+lands?\b",
            before_turn_two,
            re.I,
        )
        for claim in land_claims:
            count = _turn_number(claim.group(1))
            if count > 1 and not EXTRA_LAND_EXCEPTION_RE.search(before_turn_two):
                findings.append(
                    f"chronology gives the opponent {count} lands before the speaker's second turn "
                    "without an extra-turn or additional-land effect"
                )

    ledger_node = vignette.select_one("script.vignette-sequence-data[type='application/json']")
    if compressed and continues and ledger_node is None:
        findings.append(
            "compressed opening continues into later turns but lacks hidden .vignette-sequence-data chronology"
        )
        return findings
    if ledger_node is None:
        return findings

    raw = ledger_node.string or ledger_node.get_text("", strip=False)
    try:
        ledger = json.loads(raw)
    except json.JSONDecodeError as exc:
        findings.append(f"vignette sequence ledger is invalid JSON: {exc.msg}")
        return findings

    if ledger.get("schema_version") != 1:
        findings.append("vignette sequence ledger must declare schema_version 1")
    on_the_play = ledger.get("on_the_play")
    if on_the_play not in {"speaker", "opponent"}:
        findings.append("vignette sequence ledger on_the_play must be 'speaker' or 'opponent'")
    turns = ledger.get("turns")
    if not isinstance(turns, list) or not turns:
        findings.append("vignette sequence ledger must contain a non-empty turns array")
        return findings

    expected_player = on_the_play if on_the_play in {"speaker", "opponent"} else "speaker"
    last_player: str | None = None
    player_turns = {"speaker": 0, "opponent": 0}
    seen_pairs: set[tuple[str, int]] = set()
    story_cards = {
        node.get("data-card") for node in vignette.select(".card-name[data-card]") if node.get("data-card")
    }

    for index, event in enumerate(turns, start=1):
        if not isinstance(event, dict):
            findings.append(f"vignette sequence event {index} must be an object")
            continue
        player = event.get("active_player")
        turn = event.get("turn")
        extra_turn = bool(event.get("extra_turn"))
        if player not in {"speaker", "opponent"}:
            findings.append(f"vignette sequence event {index} has invalid active_player {player!r}")
            continue
        if not isinstance(turn, int) or turn < 1:
            findings.append(f"vignette sequence event {index} has invalid turn {turn!r}")
            continue
        if player != expected_player:
            if not (extra_turn and player == last_player):
                findings.append(
                    f"vignette sequence event {index} breaks turn order: expected {expected_player}, found {player}"
                )
        expected_turn = player_turns[player] + 1
        if turn != expected_turn:
            findings.append(
                f"vignette sequence event {index} gives {player} turn {turn}; expected turn {expected_turn}"
            )
        if (player, turn) in seen_pairs:
            findings.append(f"vignette sequence repeats {player} turn {turn}")
        seen_pairs.add((player, turn))
        player_turns[player] = max(player_turns[player], turn)

        land_drops = event.get("land_drops", [])
        if not isinstance(land_drops, list) or not all(isinstance(x, str) and x.strip() for x in land_drops):
            findings.append(f"vignette sequence event {index} land_drops must be a list of card names")
            land_drops = []
        allowance = event.get("additional_land_drops", 0)
        if not isinstance(allowance, int) or allowance < 0:
            findings.append(f"vignette sequence event {index} additional_land_drops must be a nonnegative integer")
            allowance = 0
        if len(land_drops) > 1 + allowance:
            findings.append(
                f"vignette sequence event {index} records {len(land_drops)} land drops but permits only {1 + allowance}"
            )
        for land in land_drops:
            if land not in story_cards:
                findings.append(
                    f"vignette sequence event {index} names land drop {land!r} that is not marked as a card in the visible story"
                )

        actions = event.get("actions")
        if not isinstance(actions, list) or not actions or not all(isinstance(x, str) and x.strip() for x in actions):
            findings.append(f"vignette sequence event {index} must contain a non-empty actions list")

        last_player = player
        expected_player = "opponent" if player == "speaker" else "speaker"

    if compressed and on_the_play != "speaker":
        findings.append("story acts before the opponent's first turn but sequence ledger does not put the speaker on the play")

    explicit_turns = [
        ("speaker", _turn_number(m.group(1)))
        for m in re.finditer(r"\bon my (first|second|third|fourth|fifth) turn\b", normalized_apostrophes, re.I)
    ]
    explicit_turns += [
        ("opponent", _turn_number(m.group(1)))
        for m in re.finditer(r"\bon (?:his|her|their) (first|second|third|fourth|fifth) turn\b", normalized_apostrophes, re.I)
    ]
    for player, turn in explicit_turns:
        if player_turns[player] < turn:
            findings.append(
                f"visible story reaches {player} turn {turn}, but the sequence ledger ends at turn {player_turns[player]}"
            )

    return findings


def opening_prefix(text: str, words: int = 6) -> str:
    tokens = re.findall(r"[a-z0-9]+", normalized_text(text))
    return " ".join(tokens[:words])


def vignette_mana_errors(vignette: Tag) -> list[str]:
    """Check declared payments, not an inferred or complete Magic game state.

    The optional ledger makes reviewed total costs and restricted Workshop mana
    auditable. Colored requirements, available sources across turns, discounts,
    and legality still require the separate manual sequence review.
    """
    nodes = vignette.select("script.vignette-mana-data[type='application/json']")
    if not nodes:
        return []
    if len(nodes) != 1:
        return ["vignette must contain at most one mana ledger"]
    try:
        ledger = json.loads(nodes[0].string or nodes[0].get_text("", strip=False))
    except json.JSONDecodeError:
        return ["vignette mana ledger is invalid JSON"]
    if not isinstance(ledger, dict) or ledger.get("schema_version") != 1:
        return ["vignette mana ledger must declare schema_version 1"]
    costs = ledger.get("costs")
    if not isinstance(costs, list) or not costs:
        return ["vignette mana ledger must contain a non-empty costs array"]
    findings = []
    visible_cards = {n.get("data-card") for n in vignette.select("p .card-name[data-card]")}
    for index, action in enumerate(costs, start=1):
        label = f"vignette mana payment {index}"
        if not isinstance(action, dict):
            findings.append(f"{label} must be an object")
            continue
        if action.get("object") not in visible_cards:
            findings.append(f"{label} object must be a marked card in the visible story")
        kind = action.get("kind")
        if kind not in {"artifact-spell", "nonartifact-spell", "activated-ability"}:
            findings.append(f"{label} has an invalid payment kind")
        cost = action.get("cost")
        if type(cost) is not int or cost < 0:
            findings.append(f"{label} cost must be a nonnegative integer")
            continue
        payments = action.get("payments")
        if not isinstance(payments, list):
            findings.append(f"{label} payments must be an array")
            continue
        total = 0
        for payment in payments:
            if not isinstance(payment, dict):
                findings.append(f"{label} source must be an object")
                continue
            source = payment.get("source")
            amount = payment.get("amount")
            if source not in visible_cards:
                findings.append(f"{label} source must be a marked card in the visible story")
            if type(amount) is not int or amount <= 0:
                findings.append(f"{label} amount must be a positive integer")
                continue
            total += amount
            if isinstance(source, str) and source.replace("’", "'").casefold() == "mishra's workshop" and kind != "artifact-spell":
                findings.append(f"{label} spends restricted Workshop mana on a {kind}; only artifact spells are permitted")
        if total != cost:
            findings.append(f"{label} declares cost {cost} but supplies {total} mana")
    return findings


def migration_batch(path: Path) -> str:
    match = re.match(r"^(\d{3,4})-", path.name)
    if match:
        entry = int(match.group(1))
        return f"numbered-{((entry - 1) // 50) + 1:02d}"
    return "honorable-mentions"


def article_paths() -> list[Path]:
    return sorted(ROOT.glob("*.html"))


def similarity(a: str, b: str) -> float:
    na, nb = normalized_text(a), normalized_text(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def main() -> int:
    errors: list[str] = []
    rows: list[tuple[str, int, int]] = []
    story_openings: list[tuple[Path, str, str, str, bool]] = []

    for path in article_paths():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if 'data-reader-experience="v3"' not in text:
            continue
        soup = BeautifulSoup(text, "lxml")
        body = soup.body
        card = (body.get("data-article-card") if body else None) or path.stem
        if body is None or body.get("data-vignette-specificity") != "period-grounded-oral-history":
            errors.append(f"{path.name}: body must declare data-vignette-specificity='period-grounded-oral-history'")

        opening = soup.find("section", id="opening")
        if opening is None:
            errors.append(f"{path.name}: missing #opening")
            continue
        lead = opening.select_one(".card-lead")
        if lead is None:
            errors.append(f"{path.name}: opening does not introduce the card with .card-lead")
        for finding in article_subject_integrity_errors(soup, card):
            errors.append(f"{path.name}: {finding}")
        for finding in primary_mechanics_claim_errors(soup):
            errors.append(f"{path.name}: {finding}")

        vignettes = opening.select(":scope > .play-vignette")
        if len(vignettes) != 1:
            errors.append(f"{path.name}: expected exactly one direct-child play vignette in #opening, found {len(vignettes)}")
            vignette = vignettes[0] if vignettes else None
        else:
            vignette = vignettes[0]
            if opening.find_all(recursive=False)[-1] is not vignette:
                errors.append(f"{path.name}: play vignette must be the final opening component")
            if card_name_key(vignette.get("data-featured-card", "")) != card_name_key(card):
                errors.append(f"{path.name}: vignette card {vignette.get('data-featured-card')!r} does not match {card!r}")

            # Period-grounded specificity contract.
            if vignette.get("data-vignette-scenario") != "representative-recollection":
                errors.append(f"{path.name}: vignette must declare data-vignette-scenario='representative-recollection'")
            if vignette.get("data-vignette-voice") != "first-person-recollection":
                errors.append(f"{path.name}: vignette must declare data-vignette-voice='first-person-recollection'")
            era = (vignette.get("data-vignette-era") or "").strip()
            matchup = (vignette.get("data-vignette-matchup") or "").strip()
            deck_ref = (vignette.get("data-vignette-deck-reference") or "").strip()
            if not re.search(r"\b(?:19|20)\d{2}\b", era):
                errors.append(f"{path.name}: vignette era must contain a four-digit year")
            if not re.search(r"\b(?:against|vs\.?)\b", matchup, re.I):
                errors.append(f"{path.name}: vignette matchup must name one deck against one opposing archetype")
            deck_titles = {n.get_text(" ", strip=True) for n in soup.select("details.deck summary strong")}
            if not deck_ref or deck_ref not in deck_titles:
                errors.append(f"{path.name}: vignette deck reference {deck_ref!r} is not an exact Deck Archive title")

            paragraph = vignette.find("p")
            paragraph_text = paragraph.get_text(" ", strip=True) if paragraph else ""
            for finding in vignette_chronology_errors(vignette, paragraph_text):
                errors.append(f"{path.name}: {finding}")
            for finding in vignette_mana_errors(vignette):
                errors.append(f"{path.name}: {finding}")
            vignette_words = len(re.findall(r"\b[\w’'-]+\b", paragraph_text))
            if not 70 <= vignette_words <= 170:
                errors.append(f"{path.name}: vignette body length {vignette_words} words is outside 70-170")
            lowered = paragraph_text.lower()
            if "opponent" not in lowered:
                errors.append(f"{path.name}: vignette must explicitly depict one opponent")
            if not re.search(r"\b(?:I|I['’]m|I['’]ve|I['’]d|me|my|mine)\b", paragraph_text, re.I):
                errors.append(f"{path.name}: vignette must use a first-person singular speaker")
            opening_mode = (vignette.get("data-vignette-opening") or "").strip()
            if not opening_mode:
                errors.append(f"{path.name}: vignette must declare a data-vignette-opening mode")
            prefix = opening_prefix(paragraph_text)
            if len(prefix.split()) < 4:
                errors.append(f"{path.name}: vignette opening is too short to evaluate for diversity")
            story_openings.append(
                (path, migration_batch(path), prefix, opening_mode, bool(STOCK_MEMORY_OPENING.search(paragraph_text)))
            )
            if re.search(r"\b(?:you|your|yours|yourself)\b", lowered):
                errors.append(f"{path.name}: vignette slips into second-person narration")
            for multiplayer_phrase in ("opponents", "everyone", "each player", "other players"):
                if multiplayer_phrase in lowered:
                    errors.append(f"{path.name}: vignette uses multiplayer/generalized phrasing {multiplayer_phrase!r}")
            if not re.search(r"\b(?:turn|end step|main phase|untap|upkeep|combat|attack|casts?|resolves?)\b", lowered):
                errors.append(f"{path.name}: vignette lacks concrete turn/phase/action sequencing")
            named_cards = [n.get("data-card") for n in vignette.select(".card-name[data-card]") if n.get("data-card")]
            unique_cards = set(named_cards)
            if card_name_key(card) not in {card_name_key(name) for name in unique_cards}:
                errors.append(f"{path.name}: vignette does not mark the featured card as a named card")
            if len(unique_cards) < 3:
                errors.append(f"{path.name}: vignette names only {len(unique_cards)} unique cards; expected at least 3")
            label = vignette.select_one(".vignette-label")
            if label is None or label.get_text(" ", strip=True).lower() != "a story from the table":
                errors.append(f"{path.name}: vignette label must be exactly 'A story from the table'")
            if vignette.select_one(".vignette-context") is not None:
                errors.append(f"{path.name}: visible era/matchup caption must not appear inside the vignette")
            banned_explanation = (
                "what i remember most",
                "looking back",
                "by modern standards",
                "that is the part",
                "the card did not merely",
                "the funny part is",
                "at the time, early magic",
                "most people now",
            )
            for phrase in banned_explanation:
                if phrase in lowered:
                    errors.append(f"{path.name}: vignette contains explanatory coda phrase {phrase!r}; end on the story itself")

            if lead is not None:
                direct = opening.find_all(recursive=False)
                if direct.index(lead) > direct.index(vignette):
                    errors.append(f"{path.name}: vignette appears before the card image/rules introduction")

        strategic = soup.find("section", id="strategic-legacy-brief")
        if strategic is None:
            errors.append(f"{path.name}: missing Strategic legacy")
        else:
            if opening.find_next_sibling("section") is not strategic:
                errors.append(f"{path.name}: Strategic legacy must immediately follow the completed opening")
            brief = strategic.select_one(".brief-lead")
            if brief is None:
                errors.append(f"{path.name}: Strategic legacy lacks .brief-lead")
            elif vignette is not None and similarity(vignette.get_text(" ", strip=True), brief.get_text(" ", strip=True)) >= .72:
                errors.append(f"{path.name}: vignette substantially repeats the Strategic legacy lead")
            # Catch the screenshot failure: a large thesis block immediately before strategy.
            for selector in BANNED_THESIS_SELECTORS:
                if soup.select_one(selector):
                    errors.append(f"{path.name}: reader-facing duplicate thesis block remains ({selector})")
            toc = soup.find("nav", class_="toc")
            if toc:
                opening_link = toc.find("a", href="#opening")
                strategic_link = toc.find("a", href="#strategic-legacy-brief")
                if not opening_link or not strategic_link or opening_link.find_next_sibling("a") is not strategic_link:
                    errors.append(f"{path.name}: TOC must introduce the opening before Strategic legacy")

        pill = soup.select_one(".byline .pill[data-reading-word-count][data-reading-time-wpm]")
        count = editorial_word_count(soup)
        minutes = reading_time_minutes(count)
        if pill is None:
            errors.append(f"{path.name}: read-time pill lacks derived word-count metadata")
        else:
            if pill.get("data-reading-time-wpm") != str(WORDS_PER_MINUTE):
                errors.append(f"{path.name}: read-time WPM must be {WORDS_PER_MINUTE}")
            if pill.get("data-reading-word-count") != str(count):
                errors.append(f"{path.name}: displayed word count {pill.get('data-reading-word-count')} != derived {count}")
            expected_text = f"Approximately {minutes} minute read"
            if pill.get_text(" ", strip=True) != expected_text:
                errors.append(f"{path.name}: read-time text should be {expected_text!r}")
        rows.append((path.name, count, minutes))

        style = soup.find("style", id="cr-reader-experience-v3")
        css = style.get_text("\n") if style else ""
        if style is None:
            errors.append(f"{path.name}: missing inline Reader Experience V3 style")
        else:
            for token in REQUIRED_STYLE_TOKENS:
                if token not in css:
                    errors.append(f"{path.name}: inline style missing {token!r}")

    if not rows:
        errors.append("No pages declare data-reader-experience=\"v3\"")

    # Avoid the mechanical oral-history rhythm that comes from opening every story
    # with the same memory cue. Exact six-word prefixes may not repeat within a
    # production wave, and stock "I remember" openings are limited to one.
    by_batch: dict[str, list[tuple[Path, str, str, bool]]] = {}
    for story_path, batch, prefix, mode, stock in story_openings:
        by_batch.setdefault(batch, []).append((story_path, prefix, mode, stock))
    for batch, items in by_batch.items():
        prefixes: dict[str, list[str]] = {}
        modes: dict[str, list[str]] = {}
        stock_files: list[str] = []
        for story_path, prefix, mode, stock in items:
            prefixes.setdefault(prefix, []).append(story_path.name)
            modes.setdefault(mode, []).append(story_path.name)
            if stock:
                stock_files.append(story_path.name)
        for prefix, files in prefixes.items():
            if len(files) > 1:
                errors.append(f"{batch}: repeated six-word vignette opening {prefix!r} in {', '.join(files)}")
        for mode, files in modes.items():
            if len(files) > 5:
                errors.append(f"{batch}: vignette opening mode {mode!r} is reused {len(files)} times; maximum is 5")
        if len(stock_files) > 1:
            errors.append(
                f"{batch}: stock memory-cue openings are overused in {', '.join(stock_files)}; "
                "open instead on action, dialogue, a board state, a life total, revealed information, or another distinct detail"
            )

    if errors:
        print(f"Reader Experience V3: FAIL ({len(errors)} finding(s))")
        for error in errors:
            print(f"- {error}")
        return 1

    minute_values = sorted({m for _, _, m in rows})
    print(f"Reader Experience V3: PASS ({len(rows)} migrated page(s); read times {minute_values})")
    for name, count, minutes in rows:
        print(f"- {name}: {count} words -> {minutes} minutes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
