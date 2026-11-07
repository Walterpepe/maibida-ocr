# -*- coding: utf-8 -*-
"""Add localized WhatsApp consultation content to the deployed static site.

Incremental and idempotent:
  * 88 formal pages: nav wa.me link gains a localized pre-filled chat message,
    and the footer contact column gains one localized WhatsApp line.
  * 11 contact pages: a full "WhatsApp consultation" section after the form.
  * cn/css/contact.css: styles for the new section.

Only the files that are actually changed are backed up first, with a SHA-256
manifest, before any byte is written.
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
BACKUP = ROOT.parent / f"maibida-ocr-rebuilt_whatsapp_backup_{TS}"
OUT = ROOT / "tools/whatsapp-content-patch.json"

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]

FOOT_BEGIN = "<!-- BEGIN whatsapp-footer -->"
FOOT_END = "<!-- END whatsapp-footer -->"
FOOT_RE = re.compile(r'(<div class="foot-contact">)(.*?)(</div>)', re.S)
FOOT_BLOCK_RE = re.compile(re.escape(FOOT_BEGIN) + r".*?" + re.escape(FOOT_END), re.S)
NAV_HREF_RE = re.compile(r'(<a class="vp-whatsapp-link"[^>]*?href=")[^"]*(")', re.S)
CONTACT_BLOCK_RE = re.compile(
    r"<!-- BEGIN whatsapp-consult-content -->.*?<!-- END whatsapp-consult-content -->", re.S)
FORM_END_RE = re.compile(r"(</form>)(\s*)(</main>)", re.S)
CSS_BLOCK_RE = re.compile(re.escape(W.CSS_BEGIN) + r".*?" + re.escape(W.CSS_END), re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def footer_block(lang: str) -> str:
    return FOOT_BEGIN + "\n" + W.footer_line(lang) + "\n" + FOOT_END


def patch_formal(rel: str) -> dict:
    f = ROOT / rel
    t = f.read_text(encoding="utf-8")
    lang = lang_of(rel)
    href = W.wa_href(lang)

    t2, n = NAV_HREF_RE.subn(lambda m: m.group(1) + href + m.group(2), t, count=1)
    if n != 1:
        raise RuntimeError(f"nav WhatsApp link not found: {rel}")

    m = FOOT_RE.search(t2)
    if not m:
        raise RuntimeError(f"footer contact column not found: {rel}")
    body = FOOT_BLOCK_RE.sub("", m.group(2)).rstrip("\n \t")
    idx = body.rfind("</p>")
    if idx < 0:
        raise RuntimeError(f"no fc-line paragraph in footer: {rel}")
    new_body = (body[:idx + 4] + "\n" + footer_block(lang) +
                body[idx + 4:] + "\n")
    t3 = t2[:m.start(2)] + new_body + t2[m.end(2):]
    if t3 != t:
        f.write_text(t3, encoding="utf-8")
    return {"page": rel, "lang": lang, "changed": t3 != t,
            "nav_href": href, "footer_line": True}


def patch_contact(rel: str) -> dict:
    f = ROOT / rel
    t = f.read_text(encoding="utf-8")
    lang = lang_of(rel)
    privacy_url = "privacy.html" if lang == "zh-CN" else f"privacy.{lang}.html"
    block = W.contact_block(lang, privacy_url)
    t2 = CONTACT_BLOCK_RE.sub("", t)
    t3, n = FORM_END_RE.subn(
        lambda m: m.group(1) + "\n" + block + "\n" + m.group(3), t2, count=1)
    if n != 1:
        raise RuntimeError(f"form/main boundary not found: {rel}")
    if t3 != t:
        f.write_text(t3, encoding="utf-8")
    return {"page": rel, "lang": lang, "changed": t3 != t, "section": True}


def patch_css() -> dict:
    f = ROOT / "cn/css/contact.css"
    t = f.read_text(encoding="utf-8")
    if W.CSS_BEGIN in t:
        t2 = CSS_BLOCK_RE.sub(lambda m: W.CONTACT_CSS_BLOCK, t, count=1)
    else:
        t2 = t.rstrip() + "\n\n" + W.CONTACT_CSS_BLOCK + "\n"
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
    return {"page": "cn/css/contact.css", "changed": t2 != t}


def main():
    # Superseded: the consultation section was moved into the nav entry.
    # Running this old patch would re-add the removed section below the form.
    raise SystemExit("deprecated: use tools/move-whatsapp-consult.py instead")
    rels = formal_pages() + contact_pages() + ["cn/css/contact.css"]
    # preflight: every target must exist and contain the expected anchors
    for rel in rels:
        if not (ROOT / rel).exists():
            raise RuntimeError(f"missing file: {rel}")

    BACKUP.mkdir(parents=True, exist_ok=True)
    manifest = {"timestamp": TS, "files": []}
    for rel in rels:
        src = ROOT / rel
        dst = BACKUP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        a, b = sha256(src), sha256(dst)
        if a != b:
            raise RuntimeError(f"backup hash mismatch: {rel}")
        manifest["files"].append({"path": rel, "sha256": a, "size": src.stat().st_size})
    (BACKUP / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    formal = [patch_formal(r) for r in formal_pages()]
    contacts = [patch_contact(r) for r in contact_pages()]
    css = patch_css()

    result = {
        "timestamp": TS,
        "backup": str(BACKUP),
        "backup_files": len(rels),
        "formal_pages": len(formal),
        "formal_changed": sum(1 for x in formal if x["changed"]),
        "contact_pages": len(contacts),
        "contact_changed": sum(1 for x in contacts if x["changed"]),
        "css_changed": css["changed"],
        "wa_number": W.WA_NUMBER,
        "sample_href_zh": W.wa_url("zh-CN")[:120] + "...",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
