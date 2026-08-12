#!/usr/bin/env python3
"""
Draw section headings as SVG, because it is the only way to put your own
typeface on a heading — GitHub strips <style>, style="", class="", <font>
and inline <svg> from markdown, so a heading's font is otherwise whatever
GitHub decided.

    python3 scripts/generate_headings.py

Run once, commit the output. The headings don't change nightly.

The honest cost: an image heading has no anchor link, so GitHub's README
outline (the table-of-contents button) comes up empty. The alt text carries
the word for screen readers, but the outline is genuinely gone. If you'd
rather keep it, use real `##` headings and delete this script.
"""

from __future__ import annotations

import base64
import os
from xml.sax.saxutils import escape

OUT_DIR = os.environ.get("OUT_DIR", "assets/headings")
FONT = os.environ.get("HEADING_FONT", "assets/fonts/headings.woff2")

WIDTH, HEIGHT = 860, 34
SIZE = 13
PAD = 6
RULE_X = 150   # fits the longest label in SECTIONS with room to spare

SECTIONS = [
    "whoami",
    "building",
    "signals",
    "the year",
    "now",
    "languages",
    "elsewhere",
]

FALLBACK = (
    "'JetBrains Mono','Liberation Mono','DejaVu Sans Mono',"
    "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
)


def font_face() -> str:
    if not os.path.exists(FONT):
        return ""
    with open(FONT, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return (
        "@font-face{font-family:'HeadingMono';font-weight:500;font-display:block;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
    )


def slug(name: str) -> str:
    return name.replace(" ", "-")


def draw(name: str) -> str:
    fam = f"'HeadingMono',{FALLBACK}" if os.path.exists(FONT) else FALLBACK
    label = name.lower()
    # Every rule starts at the same x rather than after the word. That reads
    # as a deliberate hanging indent across the page, and — the reason it's
    # done this way — it removes the need to measure the label at all. A
    # length-derived x would collide with the last letter the moment the
    # visitor's font is wider than the one assumed here.
    rule_x = RULE_X
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(name)}">'
        f"<title>{escape(name)}</title>"
        "<style>"
        + font_face()
        + ".t{fill:#59636E;}.r{stroke:#D1D9E0;}"
        "@media (prefers-color-scheme: dark){.t{fill:#8B949E;}.r{stroke:#30363D;}}"
        "</style>"
        f'<text x="{PAD}" y="22" class="t" font-family="{fam}" font-size="{SIZE}" '
        f'font-weight="500" letter-spacing="2.2">{escape(label.upper())}</text>'
        f'<line x1="{rule_x:.0f}" y1="17.5" x2="{WIDTH - PAD}" y2="17.5" '
        f'class="r" stroke-width="1"/>'
        "</svg>\n"
    )


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in SECTIONS:
        path = os.path.join(OUT_DIR, f"hd-{slug(name)}.svg")
        body = draw(name)
        if os.path.exists(path) and open(path, encoding="utf-8").read() == body:
            print(f"  = {path}")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        print(f"  → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
