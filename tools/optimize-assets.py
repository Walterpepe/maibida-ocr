"""Optimize large static assets without touching any HTML or CSS.

For every raster image above 300 KB (outside backup/tool directories):
  * create a WebP sibling served by Accept negotiation in preview-server.js /
    Nginx (original JPEG/PNG stays as the fallback);
  * re-save the original with lossless-ish settings (PNG optimize / JPEG q85
    progressive) so the fallback itself gets smaller too.

For every MP4 above 1 MB: re-encode to H.264/AAC with a moderate CRF and
+faststart, keeping resolution, duration and the file name unchanged.

All originals are copied to a timestamped directory OUTSIDE the web root
before anything is overwritten, so the operation is fully reversible.
"""
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
ORIG = ROOT.parent / f"maibida-ocr-rebuilt_asset_originals_{TS}"
MANIFEST = ROOT / "tools/asset-optimization.json"
SKIP = {"productInfo_bak_seo", "UserFiles_bak_bigimg", "_bak_footnav",
        "_bak_foot_full", "_bak_pathfix", "_bak_wxqrcode", "tools"}
IMG_MIN = 300 * 1024
VIDEO_MIN = 1024 * 1024


def keep_original(f):
    dst = ORIG / f.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dst)
    return str(dst)


def optimize_image(f):
    before = f.stat().st_size
    keep_original(f)
    src = Image.open(f)
    fmt = (src.format or "").upper()
    dims = list(src.size)
    has_alpha = src.mode in ("RGBA", "LA") or "transparency" in src.info
    src.load()
    im = src.copy()
    src.close()  # release the file handle before we overwrite it on Windows
    # Append rather than replace the extension: "photo.jpg.webp".
    # This makes Nginx `try_files $uri.webp $uri =404` work unchanged.
    webp = f.with_name(f.name + ".webp")
    webp_size = 0

    # WebP sibling (alpha preserved).
    try:
        wim = im.convert("RGBA" if has_alpha else "RGB")
        wim.save(webp, "WEBP", quality=82, method=6)
        webp_size = webp.stat().st_size
    except Exception:
        if webp.exists():
            webp.unlink()

    # Re-encode the fallback in place.
    tmp = f.with_name(f.name + ".tmpopt")
    try:
        if fmt == "JPEG":
            im.convert("RGB").save(tmp, "JPEG", quality=85, optimize=True, progressive=True)
        elif fmt == "PNG":
            out = im
            if out.mode == "RGBA":
                alpha = out.getchannel("A")
                if alpha.getextrema() == (255, 255):
                    out = out.convert("RGB")
            out.save(tmp, "PNG", optimize=True)
        else:
            tmp = None
        if tmp and tmp.exists():
            after_tmp = tmp.stat().st_size
            if after_tmp < before:
                shutil.move(str(tmp), str(f))
                after = f.stat().st_size
            else:
                tmp.unlink()
                after = before
        else:
            after = before
    finally:
        if tmp and tmp.exists():
            tmp.unlink()

    return {"file": f.relative_to(ROOT).as_posix(), "format": fmt,
            "dimensions": dims, "before": before, "after": after,
            "webp": webp.stat().st_size if webp.exists() else 0}


def optimize_video(f):
    before = f.stat().st_size
    keep_original(f)
    tmp = f.with_name(f.stem + ".opt.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(f),
           "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
           "-movflags", "+faststart", str(tmp)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not tmp.exists():
            if tmp.exists():
                tmp.unlink()
            return {"file": f.relative_to(ROOT).as_posix(), "format": "MP4",
                    "before": before, "after": before, "error": (r.stderr or "ffmpeg failed")[:120]}
        after = tmp.stat().st_size
        if after < before:
            shutil.move(str(tmp), str(f))
            return {"file": f.relative_to(ROOT).as_posix(), "format": "MP4",
                    "before": before, "after": f.stat().st_size}
        tmp.unlink()
        return {"file": f.relative_to(ROOT).as_posix(), "format": "MP4",
                "before": before, "after": before, "note": "re-encode not smaller, original kept"}
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        return {"file": f.relative_to(ROOT).as_posix(), "format": "MP4",
                "before": before, "after": before, "error": str(e)[:120]}


def main():
    images, videos = [], []
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file() or set(f.parts) & SKIP:
            continue
        ext = f.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg") and f.stat().st_size >= IMG_MIN:
            images.append(optimize_image(f))
        elif ext == ".mp4" and f.stat().st_size >= VIDEO_MIN:
            videos.append(optimize_video(f))

    rows = images + videos
    total_before = sum(r["before"] for r in rows)
    total_after = sum(r["after"] for r in rows)
    webp_total = sum(r.get("webp", 0) for r in images)
    manifest = {
        "timestamp": TS,
        "originals_backup": str(ORIG) if rows else None,
        "images_optimized": len(images),
        "webp_siblings": sum(1 for r in images if r.get("webp", 0) > 0),
        "webp_total_bytes": webp_total,
        "videos_optimized": len(videos),
        "fallback_bytes_before": total_before,
        "fallback_bytes_after": total_after,
        "fallback_saved_bytes": total_before - total_after,
        "fallback_saved_pct": round(100 * (total_before - total_after) / total_before, 1) if total_before else 0,
        "details": rows,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "details"},
                     ensure_ascii=False, indent=2))
    for r in rows:
        print(f'  {r["format"]:5s} {r["before"]/1024:8.0f}K -> {r["after"]/1024:8.0f}K '
              f'webp={r.get("webp",0)/1024:7.0f}K  {r["file"][:78]}')


if __name__ == "__main__":
    main()
