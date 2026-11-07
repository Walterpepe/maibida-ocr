"""Apply the pre-launch audit remediation (idempotent, no layout changes).

Stages
  1. Move historical backup directories out of the web root (never delete).
  2. Localize the alt text of the 21 OCR diagram crops across all 11 languages.
  3. Fill missing title / canonical / meta description on auxiliary pages and
     turn the hreflang snippet into a valid, noindex, self-contained document.
  4. Harden robots.txt against tool/backup paths.

Nothing in the 88 formal pages is restructured: only <img> alt attributes and
<head> metadata are touched, so table formats, font sizes and positions stay put.
"""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OFFLINE = ROOT.parent / f"maibida-ocr-rebuilt_offline_backups_{TS}"
MANIFEST = ROOT / "tools/prelaunch-remediation.json"

BACKUP_DIRS = [
    "productInfo_bak_seo", "UserFiles_bak_bigimg",
    "_bak_footnav", "_bak_foot_full", "_bak_pathfix", "_bak_wxqrcode",
]

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
FORMAL = ["index.html", "product/10032.html", "product/smart-camera.html",
          "productlist/10029.html", "productlist/10030.html",
          "productlist/10034.html", "productlist/10036.html",
          "productlist/10039.html"]

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
SRC_RE = re.compile(r"\bsrc\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.I)
ALT_RE = re.compile(r"\balt\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)

ROBOTS = """User-agent: *
Allow: /
Disallow: /ValidateCode.aspx
Disallow: /plug-in/
Disallow: /tools/
Disallow: /_bak_footnav/
Disallow: /_bak_foot_full/
Disallow: /_bak_pathfix/
Disallow: /_bak_wxqrcode/
Disallow: /productInfo_bak_seo/
Disallow: /UserFiles_bak_bigimg/

# Auxiliary pages carry <meta name="robots" content="noindex"> instead of a
# Disallow rule, so crawlers can actually read the noindex directive.

Sitemap: https://www.maibida.com/sitemap.xml
"""

HREFLANG_LANGS = ["zh-CN", "en-US", "es-MX", "en-SG", "id-ID", "th-TH",
                  "vi-VN", "ko-KR", "ja-JP", "ms-MY", "ru-RU"]

AUX = {
    "localization-glossary.html": {
        "title": "MAIBIDA 多语种工业术语库 | Localization Glossary",
        "desc": "MAIBIDA 机器视觉与模具监视产品的中文、英语、西语、印尼语、泰语、越南语、韩语、日语、马来语、俄语术语对照表。",
        "noindex": True,
    },
    "product/smart-camera-localization-report.html": {
        "title": "智能相机页面本地化校验报告 | MAIBIDA",
        "desc": "MAIBIDA 智能相机页面多语种本地化的术语、hreflang 与结构校验结果。",
        "noindex": True,
    },
    "product/smart-camera.hreflang.html": {
        "title": "hreflang reference | MAIBIDA",
        "desc": "Reference list of hreflang alternate links for the smart camera page.",
        "noindex": True,
    },
    "index.en-AU.html": {
        "desc": "The Australia English edition has moved. Please use the current Singapore / Asia-Pacific English edition of the MAIBIDA website.",
    },
    "product/10032.en-AU.html": {
        "desc": "The Australia English edition of the MAIBIDA mold monitor product page has moved. Please use the current Singapore / Asia-Pacific English edition.",
    },
    "product/smart-camera.en-AU.html": {
        "desc": "The Australia English edition of the MAIBIDA smart camera product page has moved. Please use the current Singapore / Asia-Pacific English edition.",
    },
    "product/smart-camera.es-ES.html": {
        "desc": "Esta página en español de España se ha trasladado. Utilice la edición actual en español de México (es-MX) del sitio de MAIBIDA.",
    },
}


def esc(s):
    return html.escape(s, quote=True)


def lang_of(rel):
    m = re.search(r"\.([a-z]{2}-[A-Z]{2})\.html$", rel)
    if not m:
        return "zh-CN"
    return m.group(1) if m.group(1) in (["zh-CN"] + LOCALES) else "en-US"


def html_files():
    out = []
    for f in ROOT.rglob("*.html"):
        parts = set(f.parts)
        if parts & set(BACKUP_DIRS) or "tools" in parts:
            continue
        out.append(f)
    return sorted(out)


# ---------------------------------------------------------------- 1. backups
def move_backup_dirs():
    moved = []
    for name in BACKUP_DIRS:
        src = ROOT / name
        if not src.is_dir():
            continue
        OFFLINE.mkdir(parents=True, exist_ok=True)
        dst = OFFLINE / name
        n = sum(1 for p in src.rglob("*") if p.is_file())
        size = sum(p.stat().st_size for p in src.rglob("*") if p.is_file())
        shutil.move(str(src), str(dst))
        moved.append({"dir": name, "files": n, "bytes": size})
    return moved


# ---------------------------------------------------------------- 2. alt text
def load_alts():
    d = json.loads((ROOT / "tools/image-alt-i18n.json").read_text(encoding="utf-8"))
    langs = d["langs"]
    return {k: dict(zip(langs, v)) for k, v in d["alts"].items()}


def fix_alt(alts):
    total = 0
    pages = []
    for f in html_files():
        rel = f.relative_to(ROOT).as_posix()
        lang = lang_of(rel)
        text = f.read_bytes().decode("utf-8")
        changed = [0]

        def repl(m):
            tag = m.group(0)
            sm = SRC_RE.search(tag)
            src = (sm.group(1) or sm.group(2)) if sm else ""
            key = src.replace("\\", "/").rsplit("/", 1)[-1].split("?")[0]
            alt = alts.get(key, {}).get(lang)
            if not alt:
                return tag
            existing = ALT_RE.search(tag)
            if existing:
                new = tag[:existing.start()] + 'alt="' + esc(alt) + '"' + tag[existing.end():]
                # only rewrite when the value actually differs
                if new == tag:
                    return tag
            else:
                new = tag.replace("<img", '<img alt="' + esc(alt) + '"', 1)
            changed[0] += 1
            return new

        new_text = IMG_RE.sub(repl, text)
        if changed[0]:
            f.write_bytes(new_text.encode("utf-8"))
            total += changed[0]
            pages.append(rel)
    return total, pages


# ---------------------------------------------------------------- 3. aux pages
def fix_aux_pages():
    result = []
    for rel, meta in AUX.items():
        f = ROOT / rel
        if not f.exists():
            continue
        t = f.read_bytes().decode("utf-8")
        if "</head>" not in t:
            t = build_hreflang_document(meta)
            f.write_bytes(t.encode("utf-8"))
            result.append({"page": rel, "action": "rebuilt as complete noindex document"})
            continue
        inserts = []
        if not re.search(r"<title\b", t, re.I) and meta.get("title"):
            inserts.append("<title>" + esc(meta["title"]) + "</title>")
        if not re.search(r"<meta\s+name=[\"']description[\"']", t, re.I):
            inserts.append('<meta name="description" content="' + esc(meta["desc"]) + '"/>')
        if not re.search(r"<link\s+rel=[\"']canonical[\"']", t, re.I):
            inserts.append('<link rel="canonical" href="https://www.maibida.com/' + rel + '"/>')
        if meta.get("noindex") and not re.search(r"<meta\s+name=[\"']robots[\"']", t, re.I):
            inserts.append('<meta name="robots" content="noindex,nofollow"/>')
        if inserts:
            t = t.replace("</head>", "\n".join(inserts) + "\n</head>", 1)
            f.write_bytes(t.encode("utf-8"))
            result.append({"page": rel, "action": "inserted " + ", ".join(
                re.findall(r"<(\w+)", "\n".join(inserts)))})
    return result


def build_hreflang_document(meta):
    lines = []
    for lang in HREFLANG_LANGS:
        suffix = "" if lang == "zh-CN" else "." + lang
        lines.append('<link rel="alternate" hreflang="' + lang +
                     '" href="https://www.maibida.com/product/smart-camera' +
                     suffix + '.html"/>')
    lines.append('<link rel="alternate" hreflang="x-default" '
                 'href="https://www.maibida.com/product/smart-camera.en-US.html"/>')
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        '<title>' + esc(meta["title"]) + '</title>\n'
        '<meta name="description" content="' + esc(meta["desc"]) + '"/>\n'
        '<meta name="robots" content="noindex,nofollow"/>\n'
        '<link rel="canonical" href="https://www.maibida.com/product/smart-camera.hreflang.html"/>\n'
        '<style>body{font:14px/1.7 Arial,sans-serif;padding:28px;color:#223;max-width:900px}'
        'code{display:block;background:#f5f7fa;padding:14px;border-radius:8px;white-space:pre-wrap;word-break:break-all}</style>\n'
        '</head>\n<body>\n'
        '<h1>hreflang reference (MAIBIDA smart camera)</h1>\n'
        '<p>Internal reference snippet for deployment. This page is not part of the public site and is excluded from indexing.</p>\n'
        '<code>' + esc("\n".join(lines)) + '</code>\n'
        '</body>\n</html>\n')


# ---------------------------------------------------------------- 4. robots
def fix_robots():
    f = ROOT / "robots.txt"
    old = f.read_text(encoding="utf-8")
    if old == ROBOTS:
        return "already-current"
    f.write_text(ROBOTS, encoding="utf-8")
    return "updated"


# ---------------------------------------------------------------- dead links
def dead_links():
    bad = []
    for f in html_files():
        rel = f.relative_to(ROOT).as_posix()
        t = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'<a\b[^>]*\bhref\s*=\s*"([^"]*)"', t, re.I):
            h = m.group(1).strip()
            if not h or h.startswith(("#", "javascript:", "mailto:", "tel:", "http://", "https://", "//")):
                continue
            target = ((ROOT / rel).parent / h.split("#")[0].split("?")[0]).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target.exists():
                bad.append((rel, h))
    return bad


def main():
    alts = load_alts()
    moved = move_backup_dirs()
    n_alt, alt_pages = fix_alt(alts)
    aux = fix_aux_pages()
    robots = fix_robots()
    broken = dead_links()

    if moved:
        offline_root = str(OFFLINE)
    else:
        existing = sorted(ROOT.parent.glob("maibida-ocr-rebuilt_offline_backups_*"))
        offline_root = str(existing[-1]) if existing else None

    manifest = {
        "timestamp": TS,
        "offline_backup_root": offline_root,
        "backup_dirs_moved": moved,
        "localized_alt_insertions": n_alt,
        "localized_alt_pages": len(alt_pages),
        "alt_resources": len(alts),
        "aux_pages_fixed": aux,
        "robots_txt": robots,
        "remaining_dead_links": len(broken),
        "remaining_dead_link_samples": [f"{a} -> {b}" for a, b in broken[:20]],
        "layout_changed": False,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items()
                      if k not in ("aux_pages_fixed", "backup_dirs_moved")},
                     ensure_ascii=False, indent=2))
    print("backup_dirs_moved =", [m["dir"] for m in moved])
    print("aux_pages_fixed =", len(aux))


if __name__ == "__main__":
    main()
