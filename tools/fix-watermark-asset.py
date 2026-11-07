"""H5: remove the third-party AI watermark from the LED illustration.

The watermark sits in the plain-white bottom-right corner. We repaint only
that corner with the sampled background colour, keep the same file path (so
all 11 localized pages, alt/transcript wiring and the 100/100 scoring scope
stay intact), and update the localized alt / caption / sr-only transcript so
the page no longer describes a watermark and explicitly marks the image as a
schematic illustration rather than a product photograph.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

import compliance_i18n as C

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OFFLINE = ROOT.parent / f"maibida-ocr-rebuilt_watermark_original_{TS}"
ASSET_REL = "UserFiles/upload/image/20251230/6390268955757181277238280.jpg"
ASSET = ROOT / ASSET_REL
BASE = "productlist/10036"

ALT = {
    "zh-CN": "LED 光源板示意图",
    "en-US": "Schematic illustration of an LED light board",
    "en-SG": "Schematic illustration of an LED light board",
    "es-MX": "Ilustración esquemática de una placa de LED",
    "id-ID": "Ilustrasi skematis papan lampu LED",
    "th-TH": "ภาพประกอบแผงไฟ LED แบบแผนภาพ",
    "vi-VN": "Hình minh họa sơ đồ bảng đèn LED",
    "ko-KR": "LED 광원 보드 개략도",
    "ja-JP": "LED 光源基板の模式図",
    "ms-MY": "Ilustrasi skematik papan lampu LED",
    "ru-RU": "Схематичная иллюстрация платы LED-подсветки",
}
CAPTION_SUFFIX = {
    "zh-CN": "（示意图）", "en-US": " (schematic)", "en-SG": " (schematic)",
    "es-MX": " (esquema)", "id-ID": " (skema)", "th-TH": " (ภาพแผนภาพ)",
    "vi-VN": " (sơ đồ)", "ko-KR": " (개략도)", "ja-JP": "（模式図）",
    "ms-MY": " (skematik)", "ru-RU": " (схема)",
}
TRANSCRIPT = {
    "zh-CN": "图内文字说明：LED 光源板示意图，非实际产品照片",
    "en-US": "Image note: schematic illustration of an LED light board, not an actual product photo",
    "en-SG": "Image note: schematic illustration of an LED light board, not an actual product photo",
    "es-MX": "Nota de imagen: ilustración esquemática de una placa de LED, no una foto real del producto",
    "id-ID": "Catatan gambar: ilustrasi skematis papan lampu LED, bukan foto produk sebenarnya",
    "th-TH": "หมายเหตุภาพ: ภาพประกอบแบบแผนภาพของแผงไฟ LED ไม่ใช่ภาพถ่ายผลิตภัณฑ์จริง",
    "vi-VN": "Ghi chú hình ảnh: hình minh họa sơ đồ bảng đèn LED, không phải ảnh sản phẩm thực tế",
    "ko-KR": "이미지 참고: LED 광원 보드 개략도이며 실제 제품 사진이 아닙니다",
    "ja-JP": "画像注記：LED 光源基板の模式図であり、実際の製品写真ではありません",
    "ms-MY": "Nota imej: ilustrasi skematik papan lampu LED, bukan foto produk sebenar",
    "ru-RU": "Примечание к изображению: схематичная иллюстрация платы LED-подсветки, не фотография изделия",
}


def rel(lang):
    return f"{BASE}.html" if lang == "zh-CN" else f"{BASE}.{lang}.html"


def clean_watermark():
    """Repaint the plain-white bottom-right corner; return before/after sizes."""
    OFFLINE.mkdir(parents=True, exist_ok=True)
    dst = OFFLINE / ASSET_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSET, dst)
    before = ASSET.stat().st_size
    im = Image.open(ASSET).convert("RGB")
    w, h = im.size
    # The product artwork ends well above 94% of the height; the watermark
    # occupies only the last few percent of the bottom-right corner.
    box = (int(w * 0.74), int(h * 0.945), w, h)
    bg = im.getpixel((8, 8))
    ImageDraw.Draw(im).rectangle(box, fill=bg)
    im.save(ASSET, "JPEG", quality=92, subsampling=0, optimize=True)
    # Regenerate the negotiated WebP sibling, if present.
    webp = Path(str(ASSET) + ".webp")
    if webp.exists():
        shutil.copy2(webp, OFFLINE / (ASSET_REL + ".webp"))
        im.save(webp, "WEBP", quality=82, method=6)
    return {"original_bytes": before, "cleaned_bytes": ASSET.stat().st_size,
            "dimensions": [w, h], "repainted_box": list(box),
            "original_backup": str(dst)}


def update_pages():
    """Replace alt, caption and sr-only transcript for the 11 locales."""
    import html
    import re
    changed = []
    for lang in C.LANGS:
        f = ROOT / rel(lang)
        t = f.read_bytes().decode("utf-8")
        i = t.find("6390268955757181277238280.jpg")
        if i < 0:
            continue
        a = t.rfind('<div class="swiper-slide">', 0, i)
        # The slide ends after its caption paragraph and the closing </a></div>.
        b = t.find("</a>", i)
        b = t.find("</div>", b) + len("</div>")
        if a < 0 or b <= 0:
            continue
        seg = t[a:b]
        seg2 = re.sub(r'alt="led"', 'alt="' + html.escape(ALT[lang], quote=True) + '"', seg)
        seg2 = re.sub(r'(<p>)led(</p>)',
                      lambda m: m.group(1) + "LED" + CAPTION_SUFFIX[lang] + m.group(2),
                      seg2)
        seg2 = re.sub(r'(<span class="ocr-transcript"[^>]*>).*?(</span>)',
                      lambda m: m.group(1) + html.escape(TRANSCRIPT[lang]) + m.group(2),
                      seg2, flags=re.S)
        t = t[:a] + seg2 + t[b:]
        f.write_bytes(t.encode("utf-8"))
        changed.append(rel(lang))
    return changed


def update_transcript_data():
    f = TOOLS / "image-text-transcripts.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d["texts"]["T8"] = TRANSCRIPT
    d["purpose"] = (d.get("purpose", "") +
                    " T8 was rewritten after the third-party AI watermark was "
                    "removed from the source image; the span now states that the "
                    "image is a schematic illustration, not a product photo.")
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return "T8 updated"


def main():
    if not ASSET.exists():
        raise SystemExit("watermark asset missing")
    imgs = clean_watermark()
    pages = update_pages()
    data = update_transcript_data()
    out = {"timestamp": TS, "asset": ASSET_REL, **imgs,
           "pages_updated": pages, "page_count": len(pages),
           "transcript_data": data, "scoring_scope_unchanged": True}
    (TOOLS / "watermark-fix.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "pages_updated"},
                     ensure_ascii=False, indent=2))
    if len(pages) != len(C.LANGS):
        raise SystemExit(f"FAILED: only {len(pages)}/{len(C.LANGS)} pages updated")


if __name__ == "__main__":
    main()
