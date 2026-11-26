"""Static regression checks for the bilingual interior redesign shell."""

from __future__ import annotations

import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = runpy.run_path(str(ROOT / "tools" / "redesign" / "apply-inner-shell.py"))
CSS = (ROOT / "cn" / "css" / "vision-inner.css").read_text(encoding="utf-8")

assert re.search(
    r"body\.vision-policy \.pl-section\s*\{[^}]*padding:\s*28px 24px",
    CSS,
    re.S,
)

for relative in G["PAGES"]:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    body_attrs = text.split("<body", 1)[1].split(">", 1)[0]
    assert "vision-inner" in body_attrs, relative
    expected_class = (
        "vision-product"
        if relative.startswith("product/")
        else "vision-productlist"
        if relative.startswith("productlist/")
        else "vision-contact"
        if relative.startswith("contact")
        else "vision-policy"
    )
    assert expected_class in body_attrs, relative
    prefix = "../" if "/" in relative else ""
    assert (
        f'href="{prefix}cn/css/vision-inner.css?v={G["VERSION"]}"' in text
    ), relative
    assert (
        f'src="{prefix}cn/js/vision-inner.js?v={G["VERSION"]}"' in text
    ), relative
    if relative.startswith("contact"):
        assert (
            f'{prefix}cn/images/redesign/products/camera-hero-studio.webp'
            in text
        ), relative
        assert "technology-camera.webp" not in text, relative

print(f"PASS interior shell applied to {len(G['PAGES'])} bilingual pages")
