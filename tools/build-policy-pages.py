"""Generate 11-locale Privacy Policy and Terms of Sale pages (idempotent).

These are auxiliary pages: they are registered as TOOL_PAGES in the audit,
linked from every formal page footer, allowed to be indexed, but deliberately
kept out of sitemap.xml so the 88 formal-page / 88-URL scoring scope stays
unchanged.
"""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import compliance_i18n as C

ROOT = Path(__file__).resolve().parent.parent
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT.parent / f"maibida-ocr-rebuilt_policy_backup_{TS}"


def esc(s):
    return html.escape(str(s), quote=True)


def rel(kind, lang):
    return f"{kind}.html" if lang == "zh-CN" else f"{kind}.{lang}.html"


def home(lang):
    return "index.html" if lang == "zh-CN" else f"index.{lang}.html"


POLICY_CSS = """*{box-sizing:border-box}
body{margin:0;background:#f6f9f7;color:#26313a;font-family:Arial,"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.75}
.pl-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 24px;background:#fff;border-bottom:1px solid #e4ebe7}
.pl-head img{height:44px;width:auto;max-width:220px}
.pl-nav{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.pl-nav a{color:#087b3d;text-decoration:none;font-size:14px;font-weight:700}
.pl-nav a:hover,.pl-nav a:focus{text-decoration:underline}
.pl-main{max-width:860px;margin:36px auto 72px;padding:0 20px}
.pl-main h1{margin:0 0 12px;font-size:clamp(26px,3vw,34px);color:#17352a}
.pl-lead{margin:0 0 26px;color:#4d5b64;font-size:16px}
.pl-section{padding:18px 22px;margin:0 0 14px;background:#fff;border:1px solid #dfe7e3;border-radius:12px}
.pl-section h2{margin:0 0 8px;font-size:18px;color:#17352a}
.pl-section p{margin:0;font-size:15px;color:#3b474f}
.pl-meta{margin:22px 0 0;font-size:13px;color:#68747d;border-top:1px solid #dfe7e3;padding-top:16px}
.pl-foot{margin:30px 0 0;display:flex;gap:18px;flex-wrap:wrap;font-size:14px}
.pl-foot a{color:#087b3d;text-decoration:none;font-weight:700}
@media(max-width:640px){.pl-head{padding:12px 16px}.pl-head img{height:34px}.pl-main{margin:24px auto 48px}.pl-section{padding:16px}}
"""


def page_html(kind, lang, data):
    is_policy = kind == "privacy"
    other = "terms" if is_policy else "privacy"
    own_rel = rel(kind, lang)
    p, t, _ = C.FOOTER_LABELS[lang]
    own_label = p if is_policy else t
    other_label = t if is_policy else p
    sections = "\n".join(
        f'<section class="pl-section"><h2>{esc(h)}</h2><p>{esc(b)}</p></section>'
        for h, b in data["sections"])
    desc = re.sub(r"\s+", " ", data["lead"])[:155]
    meta = (f"版本 {C.POLICY_VERSION} &middot; 生效日期 {C.EFFECTIVE_DATE}"
            if lang == "zh-CN" else
            f"Version {C.POLICY_VERSION} &middot; Effective {C.EFFECTIVE_DATE}")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="https://www.maibida.com/{own_rel}"/>
<title>{esc(data['title'])} | Maibida</title>
<link href="cn/css/policy.css" rel="stylesheet"/>
</head>
<body>
<header class="pl-head">
<a href="{home(lang)}"><img alt="Maibida" src="UserFiles/upload/image/20260130/6390537782397634082084337.png"/></a>
<nav class="pl-nav" aria-label="{esc(own_label)}">
<a href="{home(lang)}">{esc(data['back'])}</a>
<a href="{rel(other, lang)}">{esc(other_label)}</a>
</nav>
</header>
<main class="pl-main">
<h1>{esc(data['title'])}</h1>
<p class="pl-lead">{esc(data['lead'])}</p>
{sections}
<p class="pl-meta">{meta} &middot; {esc(C.COMPANY_EN)} &middot; {esc(C.EMAIL)}</p>
<p class="pl-foot"><a href="{home(lang)}">{esc(data['back'])}</a><a href="{rel(other, lang)}">{esc(other_label)}</a></p>
</main>
</body>
</html>
"""


def register_audit_pages():
    f = ROOT / "tools/full-site-audit.py"
    t = f.read_bytes().decode("utf-8")
    m = re.search(r"TOOL_PAGES\s*=\s*\[[^\]]*\]", t, re.S)
    if not m:
        return "FAILED"
    if '"privacy.html"' in m.group(0):
        return "already-present"
    block = ('TOOL_PAGES = ["localization-glossary.html", '
             '"product/smart-camera-localization-report.html", '
             '"product/smart-camera.hreflang.html", "contact.html", '
             '"privacy.html", "terms.html"] '
             '+ ["contact." + l + ".html" for l in LOCALES] '
             '+ ["privacy." + l + ".html" for l in LOCALES] '
             '+ ["terms." + l + ".html" for l in LOCALES]')
    f.write_bytes(t.replace(m.group(0), block, 1).encode("utf-8"))
    return "registered"


def main():
    targets = [rel(k, l) for k in ("privacy", "terms") for l in C.LANGS] + [
        "cn/css/policy.css", "tools/full-site-audit.py"]
    existing = [r for r in targets if (ROOT / r).exists()]
    if existing:
        BACKUP.mkdir(parents=True, exist_ok=True)
        for r in existing:
            src = ROOT / r
            dst = BACKUP / r
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (ROOT / "cn/css/policy.css").write_bytes(POLICY_CSS.encode("utf-8"))
    made = []
    for kind, store in (("privacy", C.POLICY), ("terms", C.TERMS)):
        for lang in C.LANGS:
            f = ROOT / rel(kind, lang)
            f.write_bytes(page_html(kind, lang, store[lang]).encode("utf-8"))
            made.append(f.name)
    audit = register_audit_pages()
    summary = {
        "timestamp": TS, "backup": str(BACKUP) if existing else None,
        "pages": made, "page_count": len(made),
        "css": "cn/css/policy.css", "audit_registration": audit,
        "sitemap_changed": False,
        "indexable": True,
        "policy_version": C.POLICY_VERSION,
        "effective_date": C.EFFECTIVE_DATE,
        "retention_months": C.RETENTION_MONTHS,
    }
    (ROOT / "tools/policy-pages.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "pages"},
                     ensure_ascii=False, indent=2))
    if audit == "FAILED":
        raise SystemExit("FAILED: audit registration")


if __name__ == "__main__":
    main()
