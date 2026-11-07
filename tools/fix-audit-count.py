#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Correct the audit-count wording from 21 to the actual 20 weighted audits
(crawl 5 + index 5 + content 5 + render 5 = 20, weights sum to 100)."""
from pathlib import Path

T = Path(__file__).resolve().parent


def patch(name, pairs):
    p = T / name
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert old in s, f"{name}: missing {old[:50]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"{name}: corrected")


patch("google-crawl-score.py", [
    ("21 weighted audits", "20 weighted audits"),
    ("21 项审计", "20 项审计"),
])
patch("build-final-report.py", [
    ("21 项审计", "20 项审计"),
    ("21 项加权审计", "20 项加权审计"),
])
patch("patch-final-score.py", [
    ("21 项审计", "20 项审计"),
    ("all 21 audits", "all 20 audits"),
])
patch("localization-review.json", [
    ("all 21 audits passing", "all 20 audits passing"),
])
