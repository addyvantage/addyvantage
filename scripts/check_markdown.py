#!/usr/bin/env python3
"""
Check the README against GitHub's own renderer before committing.

POST /markdown applies the same sanitiser as the site, so this tells you what
actually survives rather than what you hoped would. It also flags any
external host the page would hit at render time — the whole point of drawing
the graphics locally is that this list stays empty.

    GITHUB_TOKEN=... python3 scripts/check_markdown.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

README = os.environ.get("README_PATH", "README.md")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Things GitHub removes from markdown. If one shows up in your source, the
# effect you were counting on isn't there on the rendered page.
STRIPPED = ["<style", "style=", "class=", "<font", "<small", "<big", "<script"]


def render(md: str) -> str:
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": md, "mode": "markdown"}).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "readme-preflight",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode()


def main() -> int:
    with open(README, encoding="utf-8") as fh:
        source = fh.read()

    problems = 0

    refs = re.findall(r'src(?:set)?="([^"]+)"', source)   # <img src> and <source srcset>
    external = sorted({r for r in refs if r.startswith("http")})
    if external:
        problems += 1
        print("! external image hosts — each one can rate-limit or 503:")
        for url in external:
            print(f"    {url}")
    else:
        print("· no external image hosts")

    for token in STRIPPED:
        if token in source:
            problems += 1
            print(f"! source contains {token!r}, which GitHub strips")

    missing = [r for r in refs if not r.startswith("http") and not os.path.exists(r)]
    if missing:
        problems += 1
        print("! referenced files that don't exist yet:")
        for src in missing:
            print(f"    {src}")
    else:
        print("· every local asset referenced by the README exists")

    try:
        html = render(source)
    except Exception as exc:  # noqa: BLE001 - preflight shouldn't hard-fail
        print(f"? couldn't reach the rendering API ({exc}); skipped that check")
        return 1 if problems else 0

    imgs = len(re.findall(r"<img", html))
    print(f"· GitHub rendered {imgs} images, {len(html)} bytes of HTML")
    for token in ("<style", "class=\"custom", "<font"):
        if token in source and token not in html:
            print(f"  confirmed stripped by the renderer: {token}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
