#!/usr/bin/env python3
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
