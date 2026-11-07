# -*- coding: utf-8 -*-
"""Read-only precision re-check of compliance probe hits (false-positive filtering)."""
from __future__ import annotations
import json, re
from pathlib import Path
from collections import Counter, defaultdict
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "tools/compliance-audit-data.json").read_text(encoding="utf-8"))
PAGES = [p["rel"] for p in D["pages"]]
OFFICIAL = [p["rel"] for p in D["pages"] if p["kind"] in ("official_zh", "official_i18n")]

BRAND_WORD = re.compile(
    r"\b(?:Keyence|Cognex|Omron|Siemens|Panasonic|Mitsubishi|Basler|Sony|Canon|Nikon|"
    r"Samsung|Huawei|Apple|Microsoft|Intel|NVIDIA|ABB|Fanuc|Yaskawa|SICK|Datalogic|"
    r"Honeywell|Bosch|Schneider|Rockwell|Adobe|Baidu|Alibaba|Tencent|WeChat|WhatsApp|"
    r"Google|Facebook|YouTube)\b|基恩士|康耐视|欧姆龙|西门子|松下|三菱|索尼|佳能|尼康|百度|阿里巴巴|淘宝|京东|腾讯|微信",
    re.I)
SENS_WORD = re.compile(
    r"\b(?:military grade|weapons|ITAR|gambling|porn|counterfeit|replica|cracked|pirated)\b|"
    r"军用|武器|管制|违禁|赌博|色情|代开票|走私|翻墙", re.I)
SUPER_WORD = re.compile(
    r"\b(?:best|No\.?\s*1|number one|top[- ]rated|world[- ]leading|industry[- ]leading|"
    r"most advanced|100%\s*guaranteed?|lowest price|unbeatable|flawless|zero defects?|"
    r"perfect|guaranteed|world[- ]class|the only|ultimate)\b|"
    r"\b(?:mejor|n[úu]mero uno|100%\s*garantizad\w*|precio m[áa]s bajo|perfect[oa]|"
    r"cero defectos|l[íi]der mundial|insuperable|el [úu]nico)\b|"
    r"最好|最佳|最先进|全网最低|行业第一|世界第一|100%保证|零缺陷|零故障|国际领先|世界一流|顶级|顶尖|唯一|首创|独家",
    re.I)

out = {}

# 1) precise brand / sensitive / superlative hits over visible text
brand_hits, sens_hits, super_hits = [], [], []
for rel in PAGES:
    f = ROOT / rel
    raw = f.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    for n in soup.find_all(string=True):
        if getattr(n.parent, "name", "") in {"script", "style", "noscript", "template"}:
            continue
        t = str(n).strip()
        if not t:
            continue
        for m in BRAND_WORD.finditer(t):
            brand_hits.append({"page": rel, "brand": m.group(0),
                               "ctx": re.sub(r"\s+", " ", t[max(0, m.start()-70):m.end()+70])[:170]})
        for m in SENS_WORD.finditer(t):
            sens_hits.append({"page": rel, "word": m.group(0), "ctx": t[max(0, m.start()-60):m.end()+60]})
        for m in SUPER_WORD.finditer(t):
            super_hits.append({"page": rel, "word": m.group(0),
                               "ctx": re.sub(r"\s+", " ", t[max(0, m.start()-70):m.end()+70])[:170]})
out["brand_hits"] = brand_hits[:40]
out["brand_hits_count"] = len(brand_hits)
out["sensitive_hits"] = sens_hits[:20]
out["sensitive_hits_count"] = len(sens_hits)
out["superlative_hits"] = super_hits[:30]
out["superlative_hits_count"] = len(super_hits)

# 2) copyright blocks
cp = {}
for rel in ["index.html", "index.en-US.html", "index.es-MX.html", "index.ja-JP.html",
            "product/10032.html", "product/10032.en-US.html", "contact.html",
            "productlist/10039.html"]:
    soup = BeautifulSoup((ROOT / rel).read_text(encoding="utf-8", errors="replace"), "html.parser")
    blocks = []
    for el in soup.find_all(["footer", "div", "p"]):
        txt = el.get_text(" ", strip=True)
        if re.search(r"©|copyright|版权所有|all rights reserved|ICP|备案", txt, re.I) and len(txt) < 900:
            blocks.append(re.sub(r"\s+", " ", txt)[:400])
    cp[rel] = list(dict.fromkeys(blocks))[:2]
out["copyright"] = cp

# 3) contact links: wa.me / tel: / mailto:
links = defaultdict(lambda: defaultdict(set))
for rel in OFFICIAL:
    raw = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'href\s*=\s*["\']([^"\']*(?:wa\.me|whatsapp|tel:|mailto:)[^"\']*)["\']', raw, re.I):
        h = m.group(1)
        key = "whatsapp" if ("wa.me" in h or "whatsapp" in h) else ("tel" if h.startswith("tel:") else "mailto")
        links[key][h].add(rel)
    for m in re.finditer(r"<a\b[^>]*>([^<]{0,60})</a>", raw, re.I):
        if re.search(r"15995675085|mai_bida@163", m.group(1)):
            links["plain_contact_text"][m.group(1).strip()].add(rel)
out["contact_links"] = {k: {h: len(v) for h, v in d.items()} for k, d in links.items()}

# 4) company names from JSON-LD
names = defaultdict(set)
for rel in PAGES:
    raw = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'"legalName"\s*:\s*"([^"]+)"|"name"\s*:\s*"([^"]+)"', raw):
        v = m.group(1) or m.group(2)
        if v and ("Maibida" in v or "迈" in v or "MAIBIDA" in v or "昆山" in v):
            names[v].add(rel)
out["company_names"] = {k: len(v) for k, v in names.items()}

# 5) WebP siblings for the 9 large resources
webp = []
for item in D["findings"]["large_resources"]:
    p = ROOT / item["file"]
    sibs = [str(x.name) for x in p.parent.glob(p.name + "*")]
    webp.append({"file": item["file"], "kb": item["kb"], "siblings": sibs[:6],
                 "has_webp": any(s.lower().endswith(".webp") for s in sibs)})
out["large_asset_webp"] = webp

# 6) privacy wording inside contact pages
prv = {}
for rel in ["contact.html", "contact.en-US.html", "contact.es-MX.html"]:
    raw = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    prv[rel] = [re.sub(r"\s+", " ", m.group(0))[:200]
                for m in re.finditer(r".{0,90}privacy.{0,90}", raw, re.I)][:4]
out["contact_privacy_raw"] = prv

# 7) asset filenames / alts containing watermark or third-party brands
watermark = []
for f in ROOT.rglob("*"):
    if not f.is_file() or set(f.parts) & {"tools", "productInfo_bak_seo", "UserFiles_bak_bigimg"}:
        continue
    if re.search(r"baidu|百度|AI生成|watermark|水印|logo_|weixin|wechat|qrcode", f.name, re.I):
        watermark.append(f.relative_to(ROOT).as_posix())
out["watermark_named_assets"] = watermark[:40]
transcript = ROOT / "tools/image-text-transcripts.json"
if transcript.exists():
    tj = json.loads(transcript.read_text(encoding="utf-8"))
    s = json.dumps(tj, ensure_ascii=False)
    out["transcript_baidu_mentions"] = len(re.findall(r"百度|AI 生成|AI生成|Baidu", s, re.I))
else:
    out["transcript_baidu_mentions"] = None

# 8) robots + sitemap head
out["robots_txt"] = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="replace")
out["sitemap_head"] = (ROOT / "sitemap.xml").read_text(encoding="utf-8", errors="replace")[:600]

# 9) duplicate title detail
out["duplicate_titles"] = D["findings"]["duplicate_titles"]

# 10) lang attribute distribution
out["lang_attr"] = dict(Counter(p["lang"] for p in D["pages"]))

# 11) per-language description presence + hreflang count
hre = {}
for rel in OFFICIAL[:8]:
    raw = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    hre[rel] = len(re.findall(r'rel\s*=\s*["\']alternate["\']', raw, re.I))
out["hreflang_sample"] = hre

(ROOT / "tools/compliance-evidence.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2)[:16000])
