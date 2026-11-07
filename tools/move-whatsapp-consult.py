# -*- coding: utf-8 -*-
"""Move the WhatsApp consultation content into the nav entry.

Per user request:
  * drop the "machine vision light selection" bullet in all 11 locales,
  * remove the standalone section below the message form,
  * show the remaining consultation content in a panel opened by the
    "WhatsApp consultation" entry in the top navigation / contact header.

The wa.me href stays on the trigger itself (crawlable, works without JS);
the script only intercepts the click to expand the localized panel.
Idempotent; backs up every changed file with a SHA-256 manifest first.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whatsapp_content as W

ROOT = Path(__file__).resolve().parent.parent
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT.parent / f"maibida-ocr-rebuilt_whatsapp_move_backup_{TS}"
OUT = ROOT / "tools/whatsapp-move-patch.json"

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]

OLD_SECTION_RE = re.compile(
    r"<!-- BEGIN whatsapp-consult-content -->.*?<!-- END whatsapp-consult-content -->\s*", re.S)
OLD_CSS_RE = re.compile(
    r"/\* BEGIN whatsapp-consult-content \*/.*?/\* END whatsapp-consult-content \*/", re.S)
NEW_PANEL_RE = re.compile(
    re.escape(W.PANEL_BEGIN) + r".*?" + re.escape(W.PANEL_END), re.S)
NEW_CSS_RE = re.compile(re.escape(W.CSS_BEGIN) + r".*?" + re.escape(W.CSS_END), re.S)
NAV_LINK_RE = re.compile(r'<a class="vp-whatsapp-link"[^>]*>(.*?)</a>', re.S)
HEADER_RE = re.compile(r'(<header class="cf-head">)(.*?)(</header>)', re.S)
WIDGET_BEGIN = "<!-- BEGIN whatsapp-consult-widget -->"
WIDGET_END = "<!-- END whatsapp-consult-widget -->"
WIDGET_RE = re.compile(re.escape(WIDGET_BEGIN) + r".*?" + re.escape(WIDGET_END), re.S)
SCRIPT_RE = re.compile(r'<script src="(?:\.\./)?cn/js/whatsapp-consult\.js"[^>]*></script>\s*')
BODY_END_RE = re.compile(r"(</body>)", re.I)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lang_of(rel: str) -> str:
    m = re.search(r"\.([a-z]{2}-[A-Z]{2})\.html$", rel)
    return m.group(1) if m else "zh-CN"


def formal_pages():
    out = []
    for p in PAGES:
        out.append(p)
        q = Path(p)
        for l in LOCALES:
            out.append(str(q.with_name(q.stem + "." + l + ".html")).replace("\\", "/"))
    return out


def contact_pages():
    return ["contact.html"] + [f"contact.{l}.html" for l in LOCALES]


def prefix_of(rel: str) -> str:
    return "../" if "/" in rel else ""


def privacy_url(lang: str, prefix: str) -> str:
    name = "privacy.html" if lang == "zh-CN" else f"privacy.{lang}.html"
    return prefix + name


def add_script(t: str, prefix: str) -> str:
    tag = f'<script src="{prefix}cn/js/whatsapp-consult.js" defer></script>\n'
    t = SCRIPT_RE.sub("", t)
    if "</body>" not in t.lower():
        raise RuntimeError("no </body> anchor")
    return BODY_END_RE.sub(lambda m: tag + m.group(1), t, count=1)


def patch_formal(rel: str) -> dict:
    f = ROOT / rel
    t = f.read_text(encoding="utf-8")
    lang, prefix = lang_of(rel), prefix_of(rel)
    t = NEW_PANEL_RE.sub("", t)          # drop any previously injected panel
    m = NAV_LINK_RE.search(t)
    if not m:
        raise RuntimeError(f"nav WhatsApp link missing: {rel}")
    label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    widget = (W.nav_trigger(lang, label) + "\n" +
              W.nav_panel(lang, privacy_url(lang, prefix)))
    t2 = t[:m.start()] + widget + t[m.end():]
    t2 = add_script(t2, prefix)
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
    return {"page": rel, "lang": lang, "changed": t2 != t}


def patch_contact(rel: str) -> dict:
    f = ROOT / rel
    t = f.read_text(encoding="utf-8")
    lang = lang_of(rel)
    t = OLD_SECTION_RE.sub("", t)        # remove the section below the form
    t = NEW_PANEL_RE.sub("", t)
    t = WIDGET_RE.sub("", t)
    m = HEADER_RE.search(t)
    if not m:
        raise RuntimeError(f"contact header missing: {rel}")
    widget = (WIDGET_BEGIN + "\n" +
              W.contact_widget(lang, privacy_url(lang, "")) + "\n" + WIDGET_END)
    body = m.group(2).rstrip("\n \t") + "\n" + widget + "\n"
    t2 = t[:m.start(2)] + body + t[m.end(2):]
    t2 = add_script(t2, "")
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
    return {"page": rel, "lang": lang, "changed": t2 != t}


def patch_css(rel: str) -> dict:
    f = ROOT / rel
    t = f.read_text(encoding="utf-8")
    t = OLD_CSS_RE.sub("", t)
    t = NEW_CSS_RE.sub("", t)
    t2 = t.rstrip() + "\n\n" + W.NAV_CSS_BLOCK + "\n"
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
    return {"page": rel, "changed": t2 != t}


def main():
    rels = (formal_pages() + contact_pages() +
            ["cn/css/site-multilingual.css", "cn/css/contact.css",
             "tools/whatsapp_content.py", "tools/add-message-feature.py",
             "tools/verify-whatsapp-content.py", "tools/add-whatsapp-content.py"])
    for rel in rels:
        if not (ROOT / rel).exists():
            raise RuntimeError(f"missing file: {rel}")

    BACKUP.mkdir(parents=True, exist_ok=True)
    manifest = {"timestamp": TS, "files": []}
    for rel in rels:
        src, dst = ROOT / rel, BACKUP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        a, b = sha256(src), sha256(dst)
        if a != b:
            raise RuntimeError(f"backup hash mismatch: {rel}")
        manifest["files"].append({"path": rel, "sha256": a, "size": src.stat().st_size})
    (BACKUP / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    (ROOT / "cn/js/whatsapp-consult.js").write_text(W.NAV_JS, encoding="utf-8")
    formal = [patch_formal(r) for r in formal_pages()]
    contacts = [patch_contact(r) for r in contact_pages()]
    css = [patch_css(r) for r in ["cn/css/site-multilingual.css", "cn/css/contact.css"]]

    result = {
        "timestamp": TS, "backup": str(BACKUP), "backup_files": len(rels),
        "formal_pages": len(formal), "formal_changed": sum(x["changed"] for x in formal),
        "contact_pages": len(contacts), "contact_changed": sum(x["changed"] for x in contacts),
        "css_changed": sum(x["changed"] for x in css),
        "js": "cn/js/whatsapp-consult.js",
        "items_per_locale": len(W.DATA["zh-CN"]["items"]),
        "removed_bullet_zh": "机器视觉光源选型：条形光、环形光、同轴光、穹顶光等",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
