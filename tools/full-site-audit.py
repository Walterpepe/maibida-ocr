# -*- coding: utf-8 -*-
"""Full-site audit for the MAIBIDA static site.

Checks every deployable page (8 Chinese source pages x 11 language variants,
plus legacy/tool pages) for:
  * local asset/link integrity (404s)
  * SEO metadata (title, description, canonical, hreflang, og, JSON-LD, sitemap)
  * localisation (visible/attribute/JSON-LD Chinese leftovers, language switcher,
    html lang, cross-locale in-site links, numeric/model preservation)
  * structure (shared CSS/JS, fishbone diagram integrity)
  * runtime behaviour in Edge (HTTP status, JS errors, broken images, menu
    interaction, stacking order, initial scroll position, horizontal overflow)

Outputs tools/site-audit.json and tools/site-audit-report.html.
Read-only with respect to site content: it never modifies an existing page.

Usage:
    python tools/full-site-audit.py                 # static + runtime
    python tools/full-site-audit.py --no-runtime   # static only
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = "https://www.maibida.com/"
PREVIEW = "http://127.0.0.1:8899/"

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN", "ko-KR",
           "ja-JP", "ms-MY", "ru-RU"]
LEGACY_LOCALES = ["en-AU", "es-ES"]
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]
TOOL_PAGES = ["localization-glossary.html", "product/smart-camera-localization-report.html", "product/smart-camera.hreflang.html", "contact.html", "privacy.html", "terms.html"] + ["contact." + l + ".html" for l in LOCALES] + ["privacy." + l + ".html" for l in LOCALES] + ["terms." + l + ".html" for l in LOCALES] + ["contact." + l + ".html" for l in LOCALES]
LEGACY_PAGES = ["index.en-AU.html", "product/10032.en-AU.html",
                "product/smart-camera.en-AU.html", "product/smart-camera.es-ES.html"]
BACKUP_DIRS = {"productInfo_bak_seo", "_bak_footnav", "_bak_foot_full",
               "_bak_pathfix", "_bak_wxqrcode", "UserFiles_bak_bigimg"}

CJK = re.compile(r"[\u3400-\u9fff]")
# Simplified-Chinese-only characters: safe for spotting untranslated text on Japanese pages.
SIMPLIFIED_ONLY = re.compile(
    r"[\u8fd9\u4eec\u4e2a\u4e3a\u5e94\u8be5\u8fd8\u8fdb\u8fde\u9002\u65e0\u5382"
    r"\u5e7f\u5f00\u5173\u95ee\u9898\u4ec5\u5bfc\u51fb\u8d28\u7b80\u9009"
    r"\u62e9\u8f6f\u4f18\u5b9e\u73b0\u6807\u51c6\u7ee7\u7eed\u603b]")
SKIP = {"script", "style", "svg", "noscript", "template", "iframe"}
SKIP_CLASS = {"vp-language-switch", "g-translate", "notranslate"}
CHINESE_UNIT = re.compile(r"\d+(?:\.\d+)?\s*[–~\-]\s*\d+(?:\.\d+)?\s*[万千百]|"
                          r"\d+(?:\.\d+)?\s*[万千百寸秒倍]|SD卡")
LOCAL_SCHEMES = ("#", "javascript:", "mailto:", "tel:", "data:", "about:")
REF_TAGS = [("img", "src"), ("script", "src"), ("link", "href"), ("a", "href"),
            ("source", "src"), ("video", "src"), ("audio", "src"),
            ("iframe", "src"), ("embed", "src"), ("input", "src")]


def visible_numbers(path: Path) -> set:
    """Specification-like numbers appearing in human-readable page text.

    Attributes (including percent-encoded wa.me deep links), scripts and styles
    are deliberately excluded: their digits are encoding artifacts, not specs.
    """
    raw = CHINESE_UNIT.sub("", path.read_text(encoding="utf-8", errors="replace"))
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(list(SKIP)):
        tag.decompose()
    text = re.sub(r"%[0-9A-Fa-f]{2}", "", soup.get_text(" ", strip=True))
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def variant(rel: str, lang: str) -> str:
    p = Path(rel)
    return str(p.with_name(p.stem + "." + lang + ".html")).replace("\\", "/")


def locale_of(rel: str) -> str | None:
    m = re.search(r"\.([a-z]{2}-[A-Z]{2})\.html$", rel)
    return m.group(1) if m else None


def chinese_left(text: str, lang: str | None) -> bool:
    if lang == "ja-JP":
        return bool(SIMPLIFIED_ONLY.search(text))
    return bool(CJK.search(text))


def absolute_url(rel: str) -> str:
    return BASE + rel


def resolve_local(rel: str, href: str):
    """Return (target_rel, exists) for an in-site reference, else None."""
    h = (href or "").strip()
    if not h or h.startswith(LOCAL_SCHEMES):
        return None
    if h.startswith(("http://", "https://", "//")):
        if not (h.startswith(BASE) or h.startswith("https://www.maibida.com/")):
            return None
        p = unquote(urlparse(h).path.lstrip("/"))
        return (p, (ROOT / p).exists())
    p = unquote(h.split("#")[0].split("?")[0])
    if not p:
        return None
    target = (ROOT / rel).parent / p
    try:
        target = target.resolve()
        rel_target = target.relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return (p, False)
    return (rel_target, target.exists())


def visible_nodes(soup):
    for node in soup.find_all(string=True):
        raw = str(node)
        if not raw.strip() or isinstance(node, Comment) or node.parent.name == "[document]":
            continue
        if any(p.name in SKIP for p in node.parents):
            continue
        if any(SKIP_CLASS.intersection(p.get("class", [])) for p in node.parents if p.name):
            continue
        yield raw.strip()


class Audit:
    def __init__(self):
        self.issues = []          # {level, page, category, message}
        self.page_rows = []       # per-page summary
        self.stats = Counter()
        self.asset_refs = 0
        self.external_links = 0
        self.sitemap = {}

    def add(self, level, page, category, message):
        self.issues.append({"level": level, "page": page,
                            "category": category, "message": message})
        self.stats[level] += 1

    # ---------------------------------------------------------------- pages
    def page_sets(self):
        formal = []
        for p in PAGES:
            formal.append(p)
            formal.extend(variant(p, l) for l in LOCALES)
        return formal, LEGACY_PAGES, TOOL_PAGES

    def check_page(self, rel, kind):
        path = ROOT / rel
        if not path.exists():
            self.add("error", rel, "file", "页面文件缺失")
            return {}
        text = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(text, "html.parser")
        lang = locale_of(rel)
        row = {"page": rel, "kind": kind, "lang": lang or "zh-CN",
               "title": "", "title_len": 0, "desc_len": 0,
               "hreflang": 0, "refs": 0, "broken": 0, "chinese": 0,
               "runtime": "not-checked"}
        self.stats["pages_checked"] += 1

        # ---- doctype / lang / charset (tool/fragment pages are exempt)
        if kind != "tool":
            if not text.lstrip().lower().startswith("<!doctype html"):
                self.add("warn", rel, "structure", "缺少标准 DOCTYPE")
            if soup.html is None:
                self.add("error", rel, "structure", "缺少 <html> 元素")
            elif kind == "locale" and soup.html.get("lang") != lang:
                self.add("error", rel, "seo", f"html lang={soup.html.get('lang')}，应为 {lang}")
            elif kind == "source" and soup.html.get("lang") not in (None, "", "zh-CN"):
                self.add("warn", rel, "seo", f"中文源页 html lang={soup.html.get('lang')}")
            if not soup.find("meta", attrs={"charset": True}):
                self.add("warn", rel, "structure", "未声明 charset")

        # ---- local references
        broken = []
        for tag, attr in REF_TAGS:
            for el in soup.find_all(tag):
                href = el.get(attr)
                if not href:
                    continue
                row["refs"] += 1
                self.asset_refs += 1
                if href.startswith(("http://", "https://", "//")) and not href.startswith(BASE):
                    self.external_links += 1
                    continue
                r = resolve_local(rel, href)
                if r is None:
                    continue
                target, exists = r
                if not exists:
                    broken.append(f"{tag}[{attr}]={href}")
        row["broken"] = len(broken)
        if broken:
            level = "error" if kind in ("source", "locale") else "warn"
            label = {"source": "中文源页", "locale": "现行多语种页",
                     "legacy": "遗留页", "tool": "工具/片段页"}[kind]
            legacy_hits = sum(1 for b in broken if "es-ES" in b or "en-AU" in b)
            category = "legacy-links" if legacy_hits else "link"
            self.add(level, rel, category,
                     f"{len(broken)} 条本地引用 404（{label}，其中 {legacy_hits} 条指向已下线的 "
                     "es-ES/en-AU 页面）：" + "；".join(broken[:6]))

        # ---- shared CSS / JS
        hrefs = [el.get("href", "") for el in soup.find_all("link", href=True)]
        srcs = [el.get("src", "") for el in soup.find_all("script", src=True)]
        # Retired noindex redirect stubs have no language switcher, so they
        # need neither the multilingual stylesheet nor its script.
        is_redirect_stub = any(
            "noindex" in (m.get("content") or "").lower()
            for m in soup.find_all("meta", attrs={"name": "robots"}))
        if kind != "tool" and not (kind == "legacy" and is_redirect_stub):
            for needed, pool, label in [("site-multilingual.css", hrefs, "多语种样式"),
                                        ("site-multilingual.js", srcs, "多语种脚本")]:
                if not any(needed in x for x in pool):
                    self.add("error", rel, "structure", f"未引用{label} {needed}")

        # ---- SEO (formal pages only)
        if kind in ("source", "locale"):
            self.check_seo(rel, kind, lang, soup, row)

        # ---- localisation (locale pages only)
        if kind == "locale":
            self.check_localisation(rel, lang, soup, row)
        elif kind == "legacy":
            self.check_legacy(rel, soup)
        elif kind == "tool":
            self.add("info", rel, "scope", "交付/工具页面，不参与多语种 SEO 校验")

        # ---- fishbone diagram structure
        fish = soup.select_one(".fishbone-exact")
        if fish:
            counts = {k: len(fish.select(k)) for k in
                      [".fbx-card", ".fbx-mark", ".fbx-line", ".fbx-spine", ".fbx-result"]}
            expected = {".fbx-card": 10, ".fbx-mark": 8, ".fbx-line": 8,
                        ".fbx-spine": 1, ".fbx-result": 1}
            if counts != expected:
                self.add("warn", rel, "structure", f"鱼骨图元素数量异常 {counts}")
            self.stats["fishbone_pages"] += 1

        self.page_rows.append(row)
        return row

    # ------------------------------------------------------------------ SEO
    def check_seo(self, rel, kind, lang, soup, row):
        title = soup.title.get_text(strip=True) if soup.title else ""
        row["title"] = title
        row["title_len"] = len(title)
        if not title:
            self.add("error", rel, "seo", "缺少 <title>")
        else:
            if len(title) > 65:
                self.add("warn", rel, "seo", f"title 过长 {len(title)} 字符（建议 ≤65）")
            if kind == "locale" and chinese_left(title, lang):
                self.add("error", rel, "seo", f"title 未翻译：{title[:50]}")
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag.get("content", "").strip() if desc_tag else ""
        row["desc_len"] = len(desc)
        if not desc:
            self.add("error", rel, "seo", "缺少 meta description")
        else:
            if len(desc) > 155:
                self.add("warn", rel, "seo", f"description 过长 {len(desc)} 字符（建议 ≤155）")
            if kind == "locale" and chinese_left(desc, lang):
                self.add("error", rel, "seo", f"description 未翻译：{desc[:60]}")
        if not soup.find_all("h1"):
            self.add("warn", rel, "seo", "页面没有 h1")

        allowed_self = {absolute_url(rel)}
        if rel == "index.html":
            allowed_self.add(BASE)  # the home page may legitimately canonicalise to the root URL
        canon = [x for x in soup.find_all("link") if "canonical" in x.get("rel", [])]
        if len(canon) != 1:
            self.add("error", rel, "seo", f"canonical 数量 {len(canon)}，应为 1")
        elif canon[0].get("href") not in allowed_self:
            self.add("error", rel, "seo", f"canonical 指向 {canon[0].get('href')}，应为 {absolute_url(rel)}")

        alts = [x for x in soup.find_all("link")
                if "alternate" in x.get("rel", []) and x.get("hreflang")]
        row["hreflang"] = len(alts)
        stem = re.sub(r"\.[a-z]{2}-[A-Z]{2}\.html$|\.html$", "", rel)
        family = [p for p in PAGES if p.startswith(stem) and p.replace(".html", "") == stem]
        source_rel = family[0] if family else None
        if source_rel:
            expected = {"zh-CN": absolute_url(source_rel),
                        "x-default": absolute_url(variant(source_rel, "en-US"))}
            expected.update({l: absolute_url(variant(source_rel, l)) for l in LOCALES})
            # Generated locale pages must carry exactly the 12 current alternates.
            # Chinese source pages are kept byte-identical to the original site and
            # may still carry extra legacy alternates; those are reported as warnings.
            if kind == "locale" and len(alts) != len(expected):
                self.add("error", rel, "seo",
                         f"hreflang 数量 {len(alts)}，应为 {len(expected)}")
            for a in alts:
                h = a.get("hreflang")
                if h in expected and expected[h] != a.get("href"):
                    self.add("error", rel, "seo",
                             f"hreflang {h} 指向 {a.get('href')}，应为 {expected[h]}")
            extra = [a.get("hreflang") for a in alts if a.get("hreflang") not in expected]
            if extra:
                self.add("warn", rel, "seo",
                         "额外 hreflang（非现行 12 语种）：" + ", ".join(extra))
        else:
            self.add("warn", rel, "seo", "无法定位中文源页以校验 hreflang")

        ogs = {m.get("property"): m.get("content", "") for m in
               soup.find_all("meta", attrs={"property": True})
               if str(m.get("property", "")).startswith("og:")}
        for key in ["og:title", "og:description", "og:url", "og:image"]:
            if not ogs.get(key):
                self.add("warn", rel, "seo", f"缺少 {key}")
        if ogs.get("og:url") and ogs["og:url"] not in allowed_self:
            self.add("error", rel, "seo", f"og:url 不匹配：{ogs['og:url']}")

        for sc in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = sc.string or sc.get_text()
            try:
                json.loads(raw)
            except (ValueError, TypeError) as e:
                self.add("error", rel, "seo", f"JSON-LD 解析失败：{str(e)[:80]}")
            if kind == "locale" and chinese_left(raw, lang):
                self.add("error", rel, "seo", f"JSON-LD 含中文：{raw.strip()[:80]}")

    # -------------------------------------------------------- localisation
    def check_localisation(self, rel, lang, soup, row):
        leftover = [n[:48] for n in visible_nodes(soup) if chinese_left(n, lang)]
        row["chinese"] = len(leftover)
        if leftover:
            self.add("error", rel, "localisation",
                     f"可见中文残留 {len(leftover)} 处：" + " | ".join(leftover[:3]))

        for el in soup.find_all(True):
            for attr in ["alt", "title", "placeholder", "aria-label", "content"]:
                v = el.get(attr, "")
                if v and chinese_left(v, lang):
                    self.add("error", rel, "localisation",
                             f"{el.name}[{attr}] 未翻译：{v[:48]}")
                    break

        switch = soup.select_one(".vp-language-switch")
        links = switch.select("a[hreflang]") if switch else []
        if not switch:
            self.add("error", rel, "localisation", "缺少语言切换菜单")
        else:
            if len(links) != 1 + len(LOCALES):
                self.add("error", rel, "localisation",
                         f"语言菜单链接 {len(links)} 个，应为 {1 + len(LOCALES)}")
            for a in links:
                r = resolve_local(rel, a.get("href", ""))
                if r and not r[1]:
                    self.add("error", rel, "localisation", f"语言菜单目标不存在：{r[0]}")
                txt = a.get_text(strip=True)
                # "日本語" is a legitimate Japanese endonym containing kanji.
                if lang != "ja-JP" and CJK.search(txt) and txt != "日本語":
                    self.add("error", rel, "localisation", f"语言菜单标签未本地化：{txt}")
            if not switch.select(f'a[hreflang="{lang}"][aria-current="page"]'):
                self.add("error", rel, "localisation", "当前语种未高亮（缺 aria-current=page）")

        # In-site links should stay in the same locale (language switcher excluded).
        switch_ids = {id(a) for a in links}
        cross = []
        for a in soup.find_all("a", href=True):
            if id(a) in switch_ids:
                continue
            href = a["href"]
            if href.startswith(LOCAL_SCHEMES) or not href.endswith(".html"):
                continue
            r = resolve_local(rel, href)
            if not r or not r[1]:
                continue
            target_lang = locale_of(r[0])
            if target_lang is None and r[0] in PAGES:
                target_lang = "zh-CN"
            if target_lang != lang:
                cross.append(f"{href} → {target_lang}")
        if cross:
            self.add("warn", rel, "localisation",
                     f"{len(cross)} 条站内链接跨语种：" + ", ".join(cross[:5]))

        # Numbers / model names must survive translation. Compare visible text
        # only: URL-encoded deep links (e.g. %E6%82%A8 in wa.me ?text=), CSS,
        # scripts and HTML attributes contain digits that are not specs.
        source_rel = re.sub(r"\.[a-z]{2}-[A-Z]{2}\.html$", ".html", rel)
        if (ROOT / source_rel).exists():
            src_nums = visible_numbers(ROOT / source_rel)
            tgt_nums = visible_numbers(ROOT / rel)
            missing = sorted(src_nums - tgt_nums)
            if missing:
                self.add("warn", rel, "localisation",
                         "数字/规格可能丢失：" + ", ".join(missing[:8]))

    # --------------------------------------------------------------- legacy
    def check_legacy(self, rel, soup):
        # The 4 retired pages were converted to noindex + canonical redirect stubs.
        cans = [x.get("href", "") for x in soup.find_all("link")
                if "canonical" in x.get("rel", [])]
        is_stub = any("en-SG" in c or "es-MX" in c for c in cans)
        if is_stub:
            self.add("tip", rel, "scope",
                     "旧语种迁移页：noindex + canonical + 自动跳转，不在 sitemap，零死链")
        else:
            self.add("warn", rel, "scope", "遗留旧语种文件，不在 sitemap 与现行语言菜单中")
        alts = [x for x in soup.find_all("link")
                if "alternate" in x.get("rel", []) and x.get("hreflang")]
        dead = set()
        for a in alts:
            r = resolve_local(rel, a.get("href", ""))
            if r and not r[1]:
                dead.add(a.get("hreflang"))
        if dead:
            self.add("warn", rel, "legacy-links",
                     f"hreflang 指向 {len(dead)} 个不存在/非现行页面：" + ", ".join(sorted(dead)))

    # -------------------------------------------------------------- sitemap
    def check_sitemap(self, formal):
        f = ROOT / "sitemap.xml"
        if not f.exists():
            self.add("error", "sitemap.xml", "seo", "sitemap.xml 缺失")
            return
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(f.read_text(encoding="utf-8"))
        urls = [(e.text or "").strip() for e in tree.iter() if e.tag.endswith("loc")]
        alt_links = [e for e in tree.iter()
                     if e.tag.endswith("link") and e.get("hreflang")]
        self.sitemap = {"urls": len(urls), "hreflang": len(alt_links),
                        "formal_pages": len(formal)}
        expected = {absolute_url(p) for p in formal}
        actual = set(urls)
        self.sitemap["missing"] = sorted(expected - actual)[:20]
        self.sitemap["extra"] = sorted(actual - expected)[:20]
        if len(urls) != len(formal):
            self.add("error", "sitemap.xml", "seo",
                     f"sitemap URL {len(urls)} 个，正式页面 {len(formal)} 个")
        if self.sitemap["missing"]:
            self.add("error", "sitemap.xml", "seo",
                     "sitemap 缺少页面：" + ", ".join(self.sitemap["missing"][:5]))
        if self.sitemap["extra"]:
            self.add("warn", "sitemap.xml", "seo",
                     "sitemap 含非现行页面：" + ", ".join(self.sitemap["extra"][:5]))
        if len(alt_links) != len(formal) * 12:
            self.add("warn", "sitemap.xml", "seo",
                     f"hreflang 条目 {len(alt_links)}，预期 {len(formal) * 12}")

    # ------------------------------------------------------------- runtime
    def runtime(self, pages):
        from playwright.sync_api import sync_playwright
        results = {}
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="msedge", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            js_errors = []
            page.on("pageerror", lambda e: js_errors.append(str(e)[:160]))
            for rel, kind in pages:
                strict = kind in ("source", "locale")
                js_errors.clear()
                item = {"status": 0, "kind": kind, "js_errors": [], "broken_images": 0,
                        "scroll_y": None, "lang_menu_opens": None,
                        "active_lang": None, "css_loaded": None,
                        "js_loaded": None, "stacking": None,
                        "overflow_x": 0}
                try:
                    resp = page.goto(PREVIEW + rel, wait_until="load", timeout=45000)
                    item["status"] = resp.status if resp else 0
                    page.wait_for_timeout(260)
                    info = page.evaluate("""() => {
                      const imgs = Array.from(document.images);
                      const bodyPad = getComputedStyle(document.body).paddingTop;
                      const fish = document.querySelector('.fishbone-exact');
                      const out = {
                        broken: imgs.filter(i => i.getAttribute('src') && i.naturalWidth === 0).length,
                        scrollY: Math.round(window.scrollY),
                        bodyPad: bodyPad,
                        scrollRestoration: history.scrollRestoration,
                        overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
                        activeLang: (document.querySelector('.vp-language-switch a[aria-current="page"]')||{}).getAttribute
                          ? document.querySelector('.vp-language-switch a[aria-current="page"]').getAttribute('hreflang') : null
                      };
                      if (fish) {
                        const card = fish.querySelector('.fbx-card.top.c5');
                        const h = document.querySelector('body>.top,body>.top2');
                        out.fish = {iso: getComputedStyle(fish).isolation,
                                    cardZ: card ? getComputedStyle(card).zIndex : null,
                                    headZ: h ? getComputedStyle(h).zIndex : null};
                      }
                      return out;
                    }""")
                    item["broken_images"] = info["broken"]
                    item["scroll_y"] = info["scrollY"]
                    item["css_loaded"] = info["bodyPad"] in ("125px", "113px")
                    item["js_loaded"] = info["scrollRestoration"] == "manual"
                    item["active_lang"] = info["activeLang"]
                    item["overflow_x"] = info["overflow"]
                    if info.get("fish"):
                        item["stacking"] = info["fish"]
                    try:
                        page.click(".vp-language-switch summary", timeout=2500)
                        item["lang_menu_opens"] = page.evaluate(
                            "() => !!document.querySelector('.vp-language-switch[open]')")
                        page.keyboard.press("Escape")
                    except Exception:
                        item["lang_menu_opens"] = False
                    item["js_errors"] = list(js_errors)
                except Exception as e:
                    item["js_errors"] = ["加载异常: " + str(e)[:140]]
                results[rel] = item

                if item["status"] != 200:
                    self.add("error", rel, "runtime", f"HTTP {item['status']}")
                if item["js_errors"]:
                    self.add("error", rel, "runtime",
                             "JS 错误：" + " | ".join(item["js_errors"][:2]))
                if item["broken_images"]:
                    self.add("error", rel, "runtime", f"破图 {item['broken_images']} 张")
                if strict and item["scroll_y"] not in (0, None):
                    self.add("warn", rel, "runtime", f"首屏未从顶部开始 scrollY={item['scroll_y']}")
                if strict and item["lang_menu_opens"] is False:
                    self.add("error", rel, "runtime", "语言切换菜单打不开")
                if strict and item["css_loaded"] is False:
                    self.add("error", rel, "runtime", "site-multilingual.css 未生效")
                if strict and item["js_loaded"] is False:
                    self.add("error", rel, "runtime", "site-multilingual.js 未生效")
                if item["overflow_x"] > 40:
                    self.add("warn", rel, "runtime",
                             f"横向溢出 {item['overflow_x']}px（多为鱼骨图 min-width:980px 的既有设计）")
                if item["stacking"]:
                    f = item["stacking"]
                    if f["iso"] != "isolate" or f["cardZ"] != "3" or f["headZ"] != "1000":
                        self.add("error", rel, "runtime", f"鱼骨图层级异常：{f}")
            browser.close()
        for row in self.page_rows:
            if row["page"] in results:
                r = results[row["page"]]
                if r.get("kind") == "tool":
                    row["runtime"] = "n/a"
                elif r["status"] == 200 and not r["js_errors"] and not r["broken_images"]:
                    row["runtime"] = "ok"
                else:
                    row["runtime"] = "issue"
        self.stats["runtime_pages"] = len(results)
        return results

    # --------------------------------------------------------------- report
    def write(self, runtime_results, review):
        data = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "root": str(ROOT),
            "scope": {
                "formal_pages": 88, "legacy_pages": len(LEGACY_PAGES),
                "tool_pages": len(TOOL_PAGES),
                "backup_html_excluded": sum(
                    1 for p in ROOT.glob("**/*.html")
                    if p.relative_to(ROOT).parts[0] in BACKUP_DIRS),
                "locales": LOCALES,
            },
            "stats": dict(self.stats),
            "asset_references": self.asset_refs,
            "external_links": self.external_links,
            "sitemap": self.sitemap,
            "issues": self.issues,
            "pages": self.page_rows,
            "runtime": runtime_results,
            "known_decisions": review,
        }
        (TOOLS / "site-audit.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.write_html(data)

    def write_html(self, d):
        errs = [i for i in d["issues"] if i["level"] == "error"]
        warns = [i for i in d["issues"] if i["level"] == "warn"]
        infos = [i for i in d["issues"] if i["level"] == "info"]
        ok_pages = sum(1 for r in d["pages"] if r["runtime"] == "ok")
        runtime_total = d["stats"].get("runtime_pages", 0)
        by_cat = Counter((i["level"], i["category"]) for i in d["issues"])
        legacy_errs = [i for i in errs if i["category"] == "legacy-links"]
        legacy_pages = sorted({i["page"] for i in legacy_errs})
        legacy_refs = sum(r["broken"] for r in d["pages"] if r["kind"] == "source")

        def esc(s):
            return html_mod.escape(str(s))

        def issue_table(items):
            if not items:
                return '<p class="empty">无</p>'
            rows = "".join(
                f"<tr><td class='mono'>{esc(i['page'])}</td><td>{esc(i['category'])}</td>"
                f"<td>{esc(i['message'])}</td></tr>" for i in items[:400])
            more = (f"<tr><td colspan='3' class='more'>仅显示前 400 条，共 {len(items)} 条，"
                    "完整清单见 site-audit.json</td></tr>") if len(items) > 400 else ""
            return ("<table><thead><tr><th>页面</th><th>类别</th><th>问题</th></tr></thead>"
                    f"<tbody>{rows}{more}</tbody></table>")

        page_rows = "".join(
            f"<tr><td class='mono'>{esc(r['page'])}</td><td>{esc(r['lang'])}</td>"
            f"<td>{r['title_len']}</td><td>{r['desc_len']}</td><td>{r['hreflang']}</td>"
            f"<td>{r['refs']}</td><td class='{'bad' if r['broken'] else 'good'}'>{r['broken']}</td>"
            f"<td class='{'bad' if r['chinese'] else 'good'}'>{r['chinese']}</td>"
            f"<td class='{'good' if r['runtime']=='ok' else ('bad' if r['runtime']=='issue' else 'muted')}'>"
            f"{esc(r['runtime'])}</td></tr>" for r in d["pages"])

        cat_rows = "".join(
            f"<tr><td>{esc(k[0])}</td><td>{esc(k[1])}</td><td>{v}</td></tr>"
            for k, v in sorted(by_cat.items(), key=lambda x: (x[0][0], -x[1])))

        focus = ""
        if legacy_errs:
            focus = f"""<div class="panel" style="border-left:4px solid var(--red)">
<h2 style="margin-top:0;border-left-color:var(--red)">关键发现：中文源页残留已下线语种链接</h2>
<p>8 个中文源页仍保留旧版 <code>en-AU</code> / <code>es-ES</code> 多语种入口；生成器产出的 80 个现行多语种页已清理干净，两者不一致。
当前中文源页共有 <b class="red">{legacy_refs} 条</b> hreflang / 语言菜单引用指向不存在的
<code>*.en-AU.html</code> / <code>*.es-ES.html</code>，分布在 <b>{len(legacy_pages)} 个中文源页</b>：
{esc('、'.join(legacy_pages))}。搜索引擎会抓到 404，访客从中文页切换语言也可能点到死链。</p>
<p><b>建议</b>：移除这两组 hreflang 与菜单项（或把 es-ES → es-MX、en-AU → en-SG 重定向到现行页面），
并决定 4 个遗留 en-AU / es-ES 文件是删除还是保留。本次为只读检测，未改动任何站点页面。</p></div>"""

        labels = {"images_with_chinese_text": "共用图片内嵌中文",
                  "legacy_locale_files": "遗留旧语种文件",
                  "source_code_comments": "源码注释中文",
                  "chinese_only_tool_pages": "中文工具/报告页"}
        decisions = d["known_decisions"]
        decision_html = ""
        for key, val in decisions.items():
            name = labels.get(key, key)
            if isinstance(val, dict):
                summary = f"{val.get('count', len(val))} 项"
                bits = []
                for k, v in val.items():
                    if k == "count":
                        continue
                    if isinstance(v, str):
                        bits.append(f"{k}: {v[:80]}")
                    elif isinstance(v, (list, dict)):
                        bits.append(f"{k}: {len(v)} 条")
                    else:
                        bits.append(f"{k}: {v}")
                detail = "；".join(bits[:4])
            elif isinstance(val, list):
                summary = f"{len(val)} 项"
                detail = "、".join(esc(str(x)[:60]) for x in val[:4])
            else:
                summary, detail = esc(str(val)[:80]), ""
            decision_html += (f"<tr><td>{esc(name)}</td><td>{summary}</td>"
                              f"<td>{esc(detail)}</td></tr>")

        doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>MAIBIDA 全站检测报告</title>
<style>
:root{{--bg:#f5f7fa;--card:#fff;--ink:#1d2733;--muted:#6b7887;--line:#e3e9f0;
--red:#d93025;--amber:#e08a00;--green:#12805c;--blue:#1a66c2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",Arial,sans-serif}}
.wrap{{max-width:1220px;margin:0 auto;padding:32px 24px 64px}}
h1{{font-size:28px;margin:0 0 6px}}h2{{font-size:19px;margin:34px 0 14px;
padding-left:10px;border-left:4px solid var(--blue)}}
.sub{{color:var(--muted);margin:0 0 24px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:14px;margin:18px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}}
.card .n{{font-size:28px;font-weight:700;line-height:1.2}}
.card .l{{color:var(--muted);font-size:12px;margin-top:4px}}
.red{{color:var(--red)}}.amber{{color:var(--amber)}}.green{{color:var(--green)}}.blue{{color:var(--blue)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:16px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f0f4f9;font-weight:600;color:#41536a;white-space:nowrap}}
td.mono{{font-family:Consolas,Menlo,monospace;font-size:12px;word-break:break-all}}
.good{{color:var(--green)}}.bad{{color:var(--red);font-weight:600}}.muted{{color:var(--muted)}}
.more{{color:var(--muted);text-align:center}}.empty{{color:var(--green);margin:0}}
.tag{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;
background:#eaf2fc;color:var(--blue);margin-right:6px}}
.scroll{{max-height:520px;overflow:auto}}ul{{margin:8px 0 0 18px;padding:0}}
li{{margin:4px 0}}.foot{{color:var(--muted);font-size:12px;margin-top:32px}}
</style></head><body><div class="wrap">
<h1>MAIBIDA 全站检测报告</h1>
<p class="sub">检测时间 {esc(d['generated_at'])} ｜ 站点 {esc(d['root'])} ｜ 静态 + Edge 运行时双层检测</p>

<div class="cards">
<div class="card"><div class="n blue">{d['scope']['formal_pages']}</div><div class="l">正式页面（8 中文源页 × 11 语种）</div></div>
<div class="card"><div class="n">{d['scope']['legacy_pages'] + d['scope']['tool_pages']}</div><div class="l">遗留页 / 工具页（单独校验）</div></div>
<div class="card"><div class="n">{d['asset_references']}</div><div class="l">本地/外部资源引用检查</div></div>
<div class="card"><div class="n">{runtime_total}</div><div class="l">Edge 实际加载页面</div></div>
<div class="card"><div class="n {'red' if errs else 'green'}">{len(errs)}</div><div class="l">错误</div></div>
<div class="card"><div class="n {'amber' if warns else 'green'}">{len(warns)}</div><div class="l">警告</div></div>
<div class="card"><div class="n green">{ok_pages}</div><div class="l">运行时无异常页面</div></div>
</div>
{focus}
<div class="panel"><h2 style="margin-top:0">检测范围</h2>
<p><span class="tag">正式 88 页</span><span class="tag">遗留 4 页</span><span class="tag">工具/报告 3 页</span>
<span class="tag">备份目录 HTML {d['scope']['backup_html_excluded']} 个已排除</span></p>
<p class="sub" style="margin:8px 0 0">正式页 = 8 个中文源页 + 10 个语种 × 8 页。语种：{esc(', '.join(d['scope']['locales']))}。
备份/历史目录（_bak_*、productInfo_bak_seo、UserFiles_bak_bigimg）不属于可部署站点，不参与检测。</p></div>

<div class="panel"><h2 style="margin-top:0">问题分布</h2>
<table><thead><tr><th>级别</th><th>类别</th><th>数量</th></tr></thead><tbody>{cat_rows or '<tr><td colspan="3" class="empty">无问题</td></tr>'}</tbody></table></div>

<div class="panel"><h2 style="margin-top:0">错误清单（{len(errs)}）</h2><div class="scroll">{issue_table(errs)}</div></div>
<div class="panel"><h2 style="margin-top:0">警告清单（{len(warns)}）</h2><div class="scroll">{issue_table(warns)}</div></div>
<div class="panel"><h2 style="margin-top:0">提示（{len(infos)}）</h2><div class="scroll">{issue_table(infos)}</div></div>

<div class="panel"><h2 style="margin-top:0">逐页结果</h2>
<p class="sub" style="margin:0 0 10px">title/desc 为字符数；hreflang 为条数；refs 为引用数；broken 为 404 引用；chinese 为可见中文残留处数；runtime 为浏览器加载结论。</p>
<div class="scroll"><table><thead><tr><th>页面</th><th>语种</th><th>title</th><th>desc</th><th>hreflang</th><th>refs</th><th>404</th><th>中文</th><th>运行时</th></tr></thead>
<tbody>{page_rows}</tbody></table></div></div>

<div class="panel"><h2 style="margin-top:0">待用户决策的已知项（本次未改）</h2>
<table><thead><tr><th>项目</th><th>规模</th><th>摘要</th></tr></thead><tbody>{decision_html or '<tr><td colspan="3" class="empty">无</td></tr>'}</tbody></table></div>

<div class="panel"><h2 style="margin-top:0">检测项说明</h2><ul>
<li>静态：本地 img/script/link/a/video/iframe 引用是否 404、DOCTYPE / charset / html lang、共用 CSS/JS 引用、鱼骨图元素结构完整性。</li>
<li>SEO：title 与 description 存在性/长度/未译检测、canonical 自指、hreflang 12 项互指且目标存在、og 四项、JSON-LD 可解析且无中文、sitemap URL 与正式页集合一致。</li>
<li>本地化：可见文本 / alt / title / placeholder / aria-label / content / JSON-LD 的中文残留（日文页只查简体特有字）、语言菜单 11 项与当前语种高亮、跨语种站内链接、数字与型号保留。</li>
<li>运行时：Edge 逐页加载，HTTP 状态、JS 错误、破图、首屏 scrollY、语言菜单可展开、CSS/JS 是否生效、鱼骨图层级隔离、横向溢出。</li>
</ul></div>
<p class="foot">报告由 tools/full-site-audit.py 生成；明细数据同目录 site-audit.json。本检测为只读，不修改任何站点页面。</p>
</div></body></html>"""
        (TOOLS / "site-audit-report.html").write_text(doc, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-runtime", action="store_true", help="skip browser checks")
    args = ap.parse_args()

    a = Audit()
    formal, legacy, tools = a.page_sets()
    all_pages = [(p, "source" if locale_of(p) is None else "locale") for p in formal]
    all_pages += [(p, "legacy") for p in legacy]
    all_pages += [(p, "tool") for p in tools]
    for rel, kind in all_pages:
        a.check_page(rel, kind)
    a.check_sitemap(formal)

    # duplicate SEO titles/descriptions per page family
    for p in PAGES:
        fam = [r for r in a.page_rows
               if r["kind"] == "locale" and re.sub(r"\.[a-z]{2}-[A-Z]{2}\.html$", ".html", r["page"]) == p]
        if len(set(r["title"] for r in fam)) != len(LOCALES):
            a.add("error", p, "seo", "同一页面的 10 个语种存在重复 title")
    desc_map = defaultdict(list)
    for rel, kind in all_pages:
        if kind != "locale":
            continue
        soup = BeautifulSoup((ROOT / rel).read_text(encoding="utf-8", errors="replace"), "html.parser")
        m = soup.find("meta", attrs={"name": "description"})
        desc_map[re.sub(r"\.[a-z]{2}-[A-Z]{2}\.html$", ".html", rel)].append(
            m.get("content", "") if m else "")
    for rel, vals in desc_map.items():
        if len(set(vals)) != len(LOCALES):
            a.add("error", rel, "seo", "同一页面的 10 个语种存在重复 description")

    runtime_results = {}
    if not args.no_runtime:
        runtime_results = a.runtime(all_pages)

    review = {}
    f = TOOLS / "localization-review.json"
    if f.exists():
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
            review = raw.get("remaining_needs_decision", {})
        except (ValueError, OSError):
            pass
    a.write(runtime_results, review)

    print("pages:", a.stats["pages_checked"], "refs:", a.asset_refs,
          "runtime:", a.stats.get("runtime_pages", 0))
    print("errors:", a.stats["error"], "warnings:", a.stats["warn"],
          "info:", a.stats["info"])
    for i in a.issues:
        if i["level"] == "error":
            print("  ERROR", i["page"], i["category"], i["message"][:110])
    print("report:", TOOLS / "site-audit-report.html")


if __name__ == "__main__":
    main()
