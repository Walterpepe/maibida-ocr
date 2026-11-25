"""Apply the premium interior shell to the zh-CN and en-US subpages.

The shared product content and compliance copy remain intact. This migration
adds the new body class, stylesheet and interaction script idempotently.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = "202611250123"
PAGES = [
    "product/10032.html",
    "product/10032.en-US.html",
    "product/smart-camera.html",
    "product/smart-camera.en-US.html",
    "productlist/10029.html",
    "productlist/10029.en-US.html",
    "productlist/10030.html",
    "productlist/10030.en-US.html",
    "productlist/10034.html",
    "productlist/10034.en-US.html",
    "productlist/10036.html",
    "productlist/10036.en-US.html",
    "productlist/10039.html",
    "productlist/10039.en-US.html",
    "contact.html",
    "contact.en-US.html",
    "privacy.html",
    "privacy.en-US.html",
    "terms.html",
    "terms.en-US.html",
]


def add_body_class(source: str) -> str:
    match = re.search(r"<body\b([^>]*)>", source, re.I)
    if not match:
        raise RuntimeError("body element missing")
    attrs = match.group(1)
    class_match = re.search(r'\bclass="([^"]*)"', attrs, re.I)
    if class_match:
        classes = class_match.group(1).split()
        if "vision-inner" not in classes:
            classes.append("vision-inner")
        replacement = f'class="{" ".join(classes)}"'
        attrs = attrs[:class_match.start()] + replacement + attrs[class_match.end():]
    else:
        attrs += ' class="vision-inner"'
    return source[:match.start()] + f"<body{attrs}>" + source[match.end():]


def patch(path: Path) -> bool:
    raw = path.read_bytes()
    source = raw.decode("utf-8")
    original = source
    relative = path.relative_to(ROOT).as_posix()
    prefix = "../" if "/" in relative else ""
    newline = "\r\r\n" if "\r\r\n" in source else "\r\n" if "\r\n" in source else "\n"
    source = add_body_class(source)
    source = re.sub(
        r'<link[^>]*href="[^"]*cn/css/vision-inner\.css[^"]*"[^>]*>',
        "",
        source,
        flags=re.I,
    )
    source = re.sub(
        r'<script[^>]*src="[^"]*cn/js/vision-inner\.js[^"]*"[^>]*></script>',
        "",
        source,
        flags=re.I,
    )
    source = source.replace(
        "</head>",
        f'{newline}<link rel="stylesheet" href="{prefix}cn/css/vision-inner.css?v={VERSION}"/>'
        f"{newline}"
        "</head>",
        1,
    )
    source = source.replace(
        "</body>",
        f'{newline}<script src="{prefix}cn/js/vision-inner.js?v={VERSION}" defer></script>'
        f"{newline}"
        "</body>",
        1,
    )
    if source != original:
        path.write_bytes(source.encode("utf-8"))
        return True
    return False


def main() -> None:
    changed = [rel for rel in PAGES if patch(ROOT / rel)]
    print(f"updated {len(changed)} bilingual subpages")
    for rel in changed:
        print(rel)


if __name__ == "__main__":
    main()
