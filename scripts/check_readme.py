#!/usr/bin/env python3
"""Basic README quality gate, run by the readme-quality workflow.

Checks:
  1. Every relative link and image in README.md points to a file that exists.
  2. No emoji or decorative pictographs in README.md or any SVG asset.
  3. Every image has non-empty alt text.

External links are checked separately (lychee) because they depend on the
network and should not block an edit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

# Emoji and pictograph ranges (symbols, dingbats, emoticons, transport, flags,
# supplemental symbols) plus the emoji variation selector and zero-width joiner.
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF←-⇿⌀-⏿①-⓿"
    "■-◿☀-➿⤀-⥿⬀-⯿️‍]"
)
MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)")
HTML_ATTR = re.compile(r"""(?:src|href)=["']([^"']+)["']""")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ALT = re.compile(r"""\balt=["']([^"']*)["']""")


def main() -> int:
    errors: list[str] = []
    text = README.read_text(encoding="utf-8")

    targets = set(MD_LINK.findall(text)) | set(HTML_ATTR.findall(text))
    for t in sorted(targets):
        if re.match(r"^(https?:|mailto:|#)", t):
            continue
        path = ROOT / t.split("#")[0].split("?")[0]
        if not path.exists():
            errors.append(f"broken relative link: {t}")

    for tag in IMG_TAG.findall(text):
        m = ALT.search(tag)
        if not m or not m.group(1).strip():
            errors.append(f"image without alt text: {tag[:80]}")

    for f in [README, *sorted((ROOT / "assets").rglob("*.svg"))]:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if EMOJI.search(line):
                errors.append(f"emoji or pictograph in {f.relative_to(ROOT)}:{n}")

    if errors:
        print("README check failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"README check passed ({len(targets)} link targets verified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
