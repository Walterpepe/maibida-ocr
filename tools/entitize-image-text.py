#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Turn the Chinese wording baked into shared images into crawlable entity text.

For each of the 17 images whose on-image labels have no DOM counterpart, inserts
a visually-hidden, page-language transcript span immediately after the <img>.
The other 8 application-case images already have a visible localised
.ocr-case-title, so they are deliberately left untouched (no duplicate text).

- Idempotent: existing .ocr-transcript spans are removed and rebuilt.
- Byte-safe: only <img ...> tags are rewritten; everything else is preserved.
- Zero visual change: sr-only rules are inline, absolute, 1x1 clipped.
- A timestamped backup of every modified page is written before the first edit.

Output: tools/ocr-transcript-apply.json
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.maibida.com/"
DATA = json.loads((ROOT / "tools/image-text-transcripts.json").read_text(encoding="utf-8"))
TEXTS = DATA["texts"]
LOCALES = set(DATA["locales"]) - {"zh-CN"}
SPEC = {it["file"].split("/")[-1]: it for it in DATA["images"]}

SR_ONLY = ("position:absolute!important;width:1px!important;height:1px!important;"
           "padding:0!important;margin:-1px!important;overflow:hidden!important;"
           "clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important")
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
SRC_RE = re.compile(r"\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)
OLD_SPAN_RE = re.compile(r'<span class="ocr-transcript"[^>]*>.*?</span>', re.S | re.I)


def page_lang(rel: str) -> str:
    m = re.search(r"\.([a-z]{2}-[A-Z]{2})\.html$", rel)
    return m.group(1) if m and m.group(1) in LOCALES else "zh-CN"


def sitemap_pages():
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm, re.S)
    return [r for u in locs
            if (ROOT / (r := u.replace(BASE, "").lstrip("/"))).is_file()]


def main():
    pages = sitemap_pages()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT.parent / f"maibida-ocr-rebuilt_ocrtranscript_backup_{stamp}"
    backed_up = False
    changed_pages = 0
    inserted = 0
    by_lang = {}
    per_file = {}

    for rel in pages:
        path = ROOT / rel
        raw = path.read_text(encoding="utf-8")
        cleaned = OLD_SPAN_RE.sub("", raw)  # idempotent rebuild
        lang = page_lang(rel)

        def repl(m):
            nonlocal inserted
            tag = m.group(0)
            sm = SRC_RE.search(tag)
            if not sm:
                return tag
            base = sm.group(1).replace("\\", "/").split("/")[-1]
            spec = SPEC.get(base)
            if not spec or spec["mode"] != "transcript":
                return tag
            text = TEXTS[spec["t"]].get(lang) or TEXTS[spec["t"]]["en-US"]
            span = (f'<span class="ocr-transcript" data-ocr-for="{html.escape(base, quote=True)}" '
                    f'data-lang="{lang}" style="{SR_ONLY}">{html.escape(text)}</span>')
            inserted += 1
            by_lang[lang] = by_lang.get(lang, 0) + 1
            per_file[base] = per_file.get(base, 0) + 1
            return tag + span

        new = IMG_RE.sub(repl, cleaned)
        if new == raw:
            continue
        if not backed_up:
            backup_root.mkdir(parents=True, exist_ok=True)
            backed_up = True
        dest = backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        path.write_text(new, encoding="utf-8")
        changed_pages += 1

    report = {
        "applied_at": datetime.now().isoformat(timespec="seconds"),
        "formal_pages": len(pages),
        "changed_pages": changed_pages,
        "transcript_spans": inserted,
        "by_language": by_lang,
        "by_image": per_file,
        "images_with_visible_caption_left_untouched":
            [k for k, v in SPEC.items() if v["mode"] == "visible-caption"],
        "backup": str(backup_root) if backed_up else None,
    }
    (ROOT / "tools/ocr-transcript-apply.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pages={len(pages)} changed={changed_pages} spans={inserted}")
    print("by_language:", json.dumps(by_lang, ensure_ascii=False))
    print("images covered:", len(per_file), "of 17 transcript images")
    print("backup:", report["backup"])
    return report


if __name__ == "__main__":
    main()
