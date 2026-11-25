"""Compose product-page hero imagery from Maibida's existing photography."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "cn" / "images" / "redesign" / "products"
SIZE = (1600, 1200)


def vertical_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", SIZE, top)
    draw = ImageDraw.Draw(image)
    for y in range(SIZE[1]):
        ratio = y / (SIZE[1] - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, SIZE[0], y), fill=color)
    return image


def add_soft_shadow(canvas: Image.Image, box: tuple[int, int, int, int]) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(box, fill=(0, 0, 0, 80))
    overlay = overlay.filter(ImageFilter.GaussianBlur(46))
    canvas.alpha_composite(overlay)


def compose(
    source: Path,
    output: str,
    *,
    theme: str,
    crop: tuple[int, int, int, int] | None = None,
    max_box: tuple[int, int] = (1360, 1040),
) -> None:
    image = Image.open(source).convert("RGB")
    if crop:
        image = image.crop(crop)
    if theme == "dark":
        canvas = vertical_gradient((17, 18, 21), (7, 8, 9)).convert("RGBA")
    else:
        canvas = vertical_gradient((252, 252, 253), (235, 237, 240)).convert("RGBA")

    fitted = ImageOps.contain(image, max_box, Image.Resampling.LANCZOS)
    x = (SIZE[0] - fitted.width) // 2
    y = (SIZE[1] - fitted.height) // 2 - 20

    shadow_width = int(fitted.width * 0.68)
    shadow_height = max(42, int(fitted.height * 0.075))
    shadow_x = (SIZE[0] - shadow_width) // 2
    shadow_y = min(SIZE[1] - shadow_height - 54, y + fitted.height - shadow_height // 2)
    add_soft_shadow(canvas, (shadow_x, shadow_y, shadow_x + shadow_width, shadow_y + shadow_height))

    mask = Image.new("L", fitted.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    canvas.paste(fitted.convert("RGBA"), (x, y), mask)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(
        OUTPUT / output,
        "WEBP",
        quality=88,
        method=6,
    )
    print(f"built {output}")


def main() -> None:
    compose(
        ROOT / "cn/images/redesign/product-monitor.webp",
        "monitor-hero.webp",
        theme="light",
        max_box=(1320, 1060),
    )
    compose(
        ROOT / "UserFiles/upload/image/v3pro-site/camera-hero.webp",
        "camera-hero.webp",
        theme="dark",
        max_box=(1320, 1080),
    )
    compose(
        ROOT / "UserFiles/upload/image/feedplate/sif-robot.webp",
        "feeder-hero.webp",
        theme="dark",
        max_box=(950, 1110),
    )
    compose(
        ROOT / "cn/images/redesign/product-sorter.webp",
        "sorter-hero.webp",
        theme="light",
        crop=(0, 0, 685, 445),
        max_box=(1400, 930),
    )
    compose(
        ROOT / "UserFiles/upload/image/20251212/6390113110640403958074666.webp",
        "inline-connector-hero.webp",
        theme="light",
        crop=(250, 55, 1280, 1235),
        max_box=(1030, 1080),
    )
    compose(
        ROOT / "UserFiles/upload/image/20251212/6390112902333584171953095.webp",
        "inline-strip-hero.webp",
        theme="light",
        max_box=(1430, 1060),
    )
    compose(
        ROOT / "UserFiles/upload/image/20251230/6390268539790000497674567.webp",
        "inline-plastic-hero.webp",
        theme="dark",
        crop=(310, 0, 1600, 900),
        max_box=(1510, 920),
    )


if __name__ == "__main__":
    main()
