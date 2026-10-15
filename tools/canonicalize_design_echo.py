#!/usr/bin/env python3
"""Enforce the Eternal Dragon Design Echo component across the archive.

The component is self-contained: every article carries the canonical CSS and
an inline, queued image resolver so downloaded/standalone HTML files do not
rely on a neighboring asset file.  The shared asset contains the same runtime
for the hosted site.
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import sys
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
CSS_MARKER_START = "/* CR_CANONICAL_DESIGN_ECHO_START */"
CSS_MARKER_END = "/* CR_CANONICAL_DESIGN_ECHO_END */"
RUNTIME_MARKER_START = "/* CR_DESIGN_ECHO_RUNTIME_START */"
RUNTIME_MARKER_END = "/* CR_DESIGN_ECHO_RUNTIME_END */"
RUNTIME_SCRIPT_ID = "cr-design-echo-runtime"
EXTERNAL_SCRIPT = '<script defer src="assets/design-echo.js"></script>'
PLACEHOLDER = "data:image/gif;base64,R0lGODlhAQABAAAAACw="

CSS_BLOCK = r'''/* CR_CANONICAL_DESIGN_ECHO_START */
/* Eternal Dragon is the structural and responsive authority for every
   Design Echo image-plus-copy panel. */
.design-echo-section>.inline-image.canonical-inline-image,
.inline-image.canonical-inline-image{
  box-sizing:border-box!important;
  width:min(980px,calc(100vw - 32px))!important;
  max-width:none!important;
  margin:42px 0 48px calc((var(--reading) - min(980px,calc(100vw - 32px)))/2)!important;
  padding:0!important;
  display:grid!important;
  grid-template-columns:minmax(0,1.4fr) minmax(0,1fr)!important;
  gap:0!important;
  align-items:stretch!important;
  background:transparent!important;
  color:white!important;
  overflow:hidden!important;
  border:0!important;
  border-radius:var(--radius)!important;
  box-shadow:none!important;
  outline:0!important;
}
.inline-image.canonical-inline-image>.image{
  box-sizing:border-box!important;
  position:relative!important;
  width:100%!important;
  max-width:none!important;
  min-width:0!important;
  min-height:390px!important;
  margin:0!important;
  padding:0!important;
  overflow:hidden!important;
  background:var(--night2)!important;
  border:0!important;
  border-radius:var(--radius) 0 0 var(--radius)!important;
  box-shadow:none!important;
  transform:none!important;
}
.inline-image.canonical-inline-image>.image:before{
  position:absolute!important;
  inset:0!important;
  z-index:0!important;
  display:grid!important;
  place-items:center!important;
  box-sizing:border-box!important;
  padding:28px!important;
  color:#c7cfca!important;
  text-align:center!important;
  font:800 .82rem/1.5 Inter,system-ui,sans-serif!important;
  letter-spacing:.04em!important;
  pointer-events:none!important;
}
.inline-image.canonical-inline-image>.image.image-loading:before{
  content:"Loading " attr(data-card-label) " artwork…"!important;
}
.inline-image.canonical-inline-image>.image.image-failed:before{
  content:attr(data-card-label) " artwork could not be loaded"!important;
}
.inline-image.canonical-inline-image>.image.image-loaded:before{content:""!important}
.inline-image.canonical-inline-image .inline-image-media{
  box-sizing:border-box!important;
  position:absolute!important;
  inset:0!important;
  z-index:1!important;
  display:block!important;
  width:100%!important;
  height:100%!important;
  max-width:none!important;
  max-height:none!important;
  margin:0!important;
  padding:0!important;
  object-fit:cover!important;
  object-position:center!important;
  opacity:0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
  transform:none!important;
  transition:opacity .18s ease!important;
}
.inline-image.canonical-inline-image>.image.image-loaded .inline-image-media{
  display:block!important;
  opacity:1!important;
}
.inline-image.canonical-inline-image>.image.image-failed .inline-image-media{
  display:none!important;
  opacity:0!important;
}
.inline-image.canonical-inline-image>.copy{
  box-sizing:border-box!important;
  width:100%!important;
  max-width:none!important;
  min-width:0!important;
  margin:0!important;
  padding:35px!important;
  align-self:stretch!important;
  background:#20322f!important;
  color:white!important;
  border:1px solid #586963!important;
  border-left:0!important;
  border-radius:0 var(--radius) var(--radius) 0!important;
  box-shadow:none!important;
  transform:none!important;
}
.inline-image.canonical-inline-image>.copy .eyebrow,
.inline-image.canonical-inline-image>.copy .kicker{
  display:block!important;
  margin:0 0 12px!important;
  color:#d8b878!important;
  text-transform:uppercase!important;
  letter-spacing:.18em!important;
  font:900 .73rem/1.35 Inter,system-ui,sans-serif!important;
}
.inline-image.canonical-inline-image>.copy h3{
  margin:0 0 16px!important;
  color:white!important;
  font-size:2rem!important;
  line-height:1.12!important;
}
.inline-image.canonical-inline-image>.copy p{
  margin:0 0 1em!important;
  color:#d8d9d4!important;
}
.inline-image.canonical-inline-image>.copy p:last-child{margin-bottom:0!important}
@media(max-width:750px){
  .design-echo-section>.inline-image.canonical-inline-image,
  .inline-image.canonical-inline-image{
    width:100%!important;
    max-width:100%!important;
    margin:42px 0 48px!important;
    padding:0!important;
    grid-template-columns:minmax(0,1fr)!important;
    gap:0!important;
    background:transparent!important;
    border:0!important;
    box-shadow:none!important;
  }
  .inline-image.canonical-inline-image>.image{
    width:100%!important;
    min-height:390px!important;
    margin:0!important;
    border-radius:var(--radius) var(--radius) 0 0!important;
  }
  .inline-image.canonical-inline-image>.copy{
    width:100%!important;
    margin:0!important;
    padding:35px!important;
    border:1px solid #586963!important;
    border-top:0!important;
    border-radius:0 0 var(--radius) var(--radius)!important;
  }
}
/* CR_CANONICAL_DESIGN_ECHO_END */'''

RUNTIME_JS = r'''/* CR_DESIGN_ECHO_RUNTIME_START */
(function(){
  "use strict";
  if(window.__CR_DESIGN_ECHO_RUNTIME__){
    window.__CR_DESIGN_ECHO_RUNTIME__.scan(document);
    return;
  }

  var queue=[];
  var working=false;
  var observer=null;
  var CACHE_PREFIX="cr-design-echo:v2:";

  function delay(ms){return new Promise(function(resolve){setTimeout(resolve,ms);});}
  function cacheKey(img){return CACHE_PREFIX+(img.dataset.cardName||"").toLowerCase()+"|"+(img.dataset.cardSet||"").toLowerCase();}
  function readCache(img){
    try{
      var raw=localStorage.getItem(cacheKey(img));
      if(!raw)return null;
      var data=JSON.parse(raw);
      return data&&data.art?data:null;
    }catch(_){return null;}
  }
  function writeCache(img,data){
    if(!data||!data.art)return;
    try{localStorage.setItem(cacheKey(img),JSON.stringify(data));}catch(_){}
  }
  function imageUris(card){
    var uris=card&&card.image_uris;
    if(!uris&&card&&card.card_faces){
      for(var i=0;i<card.card_faces.length;i++){
        if(card.card_faces[i]&&card.card_faces[i].image_uris){uris=card.card_faces[i].image_uris;break;}
      }
    }
    if(!uris)return null;
    return {art:uris.art_crop||uris.large||uris.normal||"",normal:uris.normal||uris.large||uris.art_crop||""};
  }
  function setState(img,state){
    var well=img.parentElement;
    if(!well)return;
    well.classList.remove("image-loading","image-loaded","image-failed");
    well.classList.add("image-"+state);
    if(state==="failed"){
      img.style.setProperty("display","none","important");
      img.style.setProperty("opacity","0","important");
    }else{
      img.style.removeProperty("display");
    }
  }
  function loadUrl(img,url){
    return new Promise(function(resolve){
      if(!url){resolve(false);return;}
      var settled=false;
      function finish(ok){
        if(settled)return;
        settled=true;
        img.onload=null;
        img.onerror=null;
        resolve(ok);
      }
      img.onload=function(){finish(true);};
      img.onerror=function(){finish(false);};
      img.src=url;
      if(img.complete&&img.naturalWidth>0)finish(true);
    });
  }
  async function fetchCard(img){
    var api=img.dataset.apiUrl;
    if(!api)return null;
    for(var attempt=0;attempt<3;attempt++){
      try{
        var response=await fetch(api,{mode:"cors",credentials:"omit",cache:"force-cache"});
        if(response.ok)return imageUris(await response.json());
        if(response.status!==429&&response.status<500)return null;
      }catch(_){}
      await delay(500*Math.pow(2,attempt));
    }
    return null;
  }
  async function resolveImage(img){
    if(img.dataset.crResolved==="1")return;
    img.dataset.crResolved="1";
    setState(img,"loading");

    var candidates=[];
    function add(url){if(url&&candidates.indexOf(url)===-1)candidates.push(url);}
    add(img.dataset.directArt);
    add(img.dataset.directNormal);

    var cached=readCache(img);
    if(cached){add(cached.art);add(cached.normal);}

    var resolved=await fetchCard(img);
    if(resolved){
      writeCache(img,resolved);
      add(resolved.art);
      add(resolved.normal);
    }

    /* Independent last-resort paths.  They are attempted sequentially only
       after the JSON resolver/direct CDN path fails, never in a page-load burst. */
    add(img.dataset.fallbackArt);
    add(img.dataset.fallbackNormal);
    add(img.dataset.fallbackFuzzy);

    for(var i=0;i<candidates.length;i++){
      if(await loadUrl(img,candidates[i])){
        setState(img,"loaded");
        img.classList.add("image-loaded");
        return;
      }
    }
    setState(img,"failed");
  }
  async function pump(){
    if(working)return;
    working=true;
    while(queue.length){
      await resolveImage(queue.shift());
      await delay(175);
    }
    working=false;
  }
  function enqueue(img){
    if(!img||img.dataset.crQueued==="1"||img.dataset.crResolved==="1")return;
    img.dataset.crQueued="1";
    queue.push(img);
    pump();
  }
  function observe(img){
    if(!("IntersectionObserver" in window)){enqueue(img);return;}
    if(!observer){
      observer=new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){observer.unobserve(entry.target);enqueue(entry.target);}
        });
      },{rootMargin:"900px 0px"});
    }
    observer.observe(img);
  }
  function scan(root){
    (root||document).querySelectorAll(".inline-image.canonical-inline-image .inline-image-media[data-card-name]").forEach(function(img){
      var well=img.parentElement;
      if(well&&!well.classList.contains("image-loaded")&&!well.classList.contains("image-failed"))well.classList.add("image-loading");
      observe(img);
    });
  }

  window.__CR_DESIGN_ECHO_RUNTIME__={scan:scan,enqueue:enqueue};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){scan(document);},{once:true});
  else scan(document);
})();
/* CR_DESIGN_ECHO_RUNTIME_END */'''


def article_files() -> list[Path]:
    return sorted(p for p in ROOT.glob("*.html") if p.name != "index.html")


def direct_child(node: Tag, class_name: str) -> Tag | None:
    for child in node.children:
        if isinstance(child, Tag) and class_name in (child.get("class") or []):
            return child
    return None


def find_inline_blocks(raw: str) -> list[tuple[int, int]]:
    opening = re.compile(r"<div\b[^>]*\bclass=(?:\"[^\"]*\binline-image\b[^\"]*\"|'[^']*\binline-image\b[^']*')[^>]*>", re.I)
    token = re.compile(r"</?div\b[^>]*>", re.I)
    blocks: list[tuple[int, int]] = []
    for match in opening.finditer(raw):
        if any(start <= match.start() < end for start, end in blocks):
            continue
        depth = 1
        for div in token.finditer(raw, match.end()):
            if div.group(0).lower().startswith("</div"):
                depth -= 1
            else:
                depth += 1
            if depth == 0:
                blocks.append((match.start(), div.end()))
                break
        else:
            raise ValueError(f"Unclosed inline-image block at character {match.start()}")
    return blocks


def api_urls(card: str, existing_src: str = "", set_override: str = "") -> tuple[str, str, str, str, str]:
    parsed = urllib.parse.urlparse(html_lib.unescape(existing_src or ""))
    params = urllib.parse.parse_qs(parsed.query)
    set_code = set_override or (params.get("set") or [""])[0]
    query = [("exact", card)]
    if set_code:
        query.append(("set", set_code))
    json_url = "https://api.scryfall.com/cards/named?" + urllib.parse.urlencode(query)
    art_url = json_url + "&format=image&version=art_crop"
    normal_url = json_url + "&format=image&version=normal"
    fuzzy_url = "https://api.scryfall.com/cards/named?" + urllib.parse.urlencode({"fuzzy": card}) + "&format=image&version=art_crop"
    return json_url, art_url, normal_url, fuzzy_url, set_code


def build_panel(panel: Tag) -> str:
    card = str(panel.get("data-image-card") or "").strip()
    if not card:
        raise ValueError("canonical panel has no data-image-card")
    copy = direct_child(panel, "copy") or panel.find(class_="copy")
    if copy is None:
        raise ValueError(f"{card}: canonical panel has no direct .copy")
    old_img = panel.select_one(".inline-image-media")
    existing_src = str(old_img.get("src") or "") if old_img else ""
    set_override = str(old_img.get("data-card-set") or "") if old_img else ""
    if not set_override and old_img:
        old_api = str(old_img.get("data-api-url") or "")
        old_params = urllib.parse.parse_qs(urllib.parse.urlparse(html_lib.unescape(old_api)).query)
        set_override = (old_params.get("set") or [""])[0]
    json_url, art_url, normal_url, fuzzy_url, set_code = api_urls(card, existing_src, set_override)
    direct_art = existing_src if existing_src.startswith("https://cards.scryfall.io/") else ""
    direct_normal = ""
    if old_img:
        old_normal = str(old_img.get("data-direct-normal") or "")
        if old_normal.startswith("https://cards.scryfall.io/"):
            direct_normal = old_normal
    attrs = [
        f'class="inline-image-media"',
        f'alt="{html_lib.escape(card, quote=True)} artwork"',
        'decoding="async"',
        'referrerpolicy="no-referrer"',
        f'src="{PLACEHOLDER}"',
        f'data-card-name="{html_lib.escape(card, quote=True)}"',
        f'data-api-url="{html_lib.escape(json_url, quote=True)}"',
        f'data-fallback-art="{html_lib.escape(art_url, quote=True)}"',
        f'data-fallback-normal="{html_lib.escape(normal_url, quote=True)}"',
        f'data-fallback-fuzzy="{html_lib.escape(fuzzy_url, quote=True)}"',
    ]
    if set_code:
        attrs.append(f'data-card-set="{html_lib.escape(set_code, quote=True)}"')
    if direct_art:
        attrs.append(f'data-direct-art="{html_lib.escape(direct_art, quote=True)}"')
    if direct_normal:
        attrs.append(f'data-direct-normal="{html_lib.escape(direct_normal, quote=True)}"')
    return f'''<div class="inline-image canonical-inline-image" data-image-card="{html_lib.escape(card, quote=True)}">
<div class="image image-loading" data-card-label="{html_lib.escape(card, quote=True)}">
<img {' '.join(attrs)}>
</div>
{str(copy)}
</div>'''


def install_css(raw: str) -> str:
    marker = re.compile(re.escape(CSS_MARKER_START) + r".*?" + re.escape(CSS_MARKER_END), re.S)
    if marker.search(raw):
        return marker.sub(lambda _: CSS_BLOCK, raw)
    pos = raw.lower().rfind("</style>")
    if pos >= 0:
        return raw[:pos] + "\n\n" + CSS_BLOCK + "\n" + raw[pos:]
    head = raw.lower().find("</head>")
    if head < 0:
        raise ValueError("No </head> in article")
    return raw[:head] + "<style>\n" + CSS_BLOCK + "\n</style>\n" + raw[head:]


def install_inline_runtime(raw: str) -> str:
    script_pattern = re.compile(rf'<script\b[^>]*\bid=["\']{re.escape(RUNTIME_SCRIPT_ID)}["\'][^>]*>.*?</script>', re.S | re.I)
    block = f'<script id="{RUNTIME_SCRIPT_ID}">\n{RUNTIME_JS}\n</script>'
    if script_pattern.search(raw):
        return script_pattern.sub(lambda _: block, raw)
    # Place before the optional shared script so standalone files are complete.
    external_pos = raw.find(EXTERNAL_SCRIPT)
    if external_pos >= 0:
        return raw[:external_pos] + block + "\n" + raw[external_pos:]
    body = raw.lower().rfind("</body>")
    if body < 0:
        raise ValueError("No </body> in article")
    return raw[:body] + block + "\n" + EXTERNAL_SCRIPT + "\n" + raw[body:]


def migrate_file(path: Path, check: bool) -> dict:
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    panels = soup.select(".inline-image")
    blocks = find_inline_blocks(raw)
    if len(panels) != len(blocks):
        raise ValueError(f"{path.name}: parsed {len(panels)} panels but located {len(blocks)} raw blocks")
    updated = raw
    for panel, (start, end) in reversed(list(zip(panels, blocks))):
        updated = updated[:start] + build_panel(panel) + updated[end:]
    updated = install_css(updated)
    updated = install_inline_runtime(updated)
    changed = updated != raw
    if changed and not check:
        path.write_text(updated, encoding="utf-8")
    return {"file": path.name, "panels": len(panels), "changed": changed}


def update_shared_assets() -> None:
    (ROOT / "assets" / "design-echo.js").write_text(RUNTIME_JS + "\n", encoding="utf-8")
    for name in ("compulsive-research.css", "canonical-eternal-dragon.css"):
        path = ROOT / "assets" / name
        raw = path.read_text(encoding="utf-8") if path.exists() else ""
        marker = re.compile(re.escape(CSS_MARKER_START) + r".*?" + re.escape(CSS_MARKER_END), re.S)
        raw = marker.sub(lambda _: CSS_BLOCK, raw) if marker.search(raw) else raw.rstrip() + "\n\n" + CSS_BLOCK + "\n"
        path.write_text(raw, encoding="utf-8")


def update_template() -> None:
    path = ROOT / "templates" / "article-shell.html"
    raw = path.read_text(encoding="utf-8")
    # Replace the canonical image well, keeping the content placeholders.
    pattern = re.compile(
        r'<div class="inline-image canonical-inline-image" data-image-card="\{\{DESIGN_ECHO_CARD_NAME\}\}">.*?</div>\s*\{\{DESIGN_ECHO_CLOSING_HTML\}\}',
        re.S,
    )
    replacement = '''<div class="inline-image canonical-inline-image" data-image-card="{{DESIGN_ECHO_CARD_NAME}}">
        <div class="image image-loading" data-card-label="{{DESIGN_ECHO_CARD_NAME}}">
          <img class="inline-image-media"
               alt="{{DESIGN_ECHO_CARD_NAME}} artwork"
               decoding="async" referrerpolicy="no-referrer"
               src="data:image/gif;base64,R0lGODlhAQABAAAAACw="
               data-card-name="{{DESIGN_ECHO_CARD_NAME}}"
               data-api-url="{{DESIGN_ECHO_API_URL}}"
               data-fallback-art="{{DESIGN_ECHO_FALLBACK_ART_URL}}"
               data-fallback-normal="{{DESIGN_ECHO_FALLBACK_NORMAL_URL}}"
               data-fallback-fuzzy="{{DESIGN_ECHO_FALLBACK_FUZZY_URL}}">
        </div>
        <div class="copy">
          <div class="eyebrow">{{DESIGN_ECHO_SET_LABEL}}</div>
          <h3>{{DESIGN_ECHO_PANEL_TITLE}}</h3>
          {{DESIGN_ECHO_PANEL_HTML}}
        </div>
      </div>
      {{DESIGN_ECHO_CLOSING_HTML}}'''
    if pattern.search(raw):
        raw = pattern.sub(lambda _: replacement, raw)
    else:
        raise ValueError("Canonical Design Echo template block not found")
    # Keep a self-contained runtime in generated standalone files.
    runtime_block = f'<script id="{RUNTIME_SCRIPT_ID}">\n{RUNTIME_JS}\n</script>'
    if f'id="{RUNTIME_SCRIPT_ID}"' not in raw:
        if EXTERNAL_SCRIPT in raw:
            raw = raw.replace(EXTERNAL_SCRIPT, runtime_block + "\n" + EXTERNAL_SCRIPT)
        else:
            raw = raw.replace("</body>", runtime_block + "\n" + EXTERNAL_SCRIPT + "\n</body>")
    path.write_text(raw, encoding="utf-8")


def update_schema() -> None:
    path = ROOT / "templates" / "article-content.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    echo = data["properties"]["designEcho"]
    required = echo["required"]
    for old in ("imageUrl",):
        if old in required:
            required.remove(old)
    if "apiUrl" not in required:
        insert_at = required.index("fallbackNormalUrl") if "fallbackNormalUrl" in required else len(required)
        required.insert(insert_at, "apiUrl")
    if "fallbackArtUrl" not in required:
        insert_at = required.index("fallbackNormalUrl") if "fallbackNormalUrl" in required else len(required)
        required.insert(insert_at, "fallbackArtUrl")
    props = echo["properties"]
    props.pop("imageUrl", None)
    props["apiUrl"] = {"type":"string","format":"uri","description":"Exact-card JSON endpoint used lazily by the queued runtime to obtain direct static image URLs."}
    props["fallbackArtUrl"] = {"type":"string","format":"uri","description":"Sequential last-resort art_crop image endpoint; never used as the initial img src."}
    props["fallbackNormalUrl"] = {"type":"string","format":"uri"}
    props["fallbackFuzzyUrl"] = {"type":"string","format":"uri"}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_contracts() -> None:
    (ROOT / "canonical" / "DESIGN-ECHO-CONTRACT.md").write_text('''# Canonical Design Echo Contract

## Authority

The **Eternal Dragon / Timeless Dragon** section is the visual and structural
authority for every Design Echo image-plus-copy panel in Compulsive Research.

## Locked component

```html
<section id="…" class="design-echo-section">
  <div class="chapter-number">… · Design echo</div>
  <h2>…</h2>
  <p>Introductory comparison…</p>
  <div class="inline-image canonical-inline-image" data-image-card="CARD">
    <div class="image image-loading" data-card-label="CARD">
      <img class="inline-image-media"
           src="data:image/gif;base64,…"
           data-card-name="CARD"
           data-api-url="…"
           data-fallback-art="…"
           data-fallback-normal="…"
           data-fallback-fuzzy="…">
    </div>
    <div class="copy">
      <div class="eyebrow">SET · YEAR</div>
      <h3>Comparative thesis</h3>
      <p>What the later design kept, compressed, redirected, or restrained.</p>
    </div>
  </div>
  <p>Closing interpretation…</p>
</section>
```

## Image reliability

1. The image well contains a real `<img>`; CSS-only backgrounds are forbidden.
2. The initial `src` is a tiny local placeholder, not a live API image lookup.
3. A self-contained runtime waits until the panel nears the viewport, queues
   requests, resolves card JSON to direct static image URLs, caches the result,
   and retries transient failures.
4. Only after direct URLs fail may it try exact `art_crop`, exact `normal`, and
   fuzzy `art_crop` image endpoints, sequentially.
5. Final failure must hide the `<img>` and show a readable label. A blank black
   image well is forbidden.
6. Every article embeds the runtime inline for downloaded standalone use and
   also references `assets/design-echo.js` for the hosted archive.

## Geometry

Desktop uses Eternal Dragon's `1.4fr 1fr` image/copy split, 390px image
minimum, 980px component width, and zero internal gap. The copy field is the
canonical dark green `#20322f` with a restrained `#586963` border. Mobile uses
one column: the image and green copy field each reach the full component edge.
The outer component is transparent, so no black frame or inset can surround
its children.

## Prohibited variants

- `.descendant-panel` or any padded wrapper around the canonical panel
- an empty `.image` div
- card art assigned only through article-specific CSS
- `api.scryfall.com/cards/named?...format=image` as the initial `<img src>`
- green copy cards detached from the image, inset inside a black frame, or
  given bespoke margins, widths, radii, or mobile geometry
''', encoding="utf-8")

    design_contract = ROOT / "canonical" / "DESIGN-ECHO-CONTRACT.md"
    design_text = design_contract.read_text(encoding="utf-8")
    card_reference_note = """

## Card-reference discovery

The final Design Echo prose is scanned after rendering by `tools/canonicalize_card_links.py`. Exact Oracle names are discovered from `canonical/card-name-catalog.json`; `cardReferences` is only an optional ambiguity hint. Shortened titles require `cardAliases`. Publication requires `tools/validate_card_links.py`, which removes existing links in memory and independently rescans visible prose so an incomplete declaration cannot hide a missed card name. See `canonical/CARD-REFERENCE-CONTRACT.md`.
"""
    if "## Card-reference discovery" not in design_text:
        design_contract.write_text(design_text.rstrip() + card_reference_note + "\n", encoding="utf-8")

    prompt = ROOT / "canonical" / "GENERATION-PROMPT.md"
    raw = prompt.read_text(encoding="utf-8")
    raw = re.sub(
        r'11\. Supply exactly one canonical Design Echo section.*?(?=\n12\.)',
        '11. Supply exactly one canonical Design Echo section using `.inline-image.canonical-inline-image`. Its `.image` contains a real `<img class="inline-image-media">` whose initial `src` is the canonical local placeholder. Provide exact-card JSON, exact `art_crop`, exact `normal`, and fuzzy `art_crop` URLs only through the locked data attributes. The self-contained queued runtime resolves and caches direct static artwork URLs when the panel nears the viewport. Never use a live API lookup as the initial image `src`, leave `.image` empty, assign card art only in CSS, apply `.descendant-panel`, or invent alternate geometry. The copy field must be Eternal Dragon green (`#20322f`) and reach the image/component edges without a black outer frame.\n',
        raw,
        flags=re.S,
    )
    prompt.write_text(raw, encoding="utf-8")

    contract = ROOT / "canonical" / "CANONICAL-CONTRACT.md"
    raw = contract.read_text(encoding="utf-8")
    raw = re.sub(
        r'(\*\*Design echo and inline image panels\*\* — ).*?(?=\n\d+\. \*\*)',
        r'\1use the immutable `.inline-image.canonical-inline-image` component documented in `canonical/DESIGN-ECHO-CONTRACT.md`. It embeds a self-contained queued image resolver, never starts with a live API image URL, shows a readable final fallback, and uses Eternal Dragon’s edge-to-edge dark-green copy field with no black outer frame.',
        raw,
        flags=re.S,
    )
    contract.write_text(raw, encoding="utf-8")


def write_validator() -> None:
    path = ROOT / "tools" / "validate_design_echo.py"
    path.write_text(r'''#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
failures=[]; articles=0; panels=0
for path in sorted(ROOT.glob("*.html")):
    if path.name=="index.html": continue
    articles+=1
    raw=path.read_text(encoding="utf-8")
    soup=BeautifulSoup(raw,"html.parser")
    article_panels=soup.select(".inline-image.canonical-inline-image")
    if not article_panels: failures.append(f"{path.name}: no canonical Design Echo panel")
    if soup.select(".descendant-panel") or ".descendant-panel" in raw: failures.append(f"{path.name}: legacy descendant-panel remains")
    if 'id="cr-design-echo-runtime"' not in raw: failures.append(f"{path.name}: self-contained runtime missing")
    if "CR_CANONICAL_DESIGN_ECHO_START" not in raw: failures.append(f"{path.name}: canonical CSS missing")
    if "assets/design-echo.js" not in raw: failures.append(f"{path.name}: shared runtime reference missing")
    for i,panel in enumerate(article_panels,1):
        panels+=1; prefix=f"{path.name} panel {i}"
        if panel.find_parent("section",class_="design-echo-section") is None: failures.append(f"{prefix}: outside design-echo-section")
        if not panel.get("data-image-card"): failures.append(f"{prefix}: data-image-card missing")
        image=panel.find("div",class_="image",recursive=False)
        copy=panel.find("div",class_="copy",recursive=False)
        if not image: failures.append(f"{prefix}: direct .image missing"); continue
        if not copy: failures.append(f"{prefix}: direct .copy missing")
        if "image-loading" not in (image.get("class") or []): failures.append(f"{prefix}: image-loading state missing")
        if "background-image" in (image.get("style") or "").lower(): failures.append(f"{prefix}: CSS-only background remains")
        img=image.find("img",class_="inline-image-media",recursive=False)
        if not img: failures.append(f"{prefix}: real img missing"); continue
        if not (img.get("src") or "").startswith("data:image/"): failures.append(f"{prefix}: initial src is not local placeholder")
        if "api.scryfall.com/cards/named" in (img.get("src") or ""): failures.append(f"{prefix}: live API image used as initial src")
        for attr in ("data-card-name","data-api-url","data-fallback-art","data-fallback-normal","data-fallback-fuzzy"):
            if not img.get(attr): failures.append(f"{prefix}: {attr} missing")
        if "format=image" in (img.get("data-api-url") or ""): failures.append(f"{prefix}: data-api-url is not JSON endpoint")
        if "art_crop" not in (img.get("data-fallback-art") or ""): failures.append(f"{prefix}: art fallback missing")
        if "normal" not in (img.get("data-fallback-normal") or ""): failures.append(f"{prefix}: normal fallback missing")
        if "fuzzy=" not in (img.get("data-fallback-fuzzy") or ""): failures.append(f"{prefix}: fuzzy fallback missing")
        if img.get("onerror"): failures.append(f"{prefix}: obsolete inline onerror chain remains")
    # Structural CSS locks that prevent the reported black inset/frame.
    required_css=("background:transparent!important","background:#20322f!important","width:100%!important","image-failed .inline-image-media")
    for token in required_css:
        if token not in raw: failures.append(f"{path.name}: required geometry/failure CSS missing: {token}")
report={"articles":articles,"panels":panels,"failures":failures}
(ROOT/"audit"/"design-echo-validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
sys.exit(1 if failures else 0)
''', encoding="utf-8")
    path.chmod(0o755)


def refresh_lock() -> None:
    source = ROOT / "250-eternal-dragon.html"
    snapshot = ROOT / "canonical" / "250-eternal-dragon.canonical.html"
    snapshot.write_bytes(source.read_bytes())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    (ROOT / "canonical" / "250-eternal-dragon.sha256").write_text(digest + "\n", encoding="utf-8")
    lock_path = ROOT / "canonical" / "canonical-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for key in ("sha256","canonical_sha256","canonical_article_sha256"):
        lock[key]=digest
    lock["design_echo_component"]={
        "authority":"250-eternal-dragon.html#descendant",
        "class":"inline-image canonical-inline-image",
        "initial_src":"local data-image placeholder",
        "image_runtime":"inline queued resolver plus assets/design-echo.js",
        "copy_background":"#20322f",
        "outer_frame":"transparent; no inset or black border",
        "fallbacks":["cached/direct static URL","exact art_crop","exact normal","fuzzy art_crop","readable failure label"]
    }
    lock_path.write_text(json.dumps(lock,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    results=[migrate_file(path,args.check) for path in article_files()]
    changed=[r["file"] for r in results if r["changed"]]
    if args.check:
        if changed:
            print(json.dumps({"would_change":changed},indent=2)); return 1
        print(json.dumps({"articles":len(results),"panels":sum(r["panels"] for r in results),"status":"canonical"},indent=2)); return 0
    update_shared_assets(); update_template(); update_schema(); update_contracts(); write_validator(); refresh_lock()
    report={"articles_scanned":len(results),"articles_changed":len(changed),"panels_hardened":sum(r["panels"] for r in results),"files_changed":changed}
    (ROOT/"audit"/"design-echo-hardening.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="files_changed"},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
