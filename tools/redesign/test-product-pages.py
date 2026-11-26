"""Regression checks for the rebuilt bilingual product-family pages."""

from __future__ import annotations

import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = runpy.run_path(str(ROOT / "tools" / "redesign" / "build-product-pages.py"))
CSS = (ROOT / "cn" / "css" / "vision-products.css").read_text(encoding="utf-8")

assert re.search(r"\.vp2-section-intro\s*\{[^}]*padding-inline:\s*36px", CSS, re.S)
assert re.search(r"\.vp2-dossier-head > \.vp2-wrap\s*\{[^}]*padding-inline:\s*36px", CSS, re.S)
assert re.search(
    r"\.vp2-legacy \.spec-disclaimer\s*\{[^}]*padding:\s*14px 20px 16px !important",
    CSS,
    re.S,
)
assert re.search(
    r"\.vp2-theme-dark \.vp2-hero-media\s*\{[^}]*background:\s*var\(--vp2-paper\)",
    CSS,
    re.S,
)
assert re.search(
    r"body\.vp2-page \.vp2-legacy \.vp-head,\s*body\.vp2-page \.vp2-legacy \.fp-head",
    CSS,
    re.S,
)
assert re.search(
    r"body\.vp2-page \.vp2-legacy \.vp-apps-dark \.vp-head h2",
    CSS,
    re.S,
)
assert "body.vp2-page .vp2-product-menu > summary" in CSS
assert "body.vp2-page .vp2-language > summary" in CSS

for slug, entry in G["PAGES"].items():
    for lang_key in ("zh", "en"):
        relative = entry[lang_key]["file"]
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        body_attrs = text.split("<body", 1)[1].split(">", 1)[0]
        assert "vp2-page" in body_attrs, relative
        assert f"vp2-{slug}" in body_attrs, relative
        assert f"vp2-theme-{entry['theme']}" in body_attrs, relative
        assert text.count(G["HOME_MARKER"]) == 1, relative
        assert text.count(G["HOME_END"]) == 1, relative
        assert text.count(G["CTA_MARKER"]) == 1, relative
        assert text.count(G["CTA_END"]) == 1, relative
        assert text.count("vp2-legacy") >= 1, relative
        assert 'class="vp2-family-nav"' not in text, relative
        assert ".ny-navs" not in text, relative
        assert 'class="vp2-product-menu"' in text, relative
        assert 'class="vp2-product-popover"' in text, relative
        popover = text.split('class="vp2-product-popover">', 1)[1].split("</div>", 1)[0]
        assert popover.count('aria-current="page"') == 1, relative
        expected_target = next(
            target
            for key, _, _, target in G["PRODUCT_MENU"]["zh" if lang_key == "zh" else "en"]
            if key == entry["family"]
        )
        assert f'href="../{expected_target}" aria-current="page"' in popover, relative
        assert "vp2-breadcrumb" not in text, relative
        assert "vp2-loop" not in text, relative
        assert 'class="vp2-feature"><span>' not in text, relative
        assert 'href="#vp2-family"' not in text, relative
        assert f'href="../index{"" if lang_key == "zh" else ".en-US"}.html#products"' in text, relative
        assert text.lower().count("<h1") == 1, relative
        assert '<h1 id="vp2-product-title">' in text, relative
        assert 'class="sr-h1"' not in text, relative
        assert 'class="float-sild"' not in text, relative
        assert "function scrollToTop()" not in text, relative
        if slug in G["DETAILS"]:
            assert '<section class="vp2-detail">' in text, relative
        if slug == "sorter":
            assert '<section class="vp2-specifications"' in text, relative
            assert '<table class="vp2-spec-table">' in text, relative
        assert (
            f'../cn/css/vision-products.css?v={G["VERSION"]}' in text
        ), relative
        assert (
            f'../cn/js/vision-products.js?v={G["VERSION"]}' in text
        ), relative
        image = ROOT / "cn" / "images" / "redesign" / "products" / entry["image"]
        assert image.exists(), image
        assert (
            f'../cn/images/redesign/products/{entry["image"]}?v={G["VERSION"]}'
            in text
        ), relative

print(f"PASS product-family pages rebuilt: {len(G['PAGES']) * 2}")
