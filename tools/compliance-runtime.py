# -*- coding: utf-8 -*-
"""Read-only runtime spot-check for the compliance prelaunch audit."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8899/"
OUT = ROOT / "tools/compliance-runtime.json"

DESKTOP = [
    "index.html", "index.en-US.html", "index.es-MX.html", "index.ko-KR.html",
    "index.th-TH.html", "index.vi-VN.html", "product/10032.html",
    "product/10032.en-US.html", "product/10032.ja-JP.html", "product/10032.ru-RU.html",
    "product/smart-camera.html", "product/smart-camera.es-MX.html",
    "productlist/10034.html", "productlist/10036.html", "productlist/10036.en-US.html",
    "productlist/10039.th-TH.html", "contact.html", "contact.en-US.html",
    "contact.es-MX.html", "index.en-AU.html",
]
MOBILE = ["index.html", "index.en-US.html", "index.es-MX.html",
          "product/10032.html", "product/10032.en-US.html",
          "productlist/10036.html", "contact.html"]

PROBE_JS = """() => {
  const imgs = [...document.images];
  const a = [...document.querySelectorAll('a[href]')];
  const det = document.querySelectorAll('details.vp-language-switch');
  const f = document.querySelector('form.cf-form');
  const txt = document.body.innerText || '';
  return {
    title: document.title,
    textLen: txt.length,
    replacementChar: txt.includes('\\uFFFD'),
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    brokenImages: imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src).slice(0, 8),
    imgTotal: imgs.length,
    waLinks: a.filter(x => /wa\\.me|whatsapp/i.test(x.href)).length,
    telLinks: a.filter(x => x.href.startsWith('tel:')).length,
    mailLinks: a.filter(x => x.href.startsWith('mailto:')).length,
    langDetails: det.length,
    langItems: det.length ? det[0].querySelectorAll('a[href]').length : 0,
    h1: document.querySelectorAll('h1').length,
    noindex: !!document.querySelector('meta[name="robots"][content*="noindex"]'),
    form: f ? {action: f.getAttribute('action'), method: (f.getAttribute('method')||'').toLowerCase(),
               fields: [...f.querySelectorAll('[name]')].map(x=>x.getAttribute('name')),
               checkboxes: f.querySelectorAll('input[type=checkbox]').length,
               required: f.querySelectorAll('[required]').length} : null,
    navLinks: a.filter(x => x.closest('nav,.top,.top2,header')).length
  };
}"""


def main():
    results = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        for label, viewport, rels in (("desktop-1440x900", {"width": 1440, "height": 900}, DESKTOP),
                                      ("mobile-390x844", {"width": 390, "height": 844}, MOBILE)):
            page = browser.new_page(viewport=viewport)
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)[:180]))
            for rel in rels:
                item = {"viewport": label, "page": rel}
                try:
                    resp = page.goto(BASE + rel, wait_until="load", timeout=30000)
                    page.wait_for_timeout(220)
                    item["http"] = resp.status if resp else 0
                    d = page.evaluate(PROBE_JS)
                    item.update(d)
                    item["overflow"] = bool(d["scrollWidth"] > d["clientWidth"] + 1)
                    item["js_errors"] = list(errs)
                    errs.clear()
                    # language menu interaction
                    try:
                        page.locator("details.vp-language-switch summary").first.click(timeout=2500)
                        item["lang_menu_opens"] = bool(page.evaluate(
                            "!!document.querySelector('details.vp-language-switch')?.open"))
                    except Exception as e:
                        item["lang_menu_opens"] = None
                        item["lang_menu_error"] = str(e)[:100]
                    # contact form real submit (desktop only, once)
                    if label.startswith("desktop") and rel == "contact.html":
                        try:
                            page.fill("#cf-name", "Compliance Audit")
                            page.fill("#cf-email", "audit@example.com")
                            page.fill("#cf-phone", "000000")
                            page.fill("#cf-company", "Audit")
                            page.fill("#cf-country", "CN")
                            page.fill("#cf-message", "prelaunch audit submission test")
                            page.click("#message-form button[type=submit]")
                            page.wait_for_timeout(900)
                            item["submit_feedback"] = page.locator(".cf-status, .cf-msg, #cf-status").first.inner_text()[:180] \
                                if page.locator(".cf-status, .cf-msg, #cf-status").count() else "(no status node)"
                            item["submit_ok"] = bool(re_ := True)
                        except Exception as e:
                            item["submit_error"] = str(e)[:150]
                except Exception as e:
                    item["fatal"] = str(e)[:200]
                results.append(item)
            page.close()
        browser.close()

    # clean the test record so no personal data remains
    nd = Path(r"D:/20260919GPT/maibida-ocr-rebuilt_messages/messages.ndjson")
    if nd.exists():
        nd.write_text("", encoding="utf-8")

    summary = {
        "checked": len(results),
        "http_ok": sum(1 for r in results if r.get("http") == 200),
        # A short CJK page is not a blank page. Only flag pages that are short
        # AND have no heading/form to render (e.g. a failed/replaced document).
        "blank": [r["page"] for r in results
                  if r.get("textLen", 0) < 200
                  and not (r.get("h1", 0) and r.get("form"))],
        "garbled": [r["page"] for r in results if r.get("replacementChar")],
        "broken_images": [r["page"] for r in results if r.get("brokenImages")],
        "js_error_pages": [r["page"] for r in results if r.get("js_errors")],
        "overflow_pages": [{"page": r["page"], "viewport": r["viewport"],
                            "sw": r.get("scrollWidth"), "cw": r.get("clientWidth")}
                           for r in results if r.get("overflow")],
        "lang_menu_failed": [r["page"] for r in results if r.get("lang_menu_opens") is False],
        "tel_link_pages": sum(1 for r in results if r.get("telLinks", 0) > 0),
        "mailto_link_pages": sum(1 for r in results if r.get("mailLinks", 0) > 0),
        "wa_link_pages": sum(1 for r in results if r.get("waLinks", 0) > 0),
        "noindex_pages": [r["page"] for r in results if r.get("noindex")],
        "form_sample": next((r.get("form") for r in results if r.get("form")), None),
        "submit_feedback": next((r.get("submit_feedback") for r in results if r.get("submit_feedback")), None),
    }
    OUT.write_text(json.dumps({"summary": summary, "results": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
