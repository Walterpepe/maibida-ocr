#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent verification of the 100/100 convergence (read-only)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

R = Path(__file__).resolve().parent.parent
T = R / "tools"
CJK = re.compile(r"[\u4e00-\u9fff]")
ok, bad = [], []


def chk(cond, label):
    (ok if cond else bad).append(label)


sc = json.loads((T / "google-crawl-score.json").read_text(encoding="utf-8"))
chk(sc["score"] == 100.0, "score 100.0/100")
chk(len(sc["audits"]) == 20, "20 weighted audits")
chk(all(a["lost"] == 0 for a in sc["audits"]), "zero deductions across all audits")
chk(not sc["static_fails"], "zero static fails on 88 formal pages")
chk(all(d["pct"] == 100.0 for d in sc["dimensions"]), "4 dimensions at 100%")

sa = json.loads((T / "site-audit.json").read_text(encoding="utf-8"))
lv = {}
for i in sa.get("issues", []):
    lv[i["level"]] = lv.get(i["level"], 0) + 1
chk(lv.get("error", 0) == 0 and lv.get("warn", 0) == 0,
    "site audit: 0 errors / 0 warnings (tips=%d, info=%d)" %
    (lv.get("tip", 0), lv.get("info", 0)))

for f in ["final-100-report.html", "google-crawl-score.html", "site-audit-report.html"]:
    p = T / f
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    chk(bool(t) and len(t) > 2000, f + " generated")
    chk("21 \u9879" not in t, f + " has no stale '21 audits' wording")

for rel, lang in [("productlist/10039.en-US.html", "en-US"),
                  ("product/smart-camera.ru-RU.html", "ru-RU"),
                  ("product/10032.th-TH.html", "th-TH")]:
    s = BeautifulSoup((R / rel).read_text(encoding="utf-8"), "html.parser")
    nodes = s.select(".ocr-transcript")
    chk(bool(nodes) and all(n.get("data-lang") == lang and n.get_text(strip=True)
                            for n in nodes),
        rel + " transcripts localised (" + str(len(nodes)) + ")")

for rel in ["index.en-AU.html", "product/10032.en-AU.html",
            "product/smart-camera.en-AU.html", "product/smart-camera.es-ES.html"]:
    raw = (R / rel).read_text(encoding="utf-8")
    s = BeautifulSoup(raw, "html.parser")
    rob = s.find("meta", attrs={"name": "robots"})
    cans = [x.get("href", "") for x in s.find_all("link")
            if "canonical" in x.get("rel", [])]
    clean = ("noindex" in (rob.get("content", "") if rob else "")
             and any("en-SG" in c or "es-MX" in c for c in cans)
             and not CJK.search(s.get_text(" ", strip=True)))
    chk(clean, rel + " is a clean localised redirect stub")

print("PASS", len(ok))
for x in ok:
    print("  +", x)
print("FAIL", len(bad))
for x in bad:
    print("  -", x)
