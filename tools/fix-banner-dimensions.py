"""Add intrinsic dimensions to homepage banner images.

All localized banner WebPs are 1920 x 1080. Explicit dimensions let the browser
reserve the correct layout box before image bytes arrive, avoiding layout shift.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    def add_dimensions(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\bwidth=", tag, re.I) and re.search(r"\bheight=", tag, re.I):
            return tag
        if tag.endswith("/>"):
            return tag[:-2] + ' width="1920" height="1080"/>'
        return tag[:-1] + ' width="1920" height="1080">'

    text = re.sub(
        r'<img\b[^>]*\bsrc="cn/images/home-banner/ml/[^"]+/banner-0[1-5]\.webp"[^>]*>',
        add_dimensions,
        text,
        flags=re.I,
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = [path.name for path in sorted(ROOT.glob("index*.html")) if patch(path)]
    print(f"updated {len(changed)} homepage variants")


if __name__ == "__main__":
    main()
