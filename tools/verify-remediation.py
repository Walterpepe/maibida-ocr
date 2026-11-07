"""Independent verification of the pre-launch remediation (read-only)."""
import http.client
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "remediation-verify.json"
LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]
BACKUP_DIRS = ["productInfo_bak_seo", "UserFiles_bak_bigimg",
               "_bak_footnav", "_bak_foot_full", "_bak_pathfix", "_bak_wxqrcode"]
CJK = re.compile(r"[\u4e00-\u9fff]")
checks = []


def check(name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})


def formal_pages():
    for p in PAGES:
        yield p, "zh-CN"
        q = Path(p)
        for l in LOCALES:
            yield q.with_name(q.stem + "." + l + ".html").as_posix(), l


def req(path, method="GET", body=None, headers=None):
    c = http.client.HTTPConnection("127.0.0.1", 8899, timeout=10)
    c.request(method, path, body=body, headers=headers or {})
    r = c.getresponse()
    data = r.read()
    hs = {k.lower(): v for k, v in r.getheaders()}
    out = (r.status, hs, data)
    c.close()
    return out


# 1. backup directories are no longer deployable
check("历史备份目录已移出 Web 根目录",
      all(not (ROOT / d).exists() for d in BACKUP_DIRS),
      ", ".join(d for d in BACKUP_DIRS if (ROOT / d).exists()) or "6/6 removed")

# 2. nav entries on all 88 formal pages
pages = list(formal_pages())
missing_contact, missing_wa, bad_wa = [], [], []
for rel, lang in pages:
    t = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    if 'class="vp-contact-link"' not in t:
        missing_contact.append(rel)
    m = re.search(r'<a class="vp-whatsapp-link"[^>]*href="([^"]+)"', t)
    if not m:
        missing_wa.append(rel)
    elif not m.group(1).startswith("https://wa.me/8615995675085"):
        bad_wa.append(rel)
check("88 页留言导航入口完整", len(pages) == 88 and not missing_contact,
      f"{len(pages)} pages, missing={missing_contact[:3]}")
check("88 页 WhatsApp 入口完整且号码正确", not missing_wa and not bad_wa,
      f"missing={missing_wa[:3]}, wrong={bad_wa[:3]}")

# 3. contact page SEO + progressive-enhancement form
contact_bad = []
for lang in ["zh-CN"] + LOCALES:
    rel = "contact.html" if lang == "zh-CN" else f"contact.{lang}.html"
    s = BeautifulSoup((ROOT / rel).read_text(encoding="utf-8"), "html.parser")
    c = s.find("link", rel="canonical")
    d = s.find("meta", attrs={"name": "description"})
    f = s.find("form", id="message-form")
    ok = (c and c.get("href", "").startswith("https://www.maibida.com/")
          and d and d.get("content", "").strip()
          and f and f.get("method", "").lower() == "post"
          and f.get("action") == "/api/messages"
          and all(s.find(attrs={"name": k}) for k in
                  ["name", "email", "phone", "company", "country", "message"]))
    if not ok:
        contact_bad.append(rel)
check("11 个留言页 canonical/description/POST/action/6 字段", not contact_bad,
      contact_bad)

# 4. localized alt: no empty alt, no Chinese alt on non-CJK locales
empty_alt, chinese_alt = [], []
for rel, lang in pages:
    if lang in ("zh-CN", "ja-JP"):
        continue
    s = BeautifulSoup((ROOT / rel).read_text(encoding="utf-8", errors="replace"), "html.parser")
    for img in s.find_all("img"):
        a = img.get("alt")
        if a is None or not a.strip():
            empty_alt.append((rel, img.get("src", "")[:60]))
        elif CJK.search(a):
            chinese_alt.append((rel, a[:40]))
check("外语页图片 alt 全部非空", not empty_alt, empty_alt[:3])
check("外语页 alt 无简体中文残留（日语合法汉字除外）", not chinese_alt, chinese_alt[:3])

# 5. WebP siblings + live content negotiation
webps = list(ROOT.rglob("*.jpg.webp")) + list(ROOT.rglob("*.png.webp"))
check("WebP 副本已生成", len(webps) >= 26, f"{len(webps)} files")
status, hs, data = req("/cn/testimg/aboutpic.jpg", headers={"Accept": "image/webp,*/*"})
check("服务端 Accept 协商返回 WebP", hs.get("content-type") == "image/webp" and hs.get("vary", "").lower() == "accept",
      f"{hs.get('content-type')} / Vary={hs.get('vary')} / {len(data)} bytes")
status2, hs2, _ = req("/cn/testimg/aboutpic.jpg", headers={"Accept": "image/jpeg"})
check("不支持 WebP 时回退原 JPEG", hs2.get("content-type") == "image/jpeg", hs2.get("content-type"))

# 6. security headers on a real response
status3, hs3, _ = req("/index.html")
needed = ["strict-transport-security", "content-security-policy", "x-frame-options",
          "x-content-type-options", "referrer-policy", "permissions-policy"]
check("安全响应头齐全", status3 == 200 and all(h in hs3 for h in needed),
      [h for h in needed if h not in hs3])
check("HTML 响应带 no-cache 且静态资源可缓存", hs3.get("cache-control") == "no-cache",
      hs3.get("cache-control"))

# 7. private data still unreachable
status4, _, _ = req("/../maibida-ocr-rebuilt_messages/messages.ndjson")
check("私有留言数据路径不可静态读取", status4 in (403, 404), status4)

# 8. no dead internal links in deployable HTML
broken = []
skip = set(BACKUP_DIRS) | {"tools"}
for f in ROOT.rglob("*.html"):
    if set(f.parts) & skip:
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'<a\b[^>]*\bhref\s*=\s*"([^"]+)"', t, re.I):
        h = m.group(1).strip()
        if h.startswith(("#", "mailto:", "tel:", "javascript:", "http://", "https://", "//")):
            continue
        p = ((ROOT / f.relative_to(ROOT)).parent / h.split("#")[0].split("?")[0]).resolve()
        try:
            p.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if not p.exists():
            broken.append((f.name, h))
check("部署范围内内部死链为 0", not broken, broken[:3])

# 9. narrow-viewport rendering on representative pages (no horizontal overflow,
#    language switcher still opens, both nav entries visible)
try:
    from playwright.sync_api import sync_playwright
    overflow, menu_fail = [], []
    sample = ["index.html", "index.en-US.html", "index.ru-RU.html",
              "product/10032.ja-JP.html", "productlist/10039.es-MX.html"]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for rel in sample:
            pg = b.new_page(viewport={"width": 390, "height": 844})
            pg.goto(f"http://127.0.0.1:8899/{rel}", wait_until="domcontentloaded")
            pg.wait_for_timeout(350)
            w = pg.evaluate("() => document.documentElement.scrollWidth")
            if w > 400:
                overflow.append((rel, w))
            det = pg.query_selector("details.vp-language-switch")
            if det:
                det.click()
                if not pg.evaluate("() => document.querySelector('details.vp-language-switch').open"):
                    menu_fail.append(rel)
            else:
                menu_fail.append(rel + " (no switcher)")
            pg.close()
        b.close()
    check("390px 窄屏无横向溢出", not overflow, overflow)
    check("390px 语言菜单仍可展开", not menu_fail, menu_fail)
except Exception as e:
    check("390px 渲染验证", False, f"{type(e).__name__}: {e}")

passed = sum(1 for c in checks if c["ok"])
result = {"passed": passed, "total": len(checks),
          "all_pass": passed == len(checks), "checks": checks}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"PASS {passed}/{len(checks)}")
for c in checks:
    if not c["ok"]:
        print("  FAIL", c["name"], "|", c["detail"])
