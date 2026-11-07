# -*- coding: utf-8 -*-
"""Read-only probe for the pre-launch compliance / functional / SEO / content audit.

Collects raw evidence from the deployable HTML tree. Never modifies a page.
Outputs tools/compliance-audit-data.json plus a compact stdout summary.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OUT = TOOLS / "compliance-audit-data.json"

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
BASE_PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
              "productlist/10029.html", "productlist/10030.html",
              "productlist/10034.html", "productlist/10036.html",
              "productlist/10039.html"]
LEGACY_PAGES = ["index.en-AU.html", "product/10032.en-AU.html",
                "product/smart-camera.en-AU.html", "product/smart-camera.es-ES.html"]
TOOL_PAGES = {"localization-glossary.html",
              "product/smart-camera-localization-report.html",
              "product/smart-camera.hreflang.html"}
EXCLUDE_DIRS = {"tools", "productInfo_bak_seo", "UserFiles_bak_bigimg",
                "_bak_footnav", "_bak_foot_full", "_bak_pathfix",
                "_bak_wxqrcode", "node_modules"}

# ---------------------------------------------------------------- lexicons
ZH_SUPERLATIVES = [
    "最好", "最佳", "最优", "最先进", "最强", "最高端", "最低价", "最便宜",
    "最专业", "最全面", "全网最低", "行业第一", "全国第一", "世界第一", "第一品牌",
    "唯一指定", "首家", "首创", "独家", "顶级", "顶尖", "极致", "完美无缺",
    "100%保证", "百分百保证", "绝对保证", "零缺陷", "零故障", "永不", "终身",
    "包您满意", "彻底解决", "完全避免", "国家免检", "免检产品", "国际领先",
    "世界一流", "销量第一", "无敌", "史上最", "领先全球",
]
ZH_SOFT = ["保证", "承诺", "100%", "领先", "免费", "最", "零误判", "零漏检"]
EN_SUPERLATIVES = [
    r"\bbest\b", r"\bNo\.?\s*1\b", r"\bnumber\s+one\b", r"\btop[- ]rated\b",
    r"\bworld[- ]leading\b", r"\bindustry[- ]leading\b", r"\bmost\s+advanced\b",
    r"\b100%\s*guarantee", r"\bfully\s+guaranteed\b", r"\blowest\s+price\b",
    r"\bunbeatable\b", r"\bflawless\b", r"\bzero\s+defect", r"\bperfect\b",
    r"\bguaranteed\b", r"\bnever\s+fail", r"\b100%\s*accur", r"\bworld[- ]class\b",
    r"\bthe\s+only\b", r"\bfirst[- ]class\b", r"\bultimate\b",
]
ES_SUPERLATIVES = [
    r"\bmejor\b", r"\bn[úu]mero\s+uno\b", r"\b100%\s*garantizad",
    r"\bprecio\s+m[áa]s\s+bajo\b", r"\bperfect[oa]\b", r"\bcero\s+defectos\b",
    r"\bl[íi]der\s+mundial\b", r"\binsuperable\b", r"\bgarantizad",
    r"\bel\s+[úu]nico\b", r"\bprimera\s+calidad\b",
]
OTHER_SUPERLATIVES = [
    r"\bterbaik\b", r"\b100%\s*dijamin\b", r"\bterbaik\s+di\b",           # id / ms
    r"ดีที่สุด", r"รับประกัน\s*100%",                                       # th
    r"tốt nhất", r"đảm bảo\s*100%", r"hàng đầu",                           # vi
    r"최고의", r"100%\s*보장", r"세계 최고",                                  # ko
    r"最高", r" No\.?1", r"100%\s*保証", r"業界一",                            # ja
    r"лучший", r"100%\s*гаранти", r"№\s*1",                                  # ru
]
BRANDS = [
    "Keyence", "Cognex", "Omron", "Siemens", "Panasonic", "Mitsubishi", "Basler",
    "Sony", "Canon", "Nikon", "Samsung", "LG ", "Huawei", "Apple", "Microsoft",
    "Intel", "NVIDIA", "ABB", "Fanuc", "Yaskawa", "SICK", "Banner Engineering",
    "ifm", "Datalogic", "Honeywell", "Bosch", "Schneider", "Rockwell", "Adobe",
    "基恩士", "康耐视", "欧姆龙", "西门子", "松下", "三菱", "索尼", "佳能", "尼康",
    "百度", "Baidu", "阿里巴巴", "Alibaba", "淘宝", "京东", "腾讯", "微信",
]
SENSITIVE = [
    "军用", "武器", "管制", "违禁", "赌博", "色情", "代开票", "走私", "翻墙",
    "military grade", "weapons", "ITAR", "gambling", "porn", "counterfeit",
    "replica", "cracked", "pirated",
]
DISCLAIMER_MARKERS = [
    "免责", "仅供参考", "以实物为准", "如有变更", "恕不另行通知", "不承担",
    "disclaimer", "subject to change", "without notice", "for reference only",
    " specifications are", "no liability", "Descargo de responsabilidad",
    "sujeto a cambios", "仅供", "最终解释权",
]
PRIVACY_MARKERS = [
    "privacy", "privacidad", "datenschutz", "politique de confidentialité",
    "隐私", "个人信息", "隐私政策", "privacy policy", "política de privacidad",
    "data protection", "GDPR", "PDPA", "LFPDPPP", "cookie policy", "cookies",
]
OFFENSIVE = [
    r"\bcheap\s+chinese\b", r"\bthird[- ]world\b", r"\blow[- ]class\b",
    r"\binferior\b", r"\bbackward\b", r"chino barato", r"barato chino",
    r"made in china\s+cheap",
]

REF_TAGS = [("img", "src"), ("script", "src"), ("link", "href"),
            ("source", "src"), ("video", "src"), ("audio", "src"),
            ("iframe", "src"), ("embed", "src"), ("input", "src"), ("a", "href")]
LOCAL_SCHEMES = ("#", "javascript:", "mailto:", "tel:", "data:", "about:")


# ---------------------------------------------------------------- helpers
def deployable_pages():
    for f in sorted(ROOT.rglob("*.html")):
        if set(f.parts) & EXCLUDE_DIRS:
            continue
        yield f


def classify(rel: str) -> str:
    if re.search(r"\.html$", rel) and Path(rel).name.startswith("contact"):
        return "contact"
    if rel in LEGACY_PAGES or re.search(r"\.(en-AU|es-ES)\.html$", rel):
        return "legacy"
    if rel in TOOL_PAGES:
        return "tool"
    if re.search(r"\.[a-z]{2}-[A-Z]{2}\.html$", rel):
        return "official_i18n"
    if rel in BASE_PAGES:
        return "official_zh"
    return "other"


def visible_text(soup):
    skip_tags = {"script", "style", "noscript", "template", "svg", "iframe"}
    out = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        par = node.parent
        if par is None or par.name == "[document]":
            continue
        if any(p.name in skip_tags for p in node.parents if getattr(p, "name", None)):
            continue
        t = str(node).strip()
        if t:
            out.append(t)
    return "\n".join(out)


def footer_text(soup):
    chunks = []
    for el in soup.find_all(["footer", "div", "p"]):
        cls = " ".join(el.get("class", []))
        cid = el.get("id", "") or ""
        if el.name == "footer" or re.search(r"foot|bottom|copyright|copy", cls + " " + cid, re.I):
            t = el.get_text(" ", strip=True)
            if t and len(t) < 1200:
                chunks.append(t)
    return "\n".join(dict.fromkeys(chunks))


def hits(text: str, patterns, flags=re.I):
    found = []
    for p in patterns:
        for m in re.finditer(p, text, flags):
            found.append({"pattern": p, "match": m.group(0)[:80],
                          "context": re.sub(r"\s+", " ", text[max(0, m.start()-55):m.end()+55])[:170]})
    return found


def main():
    data = {
        "pages": [], "stats": {}, "findings": defaultdict(list),
        "titles": {}, "descriptions": {}, "h1_counts": {}, "langs": {},
        "contacts": defaultdict(lambda: defaultdict(set)),
        "sitemap_urls": [], "robots_text": "",
    }

    all_files = list(deployable_pages())
    all_rel = [f.relative_to(ROOT).as_posix() for f in all_files]
    existing = set(all_rel)

    title_counter = Counter()
    desc_counter = Counter()
    broken = []
    http_resources = []
    http_links = []
    missing_alt = []
    noindex_official = []
    canonical_missing = []
    h1_bad = []
    lang_menu_bad = []
    form_info = {}

    for f in all_files:
        rel = f.relative_to(ROOT).as_posix()
        kind = classify(rel)
        raw = f.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")
        text = visible_text(soup)
        foot = footer_text(soup)
        lang_attr = (soup.find("html").get("lang") if soup.find("html") else "") or ""
        is_zh = (kind == "official_zh") or lang_attr.lower().startswith("zh")
        is_ja = "ja" in lang_attr.lower()

        title = (soup.title.get_text(strip=True) if soup.title else "")
        desc_el = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
        desc = desc_el.get("content", "").strip() if desc_el else ""
        robots_el = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
        robots = robots_el.get("content", "").strip() if robots_el else ""
        canon = soup.find("link", attrs={"rel": lambda v: v and "canonical" in v})
        canon_href = canon.get("href", "") if canon else ""
        h1s = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
        h2s = soup.find_all("h2")
        imgs = soup.find_all("img")

        data["pages"].append({"rel": rel, "kind": kind, "lang": lang_attr,
                              "bytes": f.stat().st_size, "title": title,
                              "description": desc, "robots": robots,
                              "canonical": canon_href, "h1": h1s,
                              "h2_count": len(h2s), "img_count": len(imgs)})
        if title:
            title_counter[title] += 1
        if desc:
            desc_counter[desc] += 1
        data["langs"][rel] = lang_attr

        # ---- meta quality
        if not title:
            data["findings"]["title_missing"].append({"page": rel})
        if not desc:
            data["findings"]["desc_missing"].append({"page": rel})
        if len(h1s) != 1:
            h1_bad.append({"page": rel, "kind": kind, "count": len(h1s)})
        if not canon_href and kind in ("official_zh", "official_i18n"):
            canonical_missing.append({"page": rel, "kind": kind})
        if "noindex" in robots.lower() and kind in ("official_zh", "official_i18n"):
            noindex_official.append({"page": rel, "robots": robots})
        if kind in ("official_zh", "official_i18n"):
            details = soup.find_all("details", class_="vp-language-switch")
            items = soup.select(".vp-language-switch a[href]")
            if len(details) != 1 or len(items) < 10:
                lang_menu_bad.append({"page": rel, "details": len(details), "items": len(items)})

        # ---- images / alt
        for im in imgs:
            src = (im.get("src") or "").strip()
            alt = im.get("alt")
            if alt is None or not str(alt).strip():
                missing_alt.append({"page": rel, "src": src[:140]})

        # ---- local references / mixed content
        for tag, attr in REF_TAGS:
            for el in soup.find_all(tag):
                v = (el.get(attr) or "").strip()
                if not v:
                    continue
                if v.startswith("http://"):
                    rec = {"page": rel, "tag": tag, "url": v[:180]}
                    (http_resources if tag != "a" else http_links).append(rec)
                if v.startswith(("http://", "https://", "//",) ) or v.startswith(LOCAL_SCHEMES):
                    continue
                tgt = unquote(v.split("#")[0].split("?")[0])
                if not tgt:
                    continue
                try:
                    resolved = ((ROOT / rel).parent / tgt).resolve()
                    rel_t = resolved.relative_to(ROOT).as_posix()
                    ok = resolved.exists()
                except (ValueError, OSError):
                    rel_t, ok = tgt, False
                if not ok:
                    broken.append({"page": rel, "tag": tag, "target": tgt[:150]})

        # ---- compliance lexicons (visible text + meta + alt)
        scan_text = "\n".join([text, title, desc, foot,
                               " ".join(str(im.get("alt", "")) for im in imgs)])
        if is_zh:
            hh = hits(scan_text, [re.escape(w) for w in ZH_SUPERLATIVES])
            if hh:
                data["findings"]["zh_superlative"].append({"page": rel, "hits": hh[:8]})
            soft = hits(scan_text, [re.escape(w) for w in ZH_SOFT])
            if soft:
                data["findings"]["zh_soft_claim"].append({"page": rel, "hits": soft[:8]})
        if not is_zh or is_ja:
            ext = hits(scan_text, EN_SUPERLATIVES + ES_SUPERLATIVES + OTHER_SUPERLATIVES)
            if ext:
                data["findings"]["foreign_superlative"].append(
                    {"page": rel, "lang": lang_attr, "hits": ext[:8]})
            off = hits(scan_text, OFFENSIVE)
            if off:
                data["findings"]["offensive"].append({"page": rel, "hits": off[:6]})

        bh = hits(scan_text, [re.escape(b) for b in BRANDS])
        if bh:
            data["findings"]["third_party_brand"].append({"page": rel, "hits": bh[:6]})
        sh = hits(scan_text, [re.escape(w) for w in SENSITIVE])
        if sh:
            data["findings"]["sensitive"].append({"page": rel, "hits": sh[:6]})
        dh = hits(scan_text, [re.escape(w) for w in DISCLAIMER_MARKERS])
        if dh:
            data["findings"]["disclaimer_marker"].append({"page": rel, "hits": dh[:4]})
        ph = hits(scan_text, [re.escape(w) for w in PRIVACY_MARKERS])
        if ph:
            data["findings"]["privacy_marker"].append({"page": rel, "hits": ph[:4]})

        # ---- copyright
        if foot:
            cr = re.findall(r"[©℗]|copyright|版权所有|all rights reserved|版权声明",
                            foot, re.I)
            data["findings"]["copyright_sample"].append(
                {"page": rel, "marks": sorted(set(x.lower() for x in cr)),
                 "snippet": re.sub(r"\s+", " ", foot)[:230]})

        # ---- contact information
        for m in re.finditer(r"wa\.me/([0-9+]+)|api\.whatsapp\.com/send\?phone=([0-9+]+)", raw, re.I):
            data["contacts"]["whatsapp"][m.group(1) or m.group(2)].add(rel)
        for m in re.finditer(r"tel:([+0-9\-() ]{6,25})", raw, re.I):
            data["contacts"]["tel"][m.group(1).strip()].add(rel)
        for m in re.finditer(r"mailto:([^\s\"'<>?]+)", raw, re.I):
            data["contacts"]["email"][m.group(1)].add(rel)
        for m in re.finditer(r"(\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b)", text):
            data["contacts"]["email_text"][m.group(1)].add(rel)
        for m in re.finditer(r"(\+?86[- ]?1[3-9]\d{9}|\+?86[- ]?\d{3,4}[- ]?\d{7,8}|(?<!\d)1[3-9]\d{9}(?!\d))", text):
            data["contacts"]["phone_text"][m.group(1)].add(rel)
        for m in re.finditer(r"地\s*址[：:]\s*([^\n<]{6,90})|(?:Address|Address:|Direcci[óo]n|住所|주소)[：:\s]*([^\n<]{10,140})", text):
            v = (m.group(1) or m.group(2) or "").strip()
            if v:
                data["contacts"]["address"][v[:110]].add(rel)

        # ---- form / consent
        if kind == "contact":
            form = soup.find("form")
            consents = soup.find_all("input", attrs={"type": "checkbox"})
            form_info[rel] = {
                "form": bool(form),
                "action": form.get("action") if form else "",
                "method": (form.get("method") or "").lower() if form else "",
                "fields": [i.get("name") for i in soup.select("[name]") if i.get("name")],
                "checkboxes": len(consents),
                "privacy_link": bool(re.search(r"privacy|privacidad|隐私", raw, re.I)),
                "required": len(soup.select("[required]")),
            }

    # ---- duplicate titles / descriptions
    data["findings"]["duplicate_titles"] = [
        {"title": t[:120], "count": n,
         "pages": [p["rel"] for p in data["pages"] if p["title"] == t][:14]}
        for t, n in title_counter.items() if n > 1]
    data["findings"]["duplicate_descriptions"] = [
        {"description": d[:140], "count": n,
         "pages": [p["rel"] for p in data["pages"] if p["description"] == d][:14]}
        for d, n in desc_counter.items() if n > 1]

    # ---- privacy / legal page existence
    legal_like = [r for r in all_rel
                  if re.search(r"privacy|privacidad|privat|policy|política|terms|terminos|términos|legal|disclaimer|cookie|aviso", r, re.I)]
    data["findings"]["legal_pages"] = legal_like

    # ---- brand names in asset filenames
    asset_brand = []
    for f in ROOT.rglob("*"):
        if not f.is_file() or set(f.parts) & EXCLUDE_DIRS:
            continue
        if f.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4"}:
            continue
        nm = f.name
        for b in BRANDS:
            if b.strip() and b.strip().lower() in nm.lower():
                asset_brand.append({"file": f.relative_to(ROOT).as_posix(), "brand": b})
                break
    data["findings"]["brand_in_asset_name"] = asset_brand[:40]

    # ---- robots / sitemap
    robots_p = ROOT / "robots.txt"
    if robots_p.exists():
        data["robots_text"] = robots_p.read_text(encoding="utf-8", errors="replace")
    sm = ROOT / "sitemap.xml"
    sm_text = sm.read_text(encoding="utf-8", errors="replace") if sm.exists() else ""
    urls = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", sm_text)
    data["sitemap_urls"] = urls
    official = [p["rel"] for p in data["pages"] if p["kind"] in ("official_zh", "official_i18n")]
    sm_paths = {unquote(urlparse(u).path.lstrip("/")) for u in urls}
    data["findings"]["official_not_in_sitemap"] = [r for r in official if r not in sm_paths]
    data["findings"]["sitemap_only"] = sorted(sm_paths - set(all_rel))[:40]
    blocked = re.findall(r"Disallow:\s*(\S+)", data["robots_text"])
    data["findings"]["robots_disallow"] = blocked
    data["findings"]["robots_blocks_official"] = [
        r for r in official for b in blocked
        if b not in ("/",) and b.strip("/") and ("/" + r).startswith(b)]

    # ---- oversized assets without WebP sibling
    large = []
    for f in ROOT.rglob("*"):
        if not f.is_file() or set(f.parts) & EXCLUDE_DIRS:
            continue
        if f.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".js", ".css"}:
            continue
        sz = f.stat().st_size
        limit = 5 * 1024 * 1024 if f.suffix.lower() == ".mp4" else 500 * 1024
        if sz <= limit:
            continue
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif"} and f.with_suffix(".webp").exists():
            continue
        large.append({"file": f.relative_to(ROOT).as_posix(), "kb": round(sz / 1024)})
    data["findings"]["large_resources"] = sorted(large, key=lambda x: -x["kb"])[:25]

    # ---- aggregate buckets
    data["findings"]["broken_links"] = broken
    data["findings"]["http_resources"] = http_resources
    data["findings"]["http_links"] = http_links
    data["findings"]["missing_alt"] = missing_alt
    data["findings"]["noindex_official"] = noindex_official
    data["findings"]["canonical_missing"] = canonical_missing
    data["findings"]["h1_bad"] = h1_bad
    data["findings"]["lang_menu_bad"] = lang_menu_bad
    data["form_info"] = form_info

    kinds = Counter(p["kind"] for p in data["pages"])
    data["stats"] = {
        "deployable_pages": len(data["pages"]),
        "kinds": dict(kinds),
        "official_pages": len(official),
        "sitemap_urls": len(urls),
        "broken_links": len(broken),
        "http_resources": len(http_resources),
        "http_links": len(http_links),
        "missing_alt": len(missing_alt),
        "noindex_official": len(noindex_official),
        "canonical_missing": len(canonical_missing),
        "h1_bad": len(h1_bad),
        "lang_menu_bad": len(lang_menu_bad),
        "duplicate_title_groups": len(data["findings"]["duplicate_titles"]),
        "duplicate_desc_groups": len(data["findings"]["duplicate_descriptions"]),
        "legal_pages": len(legal_like),
        "zh_superlative_pages": len(data["findings"]["zh_superlative"]),
        "foreign_superlative_pages": len(data["findings"]["foreign_superlative"]),
        "third_party_brand_pages": len(data["findings"]["third_party_brand"]),
        "disclaimer_pages": len(data["findings"]["disclaimer_marker"]),
        "privacy_marker_pages": len(data["findings"]["privacy_marker"]),
        "sensitive_pages": len(data["findings"]["sensitive"]),
        "offensive_pages": len(data["findings"]["offensive"]),
        "large_resources": len(large),
    }

    # serialise sets
    contacts = {}
    for grp, vals in data["contacts"].items():
        contacts[grp] = {k: sorted(v) for k, v in vals.items()}
    data["contacts"] = contacts
    data["findings"] = dict(data["findings"])

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data["stats"], ensure_ascii=False, indent=2))
    print("\n--- KEY EVIDENCE ---")
    for key in ("legal_pages", "zh_superlative", "foreign_superlative",
                "third_party_brand", "disclaimer_marker", "privacy_marker",
                "sensitive", "offensive", "duplicate_titles",
                "robots_disallow", "robots_blocks_official",
                "official_not_in_sitemap", "large_resources"):
        v = data["findings"].get(key, [])
        print(f"\n[{key}] count={len(v)}")
        for x in (v[:6] if isinstance(v, list) else []):
            print("   ", json.dumps(x, ensure_ascii=False)[:330])
    print("\n--- CONTACTS ---")
    for grp, vals in contacts.items():
        print(f"[{grp}] {len(vals)} distinct")
        for k, pages in list(vals.items())[:8]:
            print(f"   {k[:90]}  <- {len(pages)} pages")
    print("\n--- FORM SAMPLE ---")
    for k, v in list(form_info.items())[:2]:
        print(" ", k, json.dumps(v, ensure_ascii=False))
    print("\nOUTPUT:", OUT)


if __name__ == "__main__":
    main()
