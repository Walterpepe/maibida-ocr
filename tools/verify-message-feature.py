"""Independent verification for the message form feature.

Static structure, HTTP behaviour, browser rendering at two viewports, a real
end-to-end submission, invalid-payload handling and privacy boundary.
The self-test record is removed from the NDJSON file afterwards.
"""
import http.client as hc
import json
import re
import runpy
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8899"
DATA = ROOT.parent / "maibida-ocr-rebuilt_messages" / "messages.ndjson"
G = runpy.run_path(str(ROOT / "tools" / "add-message-feature.py"))
I18N = G["I18N"]
LOCALES = G["LOCALES"]
PAGES = G["PAGES"]
FIELDS = ["name", "email", "phone", "company", "country", "message"]
STATIC_FIELDS = FIELDS + ["consent", "website"]
results = []
errors = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    if not ok:
        errors.append(f"{name}: {detail}")


def http(method, target, body=None, ctype="application/json"):
    conn = hc.HTTPConnection("127.0.0.1", 8899, timeout=10)
    conn.request(method, target, body=body, headers={"Content-Type": ctype} if body else {})
    r = conn.getresponse()
    raw = r.read().decode("utf-8", "replace")
    conn.close()
    return r.status, raw


def formal_pages():
    out = []
    for p in PAGES:
        out.append((p, "zh-CN"))
        q = Path(p)
        for l in LOCALES:
            out.append((str(q.with_name(q.stem + "." + l + ".html")).replace("\\", "/"), l))
    return out


# ---------------------------------------------------------------- static ----
for lang in ["zh-CN"] + LOCALES:
    rel = "contact.html" if lang == "zh-CN" else f"contact.{lang}.html"
    f = ROOT / rel
    if not f.exists():
        check(f"page {rel}", False, "missing")
        continue
    t = f.read_text(encoding="utf-8")
    soup = BeautifulSoup(t, "html.parser")
    ok = (
        soup.html.get("lang") == lang
        and 'noindex,follow' in t
        and len(soup.find_all("h1")) == 1
        and all(soup.find(attrs={"name": k}) for k in STATIC_FIELDS)
        and soup.find("input", {"name": "country"})
        and soup.find("input", {"name": "consent", "type": "checkbox"}) is not None
        and not soup.find("input", {"name": "consent"}).has_attr("checked")
        and 'privacy' in t and 'mailto:mai_bida@163.com' in t
        and 'cn/css/contact.css' in t
        and 'cn/js/contact.js' in t
        and all(i.get("alt") for i in soup.find_all("img"))
        and I18N[lang]["submit"] in t
    )
    check(f"page {rel}", ok, "lang/noindex/h1/6 fields/consent/privacy/honeypot/assets/alt/submit")
    check(f"page {rel} no sitemap", "contact" not in (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

for rel, lang in formal_pages():
    t = (ROOT / rel).read_text(encoding="utf-8")
    soup = BeautifulSoup(t, "html.parser")
    links = soup.select("a.vp-contact-link")
    prefix = "../" if "/" in rel else ""
    target = prefix + ("contact.html" if lang == "zh-CN" else f"contact.{lang}.html")
    ok = (len(links) == 1
          and links[0].get("href") == target
          and links[0].get_text(strip=True) == I18N[lang]["nav"]
          and (ROOT / target.lstrip("../")).exists())
    if not ok:
        check(f"nav {rel}", False, f"links={len(links)} href={links[0].get('href') if links else '-'}")

check("nav on all 88 formal pages",
      sum(1 for r in results if r["check"].startswith("nav ") and r["check"] != "nav on all 88 formal pages") == 0,
      "per-page failures listed above")
check("nav css block", "BEGIN vp-contact-link" in (ROOT / "cn/css/site-multilingual.css").read_text(encoding="utf-8"))
check("contact assets exist",
      (ROOT / "cn/css/contact.css").exists() and (ROOT / "cn/js/contact.js").exists())
audit = (ROOT / "tools" / "full-site-audit.py").read_text(encoding="utf-8")
check("audit registers 11 contact pages", '"contact.html"' in audit and 'for l in LOCALES' in audit)

# ------------------------------------------------------------------ http ----
code, _ = http("GET", "/index.html")
check("GET index.html", code == 200, code)
code, _ = http("GET", "/contact.html")
check("GET contact.html", code == 200, code)
code, raw = http("GET", "/api/messages")
check("GET /api/messages blocked", code == 405, f"{code} {raw[:80]}")
code, _ = http("GET", "/../maibida-ocr-rebuilt_messages/messages.ndjson")
check("message store not static-reachable", code == 403, code)
code, raw = http("POST", "/api/messages", json.dumps({"name": "x"}))
check("invalid payload rejected", code == 400, f"{code} {raw[:80]}")
valid = {"name": "SELF TEST HTTP", "email": "http@example.com",
         "message": "consent probe", "consent": "yes"}
code, raw = http("POST", "/api/messages", json.dumps({k: v for k, v in valid.items() if k != "consent"}))
check("submission without consent rejected", code == 400, f"{code} {raw[:80]}")
code, raw = http("POST", "/api/messages", json.dumps(dict(valid, website="http://spam.example")))
check("honeypot submission not persisted", code == 200 and "ignored" in raw, f"{code} {raw[:80]}")
code, raw = http("POST", "/api/messages", "<html>", "text/html")
check("wrong content type rejected", code == 415, f"{code} {raw[:80]}")

# -------------------------------------------------------------- browser ----
test_id = None
try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="msedge", headless=True)
        except Exception:
            browser = pw.chromium.launch(headless=True)
        for width in (1440, 390):
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            for rel in ("index.html", "index.en-US.html", "contact.html", "contact.en-US.html"):
                page = ctx.new_page()
                js_errors = []
                page.on("pageerror", lambda e: js_errors.append(str(e)))
                page.goto(f"{BASE}/{rel}", wait_until="load")
                overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                check(f"render {width} {rel} no overflow", overflow <= 1, f"overflow={overflow}px")
                check(f"render {width} {rel} no js error", not js_errors, js_errors[:1])
                if rel.startswith("index"):
                    link = page.locator("a.vp-contact-link")
                    check(f"render {width} {rel} nav visible", link.count() == 1 and link.is_visible(),
                          f"count={link.count()}")
                    page.locator("details.vp-language-switch summary").click()
                    check(f"render {width} {rel} language menu still opens",
                          page.locator("details.vp-language-switch nav").is_visible())
                else:
                    check(f"render {width} {rel} form visible",
                          page.locator("#message-form").is_visible())
                page.close()
            ctx.close()

        # end-to-end submission
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(f"{BASE}/contact.html", wait_until="load")
        page.fill("#cf-name", "SELF TEST")
        page.fill("#cf-email", "selftest@example.com")
        page.fill("#cf-phone", "0000")
        page.fill("#cf-company", "Verification")
        page.fill("#cf-country", "Testland")
        page.fill("#cf-message", "automated end-to-end verification")
        page.check("#cf-consent")
        page.click("button[type=submit]")
        page.wait_for_selector("#form-status.ok", timeout=10000)
        check("end-to-end submit shows success", True)
        if DATA.exists():
            lines = [json.loads(x) for x in DATA.read_text(encoding="utf-8").splitlines() if x.strip()]
            last = lines[-1] if lines else {}
            test_id = last.get("id")
            check("record persisted with all fields",
                  all(k in last for k in FIELDS + [
                      "id", "receivedAt", "lang", "source", "consent",
                      "consentVersion", "policyVersion", "retentionUntil", "ipHash"])
                  and last.get("name") == "SELF TEST"
                  and last.get("consent") == "yes"
                  and last.get("lang") == "zh-CN", last.get("id"))
        else:
            check("record persisted with all fields", False, "NDJSON missing")
        ctx.close()
        browser.close()
except Exception as e:
    check("browser verification", False, repr(e))

# remove only the self-test record created above
if test_id and DATA.exists():
    lines = DATA.read_text(encoding="utf-8").splitlines()
    kept = [x for x in lines if x.strip() and json.loads(x).get("id") != test_id]
    DATA.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    check("self-test record cleaned", True, f"id={test_id}")

report = {"passed": len(results) - len(errors), "total": len(results),
          "errors": errors, "results": results}
(ROOT / "tools" / "message-feature-verify.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"PASS {report['passed']}/{report['total']}")
for e in errors:
    print("FAIL", e)
raise SystemExit(1 if errors else 0)
