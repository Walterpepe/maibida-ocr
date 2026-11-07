#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only probe: for the 25 images carrying baked-in Chinese text, report
how they are referenced across the 88 formal pages, whether their alt text is
localised, and whether an entity-text transcript already exists next to them.

No site page is modified. Output: tools/probe-baked-images.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.maibida.com/"
CJK = re.compile(r"[\u4e00-\u9fff]")
LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]

rev = json.loads((ROOT / "tools/localization-review.json").read_text(encoding="utf-8"))
groups = rev["remaining_needs_decision"]["images_with_chinese_text"]["groups"]
targets = {}
for gname, g in groups.items():
    for it in g["items"]:
        targets[it["file"]] = {"group": gname, "zh": it["chinese_text"],
                               "pages": it.get("used_by_pages", [])}

sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm, re.S)
pages = []
for u in locs:
    rel = u.replace(BASE, "").lstrip("/")
    if (ROOT / rel).is_file():
        pages.append(rel)

hits = []
for rel in pages:
    raw = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "html.parser")
    lang = soup.html.get("lang", "") if soup.html else ""
    for img in soup.find_all("img"):
        src = (img.get("src") or "").replace("\\", "/")
        key = next((f for f in targets if f.split("/")[-1] in src), None)
        if not key:
            continue
        parent = img.parent
        ptext = parent.get_text(" ", strip=True)
        # sibling entity text that repeats the caption (ocr-case-title etc.)
        caps = [s.get_text(" ", strip=True) for s in parent.select(".ocr-case-title, figcaption, .ocr-transcript")]
        hits.append({
            "page": rel, "lang": lang, "src": src, "file": key,
            "group": targets[key]["group"],
            "alt": img.get("alt", ""),
            "alt_has_cjk": bool(CJK.search(img.get("alt", "") or "")),
            "parent_class": " ".join(parent.get("class") or []),
            "parent_text": ptext[:220],
            "captions": caps[:3],
            "has_transcript": bool(parent.select_one(".ocr-transcript")),
        })

# summarise per file: how many pages reference it, sample alts per language
summary = []
for f, meta in targets.items():
    rows = [h for h in hits if h["file"] == f]
    by_lang = {}
    for h in rows:
        by_lang.setdefault(h["lang"], h["alt"])[:0]
    alt_samples = {}
    for h in rows:
        alt_samples.setdefault(h["lang"], h["alt"])
    summary.append({
        "file": f, "group": meta["group"],
        "zh_text": meta["zh"],
        "used_by_pages_source": meta["pages"],
        "hit_pages": len(rows),
        "alt_cjk_pages": sum(1 for h in rows if h["alt_has_cjk"]),
        "has_caption_pages": sum(1 for h in rows if h["captions"]),
        "has_transcript_pages": sum(1 for h in rows if h["has_transcript"]),
        "alt_samples": alt_samples,
    })

out = {
    "formal_pages": len(pages),
    "target_images": len(targets),
    "total_img_hits": len(hits),
    "summary": summary,
    "hits": hits,
}
(ROOT / "tools/probe-baked-images.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"formal_pages={len(pages)} target_images={len(targets)} hits={len(hits)}")
for s in summary:
    print(f"[{s['group']}] {s['file'].split('/')[-1]}")
    print(f"   hits={s['hit_pages']} alt_cjk={s['alt_cjk_pages']} "
          f"caption={s['has_caption_pages']} transcript={s['has_transcript_pages']}")
    print(f"   zh={s['zh_text']}")
    print(f"   alt(zh)={s['alt_samples'].get('zh-CN','')!r} "
          f"alt(en-US)={s['alt_samples'].get('en-US','')!r} "
          f"alt(ru-RU)={s['alt_samples'].get('ru-RU','')!r}")
