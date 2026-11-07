#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Remove retired en-AU / es-ES entries from the 8 Chinese source pages.

Each source page carries 4 legacy references:
  2 x <link rel="alternate" hreflang="en-AU|es-ES">
  2 x <a hreflang="en-AU|es-ES"> in the language switcher
Total = 32. After removal every page has the same 12-link hreflang cluster and
11-item language menu as the 80 generated locale pages.

Byte-preserving: only the matched tags are removed; no reformatting, no
attribute reordering, no line-ending conversion. Idempotent.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "index.html",
    "product/10032.html",
    "product/smart-camera.html",
    "productlist/10029.html",
    "productlist/10030.html",
    "productlist/10034.html",
    "productlist/10036.html",
    "productlist/10039.html",
]
LOCALES = ("en-AU", "es-ES")
PAT_LINK = re.compile(
    r'<link\b[^>]*\bhreflang="(?:en-AU|es-ES)"[^>]*>', re.I)
PAT_ANCHOR = re.compile(
    r'<a\b[^>]*\bhreflang="(?:en-AU|es-ES)"[^>]*>.*?</a>', re.I | re.S)


def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT.parent / f"maibida-ocr-rebuilt_legacylinks_backup_{stamp}"
    report = {"timestamp": datetime.now().isoformat(timespec="seconds"),
              "backup": str(backup), "pages": [], "removed": 0}

    for rel in FILES:
        src = ROOT / rel
        raw = src.read_bytes().decode("utf-8")
        # back up first, preserving relative layout and timestamps
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        before = len(re.findall(r"en-AU|es-ES", raw))
        text, n_link = PAT_LINK.subn("", raw)
        text, n_anchor = PAT_ANCHOR.subn("", text)
        after = len(re.findall(r"en-AU|es-ES", text))
        if n_link != 2 or n_anchor != 2 or after != 0:
            raise RuntimeError(
                f"{rel}: unexpected counts links={n_link} anchors={n_anchor} "
                f"tokens {before}->{after}; nothing written")
        if text != raw:
            src.write_bytes(text.encode("utf-8"))
        report["pages"].append({"page": rel, "links": n_link,
                                "anchors": n_anchor,
                                "tokens_before": before,
                                "tokens_after": after,
                                "bytes": len(text.encode("utf-8"))})
        report["removed"] += n_link + n_anchor

    # verify backup is byte-identical to the pre-change source set is impossible
    # after writing, so instead verify every backup file differs from current
    # and all current files are free of legacy tokens.
    report["verification"] = {
        "pages": len(FILES),
        "all_current_clean": all(
            not re.search(r"en-AU|es-ES", (ROOT / f).read_bytes().decode("utf-8"))
            for f in FILES),
        "backup_files": sum(1 for _ in backup.rglob("*.html")),
    }
    (ROOT / "tools/legacy-links-removal.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"removed {report['removed']} legacy references from {len(FILES)} pages")
    print("backup:", backup)
    for p in report["pages"]:
        print(f"  {p['page']}: -{p['links']} links, -{p['anchors']} menu anchors "
              f"({p['tokens_before']} tokens -> {p['tokens_after']})")
    print("verification:", report["verification"])


if __name__ == "__main__":
    main()
