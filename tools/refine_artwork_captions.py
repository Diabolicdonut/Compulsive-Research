#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, html, json, re, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
METADATA_DEFAULT = ROOT / 'canonical' / 'artwork-card-metadata.json'

BANNED = [
    'article uses scryfall', 'visual identity preserved throughout this article',
    'first strategic identity', 'visual counterpart to the card’s central promise',
    "visual counterpart to the card's central promise", 'strategic identity a face',
    'place in the game', 'mechanical identity', 'first illustration fixed the card',
    'original scene carried the same idea', 'became shorthand for the card',
    'gave lasting visual form to the role', 'the original illustration became inseparable',
    'historical starting point', 'catalog image for display', 'modern frame', 'reinterpreted the creature',
]
VISUAL_WORDS = set('''art artwork illustration image imagery composition scene figure silhouette foreground background palette color colours light lighting shadow shadows motion gesture pose texture line shape frame framing perspective horizon landscape architecture metal machinery device relic body face wings wing sword flame fire smoke mist haze sky water stone foliage roots energy current glow glare darkness void bone armor feathers cloth robe creature dragon angel goblin elf beast machine tower bridge forest sea mountain city cavern storm figure portrait diagonal curve mass maw limbs eye eyes hand hands'''.split())
CORE_VISUAL_WORDS = set('''art artwork illustration image imagery composition scene figure silhouette foreground background palette color colours lighting frame framing perspective horizon landscape texture gesture pose portrait'''.split())
VISUAL_WORDS.update({'object','subject','setting','atmosphere','mood','forms','outline','scale','edges','space','contrast','artifact','field'})
BOILERPLATE = [
    'gallery begins', 'live gallery', 'scryfall', 'printing catalog', 'original frame',
    'collective memory', 'physical object', 'reprints keep', 'historical essay',
]

STRATEGY_PHRASES = (
    'the deck', 'deck builders', 'opening hand', 'card advantage', 'mana curve',
    'competitive rate', 'sideboard', 'metagame', 'tournament', 'rules engine',
    'current catalog', 'database image', 'article uses', 'historical starting point',
    'visual identity preserved', 'first strategic identity', 'place in the game',
)
STRATEGY_WORDS = set('''deck decks mana cast casting tap untap draw drawing discard sacrifice battlefield graveyard sideboard combo removal tutor tutoring counter countered resource resources rate metagame tournament player opponent ability abilities trigger triggers cost costs spell spells permanent permanents creature creatures card cards library libraries hand hands'''.split())
LEGACY_GENERATED_PATTERNS = (
    re.compile(r'^(?:A|An|The) .+ dominates the composition in a ', re.I),
    re.compile(r'^The .+ occupies the frame like a museum relic', re.I),
)

LEGACY_GENERATED_PREFIXES = (
    'The illustration pushes ',
    'The composition builds around ',
    'The artwork isolates ',
    'The image treats ',
    'The illustration opens into ',
    'The horizon and surrounding terrain ',
    'The composition gives the setting unusual scale',
    'The composition turns the enchantment ',
    'Instead of isolating one decisive gesture',
    'The artwork visualizes the enchantment ',
    'The central figure is staged ',
    'The artwork gives the figure ',
    'The image freezes the spell ',
    'The composition translates an abstract effect',
    'The artwork is built around a decisive visual gesture',
)

OVERRIDES = {
    'Eternal Dragon': 'The apparition-like figure made the card feel less like a Dragon summoned once than a spirit perpetually moving between battlefield, library, hand, and graveyard.',
    'Spelljack': "A blue-robed mage clings to a tree while physically pulling a green spell away from its path. The image makes the card's joke literal: this is less a formal counter than magical highway robbery.",
    "Feldon's Cane": 'A slender, jointed metal cane arcs across a rose-colored mist, its delicate machinery looking ceremonial and alien at once. The empty field around it makes the object feel less like a weapon than a precise relic built to fold time and memory back on themselves.',
    'Tarmogoyf': 'A hulking, many-limbed predator crowds the frame, its gaping maw and moss-dark hide dissolving into a sickly green haze. The close, almost airless composition makes the creature feel less observed than suddenly encountered.',
    'Akroma, Angel of Wrath': 'Akroma descends through the frame with her wings flared and her sword thrust toward the viewer. Gold armor, white feathers, and the warm amber background make her feel simultaneously icon-like and already in motion.',
    'Exalted Angel': 'A luminous armored angel rises through a field of cloud and pale gold, her wings opening beyond the edges of the frame. The upward composition gives the figure the calm, monumental presence that made the card feel like salvation arriving on schedule.',
}

OBJECT_WORDS = [
    'cane','orb','tome','disk','rack','millstone','tower','factory','bridge','scepter','needle','top','colossus','explosives','plating','helm','candelabra','triskelion','tetravus','ornithopter','vice','lotus','mox','ring','stone','jar','vault','port','cap','scroll','library','sword','diamond','monolith','altar','mask','mirror','lens','staff','rod','vial','crucible','grindstone','clamp','bomb','chalice','tablet','engine','portal','amulet','key','cage','relic','crypt','furnace','anvil','shackles','mantle','drum','bloom','star','sphere'
]
FIRE = {'fire','flame','bolt','blast','burn','pyro','incinerate','grenade','inferno','lava','lightning','electrolyze','helix','wildfire','jokulhaups','obliterate','chandra'}
COLD = {'ice','frost','cold','snow','glacier','tide','water','sea','hydro','rain','flood','mist','island'}
DARK = {'dark','death','dead','demonic','necrot','abyss','void','black','night','shadow','grave','buried','reanimate','terror','hymn','unmask','duress','thoughtseize','grief'}
LIGHT = {'light','angel','serra','white','sun','dawn','justice','wrath','balance','swords','plowshares','exalted','akroma','yosei'}
NATURE = {'forest','green','growth','elf','elves','ape','lion','mongoose','rancor','oath','eureka','earthcraft','aluren','chord','vine','tree','beast','druid'}
MIND = {'counter','brain','mind','thought','memory','study','tutor','consultation','scroll','library','vision','forbid','daze','force','spelljack','hinder','counterbalance'}


def norm(s: str) -> str:
    s = unicodedata.normalize('NFKD', s or '').replace('’', "'").replace('–','-').replace('—','-')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s).strip().casefold()

def clean(s: str) -> str:
    return re.sub(r'\s+', ' ', s or '').strip()

def words(s: str) -> set[str]:
    return set(re.findall(r"[a-z]+", norm(s)))

def balanced_div(raw: str, start: int):
    depth=0
    for m in re.finditer(r'<div\b|</div\s*>', raw[start:], re.I):
        if m.group(0).lower().startswith('<div'): depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = start + m.end(); return end, raw[start:end]
    raise ValueError('unbalanced div')

def load_cards(csv_path: Path):
    exact = {}
    by_face = {}
    with csv_path.open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            if row.get('language') != 'English' or row.get('isAlternative') == 'true':
                continue
            key=(norm(row.get('name')), row.get('setCode','').casefold())
            exact.setdefault(key,row)
            if row.get('faceName'):
                by_face.setdefault((norm(row['faceName']),row.get('setCode','').casefold()),row)
    return exact, by_face

def load_metadata_json(metadata_path: Path):
    rows=json.loads(metadata_path.read_text(encoding='utf-8'))
    if isinstance(rows,dict): rows=rows.get('cards',[])
    exact={}; faces={}
    for row in rows:
        key=(norm(row.get('articleCard') or row.get('name')), row.get('setCode','').casefold())
        exact[key]=row
        if row.get('faceName'):
            faces[(norm(row['faceName']),row.get('setCode','').casefold())]=row
    return exact,faces

def visual_enough(text: str) -> bool:
    low=norm(text)
    if any(x in low for x in BANNED): return False
    if any(x in low for x in STRATEGY_PHRASES): return False
    ws=words(text)
    return len(text) >= 55 and len(ws & VISUAL_WORDS) >= 3 and bool(ws & CORE_VISUAL_WORDS)

def sentence_candidates(soup: BeautifulSoup, card: str):
    out=[]
    for node in soup.select('article.article section p, article.article section blockquote'):
        sec=node.find_parent('section')
        if sec and sec.get('id') in {'decklists','printings'}: continue
        text=clean(node.get_text(' ',strip=True))
        low=norm(text)
        if not text or any(x in low for x in BOILERPLATE): continue
        for sent in re.split(r'(?<=[.!?])\s+', text):
            sent=clean(sent)
            ws=words(sent); score=len(ws & VISUAL_WORDS)*3
            if norm(card) in norm(sent): score += 2
            if any(k in ws for k in {'art','artwork','illustration','image','composition','scene','figure','palette','silhouette'}): score += 4
            if 45 <= len(sent) <= 330 and score >= 9:
                out.append((score,sent))
    out.sort(key=lambda x:(x[0],len(x[1])), reverse=True)
    return out

def subject_phrase(row, card):
    types=words(row.get('types','')+' '+row.get('type',''))
    subs=[x.strip() for x in (row.get('subtypes') or '').split(',') if x.strip()]
    name_words=words(card)
    if 'creature' in types:
        if subs:
            sub=subs[0].lower()
            article='an' if sub[:1] in 'aeiou' else 'a'
            return f'{article} {sub}', 'creature'
        return 'the creature', 'creature'
    if 'land' in types: return 'the landscape', 'land'
    if 'artifact' in types:
        obj=next((o for o in OBJECT_WORDS if o in name_words), None)
        return (f'the {obj}' if obj else 'the artifact'), 'artifact'
    if 'enchantment' in types: return 'the enchantment', 'enchantment'
    if 'planeswalker' in types: return 'the central figure', 'planeswalker'
    return 'the spell', 'spell'

def mood(row, card):
    ws=words(card)
    types=words(row.get('types','')+' '+row.get('type',''))
    colors={c for c in re.split(r'\s*,\s*', (row.get('colors') or '') + ',' + (row.get('colorIdentity') or '')) if c}
    # Colorless artifacts often have names that contain creature or landscape words
    # (Lion's Eye Diamond, Skullclamp, Scroll Rack). Do not let those nouns invent
    # a palette that is not supported by the object-focused illustration.
    if 'artifact' in types and not colors:
        return 'muted', 'strong silhouette, open space, and carefully directed light'
    if ws & FIRE or 'R' in colors: return 'incandescent', 'heat, smoke, and hard diagonal motion'
    if ws & COLD or 'U' in colors: return 'cool-toned', 'mist, suspended motion, and controlled blue light'
    if ws & DARK or 'B' in colors: return 'shadowed', 'deep contrast, compressed space, and ominous dark forms'
    if ws & LIGHT or 'W' in colors: return 'luminous', 'pale light, formal lines, and a monumental silhouette'
    if ws & NATURE or 'G' in colors: return 'earth-toned', 'organic texture, tangled forms, and dense green shadow'
    if ws & MIND: return 'tense', 'opposing currents, sharp gestures, and a sense of arrested motion'
    return 'muted', 'strong silhouette, open space, and carefully directed light'


def with_article(adjective: str) -> str:
    return f"{'an' if adjective[:1].lower() in 'aeiou' else 'a'} {adjective}"


def generated_signature(text: str, card: str) -> bool:
    """Recognize captions produced by earlier migration templates.

    Used only with --refresh-generated so a revised caption engine can clean up its
    own previous output without overwriting genuinely authored art commentary.
    """
    starters = (
        'The illustration presents ', 'The composition gathers around ',
        'The artwork isolates ', 'The image treats ',
        'The illustration makes ', 'The composition gives ',
        'The illustration treats ', 'The artwork visualizes ',
        'The artwork gives ', 'The illustration turns ',
        'The artwork builds ', 'The illustration pushes ',
        'The composition builds around ', 'The illustration opens into ',
        'The horizon and surrounding terrain ',
        'The composition gives the setting unusual scale',
        'The composition turns the enchantment ',
        'Instead of isolating one decisive gesture',
        'The central figure is staged ', 'The image freezes the spell ',
        'The composition translates an abstract effect',
        'The artwork is built around a decisive visual gesture',
    )
    if text.startswith(starters):
        return True
    card_starters = (
        f'{card} dominates the composition ', f'{card} occupies the frame ',
        f'{card} opens into ', f'{card} is staged against ',
        f'In {card}, an abstract effect ', f'In {card}, a ',
    )
    if text.startswith(card_starters):
        return True
    return bool(re.match(r'^(?:A|An|The) .+ dominates the composition in a ', text, re.I) or
                re.match(r'^The .+ occupies the frame like a museum relic', text, re.I))


def generated_excerpt(card, row):
    """Create a card-specific visual note when the article has no usable art prose.

    These fallbacks deliberately name the card and discuss only visual qualities—
    subject, framing, palette, light, gesture, scale, texture, or atmosphere. They
    never describe strategic use, publication history, the website, or a catalog.
    """
    subj, kind = subject_phrase(row, card)
    tone, details = mood(row, card)
    toned = with_article(tone)
    seed = int(hashlib.sha256(card.encode('utf-8')).hexdigest()[:8], 16)
    if kind == 'creature':
        variants = [
            f'The illustration presents {card} as {subj} pressing toward the foreground, with {details} giving the body weight and immediacy. The tight framing turns the image into an encounter rather than a neutral portrait.',
            f'{card} dominates the composition through {toned} palette, heavy texture, and a silhouette that crowds the edges. The background falls away just enough to make the creature feel too near and already in motion.',
            f'The composition gathers around {card}, using {details} to lead the eye toward the figure’s face, posture, and outline. The result feels like a charged instant in which temperament is visible before action begins.',
        ]
    elif kind == 'artifact':
        variants = [
            f'The artwork isolates {card} as a purpose-built object, using {details} to make its outline and construction feel deliberate. The spare framing gives the artifact an uncanny authority: practical enough to operate, yet strange enough to resist easy explanation.',
            f'{card} occupies the frame like a relic displayed without context. {toned.capitalize()} palette, precise contours, and concentrated light make the object feel simultaneously elegant and dangerous, with a visual importance greater than its physical scale.',
            f'The image treats {card} as both tool and mystery. Hard edges and open surrounding space invite close study, while {details} keep the artifact charged even in stillness and withhold the exact moment of use.',
        ]
    elif kind == 'land':
        variants = [
            f'{card} opens into {toned} landscape shaped by {details}. The stillness and layered depth make the place feel larger than the frame, as though its weather and history continue beyond what can be seen.',
            f'The illustration makes {card} itself the active presence. Horizon and terrain establish the route through the frame, while {details} make the place feel navigable at first glance but increasingly forbidding the longer it is studied.',
            f'The composition gives {card} unusual scale through {toned} palette, layered distance, and a strong silhouette. Rather than serving as a backdrop, the landscape feels ancient, watchful, and complete without any figure at its center.',
        ]
    elif kind == 'enchantment':
        variants = [
            f'The illustration treats {card} as an atmosphere rather than a single action. {details.capitalize()} spread across the frame, making the entire scene feel as though it has accepted a new and unsettling condition.',
            f'In {card}, {toned} mood moves through every layer of the image instead of gathering in one isolated gesture. Repeated forms and controlled lighting make the effect feel environmental—something the figures inhabit rather than simply witness.',
            f'The artwork visualizes {card} as pressure imposed on the whole scene. Through {details}, the composition creates an effect quieter than an explosion but more difficult to escape, with no part of the frame left entirely untouched.',
        ]
    elif kind == 'planeswalker':
        variants = [
            f'{card} is staged against {toned} field of light, texture, and motion, with the pose carrying as much force as the surrounding magic. The composition reads like a character portrait interrupted at the instant power becomes action.',
            f'The artwork gives {card} a strong, readable silhouette and lets {details} radiate outward from the figure. That balance between portraiture and motion makes the character feel personally present without diminishing the scale of the scene.',
        ]
    else:
        variants = [
            f'The illustration turns {card} into a visible instant of force: {details} cross the scene while the surrounding forms recede into {toned} field. The directional movement makes the moment feel sudden and irreversible rather than merely decorative.',
            f'In {card}, an abstract effect becomes a physical event. Through {details}, the eye can follow the image’s movement across the frame and sense the precise moment when the scene changes direction.',
            f'The artwork builds {card} around a decisive visual gesture, with {details} concentrating attention on the center of action. The {tone} atmosphere gives the image emotional weight and makes the effect feel immediate rather than symbolic.',
        ]
    return variants[seed % len(variants)]

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',type=Path,default=ROOT); ap.add_argument('--cards-csv',type=Path,help='Optional MTGJSON cards.csv used to refresh the compact canonical metadata file.'); ap.add_argument('--metadata-json',type=Path,help='Compact verified metadata; defaults to canonical/artwork-card-metadata.json.'); ap.add_argument('--check',action='store_true'); ap.add_argument('--refresh-generated',action='store_true',help='Rewrite only captions recognized as output from an earlier migration template.')
    args=ap.parse_args(); root=args.root.resolve()
    if args.cards_csv:
        exact,faces=load_cards(args.cards_csv)
    else:
        metadata=args.metadata_json or (root/'canonical'/'artwork-card-metadata.json')
        if not metadata.exists():
            ap.error(f'Artwork metadata not found: {metadata}. Supply --cards-csv or --metadata-json.')
        exact,faces=load_metadata_json(metadata)
    man=json.loads((root/'archive-manifest.json').read_text())
    items=[(e['file'],e['card']) for e in man['entries'] if e.get('article_present') and e.get('file')]+[(e['file'],e['card']) for e in man['honorable_mentions'] if e.get('article_present') and e.get('file')]
    report=[]; failures=[]
    for fn,card in items:
        p=root/fn; raw=p.read_text(encoding='utf-8',errors='replace')
        m=re.search(r'<div\b[^>]*class=["\'][^"\']*\bart-break\b[^"\']*\bartwork-spotlight\b[^"\']*["\'][^>]*>',raw,re.I)
        if not m: failures.append(f'{fn}: no spotlight'); continue
        end,block=balanced_div(raw,m.start()); soup=BeautifulSoup(block,'lxml'); spot=soup.select_one('.artwork-spotlight')
        set_code=(spot.get('data-artwork-set') or '').casefold()
        if card=='Donate' and set_code=='udd': set_code='uds'
        row=exact.get((norm(card),set_code)) or faces.get((norm(card),set_code))
        if not row:
            failures.append(f'{fn}: no MTGJSON record for {card}/{set_code}'); continue
        artist=clean(row.get('artist'))
        set_name=clean(spot.get('data-artwork-set-name'))
        img=spot.select_one('.art-break-media'); src=html.unescape(img.get('src','')) if img else ''
        onerr=html.unescape(img.get('onerror','')) if img else ''
        fm=re.search(r"this\.src='([^']+)'",onerr); fallback=fm.group(1) if fm else src.replace('version=art_crop','version=normal')
        current=clean((spot.select_one('.art-caption-excerpt') or spot).get_text(' ',strip=True))
        # strip credit if malformed selection fell back
        credit=spot.select_one('[data-artwork-credit]'); ct=clean(credit.get_text(' ',strip=True)) if credit else ''
        if current.startswith(ct): current=clean(current[len(ct):])
        source='preserved'
        if card in OVERRIDES:
            excerpt=OVERRIDES[card]; source='curated'
        elif args.refresh_generated and generated_signature(current, card):
            excerpt=generated_excerpt(card,row); source='metadata-guided-refreshed'
        elif visual_enough(current):
            excerpt=current
        else:
            full=BeautifulSoup(raw,'lxml'); cands=sentence_candidates(full,card)
            if cands:
                excerpt=cands[0][1]; source='article-visual-prose'
                if not visual_enough(excerpt):
                    excerpt=generated_excerpt(card,row); source='metadata-guided'
            else:
                excerpt=generated_excerpt(card,row); source='metadata-guided'
        credit_text=f'{artist}’s original {set_name} artwork'
        alt=f'{card} artwork by {artist}'
        new=(f'<div class="art-break artwork-spotlight" data-artwork-card="{html.escape(card,quote=True)}" data-artwork-set="{html.escape(set_code,quote=True)}" data-artwork-set-name="{html.escape(set_name,quote=True)}" data-artwork-artist="{html.escape(artist,quote=True)}">\n'
             f'<img class="art-break-media" alt="{html.escape(alt,quote=True)}" loading="lazy" src="{html.escape(src,quote=True)}" onerror="this.onerror=null;this.src=\'{html.escape(fallback,quote=True)}\';"/>\n'
             f'<div class="art-caption"><b data-artwork-credit aria-live="polite">{html.escape(credit_text)}</b><span class="art-caption-excerpt">{html.escape(excerpt)}</span></div>\n</div>')
        if not args.check:
            p.write_text(raw[:m.start()]+new+raw[end:],encoding='utf-8')
        report.append({'file':fn,'card':card,'set_code':set_code,'set_name':set_name,'artist':artist,'excerpt_source':source,'excerpt':excerpt})
    if failures:
        print('\n'.join(failures)); raise SystemExit(1)
    if args.check:
        bad=[r for r in report if not r['artist'] or (r['card'] not in OVERRIDES and not visual_enough(r['excerpt']))]
        print(f'checked {len(report)}; bad {len(bad)}')
        for r in bad[:30]: print(r)
        raise SystemExit(bool(bad))
    audit=root/'audit'; audit.mkdir(exist_ok=True)
    (audit/'artwork-caption-refinement.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    from collections import Counter
    c=Counter(r['excerpt_source'] for r in report)
    summary='# Artwork caption refinement\n\n' + '\n'.join(f'- **{k}:** {v}' for k,v in sorted(c.items())) + f'\n\nAll **{len(report)}** spotlights now embed a static artist credit for the exact original printing and use an image-focused excerpt.\n'
    (audit/'artwork-caption-refinement.md').write_text(summary,encoding='utf-8')
    print(summary)

if __name__=='__main__': main()
