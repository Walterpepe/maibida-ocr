"""Apply the H1-H6 + M/O remediation to all 88 formal pages (idempotent).

Scope:
  H4  conditional wording instead of "100% inspection, zero misses" (11 locales)
  H6  11-locale technical disclaimer under every parameter table
  M1/O6  unified footer injected into the 11 homepages
  M2  remove the incomplete ICP-filing placeholder link
  M3  clickable tel:/mailto: contact details on all 88 pages
  M4/M7  replace the "sensor brand / Sony" table cell with a neutral CMOS spec
  M5  remove unconditional delivery-time guarantees (11 locales)
  O1  Japanese 最高 -> 最大
  O2  handled in add-message-feature.py
  O5  BreadcrumbList JSON-LD on the 11 homepages
  Privacy / Terms footer links on all 88 pages
"""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import compliance_i18n as C

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT.parent / f"maibida-ocr-rebuilt_compliance_pages_{TS}"

HOME = "index.html"
CONTENT_PAGES = ["product/10032.html", "product/smart-camera.html",
                 "productlist/10029.html", "productlist/10030.html",
                 "productlist/10034.html", "productlist/10036.html",
                 "productlist/10039.html"]
ALL_BASE = [HOME] + CONTENT_PAGES

BEGIN_DISCLAIMER = "<!-- spec-disclaimer -->"
END_DISCLAIMER = "<!-- /spec-disclaimer -->"
BEGIN_HOME_FOOT = "<!-- home-footer -->"
END_HOME_FOOT = "<!-- /home-footer -->"
BEGIN_BREADCRUMB = "<!-- home-breadcrumb -->"
END_BREADCRUMB = "<!-- /home-breadcrumb -->"

DISCLAIMER_STYLE = ("font-size:12px;line-height:1.7;color:#5c6871;margin:12px 0 0;"
                    "padding:9px 12px;border-left:3px solid #009944;background:#f6f9f7")


def esc(s):
    return html.escape(str(s), quote=True)


def lang_rel(base, lang):
    return base if lang == "zh-CN" else base.replace(".html", "." + lang + ".html")


def policy_rel(lang):
    return "privacy.html" if lang == "zh-CN" else f"privacy.{lang}.html"


def terms_rel(lang):
    return "terms.html" if lang == "zh-CN" else f"terms.{lang}.html"


def prefix_of(rel):
    return "../" if "/" in rel else ""


def all_pages():
    return [(lang_rel(b, l), l) for b in ALL_BASE for l in C.LANGS]


def backup(rels):
    BACKUP.mkdir(parents=True, exist_ok=True)
    for rel in rels:
        src = ROOT / rel
        if not src.exists():
            continue
        dst = BACKUP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return str(BACKUP)


def strip_blocks(t):
    """Remove our own injected blocks so the script is safely re-runnable."""
    for b, e in ((BEGIN_DISCLAIMER, END_DISCLAIMER),
                 (BEGIN_HOME_FOOT, END_HOME_FOOT),
                 (BEGIN_BREADCRUMB, END_BREADCRUMB)):
        t = re.sub(re.escape(b) + r".*?" + re.escape(e) + r"\s*", "", t, flags=re.S)
    t = re.sub(r'<p class="foot-legal">.*?</p>\s*', "", t, flags=re.S)
    return t


def fix_wording(t, lang):
    """H4, M5, M4/M7, O1 — exact phrase replacements only."""
    hits = {}
    old, new = C.H4_FIX[lang]
    n = t.count(old)
    if n:
        t = t.replace(old, new)
    hits["h4"] = n
    old, new = C.M5_FIX[lang]
    n = t.count(old)
    if n:
        t = t.replace(old, new)
    hits["m5"] = n
    old_h = C.SENSOR_HEADER_OLD[lang]
    n = t.count(f'>{old_h}<')
    if n:
        t = t.replace(f'>{old_h}<', f'>{esc(C.SENSOR_HEADER[lang])}<')
        t = t.replace('<td>Sony</td>', f'<td>{esc(C.SENSOR_VALUE[lang])}</td>')
    hits["sensor"] = n
    if lang == "ja-JP":
        n = 0
        for a, b in C.O1_FIX_JA:
            n += t.count(a)
            t = t.replace(a, b)
        hits["o1"] = n
    return t, hits


def fix_contacts(t):
    """M3 — wrap the plain-text phone/email in clickable links."""
    n = 0
    pat_phone = re.compile(r'(<span>)\s*15995675085\s*(</span>)')
    pat_mail = re.compile(r'(<span>)\s*mai_bida@163\.com\s*(</span>)')
    t, a = pat_phone.subn(
        r'\1<a href="tel:+8615995675085" aria-label="Call +86 159 9567 5085" '
        r'style="color:inherit;text-decoration:none">15995675085</a>\2', t)
    t, b = pat_mail.subn(
        r'\1<a href="mailto:mai_bida@163.com" aria-label="Email mai_bida@163.com" '
        r'style="color:inherit;text-decoration:none">mai_bida@163.com</a>\2', t)
    n = a + b
    return t, n


def remove_icp_placeholder(t):
    """M2 — the filing number was never supplied; showing a bare placeholder is worse."""
    return re.sub(r'<a\s+href="https://beian\.miit\.gov\.cn/"[^>]*>.*?</a>',
                  "", t, flags=re.S | re.I)


def footer_links(t, lang, prefix):
    """Add localized Privacy / Terms links inside the .eaoplc block."""
    p, terms, _ = C.FOOTER_LABELS[lang]
    legal = (f'<p class="foot-legal" style="margin:8px 0 0">'
             f'<a href="{prefix}{policy_rel(lang)}" style="color:inherit;text-decoration:underline">{esc(p)}</a>'
             f' &nbsp;·&nbsp; '
             f'<a href="{prefix}{terms_rel(lang)}" style="color:inherit;text-decoration:underline">{esc(terms)}</a>'
             f'</p>')
    m = re.search(r'(<div class="eaoplc">.*?)(</div>)', t, re.S)
    if m:
        return t[:m.end(1)] + legal + t[m.end(1):]
    return t


def inject_disclaimer(t, lang, prefix):
    """H6 — one localized notice per parameter page."""
    label = C.FOOTER_LABELS[lang][2]
    block = (BEGIN_DISCLAIMER + "\n" +
             f'<p class="spec-disclaimer" style="{DISCLAIMER_STYLE}">'
             f'{esc(C.DISCLAIMER[lang])} '
             f'<a href="{prefix}{terms_rel(lang)}" style="color:#087b3d">{esc(label)}</a>'
             f'</p>\n' + END_DISCLAIMER)
    pos = t.rfind("</table>")
    if pos >= 0:
        pos += len("</table>")
        return t[:pos] + "\n" + block + t[pos:]
    pos = t.find('<div class="foot">')
    if pos >= 0:
        return t[:pos] + block + "\n" + t[pos:]
    return t


def inject_breadcrumb(t, rel):
    """O5 — a minimal BreadcrumbList on homepages (no visual change)."""
    data = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [{
            "@type": "ListItem", "position": 1, "name": "Maibida",
            "item": "https://www.maibida.com/" + rel,
        }],
    }
    block = (BEGIN_BREADCRUMB + '\n<script type="application/ld+json">' +
             json.dumps(data, ensure_ascii=False) + "</script>\n" + END_BREADCRUMB)
    pos = t.find("</head>")
    return t[:pos] + block + "\n" + t[pos:] if pos >= 0 else t


def homepage_footer(lang):
    """M1/O6 — reuse the already-enhanced footer of the matching product page."""
    src = ROOT / lang_rel("product/10032.html", lang)
    t = src.read_bytes().decode("utf-8")
    a = t.find('<div class="foot">')
    b = t.find("<!-- foot结束 -->")
    if a < 0 or b < 0:
        raise RuntimeError(f"footer template not found: {src}")
    block = t[a:b].replace("../", "")
    # Two footer links are same-directory relative on product pages
    # ("10032.<lang>.html"), which would resolve to the wrong place once the
    # block is moved to a root-level homepage.
    block = block.replace('href="10032.', 'href="product/10032.')
    block = block.replace('href="smart-camera.', 'href="product/smart-camera.')
    return BEGIN_HOME_FOOT + "\n" + block + "\n" + END_HOME_FOOT


def inject_home_footer(t, lang):
    block = homepage_footer(lang)
    pos = t.find('<div class="float-sild">')
    if pos < 0:
        pos = t.find("</body>")
    return t[:pos] + block + "\n" + t[pos:]


def main():
    rels = [r for r, _ in all_pages()]
    backup_path = backup(rels)
    stats = {"h4": 0, "m5": 0, "sensor": 0, "o1": 0, "tel_mailto": 0,
             "disclaimer": 0, "footer_links": 0, "home_footer": 0,
             "breadcrumb": 0, "icp_removed": 0}
    changed = []

    # ---- Pass 1: inner pages (the homepage footer template is taken from these)
    for rel, lang in [(r, l) for r, l in all_pages() if r != HOME
                      and not r.startswith("index.")]:
        f = ROOT / rel
        t = f.read_bytes().decode("utf-8")
        orig = t
        t = strip_blocks(t)
        t, hits = fix_wording(t, lang)
        for k, v in hits.items():
            stats[k] += v
        t, n = fix_contacts(t)
        stats["tel_mailto"] += n
        t2 = remove_icp_placeholder(t)
        if t2 != t:
            stats["icp_removed"] += 1
        t = t2
        prefix = prefix_of(rel)
        t = footer_links(t, lang, prefix)
        stats["footer_links"] += 1
        if rel.startswith("product/") or rel.startswith("productlist/"):
            t = inject_disclaimer(t, lang, prefix)
            stats["disclaimer"] += 1
        if t != orig:
            f.write_bytes(t.encode("utf-8"))
            changed.append(rel)

    # ---- Pass 2: homepages
    for lang in C.LANGS:
        rel = lang_rel(HOME, lang)
        f = ROOT / rel
        t = f.read_bytes().decode("utf-8")
        orig = t
        t = strip_blocks(t)
        t = inject_home_footer(t, lang)
        stats["home_footer"] += 1
        t = inject_breadcrumb(t, rel)
        stats["breadcrumb"] += 1
        if t != orig:
            f.write_bytes(t.encode("utf-8"))
            changed.append(rel)

    out = {
        "timestamp": TS, "backup": backup_path,
        "pages_changed": changed, "pages_changed_count": len(changed),
        "stats": stats,
        "note": "sitemap.xml unchanged (88 formal URLs); new policy/terms pages are auxiliary",
    }
    (TOOLS / "compliance-pages.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "pages_changed"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
