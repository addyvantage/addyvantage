#!/usr/bin/env python3
"""
Turn a photograph into a self-typing ASCII portrait, as an SVG.

Run this once, locally, and commit the result. It is deliberately not part of
the nightly workflow: the face doesn't change, and the background-removal
model is a ~176 MB download you don't want in CI.

    pip install pillow numpy opencv-python-headless rembg onnxruntime
    python3 scripts/portrait.py me.jpg -o portrait.svg

    # skip the cut-out if your photo already has a clean white background
    python3 scripts/portrait.py me.jpg -o portrait.svg --no-rembg

The photo decides everything. ASCII draws with shadow, not detail — there are
thirteen brightness levels to work with, and no parameter rescues a bad input:

  · side light, roughly 45°, everything else off. Flat frontal light renders
    the face as one mid-tone, which comes out as a hole.
  · crop tight, chin to just above the hair. At 90 columns a face filling 30%
    of the frame gets ~30 characters across and the eyes won't resolve.
  · 1200px or larger. Thin features — glasses frames especially — get averaged
    out of existence when a small image is downscaled.
  · plain background, and don't wear black against a dark wall.
  · slight angle rather than dead-on, so the nose and jaw cast an edge.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from xml.sax.saxutils import escape

import cv2
import numpy as np
from PIL import Image

# Dark → light. The leading space clears the background to nothing.
RAMP = " .`:-=+*cs#%@"

FALLBACK = (
    "'JetBrains Mono','Liberation Mono','DejaVu Sans Mono',"
    "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
)


def cutout(img: Image.Image) -> Image.Image:
    """
    Force everything outside the subject to white.

    Without this the background maps onto the dark end of the ramp and fills
    with '@', which drowns the portrait — the single biggest failure mode.
    """
    try:
        from rembg import remove
    except ImportError:
        print("! rembg not installed — skipping cut-out", file=sys.stderr)
        return img.convert("RGB")

    cut = remove(img.convert("RGBA"))
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    white.paste(cut, mask=cut.split()[3])
    return white.convert("RGB")


def to_ascii(
    img: Image.Image, cols: int, gamma: float, clip: float, for_dark: bool = False
) -> list[str]:
    grey = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    # Remember the background before anything touches the tones. Whitening the
    # background and then running CLAHE over it pulls it straight back to a
    # mid grey, which the ramp renders as a field of characters around the
    # head — so the mask has to be captured here and reapplied at the end.
    background = grey >= 250

    # Smooth skin without softening the edges that carry the likeness.
    grey = cv2.bilateralFilter(grey, 9, 75, 75)

    # Local contrast per tile. A global stretch leaves an evenly-lit face as
    # a single tone no matter how hard it is pushed. Clip is the dial that
    # matters most for a studio photo: high values on an already well-exposed
    # face drive the skin to the dark end of the ramp and fill it in solid.
    grey = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(grey)

    # The darkening curve. With a linear map the face comes out washed out and
    # featureless; this is what keeps brows, lips and glasses alive.
    grey = np.power(grey / 255.0, gamma) * 255.0

    grey[background] = 255.0

    h, w = grey.shape
    # Monospace cells are about twice as tall as they are wide.
    rows = max(1, int(cols * (h / w) * 0.48))
    small = cv2.resize(grey, (cols, rows), interpolation=cv2.INTER_AREA)
    bg_cells = cv2.resize(
        background.astype(np.float32), (cols, rows), interpolation=cv2.INTER_AREA
    ) > 0.5

    idx = (small / 255.0 * (len(RAMP) - 1)).round().astype(int)
    if not for_dark:
        # Light page: a dense glyph puts more black on white, so dark pixels
        # take the dense end. This is the orientation every ASCII-art tutorial
        # assumes, because it assumes paper.
        idx = len(RAMP) - 1 - idx

    # A dense glyph on a dark page emits more *light*, so the same text is a
    # photographic negative there — hair glowing white, skin in shadow. The
    # orientation has to flip, and since density is baked into the characters
    # themselves no amount of CSS can flip it later. Hence two files and a
    # <picture> element.
    idx = np.clip(idx, 0, len(RAMP) - 1)

    art = ["".join(RAMP[i] for i in row) for row in idx]

    # Blank the background explicitly. In the dark orientation white maps to
    # the *dense* end, so relying on "white becomes a space" would fill the
    # entire frame with '@'.
    return [
        "".join(" " if bg_cells[r][c] else ch for c, ch in enumerate(row))
        for r, row in enumerate(art)
    ]


def inline_font(path: str | None) -> str:
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return (
        "@font-face{font-family:'PortraitMono';font-weight:400;font-display:block;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
    )


def build_svg(
    art: list[str],
    char_w: float,
    line_h: float,
    size: float,
    stagger: float,
    dur: float,
    font: str | None,
) -> str:
    cols = max(len(r) for r in art)
    w = cols * char_w
    h = len(art) * line_h + size * 0.4

    fam = f"'PortraitMono',{FALLBACK}" if font else FALLBACK
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}" height="{h:.1f}" '
        f'viewBox="0 0 {w:.1f} {h:.1f}" role="img" '
        'aria-label="ASCII portrait, typing itself out">',
        "<title>ASCII portrait</title>",
        "<style>"
        + inline_font(font)
        + ".g{fill:#1F2328;}.cur{fill:#9A6700;}"
        "@media (prefers-color-scheme: dark){.g{fill:#E6EDF3;}.cur{fill:#D29922;}}"
        "</style>",
        "<defs>",
    ]

    # One wipe per row. Scripts are stripped from anything GitHub renders, so
    # the motion has to be SMIL living inside the file — which GitHub does run.
    for i in range(len(art)):
        begin = f"{i * stagger:.2f}s"
        parts.append(
            f'<clipPath id="c{i}"><rect x="0" y="{i * line_h:.1f}" '
            f'width="0" height="{line_h + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{w:.1f}" '
            f'begin="{begin}" dur="{dur}s" fill="freeze"/>'
            "</rect></clipPath>"
        )
    parts.append("</defs>")

    for i, row in enumerate(art):
        y = (i + 1) * line_h
        begin = f"{i * stagger:.2f}s"
        # Every glyph gets an explicit x. The usual approach leans on the
        # font's 0.600em advance, but a visitor who falls back to Consolas
        # (~0.55em) sees the whole portrait ~7% narrow and sheared. An x-list
        # is immune to whatever font actually loads.
        # Trim trailing zeros: at 130 columns × 78 rows this list *is* the
        # file, and a whole-number advance width keeps it to three or four
        # characters per position instead of seven.
        xs = " ".join(f"{c * char_w:g}" for c in range(len(row)))
        parts.append(
            f'<g clip-path="url(#c{i})">'
            f'<text x="{xs}" y="{y:.1f}" class="g" font-family="{fam}" '
            f'font-size="{size}" xml:space="preserve">{escape(row)}</text></g>'
        )
        # A block riding the wipe edge, which vanishes when the row lands.
        parts.append(
            f'<rect class="cur" x="0" y="{y - size * 0.8:.1f}" '
            f'width="{char_w * 0.9:.2f}" height="{size * 0.9:.1f}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin}"/>'
            f'<animate attributeName="x" from="0" to="{w:.1f}" '
            f'begin="{begin}" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{i * stagger + dur:.2f}s"/>'
            "</rect>"
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("-o", "--out", default="portrait.svg")
    ap.add_argument("--cols", type=int, default=90,
                    help="below ~88 the face muddies; far above it the block eats the page")
    ap.add_argument("--gamma", type=float, default=1.7, help="darkening curve; raise for more shadow")
    ap.add_argument("--clip", type=float, default=3.0,
                    help="CLAHE clip limit; drop to ~1.2 for evenly-lit studio photos")
    ap.add_argument("--size", type=float, default=12.9, help="font size")
    ap.add_argument("--char-w", type=float, default=None, help="advance width (default 0.600em)")
    ap.add_argument("--line-h", type=float, default=None, help="line height (default 0.86em)")
    ap.add_argument("--stagger", type=float, default=0.09, help="delay between rows")
    ap.add_argument("--dur", type=float, default=0.6, help="wipe duration per row")
    ap.add_argument("--font", default="assets/fonts/ramp.woff2", help="woff2 subset to inline")
    ap.add_argument("--no-rembg", action="store_true")
    ap.add_argument("--dark", action="store_true",
                    help="orientation for dark backgrounds; generate both and swap with <picture>")
    ap.add_argument("--txt", help="also write the raw text, useful for tuning")
    args = ap.parse_args()

    char_w = args.char_w if args.char_w else args.size * 0.600
    line_h = args.line_h if args.line_h else args.size * 0.86

    img = Image.open(args.image)
    if img.width < 800:
        print(f"! {args.image} is {img.width}px wide — thin features will not survive", file=sys.stderr)
    if not args.no_rembg:
        img = cutout(img)
    else:
        img = img.convert("RGB")

    art = to_ascii(img, args.cols, args.gamma, args.clip, for_dark=args.dark)

    ink = sum(1 for row in art for ch in row if ch != " ") / (len(art) * args.cols)
    print(f"· {args.cols}×{len(art)} characters, {ink:.0%} ink")
    if ink > 0.80:
        print(
            f"! {ink:.0%} ink — the background is almost certainly still there. "
            "Run without --no-rembg, or white out the background first.",
            file=sys.stderr,
        )
    elif ink < 0.25:
        print("! very sparse — try raising --gamma or cropping tighter", file=sys.stderr)

    if args.txt:
        with open(args.txt, "w", encoding="utf-8") as fh:
            fh.write("\n".join(art) + "\n")
        print(f"  → {args.txt}")

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(build_svg(art, char_w, line_h, args.size, args.stagger, args.dur,
                           args.font if os.path.exists(args.font) else None))
    total = (len(art) - 1) * args.stagger + args.dur
    print(f"  → {args.out} (types for {total:.1f}s, then freezes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
