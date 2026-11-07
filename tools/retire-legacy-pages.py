#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decision for the 4 orphan en-AU / es-ES files: retire, do not hard-delete.

They are not in sitemap.xml and no formal page links to them any more, but an
old external link or bookmark could still request the URL. Deleting them would
produce a hard 404. Instead each becomes a minimal canonical redirect stub:

  - meta robots noindex,follow  -> not indexed as a standalone page
  - canonical -> the current equivalent page (signals cluster consolidation)
  - meta refresh + a visible link -> visitors land on the current page
  - language-appropriate copy, no Chinese, no language switcher, no hreflang

This removes their internal 404 links, Chinese JSON-LD residue and the stale
"简体中文" switcher entry while keeping old URLs resolvable.

Mapping (decided): en-AU -> en-SG (APAC English), es-ES -> es-MX (LatAm Spanish).
Originals are backed up before being replaced.
Output: tools/legacy-pages-decision.json
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAP = {
    "index.en-AU.html": {
        "target": "index.en-SG.html", "lang": "en",
        "title": "Page moved - MAIBIDA",
        "heading": "This page has moved",
        "body": "The Australia English edition is no longer published. The current English edition for Singapore and the Asia-Pacific region is available at the link below.",
        "link": "Continue to the current English page",
        "reason": "en-AU retired in favour of the maintained APAC English edition en-SG",
    },
    "product/10032.en-AU.html": {
        "target": "product/10032.en-SG.html", "lang": "en",
        "title": "IMX-790 page moved - MAIBIDA",
        "heading": "This page has moved",
        "body": "The Australia English edition of the IMX-790 mold monitor page is no longer published. The current English product page is available at the link below.",
        "link": "Continue to the current product page",
        "reason": "en-AU retired in favour of en-SG",
    },
    "product/smart-camera.en-AU.html": {
        "target": "product/smart-camera.en-SG.html", "lang": "en",
        "title": "V3 Pro page moved - MAIBIDA",
        "heading": "This page has moved",
        "body": "The Australia English edition of the V3 Pro AI vision sensor page is no longer published. The current English product page is available at the link below.",
        "link": "Continue to the current product page",
        "reason": "en-AU retired in favour of en-SG",
    },
    "product/smart-camera.es-ES.html": {
        "target": "product/smart-camera.es-MX.html", "lang": "es",
        "title": "Página movida - MAIBIDA",
        "heading": "Esta página se ha movido",
        "body": "La edición en español de España ya no se publica. La versión vigente en español de Latinoamérica (México) está disponible en el enlace siguiente.",
        "link": "Ir a la página actual",
        "reason": "es-ES retired in favour of the LatAm Spanish edition es-MX",
    },
}

CSS = ("body{margin:0;background:#f5f7fa;color:#1e293b;font-family:Segoe UI,"
       "Arial,sans-serif;line-height:1.6;display:grid;place-items:center;"
       "min-height:100vh;padding:24px}"
       "main{max-width:640px;background:#fff;border:1px solid #e2e8f0;"
       "border-radius:14px;padding:34px 38px;box-shadow:0 2px 14px rgba(15,23,42,.05)}"
       "h1{font-size:23px;margin:0 0 12px}p{margin:0 0 16px;color:#475569}"
       "a{color:#0f766e;font-weight:600;text-decoration:none}"
       "a:hover{text-decoration:underline}"
       ".tag{font-size:12px;letter-spacing:.08em;text-transform:uppercase;"
       "color:#0f766e;font-weight:700;margin-bottom:10px}")


def html_for(rel, m):
    # relative link works from the stub's own directory
    local = m["target"].split("/")[-1]
    canonical = "https://www.maibida.com/" + m["target"]
    return f"""<!doctype html>
<html lang="{m['lang']}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{m['title']}</title>
<meta name="robots" content="noindex,follow"/>
<link rel="canonical" href="{canonical}"/>
<meta http-equiv="refresh" content="0;url={local}"/>
<style>{CSS}</style>
</head>
<body>
<main>
<div class="tag">MAIBIDA · {m['lang'].upper()}</div>
<h1>{m['heading']}</h1>
<p>{m['body']}</p>
<p><a href="{local}">{m['link']} &rarr;</a></p>
</main>
</body>
</html>
"""


def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT.parent / f"maibida-ocr-rebuilt_legacypages_backup_{stamp}"
    records = []
    for rel, m in MAP.items():
        src = ROOT / rel
        if not src.is_file():
            records.append({"page": rel, "status": "missing"})
            continue
        target = ROOT / m["target"]
        if not target.is_file():
            raise SystemExit(f"redirect target missing: {m['target']}")
        dest = backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        src.write_text(html_for(rel, m), encoding="utf-8")
        records.append({
            "page": rel, "status": "retired_to_redirect_stub",
            "redirect_target": m["target"], "lang": m["lang"],
            "canonical": "https://www.maibida.com/" + m["target"],
            "robots": "noindex,follow", "reason": m["reason"],
            "internal_dead_links_after": 0,
        })

    out = {
        "decided_at": datetime.now().isoformat(timespec="seconds"),
        "decision": "retire as canonical noindex redirect stubs (keep URLs resolvable, avoid hard 404)",
        "why_not_delete": "Old external links/bookmarks would otherwise return a hard 404; a noindex + canonical stub consolidates signals to the current page.",
        "why_not_keep_as_content": "They are outside sitemap.xml and outside the 12-member hreflang cluster; keeping full content would create duplicate/orphan indexed pages.",
        "pages": records,
        "backup": str(backup_root),
    }
    (ROOT / "tools/legacy-pages-decision.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("retired:", len([r for r in records if r["status"] == "retired_to_redirect_stub"]))
    for r in records:
        print(f"  {r['page']} -> {r.get('redirect_target')}")
    print("backup:", backup_root)


if __name__ == "__main__":
    main()
