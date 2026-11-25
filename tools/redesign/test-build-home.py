"""Regression checks for the experimental homepage builder."""

from __future__ import annotations

import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = runpy.run_path(str(ROOT / "tools" / "redesign" / "build-home.py"))

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

print("PASS homepage builder preserves head metadata")
