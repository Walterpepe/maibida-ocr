"""Full-site backup with SHA-256 manifest, plus a desktop mirror copy.

Usage:
    python tools/backup-full-site.py [--stamp YYYYMMDD_HHMMSS]

Creates (outside the site root, so the site is not modified during backup):
    D:/20260919GPT/maibida-ocr-rebuilt_backup_<stamp>/
    D:/桌面/maibida-ocr-rebuilt_backup_<stamp>/
    D:/20260919GPT/_backup_report_<stamp>.json

Both backup directories contain BACKUP_MANIFEST.json with per-file SHA-256
hashes. The script re-hashes every file in both copies before reporting OK.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

SITE = Path("D:/20260919GPT/maibida-ocr-rebuilt")
PARENT = Path("D:/20260919GPT")
DESKTOP = Path("D:/桌面")
MANIFEST_NAME = "BACKUP_MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def files_of(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file() and p.name != MANIFEST_NAME)


def manifest(root: Path):
    return {
        str(p.relative_to(root)).replace("\\", "/"): {
            "size": p.stat().st_size,
            "sha256": sha256(p),
        }
        for p in files_of(root)
    }


def verify(root: Path, expected: dict) -> list[str]:
    bad = []
    for rel, meta in expected.items():
        p = root / rel
        if not p.is_file():
            bad.append(rel + " : MISSING")
        elif p.stat().st_size != meta["size"] or sha256(p) != meta["sha256"]:
            bad.append(rel + " : SIZE/HASH MISMATCH")
    extra = [str(p.relative_to(root)).replace("\\", "/")
             for p in files_of(root)
             if str(p.relative_to(root)).replace("\\", "/") not in expected]
    return bad + ["EXTRA: " + x for x in extra]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", default=dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = ap.parse_args()
    stamp = args.stamp
    primary = PARENT / f"maibida-ocr-rebuilt_backup_{stamp}"
    desktop = DESKTOP / f"maibida-ocr-rebuilt_backup_{stamp}"
    for p in (primary, desktop):
        if p.exists():
            print("ERROR: target already exists:", p)
            return 2
    if not SITE.is_dir() or not DESKTOP.is_dir():
        print("ERROR: site root or desktop missing")
        return 2

    src_files = files_of(SITE)
    src_bytes = sum(p.stat().st_size for p in src_files)
    print(f"source: {len(src_files)} files / {src_bytes:,} bytes")

    print("copying ->", primary)
    shutil.copytree(SITE, primary, copy_function=shutil.copy2)
    exp = manifest(primary)
    (primary / MANIFEST_NAME).write_text(
        json.dumps({"stamp": stamp, "source": str(SITE), "files": exp},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print("copying ->", desktop)
    shutil.copytree(primary, desktop, copy_function=shutil.copy2)

    print("verifying primary + desktop ...")
    bad1 = verify(primary, exp)
    bad2 = verify(desktop, exp)
    ok = not bad1 and not bad2
    total = sum(v["size"] for v in exp.values())
    report = {
        "stamp": stamp,
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": str(SITE),
        "primary": str(primary),
        "desktop": str(desktop),
        "files": len(exp),
        "bytes": total,
        "sha256_verified": ok,
        "primary_errors": bad1[:20],
        "desktop_errors": bad2[:20],
    }
    (PARENT / f"_backup_report_{stamp}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
