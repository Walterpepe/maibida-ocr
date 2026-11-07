#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix the oversized whitespace in the smart-camera "应用案例" marquee.

The case images are about 2:1 while the cards were forced to 1.08/1, so every
card had ~160px of empty white space below the picture. This script replaces the
identical inline marquee <style> block in all 13 smart-camera language pages
with a version whose card ratio matches the images.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "product"

OLD = re.compile(
    r"<style>\s*/\* 应用案例：从右向左无缝移动轮流播放.*?</style>",
    re.S,
)

NEW = """<style>
/* 应用案例：从右向左无缝移动轮流播放（8个案例复制2份构成连续循环） */
/* 案例原图约为 2:1，卡片同比例后不再出现图片下方的大块空白 */
.vp-app-viewport{position:relative;overflow:hidden;--vp-app-gap:18px;-webkit-mask-image:linear-gradient(to right,#000 calc(100% - 72px),transparent);mask-image:linear-gradient(to right,#000 calc(100% - 72px),transparent)}
.vp-app-track{display:flex;align-items:stretch;gap:var(--vp-app-gap);width:max-content;animation:vp-apps-roll 46s linear infinite;will-change:transform}
@keyframes vp-apps-roll{from{transform:translateX(0)}to{transform:translateX(calc(-50% - var(--vp-app-gap)/2))}}
.vp-app-viewport:hover .vp-app-track{animation-play-state:paused}
.vp-app-track .vp-app{flex:0 0 calc((min(1180px,100vw - 40px) - 2*var(--vp-app-gap))/3);height:auto;aspect-ratio:2/1}
.vp-app-track .vp-app .ocr-case-card{display:block;width:100%;height:100%}
.vp-app-track .vp-app .ocr-case-card>img{display:block;width:100%;height:100%;min-height:0;object-fit:contain;object-position:center;background:#fff}
.vision-page>section#apps{padding:60px 0}
.vision-page>section#apps .vp-head{margin-bottom:28px}
@media (max-width:900px){.vp-app-viewport{--vp-app-gap:14px}.vp-app-track .vp-app{flex-basis:calc((min(1180px,100vw - 40px) - var(--vp-app-gap))/2)}}
@media (max-width:560px){.vp-app-track .vp-app{flex-basis:calc((min(1180px,100vw - 40px) - var(--vp-app-gap))/1.35)}.vision-page>section#apps{padding:44px 0}}
@media (prefers-reduced-motion:reduce){.vp-app-track{animation:none}}
</style>"""


def main() -> None:
    changed = []
    for path in sorted(PRODUCT.glob("smart-camera*.html")):
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        text, count = OLD.subn(lambda _: NEW, text, count=1)
        if count != 1:
            if "vp-app-track" in text:
                raise RuntimeError(f"Unexpected marquee markup in {path.name}")
            continue
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
        changed.append(path.name)
    print(f"updated {len(changed)} pages")
    for name in changed:
        print(" -", name)
    if len(changed) != 13:
        raise RuntimeError(f"Expected 13 pages, updated {len(changed)}")


if __name__ == "__main__":
    main()
