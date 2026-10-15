#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import quote, quote_plus

from bs4 import BeautifulSoup, Tag

from headline_identity import editorial_headline
from reader_experience_v3 import WORDS_PER_MINUTE, editorial_word_count, reading_time_minutes

ROOT = Path(__file__).resolve().parents[1]
CARDS_CSV = Path('/mnt/data/mtgjson_cards.csv')
IDS_CSV = Path('/mnt/data/mtgjson_cardIdentifiers.csv')
SETS_CSV = Path('/mnt/data/sets.csv')
TODAY = date(2026, 7, 30)
PLACEHOLDER = 'data:image/gif;base64,R0lGODlhAQABAAAAACw='

TAG_RULES = {
    'mana acceleration': [r'add [^{\n]*\{', r'untap (?:up to )?(?:two |three )?(?:target )?lands?', r'costs? \{?\d?\}? less'],
    'card advantage': [r'draw (?:a|two|three|x) cards?', r'put .* into your hand', r'look at the top .* put .* into your hand'],
    'selection': [r'scry', r'surveil', r'look at the top', r'choose .* card'],
    'removal': [r'destroy target', r'exile target', r'deals? \d+ damage to target', r'-\d+/-\d+', r'return target .* to (?:its|their) owner'],
    'permission': [r'counter target', r'unless (?:its|that spell.s) controller pays'],
    'discard': [r'discards? a card', r'reveals? .* hand'],
    'tokens': [r'create .* token', r'populate'],
    'graveyard': [r'graveyard', r'mill', r'dredge', r'delirium'],
    'recursion': [r'return target .* from your graveyard', r'cast .* from your graveyard', r'from your graveyard to'],
    'tutoring': [r'search your library', r'search target player.s library'],
    'direct damage': [r'deals? .* damage'],
    'life exchange': [r'gain .* life', r'lose .* life', r'pay .* life'],
    'combat pressure': [r'haste', r'double strike', r'first strike', r'trample', r'menace', r'can.t block', r'attacks?'],
    'protection': [r'hexproof', r'shroud', r'indestructible', r'protection from', r'ward'],
    'sacrifice': [r'sacrifice'],
    'copying': [r'copy target', r'create a token that.s a copy', r'copy that spell'],
    'counters': [r'\+1/\+1 counter', r'charge counter', r'counter on'],
    'blink': [r'exile .* then return', r'exile .* return .* battlefield'],
    'cost manipulation': [r'without paying', r'alternative cost', r'rather than pay', r'costs? .* less'],
    'land development': [r'landfall', r'put .* land .* battlefield', r'additional land', r'land card'],
    'tribal scaling': [r'for each .* you control', r'shares? a creature type', r'creature type'],
    'alternate victory': [r'you win the game', r'loses the game'],
}

ROLE_TITLES = {
    'mana acceleration': 'Mana That Changes the Curve',
    'card advantage': 'One Card Becoming a Longer Game',
    'removal': 'The Exchange That Sets the Terms',
    'permission': 'The Right to Say No',
    'discard': 'Information Before Action',
    'tokens': 'More Material Than One Card',
    'graveyard': 'A Second Hand Below the Table',
    'recursion': 'The Resource That Refuses to Stay Spent',
    'tutoring': 'Consistency With a Cost',
    'direct damage': 'Damage as Removal and Clock',
    'combat pressure': 'A Body With Immediate Consequences',
    'protection': 'The Threat That Demands the Right Answer',
    'sacrifice': 'Turning Loss Into an Engine',
    'copying': 'The Value of Doing It Again',
    'counters': 'Small Marks, Compounding Consequences',
    'land development': 'The Mana Base as Strategy',
    'selection': 'The Difference Between Drawing and Finding',
    'cost manipulation': 'Breaking the Price of a Spell',
}

ROLE_EXPLANATIONS = {
    'mana acceleration': 'compressing the mana curve and moving important plays earlier than normal',
    'card advantage': 'converting one draw or permanent into additional usable cards over time',
    'selection': 'improving the quality of future draws without pretending that selection is the same as raw advantage',
    'removal': 'trading for opposing material while preserving the timing needed for a larger plan',
    'permission': 'making the opponent commit mana before deciding whether a spell is allowed to matter',
    'discard': 'trading resources while exposing information that changes later sequencing',
    'tokens': 'splitting one card into several battlefield objects with different tactical uses',
    'graveyard': 'treating the graveyard as a resource zone rather than a record of spent cards',
    'recursion': 'reusing material that ordinary play would count as exhausted',
    'tutoring': 'turning deck construction into a menu of situational answers and payoffs',
    'direct damage': 'letting the same points answer creatures, pressure planeswalkers, or finish a player',
    'life exchange': 'converting life total into cards, tempo, reach, or permission to take another action',
    'combat pressure': 'forcing defensive decisions immediately through efficient or evasive combat',
    'protection': 'changing which answers function and when the opponent must deploy them',
    'sacrifice': 'making a permanent valuable both before and at the moment it leaves play',
    'copying': 'scaling the best available spell or permanent without paying its full original cost again',
    'counters': 'allowing small incremental changes to compound into a durable battlefield advantage',
    'blink': 'reusing enters-the-battlefield text while temporarily removing an object from danger',
    'cost manipulation': 'changing the relationship between printed mana value and actual tempo investment',
    'land development': 'making land drops, land types, or land movement part of the active game plan',
    'tribal scaling': 'rewarding a deck for concentrating on a creature type or repeated permanent class',
    'alternate victory': 'creating a second scoreboard that opponents must respect alongside life total',
}

GENERIC_BY_COLOR = {
    'W': ['Swords to Plowshares', 'Path to Exile', 'Wrath of God', 'Disenchant', 'Mother of Runes', 'Stoneforge Mystic', 'Esper Sentinel'],
    'U': ['Brainstorm', 'Ponder', 'Counterspell', 'Force of Will', 'Preordain', 'Spell Pierce', 'Snapcaster Mage'],
    'B': ['Thoughtseize', 'Fatal Push', 'Dark Ritual', 'Duress', 'Demonic Tutor', 'Reanimate', 'Cabal Therapy'],
    'R': ['Lightning Bolt', 'Faithless Looting', 'Pyroblast', 'Fireblast', 'Abrade', 'Goblin Guide', 'Fable of the Mirror-Breaker'],
    'G': ['Birds of Paradise', 'Llanowar Elves', 'Giant Growth', 'Natural Order', 'Sylvan Library', 'Elvish Spirit Guide', 'Green Sun\'s Zenith'],
    'C': ['Sol Ring', 'Mishra\'s Bauble', 'Pithing Needle', 'Chromatic Star', 'Relic of Progenitus', 'Walking Ballista', 'Expedition Map'],
}

BASIC_BY_COLOR = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}


def slugify(name: str) -> str:
    value = name.casefold().replace('æ', 'ae')
    value = re.sub(r"[^a-z0-9]+", '-', value).strip('-')
    return value


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def card_span(name: str, display: str | None = None) -> str:
    return f'<span class="card-name" data-card="{esc(name)}" tabindex="0">{esc(display or name)}</span>'


def clean_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value or '').strip()


def load_manifest() -> dict:
    return json.loads((ROOT / 'archive-manifest.json').read_text(encoding='utf-8'))


def load_sets() -> dict[str, dict]:
    out = {}
    with SETS_CSV.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            out[row['code'].upper()] = row
    return out


def row_article_name(row: dict, wanted: set[str]) -> str | None:
    if row['name'] in wanted:
        return row['name']
    if row.get('faceName') in wanted:
        return row['faceName']
    return None


def build_card_data(names: set[str], sets: dict[str, dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    uuids: set[str] = set()
    with CARDS_CSV.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            article_name = row_article_name(row, names)
            if not article_name:
                continue
            if row.get('language') != 'English':
                continue
            if 'paper' not in (row.get('availability') or '').split(', '):
                continue
            if (row.get('isOnlineOnly') or '').lower() == 'true':
                continue
            if (row.get('isRebalanced') or '').lower() == 'true':
                continue
            if row.get('side') not in {'', 'a'}:
                continue
            set_info = sets.get(row['setCode'].upper(), {})
            released = set_info.get('releaseDate') or row.get('originalReleaseDate') or '9999-12-31'
            try:
                if date.fromisoformat(released) > TODAY:
                    continue
            except ValueError:
                pass
            row = dict(row)
            row['_article_name'] = article_name
            row['_releaseDate'] = released
            row['_setName'] = set_info.get('name') or row['setCode']
            row['_setType'] = set_info.get('type') or ''
            grouped[article_name].append(row)
            uuids.add(row['uuid'])

    ids: dict[str, dict] = {}
    with IDS_CSV.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['uuid'] in uuids:
                ids[row['uuid']] = row

    data: dict[str, dict] = {}
    for name in names:
        rows = grouped.get(name, [])
        if not rows:
            continue
        for row in rows:
            row['_ids'] = ids.get(row['uuid'], {})
        rows = [r for r in rows if r['_ids'].get('scryfallId') and r['_ids'].get('scryfallOracleId')]
        if not rows:
            continue
        rows.sort(key=lambda r: (
            r['_releaseDate'],
            1 if (r.get('isPromo') or '').lower() == 'true' else 0,
            1 if (r.get('isReprint') or '').lower() == 'true' else 0,
            r['setCode'],
            r['number'],
        ))
        original = rows[0]
        oracle_id = original['_ids']['scryfallOracleId']
        rows = [r for r in rows if r['_ids'].get('scryfallOracleId') == oracle_id]

        # Original, then one representative per unique illustration, then chronological fill.
        selected: list[dict] = []
        seen_ids: set[str] = set()
        seen_arts: set[str] = set()
        def add(r: dict) -> None:
            sid = r['_ids'].get('scryfallId', '')
            if sid and sid not in seen_ids and len(selected) < 12:
                selected.append(r); seen_ids.add(sid)
                art = r['_ids'].get('scryfallIllustrationId') or sid
                seen_arts.add(art)
        add(original)
        for r in rows:
            art = r['_ids'].get('scryfallIllustrationId') or r['_ids'].get('scryfallId')
            if art not in seen_arts:
                add(r)
        for r in rows:
            add(r)

        text = clean_text(original.get('text') or original.get('originalText'))
        type_line = clean_text(original.get('type') or original.get('printedType'))
        colors = [x for x in (original.get('colorIdentity') or original.get('colors') or '').split(', ') if x]
        if not colors:
            colors = []
        tags = derive_tags(type_line, text, original)
        data[name] = {
            'articleName': name,
            'canonicalName': original['name'],
            'faceName': original.get('faceName') or '',
            'setCode': original['setCode'].lower(),
            'setName': original['_setName'],
            'releaseDate': original['_releaseDate'],
            'year': int(original['_releaseDate'][:4]) if original['_releaseDate'][:4].isdigit() else 1993,
            'artist': original.get('artist') or 'Artist not listed',
            'type': type_line or 'Card',
            'types': [x for x in (original.get('types') or '').split(', ') if x],
            'subtypes': [x for x in (original.get('subtypes') or '').split(', ') if x],
            'colors': colors,
            'manaCost': original.get('manaCost') or '—',
            'manaValue': original.get('manaValue') or '0',
            'power': original.get('power') or '',
            'toughness': original.get('toughness') or '',
            'loyalty': original.get('loyalty') or '',
            'oracleText': text or 'This printing has no Oracle rules text.',
            'rarity': (original.get('rarity') or '').title(),
            'keywords': [x for x in (original.get('keywords') or '').split(', ') if x],
            'oracleId': oracle_id,
            'scryfallId': original['_ids']['scryfallId'],
            'illustrationId': original['_ids'].get('scryfallIllustrationId') or '',
            'tags': tags,
            'printings': [printing_record(r, name, original) for r in selected],
            'printingCount': len(rows),
        }
    return data


def printing_record(row: dict, article_name: str, original: dict) -> dict:
    ids = row['_ids']
    sid = ids['scryfallId']
    is_original = sid == original['_ids']['scryfallId']
    return {
        'cardName': article_name,
        'oracleId': ids['scryfallOracleId'],
        'scryfallId': sid,
        'illustrationId': ids.get('scryfallIllustrationId') or '',
        'setCode': row['setCode'].lower(),
        'setName': row['_setName'],
        'collectorNumber': row['number'],
        'artist': row.get('artist') or 'Artist not listed',
        'releaseDate': row['_releaseDate'],
        'original': is_original,
        'imageUrl': f'https://api.scryfall.com/cards/{sid}?format=image&version=normal',
        'artUrl': f'https://api.scryfall.com/cards/{sid}?format=image&version=art_crop',
    }


def derive_tags(type_line: str, text: str, row: dict) -> list[str]:
    hay = (type_line + ' ' + text + ' ' + (row.get('keywords') or '')).casefold()
    tags = []
    if 'land' in type_line.casefold(): tags.append('land development')
    if 'planeswalker' in type_line.casefold(): tags.append('counters')
    if 'creature' in type_line.casefold(): tags.append('combat pressure')
    if 'equipment' in type_line.casefold() or 'aura' in type_line.casefold(): tags.append('combat pressure')
    for tag, patterns in TAG_RULES.items():
        if any(re.search(pattern, hay) for pattern in patterns):
            tags.append(tag)
    if not tags:
        if 'artifact' in type_line.casefold(): tags.append('cost manipulation')
        elif 'enchantment' in type_line.casefold(): tags.append('resource engine')
        else: tags.append('efficiency')
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(tags))


def similarity(a: dict, b: dict, ea: int, eb: int) -> float:
    ta, tb = set(a['tags']), set(b['tags'])
    score = 4 * len(ta & tb)
    score += 1.5 * len(set(a['types']) & set(b['types']))
    score += 0.7 * len(set(a['colors']) & set(b['colors']))
    if a['manaValue'] == b['manaValue']: score += 0.4
    score -= min(abs(ea-eb), 300) / 500
    return score


def choose_related(entry: int, card: dict, entries: list[dict], data: dict[str, dict], count: int = 16) -> list[str]:
    scored = []
    for rec in entries:
        other_name = rec['card']
        if other_name == card['articleName'] or other_name not in data:
            continue
        score = similarity(card, data[other_name], entry, rec['entry'])
        scored.append((score, -abs(rec['entry']-entry), other_name, rec['entry']))
    scored.sort(reverse=True)
    names = []
    for _, _, name, _ in scored:
        if name not in names:
            names.append(name)
        if len(names) >= count:
            break
    return names


def primary_role(card: dict) -> str:
    return card['tags'][0] if card['tags'] else 'efficiency'


def role_title(card: dict) -> str:
    # Every generated article receives a deterministic, card-specific headline.
    return editorial_headline(card)


def role_explanation(card: dict) -> str:
    return ROLE_EXPLANATIONS.get(primary_role(card), 'converting a compact piece of rules text into a repeatable strategic advantage')


def stats_html(card: dict) -> str:
    pt = ''
    if card['power'] or card['toughness']:
        pt = f'<div class="stat"><b>Power / toughness</b>{esc(card["power"] or "—")} / {esc(card["toughness"] or "—")}</div>'
    elif card['loyalty']:
        pt = f'<div class="stat"><b>Starting loyalty</b>{esc(card["loyalty"])}</div>'
    else:
        pt = f'<div class="stat"><b>Card class</b>{esc(card["type"])}</div>'
    return (
        f'<div class="stats"><div class="stat"><b>Original set</b>{esc(card["setName"])} · {card["year"]}</div>'
        f'<div class="stat"><b>Mana cost</b>{esc(card["manaCost"])}</div>'
        f'<div class="stat"><b>Mana value</b>{esc(card["manaValue"])}</div>{pt}</div>'
    )


def section_html(section_id: str, chapter: str, title: str, paragraphs: list[str], extra: str = '', classes: str = '') -> str:
    cls = f' class="{classes}"' if classes else ''
    body = ''.join(f'<p>{p}</p>' for p in paragraphs)
    return f'<section id="{section_id}"{cls}><div class="chapter-number">{esc(chapter)}</div><h2>{esc(title)}</h2>{body}{extra}</section>'


def prose_sections(rec: dict, card: dict, related: list[str]) -> list[tuple[str, str]]:
    name = esc(card['articleName'])
    role = esc(primary_role(card))
    mechanism = esc(role_explanation(card))
    set_name = esc(card['setName'])
    year = card['year']
    type_line = esc(card['type'])
    oracle = esc(card['oracleText']).replace('\n', '<br/>')
    rel = related + ['Black Lotus'] * 8
    r1, r2, r3, r4, r5, r6 = [card_span(x) for x in rel[:6]]
    tag_list = ', '.join(esc(t) for t in card['tags'][:4])
    opening_extra = (
        f'<div class="card-lead"><img alt="{name} card image" loading="eager" decoding="async" '
        f'src="https://api.scryfall.com/cards/{card["scryfallId"]}?format=image&amp;version=normal"/>'
        f'<div class="oracle"><div class="eyebrow">Original object · {set_name}</div><h3>{name}</h3>'
        f'<p><b>{type_line}</b></p><p>{oracle}</p>{stats_html(card)}</div></div>'
    )
    opening = section_html('opening', 'I · Opening hand', role_title(card), [
        f'<span class="dropcap">{name[0]}</span>{name[1:]} is easiest to understand when the card is treated as a decision machine rather than a reputation. Its printed object combines {type_line.lower()} structure with an emphasis on {role}. The important question is not merely whether the card is powerful. It is what sequence, resource exchange, and deck construction make that power reliable.',
        f'The core operation is {mechanism}. That operation can look modest in isolation because Magic cards are not played in isolation. Mana development, combat, hidden information, opposing interaction, and the value of future draw steps all change what the same line of text is worth. A useful history therefore begins with the card as played, not with a ranking or a slogan.',
        f'This dossier records the stable facts first: {name} appeared in {set_name} in {year}, carries the type line {type_line}, and is credited to {esc(card["artist"])} in its original printing. From there, the article follows the card through rules texture, deck-building demands, sequencing, counterplay, comparison, and material print history. Where tournament documentation has not been independently verified, the deck archive uses transparent editorial study shells instead of invented registrations.'
    ], opening_extra, 'opening')

    origin = section_html('origin', 'II · First printing', 'The original object and its constraints', [
        f'The original {set_name} printing fixed three things at once: a mana cost of {esc(card["manaCost"])}, a mana value of {esc(card["manaValue"])}, and the exact rules package reproduced above. Those facts establish the card’s floor before metagames and memories add interpretation. A lower cost changes how early the object can enter play; a higher cost increases the amount of protection or setup a deck may need. Neither number alone determines quality, but both determine the kinds of turns on which the card can participate.',
        f'Type line matters just as much. As a {type_line}, the card enters a web of rules that controls when it can be cast, what zones and removal effects can reach it, whether it can attack or block, and what other cards can search for or reuse it. The card’s identity is therefore partly printed text and partly the general rules carried by its types. This is why apparently concise designs can create long strategic arguments.',
        f'The original environment is not reconstructed here by invented anecdotes. The defensible claim is narrower: once {name} entered the card pool in {year}, deck builders could test {mechanism} at this exact rate and with this exact object type. Later card pools supplied different companions and opponents, but they did not erase the baseline established by the first printing.',
        f'Comparison clarifies the baseline. {r1} and {r2} occupy adjacent design territory, yet each changes at least one of cost, timing, card type, targeting restriction, or payoff. Reading those differences prevents the archive from collapsing every card with a similar purpose into the same story.'
    ])

    rules = section_html('rules', 'III · Rules text', 'Read every verb, cost, and timing window', [
        f'The Oracle text of {name} should be parsed in order. Costs are paid before effects happen. Targets, if any, are chosen when the spell or ability is put on the stack. Conditional clauses determine whether the promised exchange occurs, while duration language determines how long a bonus, restriction, or permission survives. These are elementary rules, but the card’s practical ceiling depends on respecting them.',
        f'The listed mechanical themes—{tag_list}—describe the card’s jobs, not shortcuts around its wording. A card that produces mana still requires a plan for spending it. A card that removes something still depends on legal targets and the opponent’s response window. A card that creates material still asks whether that material can be converted into damage, cards, mana, or protection before the battlefield changes.',
        f'Players often lose value by treating the most visible sentence as the whole card. The hidden text includes the cost of holding mana open, the information revealed by a chosen target, the opportunity cost of using an ability now rather than later, and the possibility that an opponent can answer the enabling permanent instead of the payoff. Exact play begins by naming those hidden costs.',
        f'{r3} offers a useful comparison because its text reaches a related strategic destination through a different rules path. The lesson is not that the cards are interchangeable. It is that timing words, zone changes, and target restrictions are part of power, even when deck summaries reduce both cards to the same role label.'
    ])

    economy = section_html('economy', 'IV · Resource economy', 'What the exchange is actually worth', [
        f'Every use of {name} can be described as an exchange among cards, mana, time, life, board position, and information. The printed effect may directly name only one or two of those resources, but the others remain present. Spending a card and mana now may protect several future draw steps. Declining to act may preserve flexibility but allow the opponent to improve their board. The right evaluation is situational rather than absolute.',
        f'The card’s strongest turns usually compress two tasks into one decision. A threat that also protects a resource, an answer that also advances a clock, or an engine that also stabilizes the board reduces the number of separate cards a deck must draw. Conversely, a use that accomplishes only the smallest printed task can leave the controller behind even when the effect technically resolves.',
        f'Tempo is especially easy to misread. Mana value {esc(card["manaValue"])} tells us the printed investment, but not the full turn cost. Colored requirements affect the mana base. Sorcery-speed commitment may expose a player to a counterattack. Holding the card for a perfect target can waste mana that might have advanced another plan. Good play asks which resource is scarce on this turn, not which mode looks most impressive in a vacuum.',
        f'{r4} and {r5} help frame the same exchange from other angles. One may ask for more mana but offer a broader result; the other may be narrower yet easier to sequence. The archive uses such comparisons to identify the essential bargain without pretending that a card has one fixed numerical value in every game.'
    ])

    deckbuilding = section_html('deckbuilding', 'V · Construction', 'What a deck must provide', [
        f'A deck that includes {name} must do more than make the mana cost legal. It must decide whether the card is an engine, an answer, a threat, a bridge between phases of the game, or a redundant copy of an effect the deck already wants. Those roles imply different copy counts. Engines reward early access but can be poor in multiples. Reactive cards depend on the expected targets. Finishers require enough setup to survive until their turn arrives.',
        f'The mana base should be built from actual colored requirements rather than total color count. A spell needed on curve may demand more sources than a later splash card with the same symbols. Lands also carry opportunity cost: tapped lands slow interaction, utility lands reduce colored consistency, and greedy fixing may expose the deck to nonbasic-land pressure. The printed cost of {name} is therefore a deck-building instruction as well as a rules fact.',
        f'Support cards should cover failure states rather than merely imitate the best-case scenario. If {name} needs a battlefield, include ways to establish one. If it is vulnerable to a particular answer, decide whether protection, recursion, redundancy, or speed is the better response. If it is strongest after an exchange, include cards that force that exchange. Synergy is most durable when the surrounding deck remains functional without drawing the namesake card.',
        f'Adjacent archive cards such as {r1}, {r3}, and {r6} illustrate three common construction choices: redundancy, complement, and alternate angle. Redundancy increases consistency; complement covers a weakness; an alternate angle punishes opponents for sideboarding too narrowly. The best package is the one that improves the deck’s total decision tree rather than maximizing a single screenshot-worthy turn.'
    ])

    sequencing = section_html('sequencing', 'VI · Sequencing', 'The turn before the famous turn', [
        f'The decisive play with {name} is often prepared one turn earlier. A land was fetched to preserve the right color. A disposable permanent was held rather than traded. An opponent was allowed to resolve a minor spell so that interaction remained available for the true bottleneck. These choices are difficult to notice because the payoff card receives the visual attention while preparation looks like ordinary housekeeping.',
        f'Before casting the card, count available mana on both sides, identify likely instant-speed responses, and decide what happens if the first plan fails. This does not require perfect knowledge. It requires a branch: if the opponent answers now, which resource did they spend and what becomes possible next? If they decline, what follow-up converts the resolved card into an advantage before their next untap?',
        f'After resolution, avoid automatic activation. Permanents with choices are most powerful when their controller values the future option as part of the current board. The obvious mode may create immediate material, while a quieter mode protects against a sweep, preserves mana, or changes combat math. Even a straightforward spell can create a post-resolution choice about targets, attacks, and which resource to expose.',
        f'The comparison with {r2} is useful here because two cards can share a role while demanding opposite sequencing. One rewards deployment into an empty window; another rewards patience until a target appears. Role labels help with deck selection, but timing texture determines actual play.'
    ])

    counterplay = section_html('counterplay', 'VII · Counterplay', 'How opponents reduce the ceiling', [
        f'Counterplay begins by separating the card from the conditions that make it exceptional. Sometimes the efficient answer is the card itself. In other games, the better target is the mana source, token maker, graveyard enabler, protection spell, or payoff that turns a fair exchange into an engine. The opponent should attack the narrowest structural point rather than the most famous permanent.',
        f'Timing matters. Answering before an ability resolves can prevent value; answering afterward may still be correct if it removes a repeated source of advantage. Leaving mana untapped can alter the controller’s sequence even when no answer is held. Conversely, representing too much can give the {name} player free time to develop a second plan. Good counterplay balances actual interaction with the cost of bluffing it.',
        f'Sideboarding should identify which part of the card matters in the matchup. Graveyard hate is weak if the deck can win as an ordinary midrange strategy. Narrow removal is poor if the card’s value is already earned on entry. Expensive universal answers may solve the object but lose the mana exchange. The best sideboard card often changes several matchups while still reaching the relevant permanent or zone.',
        f'{r4} demonstrates a different failure mode within related territory, while {r5} shows another kind of resilience. Studying both helps an opponent avoid the mistake of using one answer pattern against every card that shares a broad strategic label.'
    ])

    formats = section_html('formats', 'VIII · Formats', 'The same text under different clocks', [
        f'Formats change the value of {name} without changing its Oracle text. Faster environments punish setup and reward low opportunity cost. Slower environments increase the value of repeatable engines and flexible topdecks. Larger card pools supply stronger combinations but also stronger answers. Multiplayer adds more opponents, more total resources, and a political cost to becoming the visible leader.',
        f'The right question is therefore not whether the card is “a Modern card,” “a Commander card,” or “a Standard card” in the abstract. The question is what job it performs in a specific deck under a specific clock. A card can be central in one shell, a sideboard tool in another, and a nostalgic but inefficient option in a third. Those differences are evidence of context, not contradictions.',
        f'Legality and metagame position can change, so this archive does not freeze current format claims into prose. Before building for sanctioned play, readers should check the official format policy and the card’s current legality. The stable historical object remains the printed cost, type, text, and release; competitive status is a moving layer placed on top.',
        f'Comparisons to {r1}, {r2}, and {r3} show how card-pool scale changes evaluation. A newer or broader environment may offer cleaner redundancy. An older or narrower environment may make a distinctive effect uniquely important. Both situations can explain influence without requiring the card to remain optimal forever.'
    ])

    memory = section_html('memory', 'IX · Memory', 'Why the card remains easy to remember', [
        f'Cards endure in player memory for more than win rate. Some create a recognizable turn pattern. Some change how hands are mulliganed or how opponents leave mana open. Some make a deck’s plan legible from a single battlefield object. {name} belongs in an archive because its combination of {role} and {type_line.lower()} structure gives players a compact story about what a deck is trying to do.',
        f'That story can survive even after the card’s competitive share falls. Later designs may improve the rate, divide the effect across new card types, or attach the same idea to a different color. The older card remains useful as vocabulary. Players can point to it when explaining a family of decisions, and designers can vary its constraints while preserving the recognizable question.',
        f'Material history reinforces that memory. The archive currently identifies {card["printingCount"]} English paper printing record(s) sharing the same Oracle identity in the source export, with up to twelve shown below and distinct illustration records prioritized. Different frames and artworks change the object’s emotional tone even when the rules remain stable.',
        f'The original credit to {esc(card["artist"])} is therefore not decorative metadata. It records the first visual form through which players encountered the card. Rules create strategic memory; image, frame, set symbol, and physical handling create object memory. A preservation project needs both.'
    ])

    case = section_html('case-study', 'XI · Practical reading', 'A representative decision tree', [
        f'Imagine a game in which {name} is available, the opponent can plausibly interact, and both players have competing uses for their mana. The first branch is whether casting the card now improves the board enough to justify exposing it. The second is whether waiting gains information or merely gives the opponent a cleaner development turn. The third is what resource the controller is willing to lose if the answer arrives.',
        f'On the proactive branch, the controller casts the card and immediately plans the next conversion: attack, activate, sacrifice, recur, protect, or spend newly created mana. On the patient branch, the controller advances with another card while preserving {name} as a later pivot. Neither branch is automatically correct. The choice depends on hand texture, known information, and whether the opponent’s likely answer is more valuable than the card being exposed.',
        f'Now reverse the seat. The opponent asks whether a direct answer is necessary, whether the enabling resource can be attacked, and whether racing is more efficient than interaction. A player who answers every famous card on sight can be manipulated into poor exchanges. A player who refuses to respect an engine can lose several turns to one unresolved object. The skill is identifying the turn on which the card crosses from possibility into inevitability.',
        f'{r5} supplies a useful alternate branch because it asks a similar strategic question at a different rate or with a different vulnerability. Comparing the two makes the decision tree concrete: which card is better when behind, which is safer when ahead, and which leaves more useful play when the first plan is answered?'
    ])

    close = section_html('close-reading', 'XII · Closing argument', 'Preserve the question, not only the result', [
        f'The lasting value of {name} is the question it repeatedly asks: how much is {mechanism} worth at this cost, on this card type, and at this point in the game? That question can be answered differently by different formats and eras without making the archive incoherent. Influence is often the persistence of the question rather than permanent dominance of one answer.',
        f'A complete reading therefore resists two simplifications. The first is nostalgia, which treats remembered success as proof that the card remains universally efficient. The second is presentism, which treats later competition as proof that the earlier design no longer matters. The historical object sits between them. It established a playable rate, taught a sequence, and became a comparison point for later cards.',
        f'The related cards discussed throughout this dossier—{r1}, {r2}, {r3}, {r4}, and {r5}—do not replace {name}. They map the design space around it. Some preserve the role while changing the cost. Others preserve the timing while changing the payoff. Together they show why card history is best written as a network of decisions rather than a list of isolated rankings.',
        f'For play, the practical conclusion is equally direct: build the surrounding deck to make the ordinary case acceptable, sequence for the opponent’s real answers, and treat the spectacular case as upside rather than entitlement. That discipline is what turns a famous card from a story into a tool.'
    ])
    return [('opening', opening), ('origin', origin), ('rules', rules), ('economy', economy), ('deckbuilding', deckbuilding), ('sequencing', sequencing), ('counterplay', counterplay), ('formats', formats), ('memory', memory), ('case-study', case), ('close-reading', close)]


def artwork_spotlight(card: dict) -> str:
    sid = card['scryfallId']; name = esc(card['articleName']); artist = esc(card['artist']); set_name = esc(card['setName'])
    if 'Creature' in card['type'] or 'Planeswalker' in card['type']:
        excerpt = 'The illustration organizes the figure through a readable silhouette, layered depth, and directional light. Foreground texture and background atmosphere keep the subject legible at card size while still suggesting a larger world beyond the frame.'
    elif 'Land' in card['type']:
        excerpt = 'The landscape is arranged through depth, horizon, and changes in scale, with light guiding the eye from the foreground into the setting. Texture and atmospheric distance make the location feel like a place rather than a decorative backdrop.'
    elif 'Artifact' in card['type']:
        excerpt = 'The composition gives the central object a clear silhouette and material texture, using contrast and surrounding space to communicate weight and purpose. Light catches the focal form while the background supplies atmosphere without obscuring it.'
    else:
        excerpt = 'The illustration uses framing, contrast, and directional motion to turn an abstract magical event into a readable scene. Light and shadow separate the focal action from the background, preserving clarity even at the small scale of a card.'
    return (
        f'<div class="art-break artwork-spotlight" data-artwork-artist="{artist}" data-artwork-card="{name}" '
        f'data-artwork-set="{card["setCode"]}" data-artwork-set-name="{set_name}">'
        f'<img alt="{name} artwork by {artist}" class="art-break-media" loading="lazy" '
        f'onerror="this.onerror=null;this.src=\'https://api.scryfall.com/cards/{sid}?format=image&amp;version=normal\';" '
        f'src="https://api.scryfall.com/cards/{sid}?format=image&amp;version=art_crop"/>'
        f'<div class="art-caption"><b aria-live="polite" data-artwork-credit="">{artist}’s original {set_name} artwork</b>'
        f'<span class="art-caption-excerpt">{excerpt}</span></div></div>'
    )


def design_echo_section(card: dict, echo_name: str, echo_card: dict) -> str:
    exact = quote_plus(echo_name)
    refs = json.dumps([echo_name], ensure_ascii=False)
    return (
        f'<section class="design-echo-section" data-card-discovery="oracle-catalog-v2" '
        f'data-card-references=\'{esc(refs)}\' id="descendant">'
        f'<div class="chapter-number">X · Design echo</div><h2>A later comparison</h2>'
        f'<p>{card_span(echo_name)} occupies adjacent design territory. The comparison is conceptual rather than a claim of direct lineage: it isolates what later design kept, redirected, restricted, or priced differently.</p>'
        f'<div class="inline-image canonical-inline-image" data-image-card="{esc(echo_name)}">'
        f'<div class="image image-loading" data-card-label="{esc(echo_name)}"><img alt="{esc(echo_name)} artwork" '
        f'class="inline-image-media" data-api-url="https://api.scryfall.com/cards/named?exact={exact}" data-card-name="{esc(echo_name)}" '
        f'data-fallback-art="https://api.scryfall.com/cards/named?exact={exact}&amp;format=image&amp;version=art_crop" '
        f'data-fallback-fuzzy="https://api.scryfall.com/cards/named?fuzzy={exact}&amp;format=image&amp;version=art_crop" '
        f'data-fallback-normal="https://api.scryfall.com/cards/named?exact={exact}&amp;format=image&amp;version=normal" '
        f'decoding="async" referrerpolicy="no-referrer" src="{PLACEHOLDER}"/></div>'
        f'<div class="copy"><div class="eyebrow">A comparative echo</div><h3>{esc(echo_name)}</h3>'
        f'<p>Both cards engage {esc(primary_role(card))}, but the later object changes cost, type, timing, or required support. Those changes reveal which part of the older card’s question remained reusable.</p></div></div>'
        f'<p>{card_span(echo_name)} should not be read as a replacement verdict. A later card can be more efficient in one environment while exposing a different weakness in another. The useful comparison is the shape of the decision: what must be invested, when value is earned, and how an opponent can interrupt it.</p>'
        f'<p>Design echoes are rarely exact copies. They distribute an older idea across new card types, colors, zones, or multiplayer assumptions. Preserving the original card alongside the echo makes that evolution visible without inventing a single straight line of descent.</p></section>'
    )


def choose_deck_pool(card: dict, related: list[str], all_names: set[str]) -> list[str]:
    pool = list(related)
    colors = card['colors'] or ['C']
    for color in colors:
        pool.extend(GENERIC_BY_COLOR.get(color, []))
    pool.extend(GENERIC_BY_COLOR['C'])
    # Ensure actual known cards and avoid subject.
    out = []
    for name in pool:
        if name in all_names and name != card['articleName'] and name not in out:
            out.append(name)
    return out


def land_rows(colors: list[str], shift: int = 0) -> list[tuple[int, str]]:
    actual = [c for c in colors if c in BASIC_BY_COLOR] or ['C']
    if actual == ['C']:
        return [(24, 'Wastes')]
    n = len(actual)
    base = 24 // n
    rem = 24 % n
    rows = []
    for i, c in enumerate(actual):
        qty = base + (1 if ((i + shift) % n) < rem else 0)
        rows.append((qty, BASIC_BY_COLOR[c]))
    return rows


def deck_section(entry: int, card: dict, related: list[str], all_names: set[str]) -> str:
    pool = choose_deck_pool(card, related, all_names)
    while len(pool) < 20:
        for fallback in ['Lightning Bolt', 'Counterspell', 'Swords to Plowshares', 'Thoughtseize', 'Birds of Paradise', 'Sol Ring', 'Pithing Needle']:
            if fallback in all_names and fallback != card['articleName'] and fallback not in pool:
                pool.append(fallback)
    shell_names = ['Efficiency model', 'Synergy model', 'Resilience model', 'Interaction model', 'Long-game model']
    decks = []
    for i, shell_name in enumerate(shell_names, 1):
        rotated = pool[i-1:] + pool[:i-1]
        support = rotated[:4]
        interaction = rotated[4:8]
        side = rotated[8:13]
        lands = land_rows(card['colors'], i-1)
        deck_id = f'deck-{entry:03d}-{slugify(card["articleName"])}-{i}'
        def row(qty: int, name: str, subject: bool = False) -> str:
            label = esc(name) if subject else card_span(name)
            return f'<div class="row"><span class="qty">{qty}</span>{label}</div>'
        main_rows = [row(4, card['articleName'], True)] + [row(4, n) for n in support]
        int_rows = [row(4, n) for n in interaction]
        land_html = ''.join(row(q, n) for q, n in lands)
        side_html = ''.join(row(3, n) for n in side)
        pre_lines = [f'{shell_name} — {card["articleName"]}', 'Editorial study shell; not a tournament registration', '', 'Core', f'4 {card["articleName"]}']
        pre_lines += [f'4 {n}' for n in support] + ['', 'Interaction'] + [f'4 {n}' for n in interaction] + ['', 'Lands'] + [f'{q} {n}' for q,n in lands] + ['', 'Sideboard'] + [f'3 {n}' for n in side]
        decks.append(
            f'<details class="deck"{" open=\"\"" if i==1 else ""}><summary><span><strong>{esc(shell_name)} — {esc(card["articleName"])}</strong>'
            f'<small>Format-agnostic editorial exercise · 60 cards + 15 sideboard</small></span><span class="plus">+</span></summary>'
            f'<div class="deck-body"><span class="provenance-badge">Editorial study shell</span>'
            f'<p>This list is a teaching model for testing sequencing and role density. It is not presented as a historical tournament registration, a legality claim, or an optimized recommendation.</p>'
            f'<div class="deck-meta"><div><b>Compulsive Research editorial laboratory</b><div class="small">Main deck 60 · Sideboard 15</div></div>'
            f'<button class="copy" data-target="{deck_id}">Copy decklist</button></div>'
            f'<div class="deck-columns"><div class="deck-col"><div class="group"><h4>Core and support · 20</h4>{"".join(main_rows)}</div>'
            f'<div class="group"><h4>Interaction and texture · 16</h4>{"".join(int_rows)}</div></div>'
            f'<div class="deck-col"><div class="group"><h4>Lands · 24</h4>{land_html}</div><div class="group"><h4>Sideboard · 15</h4>{side_html}</div></div></div>'
            f'<pre hidden="" id="{deck_id}">{esc(chr(10).join(pre_lines))}</pre></div></details>'
        )
    intro = (
        '<p>The original project standard favors documented tournament registrations. For this full-sequence continuation, no player, event, placement, or historical seventy-five is asserted without independent verification. The five shells below are clearly labeled editorial exercises: they preserve the page’s interactive deck component and provide practical testing material while leaving provenance research visible as future editorial work.</p>'
        '<div class="archive-standard-note">These lists are not historical evidence. They are format-agnostic teaching shells built to test the namesake card’s ordinary sequencing, support requirements, and interaction patterns.</div>'
    )
    return f'<section id="decklists"><div class="chapter-number">XIII · Deck laboratory</div><h2>The deck archive</h2>{intro}<div class="deck-archive">{"".join(decks)}</div></section>'


def printings_section(card: dict) -> str:
    figures = []
    for i, p in enumerate(card['printings']):
        cls = 'printing original-printing' if i == 0 else 'printing'
        figures.append(
            f'<figure class="{cls}" data-card-name="{esc(card["articleName"])}" '
            f'data-scryfall-id="{p["scryfallId"]}" data-set="{p["setCode"]}" '
            f'data-collector-number="{esc(p["collectorNumber"])}" data-identity-status="verified-mtgjson-snapshot">'
            f'<img alt="{esc(card["articleName"])} — {esc(p["setName"])}" loading="lazy" decoding="async" src="{p["imageUrl"]}"/>'
            f'<figcaption><b>{esc(p["setName"])} · {p["releaseDate"][:4]}</b><br/>{"Original printing · " if i==0 else ""}{esc(p["artist"])} · {esc(p["collectorNumber"])}</figcaption></figure>'
        )
    q = quote(card['articleName'], safe='')
    sources = [
        (f'Scryfall printing catalog for {card["articleName"]}', f'https://scryfall.com/search?q=%21%22{q}%22&unique=prints&as=grid&order=released', 'Card identity, printing chronology, images, and illustration records.'),
        ('Gatherer card record', f'https://gatherer.wizards.com/Pages/Search/Default.aspx?name=+%5B{q}%5D', 'Official Oracle wording and rulings reference.'),
        ('MTGJSON card and printing data', 'https://mtgjson.com/downloads/all-files/', 'Machine-readable set, printing, artist, and identifier data used for the static snapshot.'),
        ('Magic Comprehensive Rules', 'https://magic.wizards.com/en/rules', 'Official rules framework for timing, zones, costs, targets, and card types.'),
        ('Official Banned & Restricted list', 'https://magic.wizards.com/en/banned-restricted-list', 'Current legality should be verified here because format policy changes over time.'),
    ]
    source_html = ''.join(f'<li><a href="{url}">{esc(title)}</a><span>{esc(note)}</span></li>' for title,url,note in sources)
    return (
        f'<section id="printings"><div class="chapter-number">XIV · Material history</div><h2>Printings and sources</h2>'
        f'<p>The static gallery begins with the earliest verified English paper printing in the current data snapshot, then prioritizes distinct illustration identifiers before filling remaining slots chronologically. It shows up to twelve exact-identity printings; the canonical runtime rechecks Scryfall when the page is online.</p>'
        f'<div class="printings canonical-printing-gallery" data-card="{esc(card["articleName"])}" data-gallery-fallback-count="{len(figures)}" '
        f'data-gallery-max="12" data-gallery-mode="hydrate" data-identity-policy="exact-name-and-oracle-id" data-original-set="{card["setCode"]}" '
        f'data-selection-policy="unique-artwork-first" id="printing-grid">{"".join(figures)}</div>'
        f'<h3>Sources</h3><ul class="sources">{source_html}</ul>'
        f'<p class="editor-note">The metadata snapshot records {card["printingCount"]} English paper printing record(s) with the selected Oracle identity. Double-faced cards may retain the verified static gallery if Scryfall’s exact-name runtime returns the combined face name.</p></section>'
    )


def update_hero_and_nav(soup: BeautifulSoup, rec: dict, card: dict, title: str) -> None:
    soup.title.string = f'{card["articleName"]}: {title} — Compulsive Research'
    meta = soup.find('meta', attrs={'name':'description'})
    if meta: meta['content'] = f'A Compulsive Research study of {card["articleName"]}, first printed in {card["setName"]}.'
    art_url = f'https://api.scryfall.com/cards/{card["scryfallId"]}?format=image&version=art_crop'
    normal_url = f'https://api.scryfall.com/cards/{card["scryfallId"]}?format=image&version=normal'
    if soup.body:
        soup.body['data-article-card'] = card['articleName']
    headline_meta = soup.find('meta', attrs={'name': 'article-headline'})
    if not headline_meta:
        headline_meta = soup.new_tag('meta')
        headline_meta['name'] = 'article-headline'
        soup.head.append(headline_meta)
    headline_meta['content'] = title
    hero_header = soup.select_one('header.hero')
    hero_header['data-hero-card'] = card['articleName']
    hero_header['data-headline-card'] = card['articleName']
    hero_media = hero_header.select_one('img.hero-media')
    if not hero_media:
        hero_media = soup.new_tag('img')
        hero_header.insert(0, hero_media)
    hero_media['class'] = ['hero-media']
    hero_media['alt'] = f'{card["articleName"]} artwork'
    hero_media['loading'] = 'eager'
    hero_media['decoding'] = 'async'
    hero_media['fetchpriority'] = 'high'
    hero_media['referrerpolicy'] = 'no-referrer'
    hero_media['data-hero-card'] = card['articleName']
    hero_media['src'] = art_url
    hero_media['onerror'] = f"this.onerror=null;this.src='{normal_url}';"
    contract = soup.find('style', id='hero-identity-contract')
    if not contract:
        contract = soup.new_tag('style', id='hero-identity-contract')
        soup.head.append(contract)
    contract.string = f"""
/* Card-specific hero contract. */
.hero:before{{background-image:url("{art_url}")!important;background-position:center 28%!important}}
.art-break{{background-image:url("{art_url}")!important}}
"""
    hero = soup.select_one('.hero-inner')
    hero.select_one('.archive-link')['href'] = rec['landing_return_href']
    hero.select_one('.eyebrow').string = f'Entry {rec["entry"]:03d} · Wave {rec["wave"]["number"]:02d} · {rec["wave"]["title"]}'
    h1 = hero.select_one('h1')
    h1.clear()
    h1['data-headline-card'] = card['articleName']
    h1.string = title
    hero.select_one('.deckline').string = (
        f'{card["articleName"]} entered Magic in {card["setName"]} ({card["year"]}) as a {card["type"]} centered on {primary_role(card)}. '
        'This metadata-grounded dossier studies the decisions created by that object without inventing tournament provenance.'
    )
    byline = hero.select_one('.byline')
    byline.clear()
    for text in ['A Compulsive Research essay', f'{card["setName"]}, {card["year"]}', 'Reading time calculated at build']:
        span = soup.new_tag('span'); span['class'] = ['pill']; span.string = text; byline.append(span)
    nav = soup.select_one('.rank-nav')
    nav.clear()
    if rec.get('previous'):
        a = soup.new_tag('a', href=rec['previous']['href']); a.string = f'← Entry {rec["previous"]["entry"]:03d} · {rec["previous"]["card"]}'; nav.append(a)
    center = soup.new_tag('span'); center['class']=['center']; center.string=f'Entry {rec["entry"]:03d} of 1,000'; nav.append(center)
    if rec.get('next'):
        a = soup.new_tag('a', href=rec['next']['href']); a.string = f'Entry {rec["next"]["entry"]:03d} · {rec["next"]["card"]} →'; nav.append(a)


def update_end_nav(soup: BeautifulSoup, rec: dict, card: dict) -> None:
    end = soup.select_one('.end-nav')
    if end:
        end.clear()
        if rec.get('previous'):
            a = soup.new_tag('a', href=rec['previous']['href'])
            small=soup.new_tag('small'); small.string=f'Previous entry · {rec["previous"]["entry"]:03d}'; a.append(small); a.append(rec['previous']['card']); end.append(a)
        if rec.get('next'):
            a = soup.new_tag('a', href=rec['next']['href'])
            small=soup.new_tag('small'); small.string=f'Next entry · {rec["next"]["entry"]:03d}'; a.append(small); a.append(rec['next']['card']); end.append(a)
        parent = end.find_parent('section')
        if parent:
            p=parent.find('p')
            if p: p.string=f'{card["articleName"]} is entry {rec["entry"]:03d} in the archive’s reading sequence. The number preserves archive order.'
    footer=soup.select_one('footer.footer')
    if footer: footer.string=f'Compulsive Research · Entry {rec["entry"]:03d} · {card["articleName"]} · Independent, noncommercial Magic history project.'


def render_article(template_text: str, rec: dict, card: dict, related: list[str], data: dict[str,dict], all_names:set[str]) -> str:
    soup = BeautifulSoup(template_text, 'lxml')
    title = role_title(card)
    update_hero_and_nav(soup, rec, card, title)
    article = soup.select_one('article.article')
    article.clear()
    sections = prose_sections(rec, card, related)
    # Insert first two sections, spotlight, remaining study sections, Design Echo, closing, decks, printings.
    for idx, (sid, markup) in enumerate(sections):
        fragment = BeautifulSoup(markup, 'lxml').find('section')
        article.append(fragment)
        if idx == 1:
            article.append(BeautifulSoup(artwork_spotlight(card), 'lxml').find(class_='artwork-spotlight'))
        if sid == 'memory':
            echo_name = next((n for n in related if n in data and n != card['articleName']), related[0])
            article.append(BeautifulSoup(design_echo_section(card, echo_name, data[echo_name]), 'lxml').find('section'))
    article.append(BeautifulSoup(deck_section(rec['entry'], card, related, all_names), 'lxml').find('section'))
    article.append(BeautifulSoup(printings_section(card), 'lxml').find('section'))

    # Canonical TOC in document order.
    toc = soup.select_one('nav.toc')
    toc.clear()
    strong=soup.new_tag('strong'); strong.string='Contents'; toc.append(strong)
    for section in article.select(':scope > section[id]'):
        a=soup.new_tag('a', href='#'+section['id'])
        h2=section.find('h2'); a.string=h2.get_text(' ',strip=True) if h2 else section['id']; toc.append(a)
    update_end_nav(soup, rec, card)
    word_count = editorial_word_count(soup)
    minutes = reading_time_minutes(word_count)
    pill = soup.select_one('.byline .pill:last-child')
    if pill:
        pill.string = f'Approximately {minutes} minute read'
        pill['data-reading-word-count'] = str(word_count)
        pill['data-reading-time-wpm'] = str(WORDS_PER_MINUTE)
    return '<!DOCTYPE html>\n' + str(soup.html)


def update_index(manifest: dict, data: dict[str,dict]) -> None:
    path = ROOT / 'index.html'
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'lxml')
    for rec in manifest['entries']:
        entry = rec['entry']
        if entry < 401 or entry > 1000 or entry == 605:
            continue
        node = soup.find(id=f'entry-{entry}')
        if not node:
            continue
        filename = f'{entry:03d}-{slugify(rec["card"])}.html'
        if node.name != 'a':
            node.name = 'a'
        node['href'] = filename
        node['aria-label'] = f'Read the complete article for {rec["card"]}'
        node['class'] = ['entry','entry-published']
        node['data-status'] = 'published'
        card = data[rec['card']]
        node['data-search'] = f'{entry} {rec["card"]} {rec["lens"]} {card["setName"]} {card["year"]} {" ".join(card["tags"])}'
        status = node.select_one('.entry-status')
        if status: status.decompose()
        op = node.select_one('.entry-open')
        if not op:
            op = soup.new_tag('span'); op['class']=['entry-open']; node.append(op)
        op.string = 'Read article →'
    path.write_text('<!DOCTYPE html>\n'+str(soup.html), encoding='utf-8')


def update_metadata_file(manifest:dict, data:dict[str,dict]) -> None:
    path=ROOT/'canonical'/'artwork-card-metadata.json'
    payload=json.loads(path.read_text(encoding='utf-8'))
    by_file={x['file']:x for x in payload['cards']}
    for rec in manifest['entries']:
        if rec['entry']<401 or rec['entry']>1000 or rec['entry']==605: continue
        card=data[rec['card']]
        filename=f'{rec["entry"]:03d}-{slugify(rec["card"])}.html'
        by_file[filename]={
            'file':filename,'articleCard':card['articleName'],'name':card['canonicalName'],'faceName':card['faceName'],
            'setCode':card['setCode'],'setName':card['setName'],'artist':card['artist'],'type':card['type'],
            'types':', '.join(card['types']),'subtypes':', '.join(card['subtypes']),'colors':', '.join(card['colors']),
            'colorIdentity':', '.join(card['colors'])
        }
    payload['cards']=sorted(by_file.values(),key=lambda x:x['file'])
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def write_snapshot(manifest:dict,data:dict[str,dict],related_map:dict[str,list[str]]) -> None:
    out={'generatedOn':str(TODAY),'source':'MTGJSON CSV export downloaded 2026-07-30','entryCount':len(data),'cards':[]}
    entries_by_name={r['card']:r for r in manifest['entries']}
    for name,card in sorted(data.items(),key=lambda kv: entries_by_name.get(kv[0],{}).get('entry',99999)):
        if name not in entries_by_name: continue
        rec=entries_by_name[name]
        out['cards'].append({'entry':rec['entry'],**card,'relatedCards':related_map.get(name,[])})
    d=ROOT/'data'; d.mkdir(exist_ok=True)
    (d/'remaining-entry-card-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main() -> int:
    parser=argparse.ArgumentParser(description="Legacy metadata-only continuation generator (retired by Editorial V2).")
    parser.add_argument("--unsafe-legacy-metadata-generation", action="store_true", help="Explicitly run the retired generic generator. Never use for production.")
    args=parser.parse_args()
    if not args.unsafe_legacy_metadata_generation:
        raise SystemExit(
            "REFUSED: metadata-only generation is retired. Build and validate an Editorial V2 research dossier, "
            "then use the reviewed article workflow. The old generator is retained only for reproducibility."
        )
    manifest=load_manifest(); sets=load_sets(); names={r['card'] for r in manifest['entries']}
    data=build_card_data(names,sets)
    missing=sorted(names-set(data))
    if missing:
        raise SystemExit(f'Missing card data for {len(missing)} names: {missing}')
    entries=manifest['entries']
    related_map={}
    for rec in entries:
        related_map[rec['card']]=choose_related(rec['entry'],data[rec['card']],entries,data)
    template=(ROOT/'400-garruk-wildspeaker.html').read_text(encoding='utf-8')
    all_names=set(data)
    generated=[]
    for rec in entries:
        if rec['entry']<401 or rec['entry']>1000 or rec['entry']==605: continue
        filename=f'{rec["entry"]:03d}-{slugify(rec["card"])}.html'
        text=render_article(template,rec,data[rec['card']],related_map[rec['card']],data,all_names)
        (ROOT/filename).write_text(text,encoding='utf-8')
        generated.append(filename)
        if len(generated)%50==0: print(f'generated {len(generated)} pages; latest {filename}',flush=True)
    update_index(manifest,data)
    update_metadata_file(manifest,data)
    write_snapshot(manifest,data,related_map)
    report={'generated':len(generated),'preserved':['605-grief.html'],'first':generated[0],'last':generated[-1]}
    (ROOT/'audit'/'generation-summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
