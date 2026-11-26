"""Regression checks for the experimental homepage builder."""

from __future__ import annotations

import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = runpy.run_path(str(ROOT / "tools" / "redesign" / "build-home.py"))
CSS = (ROOT / "cn" / "css" / "vision-home.css").read_text(encoding="utf-8")
HOME_IMAGES = {
    "products/monitor-hero-studio.webp",
    "products/camera-hero-studio.webp",
    "products/sorter-hero-studio.webp",
    "products/feeder-hero-studio.webp",
    "products/inline-connector-hero-studio.webp",
}

for selector in (
    ".vh-manifesto-inner",
    ".vh-section-head",
    ".vh-tech-inner",
    ".vh-applications-layout",
):
    assert re.search(
        rf"{re.escape(selector)}\s*\{{[^}}]*padding-inline:\s*36px",
        CSS,
        re.S,
    ), selector

assert re.search(
    r"body\.vision-home \.vh-menu > summary\s*\{[^}]*font-size:\s*14px[^}]*line-height:\s*44px",
    CSS,
    re.S,
)
assert re.search(
    r"\.vh-metrics\s*\{[^}]*width:\s*min\(1240px, calc\(100% - 40px\)\)",
    CSS,
    re.S,
)

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
    assert '<article class="vh-application"><span' not in body, code
    assert '<article class="vh-application"><h3' in body, code
    for image in HOME_IMAGES:
        assert f"cn/images/redesign/{image}" in body, (code, image)
    assert "cn/images/redesign/technology-camera.webp" not in body, code

print("PASS homepage builder preserves head metadata")
