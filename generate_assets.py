"""Utility script to generate PNG/JPEG assets from SVG thumbnails.

Optional dependency: cairosvg
Install with: pip install cairosvg

Usage:
  python generate_assets.py  # creates png/jpg versions in ./assets
"""
from pathlib import Path
import sys

OUTPUT_DIR = Path("assets")
SVG_FILES = [
    Path("thumbnail.svg"),
    Path("thumbnail_dark.svg"),
    Path("thumbnail.min.svg"),
]

TRY_FORMATS = [
    ("png", {"scale": 1.0}),
    ("png", {"scale": 2.0}),  # retina
    ("jpg", {"scale": 1.0}),
]

def have_cairosvg():
    try:
        import cairosvg  # noqa: F401
        return True
    except ImportError:
        return False

def convert(svg_path: Path):
    import cairosvg
    for fmt, opts in TRY_FORMATS:
        out = OUTPUT_DIR / f"{svg_path.stem}@{int(opts.get('scale',1))}x.{fmt}"
        try:
            cairosvg.svg2png(url=str(svg_path), write_to=str(out), scale=opts.get("scale", 1.0)) if fmt == "png" else \
                cairosvg.svg2png(url=str(svg_path), write_to=str(out.with_suffix('.png')), scale=opts.get("scale", 1.0))
            print(f"Generated: {out}")
        except Exception as e:
            print(f"Failed to convert {svg_path} -> {out}: {e}")


def main():
    if not have_cairosvg():
        print("cairosvg not installed. Install with 'pip install cairosvg' to enable asset generation.")
        return 0
    OUTPUT_DIR.mkdir(exist_ok=True)
    for svg in SVG_FILES:
        if svg.exists():
            convert(svg)
        else:
            print(f"Skipping missing {svg}")
    print("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
