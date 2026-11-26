"""Create consistent studio treatments without removing product components."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "cn" / "images" / "redesign" / "products"
CAMERA_SOURCE = ROOT / "tools" / "redesign" / "source" / "camera-hero-extended.png"
SIZE = (1600, 1200)


def grade_image(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(1.035)
    image = ImageEnhance.Color(image).enhance(0.96)
    return ImageEnhance.Brightness(image).enhance(1.018)


def extended_backdrop(image: Image.Image, tone: str) -> Image.Image:
    """Extend the source atmosphere into a quiet, full-bleed stage."""
    backdrop = ImageOps.fit(
        image,
        SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    backdrop = backdrop.filter(ImageFilter.GaussianBlur(64))
    if tone == "dark":
        tint = Image.new("RGB", SIZE, (17, 18, 20))
        backdrop = Image.blend(backdrop, tint, 0.62)
    else:
        tint = Image.new("RGB", SIZE, (246, 246, 248))
        backdrop = Image.blend(backdrop, tint, 0.76)
    return backdrop.convert("RGBA")


def extend_product_photo(
    source: Path,
    output: str,
    *,
    tone: str,
    max_box: tuple[int, int],
    crop: tuple[int, int, int, int] | None = None,
    radius: int = 24,
    feather: int = 20,
) -> None:
    """Keep the full product frame intact and extend the canvas around it."""
    source_image = Image.open(source).convert("RGB")
    if crop:
        source_image = source_image.crop(crop)

    framed = ImageOps.contain(
        grade_image(source_image),
        max_box,
        Image.Resampling.LANCZOS,
    ).convert("RGBA")
    canvas = extended_backdrop(source_image, tone)

    # The mask only feathers the outer photo edge. Nothing inside the source
    # frame is segmented, keyed out, recolored, or treated as disposable.
    mask = Image.new("L", framed.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, framed.width - 1, framed.height - 1),
        radius=radius,
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    x = (SIZE[0] - framed.width) // 2
    y = (SIZE[1] - framed.height) // 2
    canvas.paste(framed, (x, y), mask)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUTPUT / output, "WEBP", quality=92, method=6)
    print(f"built {output}")


def build_camera_scene(output: str) -> None:
    """Encode the curated full-frame outpaint of both camera bodies."""
    image = Image.open(CAMERA_SOURCE).convert("RGB")
    if image.size != SIZE:
        raise ValueError(f"unexpected camera source size: {image.size}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / output, "WEBP", quality=94, method=6)
    print(f"built {output}")


def main() -> None:
    extend_product_photo(
        ROOT / "cn/images/redesign/product-monitor.webp",
        "monitor-hero-studio.webp",
        tone="light",
        max_box=(1320, 1080),
    )
    build_camera_scene("camera-hero-studio.webp")
    extend_product_photo(
        ROOT / "UserFiles/upload/image/feedplate/hero-robot.webp",
        "feeder-hero-studio.webp",
        tone="dark",
        max_box=(1120, 1140),
    )
    extend_product_photo(
        ROOT / "cn/images/redesign/product-sorter.webp",
        "sorter-hero-studio.webp",
        tone="light",
        max_box=(1400, 940),
        crop=(0, 0, 685, 452),
    )
    extend_product_photo(
        ROOT / "UserFiles/upload/image/20251212/6390113110640403958074666.webp",
        "inline-connector-hero-studio.webp",
        tone="light",
        max_box=(1080, 1140),
    )
    extend_product_photo(
        ROOT / "UserFiles/upload/image/20251212/6390112902333584171953095.webp",
        "inline-strip-hero-studio.webp",
        tone="light",
        max_box=(1400, 1000),
    )
    extend_product_photo(
        ROOT / "UserFiles/upload/image/20251230/6390268539790000497674567.webp",
        "inline-plastic-hero-studio.webp",
        tone="dark",
        max_box=(1600, 1120),
    )


if __name__ == "__main__":
    main()
