# -*- coding: utf-8 -*-
"""Replace the raster technical-specification table with selectable HTML.

Source: UserFiles/upload/image/20251030/6389743000645652104098007.png
Wording comes from ocr-inventory.json / ocr-text.txt, verified against the
original raster. Geometry follows the original 2066 x 1888 pixel grid.
Only the first tab's raster image is replaced; the existing ocr-table in the
second tab and the dimension drawing are left untouched.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE_DIR = ROOT / "product"
IMAGE_NAME = "6389743000645652104098007.png"
CSS_HREF = "../cn/css/ocr-spec-table.css"
PHOTO_DIR = "../cn/images/ocr-spec/"

ZH = {
    "lang": "zh-CN",
    "css": "ocr-spec-table",
    "caption": "技术参数表",
    "model": "型号",
    "param": "参数",
    "rows": [
        ("相机型号", "V1 Pro", "千兆网工业相机\nMD-GE500W", "camera-v1pro.png", "camera-gige.png", True),
        ("显示尺寸", "14寸触摸电容屏", "13.3寸触摸电容屏", None, None, False),
        ("屏幕分辨率", "1920*1080", "1920*1080", None, None, False),
        ("支持相机数量", "4个", "4个", None, None, False),
        ("主机主动氛围灯", "待机白色、运行蓝色、报警红色", "无", None, None, False),
        ("相机主动氛围灯", "1000M蓝色，100M白色、故障红色", "无", None, None, False),
        ("相机镜头光源组合方式", "3合一一体化", "3个部件分体式", None, None, False),
        ("相机分辨率", "800万（3840*2140）向下兼容", "200万/500万", "camera-resolution.png", "lens-resolution.png", True),
        ("彩色支持", "有（彩色/黑白）", "黑白", None, None, False),
        ("红外光", "有", "有（外置）", None, None, False),
        ("白光", "有", "无", "camera-white.png", "ring-light.png", True),
        ("彩色黑白切换", "有", "无", None, None, False),
        ("相机自带光源", "有", "无", None, None, False),
        ("镜头放大倍率", "10x(5-50mm)", "7-36MM", None, None, False),
        ("放大倍率调节", "电动调节", "手动调节", None, None, False),
        ("对焦操作", "电动自动对焦", "手动对焦", None, None, False),
        ("对焦方式", "全景自动对焦/fov自动对焦/多点对焦", "无", None, None, False),
        ("AI自动拍照时间功能", "有", "无", None, None, False),
        ("AI自动图像采集功能", "有", "无", None, None, False),
        ("超景深融合技术", "有（专利技术）", "无", None, None, False),
        ("IO盒", "通用", "通用", None, None, False),
        ("供电", "DC24V", "DC24V", None, None, False),
        ("认证", "CE.FCC", "CE.FCC", None, None, False),
    ],
}

EN = {
    "lang": "en",
    "css": "ocr-spec-table lang-en",
    "caption": "Technical Specifications",
    "model": "Model",
    "param": "Parameter",
    "rows": [
        ("Camera Model", "V1 Pro", "Gigabit Ethernet Industrial Camera\nMD-GE500W", "camera-v1pro.png", "camera-gige.png", True),
        ("Display Size", '14" Capacitive Touchscreen', '13.3" Capacitive Touchscreen', None, None, False),
        ("Screen Resolution", "1920*1080", "1920*1080", None, None, False),
        ("Supported Cameras", "4", "4", None, None, False),
        ("Main Unit Ambient Light", "Standby White, Running Blue, Alarm Red", "None", None, None, False),
        ("Camera Ambient Light", "1000M Blue, 100M White, Fault Red", "None", None, None, False),
        ("Camera/Lens/Light Assembly", "3-in-1 Integrated", "3 Separate Components", None, None, False),
        ("Camera Resolution", "8 MP (3840*2140), Backward Compatible", "2 MP / 5 MP", "camera-resolution.png", "lens-resolution.png", True),
        ("Color Support", "Yes (Color / Monochrome)", "Monochrome", None, None, False),
        ("Infrared Light", "Yes", "Yes (External)", None, None, False),
        ("White Light", "Yes", "No", "camera-white.png", "ring-light.png", True),
        ("Color / Monochrome Switching", "Yes", "No", None, None, False),
        ("Built-in Camera Light", "Yes", "No", None, None, False),
        ("Lens Magnification", "10x (5-50mm)", "7-36MM", None, None, False),
        ("Magnification Adjustment", "Motorized", "Manual", None, None, False),
        ("Focus Operation", "Motorized Auto Focus", "Manual Focus", None, None, False),
        ("Focus Modes", "Panoramic AF / FOV AF / Multi-Point AF", "None", None, None, False),
        ("AI Auto Capture Timing", "Yes", "No", None, None, False),
        ("AI Auto Image Acquisition", "Yes", "No", None, None, False),
        ("Extended Depth-of-Field Fusion", "Yes (Patented Technology)", "No", None, None, False),
        ("I/O Box", "Universal", "Universal", None, None, False),
        ("Power Supply", "DC24V", "DC24V", None, None, False),
        ("Certification", "CE.FCC", "CE.FCC", None, None, False),
    ],
}


def esc(text):
    return html.escape(text, quote=False).replace("\n", "<br/>")


def photo(name, cls):
    if not name:
        return ""
    return (
        f'<img class="{cls}" src="{PHOTO_DIR}{name}" alt="" aria-hidden="true"/>'
    )


def build(ctx):
    parts = [
        '<div class="ocr-spec-scroll"><div class="ocr-spec-inner">',
        f'<table class="{ctx["css"]}" lang="{ctx["lang"]}">',
        f'<caption>{esc(ctx["caption"])}</caption>',
        '<colgroup><col class="c-label"/><col class="c-a"/><col class="c-b"/></colgroup>',
        "<thead><tr>",
        f'<th class="ocr-spec-corner" scope="col"><span class="cr-model">{esc(ctx["model"])}</span>'
        f'<span class="cr-param">{esc(ctx["param"])}</span></th>',
        f'<th scope="col"><span class="ocr-spec-model">IMX-790</span>'
        f'{photo("unit-790.png", "ocr-spec-unit-photo")}</th>',
        f'<th scope="col"><span class="ocr-spec-model">IMX-760</span>'
        f'{photo("unit-760.png", "ocr-spec-unit-photo")}</th>',
        "</tr></thead><tbody>",
    ]
    for label, a, b, photo_a, photo_b, tall in ctx["rows"]:
        cls = ' class="tall"' if tall else ""
        parts.append(
            f"<tr{cls}><th scope=\"row\">{esc(label)}</th>"
            f'<td><span class="ocr-spec-cell-text">{esc(a)}</span>{photo(photo_a, "ocr-spec-photo")}</td>'
            f'<td><span class="ocr-spec-cell-text">{esc(b)}</span>{photo(photo_b, "ocr-spec-photo")}</td></tr>'
        )
    parts.append("</tbody></table></div></div>")
    return "".join(parts)


IMAGE_RE = re.compile(
    r'<p><img alt="[^"]*" src="\.\./UserFiles/upload/image/20251030/'
    + re.escape(IMAGE_NAME)
    + r'"[^>]*/?></p>'
)


def main():
    for page in sorted(PAGE_DIR.glob("10032*.html")):
        ctx = EN if page.name != "10032.html" else ZH
        raw = page.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        text, count = IMAGE_RE.subn(lambda m: build(ctx), text, count=1)
        if count != 1:
            raise RuntimeError(f"{page.name}: expected 1 raster table, found {count}")
        if CSS_HREF not in text:
            text = text.replace(
                "</head>", f'<link href="{CSS_HREF}" rel="stylesheet"/></head>', 1
            )
        page.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
        print("rebuilt", page.name, "rows", len(ctx["rows"]))


if __name__ == "__main__":
    main()
