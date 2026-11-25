"""Regression checks for the experimental homepage builder."""

from __future__ import annotations

import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = runpy.run_path(str(ROOT / "tools" / "redesign" / "build-home.py"))
CSS = (ROOT / "cn" / "css" / "vision-home.css").read_text(encoding="utf-8")

for selector, declaration in (
    (".vh-hero-shell", "grid-template-columns: repeat(12"),
    (".vh-proof-inner", "grid-template-columns"),
    (".vh-product-catalog", "grid-template-columns: repeat(5"),
    (".vh-product-grid", "grid-template-columns: repeat(12"),
    (".vh-cta-inner", "grid-template-columns"),
):
    assert re.search(
        rf"{re.escape(selector)}\s*\{{[^}}]*{re.escape(declaration)}",
        CSS,
        re.S,
    ), selector
assert re.search(r"--vh-orange:\s*#ff5a1f", CSS, re.I)

for code, data in G["LOCALES"].items():
    source = subprocess.check_output(
        ["git", "show", f"{G['BASE_COMMIT']}:{data['file']}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    head = G["build_head"](source, data)
    assert re.search(r'<meta[^>]+name="viewport"', head, re.I), (
        f"{code} missing viewport; "
        f"source={bool(re.search(r'name=.viewport', source, re.I))} "
        f"head={head[:500]}"
    )
    assert "<title>" in head.lower(), f"{code} missing title; {head[:500]}"
    assert head.lower().count("<head") == 1, code
    assert head.lower().count("</head>") == 1, code

body = G["build_body"](data)
assert '<section class="vh-proof"' in body, code
assert '<nav class="vh-product-catalog"' in body, code
assert "vh-product-card--hero" in body, code
assert '<div class="vh-hero-shell">' in body, code

print("PASS commercial homepage builder and product matrix")
