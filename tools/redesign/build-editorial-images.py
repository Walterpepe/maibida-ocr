"""Encode the curated full-frame product photography used by the redesign."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "tools" / "redesign" / "source"
OUTPUT_DIR = ROOT / "cn" / "images" / "redesign" / "products"
SIZE = (1600, 1200)

IMAGES = {
    "monitor-hero-extended.png": "monitor-hero-studio.webp",
    "camera-hero-extended.png": "camera-hero-studio.webp",
    "feeder-hero-extended.png": "feeder-hero-studio.webp",
    "sorter-hero-extended.png": "sorter-hero-studio.webp",
    "connector-hero-extended.png": "inline-connector-hero-studio.webp",
    "strip-hero-extended.png": "inline-strip-hero-studio.webp",
    "plastic-hero-extended.png": "inline-plastic-hero-studio.webp",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, output_name in IMAGES.items():
        source = SOURCE_DIR / source_name
        with Image.open(source) as rendered:
            image = rendered.convert("RGB")
        if image.size != SIZE:
            raise ValueError(f"unexpected source size: {source} {image.size}")
        image.save(
            OUTPUT_DIR / output_name,
            "WEBP",
            quality=94,
            method=6,
        )
        print(f"built {output_name}")


if __name__ == "__main__":
    main()
