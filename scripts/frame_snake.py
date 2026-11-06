#!/usr/bin/env python3
"""Give the generated contribution snake the same navy card frame as the other
profile cards.

The snake action emits a transparent SVG. This script adds padding, a navy
panel and a 1px border so it matches the rest of the profile in light and dark
mode. It is idempotent: a file that is already framed is left untouched.

    python scripts/frame_snake.py dist/snake.svg assets/generated/snake.svg
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PANEL, BORDER, PAD = "#0F1830", "#1E2A44", 20


def frame(svg: str) -> str:
    if 'data-framed="1"' in svg:
        return svg
    m = re.search(r"<svg\b[^>]*>", svg)
    vb = re.search(r'viewBox="\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)\s*"', m.group(0)) if m else None
    if not m or not vb:
        raise ValueError("input does not look like an SVG with a viewBox")
    x, y, w, h = (float(v) for v in vb.groups())
    nx, ny, nw, nh = x - PAD, y - PAD, w + 2 * PAD, h + 2 * PAD

    tag = m.group(0)
    tag = re.sub(r'viewBox="[^"]*"', f'viewBox="{nx:g} {ny:g} {nw:g} {nh:g}"', tag)
    tag = re.sub(r'\swidth="[^"]*"', "", tag)
    tag = re.sub(r'\sheight="[^"]*"', "", tag)
    tag = tag[:-1] + f' width="{nw:g}" height="{nh:g}" data-framed="1">'

    panel = (
        f'<rect x="{nx:g}" y="{ny:g}" width="{nw:g}" height="{nh:g}" rx="14" fill="{PANEL}"/>'
        f'<rect x="{nx + 0.5:g}" y="{ny + 0.5:g}" width="{nw - 1:g}" height="{nh - 1:g}" rx="13.5" '
        f'fill="none" stroke="{BORDER}"/>'
    )
    return svg[: m.start()] + tag + panel + svg[m.end():]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        out = frame(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Snake framing failed, keeping existing asset: {exc}", file=sys.stderr)
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"Wrote framed snake to {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
