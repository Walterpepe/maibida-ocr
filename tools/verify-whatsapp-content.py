# -*- coding: utf-8 -*-
"""Static verification for the WhatsApp consultation content (now in the nav)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whatsapp_content as W
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools/whatsapp-content-verify.json"
LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]
CJK = re.compile(r"[\u4e00-\u9fff]")
REMOVED = "机器视觉光源选型"
REMOVED_EN = "Machine vision light selection"


def lang_of(rel):
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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def ck(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    # 1. All 11 locales: the requested bullet is gone, 3 items remain.
    removed_bad = [l for l in W.LANGS
                   if len(W.DATA[l]["items"]) != 3 or
                   any(REMOVED in x or REMOVED_EN.lower() in x.lower()
                       for x in W.DATA[l]["items"])]
    ck("11 语种已删除「机器视觉光源选型」条目，剩 3 条",
       not removed_bad, ", ".join(removed_bad) or "11/11 × 3 条")

    # 2. Formal pages: nav trigger, panel, script, footer line.
    nav_bad, panel_bad, script_bad, foot_bad, cjk_bad = [], [], [], [], []
    for rel in formal_pages():
        t = (ROOT / rel).read_text(encoding="utf-8")
        lang = lang_of(rel)
        prefix = "../" if "/" in rel else ""
        expected = W.wa_href(lang)
        s = BeautifulSoup(t, "html.parser")
        trig = s.select_one("a.vp-whatsapp-link[data-wa-toggle]")
        if (not trig or trig.get("href") != expected or
                trig.get("aria-controls") != "wa-consult-panel" or
                trig.get("aria-haspopup") != "dialog" or
                "noopener" not in (trig.get("rel") or [])):
            nav_bad.append(rel + ":trigger")
        panel = s.select_one("div.wa-consult-panel")
        if (not panel or panel.get("hidden") is None or
                panel.get("id") != "wa-consult-panel"):
            panel_bad.append(rel + ":panel")
        else:
            h2 = panel.select_one("h2")
            if (not h2 or h2.get_text(strip=True) != W.DATA[lang]["title"] or
                    len(panel.select("ul.wa-consult-list li")) != 3 or
                    W.DATA[lang]["button"] not in
                    (panel.select_one("a.wa-consult-btn").get_text(strip=True)
                     if panel.select_one("a.wa-consult-btn") else "")):
                panel_bad.append(rel + ":content")
            if t.count(W.PANEL_BEGIN) != 1:
                panel_bad.append(rel + ":duplicate")
            if lang not in ("zh-CN", "ja-JP") and CJK.search(panel.get_text(" ", strip=True)):
                cjk_bad.append(rel)
        sc = s.select_one('script[src="' + prefix + 'cn/js/whatsapp-consult.js"]')
        if not sc:
            script_bad.append(rel)
        block = re.search(r"<!-- BEGIN whatsapp-footer -->(.*?)<!-- END whatsapp-footer -->", t, re.S)
        if not block or 'class="fc-line fc-wa"' not in block.group(1) or expected not in block.group(1):
            foot_bad.append(rel)
    ck("88 页导航 WhatsApp 按钮保留可抓取 wa.me 深链接 + 面板触发属性",
       not nav_bad, ", ".join(nav_bad[:5]) or "88/88")
    ck("88 页导航内含 1 个默认折叠的本地化咨询面板（3 条范围）",
       not panel_bad, ", ".join(panel_bad[:5]) or "88/88")
    ck("88 页面板脚本引用路径正确", not script_bad, ", ".join(script_bad[:5]) or "88/88")
    ck("88 页页脚 WhatsApp 咨询行保留", not foot_bad, ", ".join(foot_bad[:5]) or "88/88")
    ck("面板非中文/日文语种无汉字残留", not cjk_bad, ", ".join(cjk_bad[:5]) or "0")

    # 3. Contact pages: section removed, widget moved into the header.
    moved_bad, widget_bad, policy_bad, heading_bad = [], [], [], []
    for rel in contact_pages():
        lang = lang_of(rel)
        t = (ROOT / rel).read_text(encoding="utf-8")
        s = BeautifulSoup(t, "html.parser")
        if "<!-- BEGIN whatsapp-consult-content -->" in t or s.select("section.cf-wa"):
            moved_bad.append(rel)
        head = s.select_one("header.cf-head")
        trig = s.select_one("header.cf-head [data-wa-toggle]") if head else None
        panel = s.select_one("div.wa-consult-panel") if head else None
        if not head or not trig or not panel or panel.parent.name == "main":
            widget_bad.append(rel + ":structure")
        else:
            h2 = panel.select_one("h2")
            if not h2 or h2.get_text(strip=True) != W.DATA[lang]["title"]:
                heading_bad.append(rel)
            if len(panel.select("ul.wa-consult-list li")) != 3:
                widget_bad.append(rel + ":items")
            btn = panel.select_one("a.wa-consult-btn")
            if (not btn or btn.get("href") != W.wa_href(lang) or
                    btn.get_text(strip=True) != W.DATA[lang]["button"] or
                    "noopener" not in (btn.get("rel") or [])):
                widget_bad.append(rel + ":button")
        expected_policy = "privacy.html" if lang == "zh-CN" else f"privacy.{lang}.html"
        p = s.select_one("p.wa-consult-note a")
        if (not p or p.get("href") != expected_policy or
                p.get_text(strip=True) != W.C.FOOTER_LABELS[lang][0] or
                not (ROOT / expected_policy).exists()):
            policy_bad.append(rel)
        if len(s.find_all("h1")) != 1 or len(s.find_all("h2")) != 1:
            heading_bad.append(rel + ":headings")
        if not s.select_one('script[src="cn/js/whatsapp-consult.js"]'):
            widget_bad.append(rel + ":script")
    ck("11 个留言页已移除表单下方的旧咨询板块",
       not moved_bad, ", ".join(moved_bad[:5]) or "11/11")
    ck("11 个留言页咨询内容已搬入页头导航组件（含 3 条与主按钮）",
       not widget_bad, ", ".join(widget_bad[:5]) or "11/11")
    ck("11 个面板 H1/H2 层级与标题正确",
       not heading_bad, ", ".join(heading_bad[:5]) or "11/11")
    ck("11 个面板隐私政策链接指向对应语种且文件存在",
       not policy_bad, ", ".join(policy_bad[:5]) or "11/11")

    # 4. Deep-link payload, shared assets, generator, backup.
    payload_bad = []
    for lang in W.LANGS:
        u = urlparse(W.wa_url(lang))
        q = parse_qs(u.query)
        if (u.scheme != "https" or u.netloc != "wa.me" or
                u.path.strip("/") != W.WA_NUMBER or
                q.get("text", [""])[0] != W.DATA[lang]["prefill"]):
            payload_bad.append(lang)
    ck("11 语种 wa.me ?text= 解码后与话术一致、号码正确",
       not payload_bad, ", ".join(payload_bad) or "11/11")

    css_bad = []
    for rel in ["cn/css/site-multilingual.css", "cn/css/contact.css"]:
        css = (ROOT / rel).read_text(encoding="utf-8")
        if (css.count(W.CSS_BEGIN) != 1 or css.count(W.CSS_END) != 1 or
                ".wa-consult-panel" not in css or ".cf-wa{" in css):
            css_bad.append(rel)
    ck("两份共用 CSS 各含 1 份面板样式、旧板块样式已清除",
       not css_bad, ", ".join(css_bad) or "2/2")
    js = (ROOT / "cn/js/whatsapp-consult.js").read_text(encoding="utf-8")
    ck("面板交互脚本存在（点击/关闭/ESC/外部点击）",
       all(k in js for k in ["data-wa-toggle", "preventDefault", "Escape",
                             "wa-consult-close", "aria-expanded"]),
       f"{len(js)} bytes")
    gen = (ROOT / "tools/add-message-feature.py").read_text(encoding="utf-8")
    ck("留言页生成器已同步（重建不丢内容）",
       all(k in gen for k in ["W.nav_trigger", "W.nav_panel", "W.contact_widget",
                              "W.NAV_CSS_BLOCK", "W.NAV_JS", "{wa_block}"]), "6/6")
    patch = json.loads((ROOT / "tools/whatsapp-move-patch.json").read_text(encoding="utf-8"))
    bp = Path(patch["backup"])
    mf = json.loads((bp / "manifest.json").read_text(encoding="utf-8"))
    bad_hash = [x["path"] for x in mf["files"]
                if not (bp / x["path"]).exists() or sha256(bp / x["path"]) != x["sha256"]]
    ck("变更备份 SHA-256 清单校验一致",
       len(mf["files"]) >= 100 and not bad_hash,
       f"files={len(mf['files'])}, bad={bad_hash[:3]}")

    passed = sum(1 for c in checks if c["ok"])
    result = {"checks": checks, "passed": passed, "total": len(checks),
              "all_ok": passed == len(checks)}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in checks:
        print(("PASS " if c["ok"] else "FAIL ") + c["name"] +
              (" | " + c["detail"] if c["detail"] else ""))
    print(f"\n{passed}/{len(checks)} checks passed")
    return 0 if result["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
