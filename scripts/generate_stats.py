#!/usr/bin/env python3
"""
Draw the profile's data graphics as SVG files inside this repository.

Outputs (all committed to the repo, all served from it — zero third-party
requests from the rendered README):

    stats.svg    hero total + weekly contribution columns
    streak.svg   current / longest streak with date ranges
    langs.svg    top languages by bytes and by repo
    year.svg     the last 365 days, one character per day

Standard library only, so there is nothing to install in CI and nothing that
can break when a transitive dependency publishes a bad release.

Env:
    GITHUB_TOKEN   required; the workflow's built-in token is sufficient
    GH_LOGIN       GitHub login to profile (default: repository owner)
    OUT_DIR        where to write the SVGs (default: repo root)
    FONT_DIR       optional woff2 subsets to inline (default: assets/fonts)
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

LOGIN = os.environ.get("GH_LOGIN", "addyvantage")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_DIR = os.environ.get("OUT_DIR", ".")
FONT_DIR = os.environ.get("FONT_DIR", "assets/fonts")

GRAPHQL = "https://api.github.com/graphql"

# --------------------------------------------------------------------------- #
# Design tokens
#
# One accent, everything else monochrome. Language bars use opacity steps of
# the accent rather than the API's per-language colours — six saturated hues
# in one graphic is what makes most stat cards look like a toolbar.
# --------------------------------------------------------------------------- #
WIDTH = 860
PAD = 6                      # glyph side-bearings overhang x=0; without this the
W = WIDTH - 2 * PAD          # first character of every left-aligned line clips
CARD = os.environ.get("THEME", "auto").lower() == "card"
ACCENT_DARK = "#D29922"
ACCENT_LIGHT = "#9A6700"
INK_DARK, INK_LIGHT = "#E6EDF3", "#1F2328"
MUTED_DARK, MUTED_LIGHT = "#8B949E", "#59636E"
RULE_DARK, RULE_LIGHT = "#30363D", "#D1D9E0"

# The ramp is shared with the portrait so the year grid and the face read as
# one drawing. Leading space = a blank day.
RAMP = " .:-=+*#%@"

MONO_FALLBACK = (
    "'JetBrains Mono','Liberation Mono','DejaVu Sans Mono',"
    "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
)


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    name
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    repositories(
      first: 100
      privacy: PUBLIC
      isFork: false
      ownerAffiliations: OWNER
      orderBy: { field: PUSHED_AT, direction: DESC }
    ) {
      totalCount
      nodes {
        name
        description
        stargazerCount
        forkCount
        primaryLanguage { name }
        languages(first: 12, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def window() -> tuple[str, str]:
    """
    Pin the query to whole UTC days.

    Left to its own devices, contributionsCollection measures "the past year"
    from the instant of the request. Two runs a few minutes apart then bucket
    boundary days into different weeks, the columns shift by a sub-pixel, and
    the file differs — so the workflow commits every night having learned
    nothing. Anchoring to 00:00:00Z / 23:59:59Z makes a given day's output a
    pure function of that day's data.
    """
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    return f"{start}T00:00:00Z", f"{today}T23:59:59Z"


def fetch() -> dict:
    if not TOKEN:
        sys.exit("fatal: GITHUB_TOKEN is not set")
    frm, to = window()
    payload = json.dumps(
        {"query": QUERY, "variables": {"login": LOGIN, "from": frm, "to": to}}
    ).encode()
    req = urllib.request.Request(
        GRAPHQL,
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": f"{LOGIN}-profile-generator",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    if "errors" in body:
        sys.exit(f"fatal: GraphQL: {body['errors']}")
    return body["data"]["user"]


# --------------------------------------------------------------------------- #
# Derivations
# --------------------------------------------------------------------------- #
def days_from(user: dict) -> list[tuple[str, int]]:
    out = []
    for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            out.append((day["date"], day["contributionCount"]))
    return out


def streaks(days: list[tuple[str, int]]) -> dict:
    """
    Current streak ignores today when today is still empty — a streak
    shouldn't be reported as broken at 05:00 UTC because the day is young.
    """
    longest = cur = 0
    longest_end = cur_start = None
    best_start = best_end = None
    for date, count in days:
        if count > 0:
            cur += 1
            if cur == 1:
                cur_start = date
            if cur > longest:
                longest, best_start, best_end = cur, cur_start, date
        else:
            cur, cur_start = 0, None

    trailing = list(days)
    if trailing and trailing[-1][1] == 0:
        trailing.pop()
    current, current_start = 0, None
    for date, count in reversed(trailing):
        if count == 0:
            break
        current += 1
        current_start = date

    return {
        "current": current,
        "current_start": current_start,
        "current_end": trailing[-1][0] if trailing and current else None,
        "longest": longest,
        "longest_start": best_start,
        "longest_end": best_end,
        "active": sum(1 for _, c in days if c > 0),
        "total_days": len(days),
    }


def language_stats(repos: list[dict]) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    by_bytes: Counter = Counter()
    by_repo: Counter = Counter()
    skip = {"HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Shell", "Batchfile", "Procfile"}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name not in skip:
                by_bytes[name] += edge["size"]
        primary = (repo.get("primaryLanguage") or {}).get("name")
        if primary and primary not in skip:
            by_repo[primary] += 1
    return by_bytes.most_common(6), by_repo.most_common(6)


def human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


def pretty(date: str | None) -> str:
    if not date:
        return "—"
    return datetime.strptime(date, "%Y-%m-%d").strftime("%d %b %Y")


# --------------------------------------------------------------------------- #
# SVG scaffolding
# --------------------------------------------------------------------------- #
def inline_font(filename: str, family: str, weight: int = 400) -> str:
    """
    Embed a woff2 subset as a data URI.

    An external font URL cannot work here: these files load through an <img>
    tag, and browsers refuse subresource fetches for image documents. A
    base64 @font-face inside the file does work — which also means every SVG
    carries its own copy, hence the per-role subsets.
    """
    path = os.path.join(FONT_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"font-display:block;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
    )


def theme_css() -> str:
    """
    A <style> block inside the SVG survives, because the SVG is a separate
    document rather than markdown GitHub sanitises. So the file can theme
    itself and one asset serves both GitHub themes — no <picture> pairs, no
    two sets of files to keep in sync.
    """
    return (
        f".ink{{fill:{INK_LIGHT};}}"
        f".muted{{fill:{MUTED_LIGHT};}}"
        f".accent{{fill:{ACCENT_LIGHT};}}"
        f".rule{{stroke:{RULE_LIGHT};}}"
        f".bar{{fill:{ACCENT_LIGHT};}}"
        f".card{{fill:#FFFFFF;stroke:{RULE_LIGHT};}}"
        "@media (prefers-color-scheme: dark){"
        f".ink{{fill:{INK_DARK};}}"
        f".muted{{fill:{MUTED_DARK};}}"
        f".accent{{fill:{ACCENT_DARK};}}"
        f".rule{{stroke:{RULE_DARK};}}"
        f".bar{{fill:{ACCENT_DARK};}}"
        f".card{{fill:#0D1117;stroke:{RULE_DARK};}}"
        "}"
    )


def svg_open(w: int, h: int, title: str, extra_css: str = "", fonts: str = "") -> list[str]:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}" '
        'font-family="' + MONO_FALLBACK + '">',
        f"<title>{escape(title)}</title>",
        f"<style>{fonts}{theme_css()}{extra_css}</style>",
    ]
    if CARD:
        # THEME=card draws the background into the image itself, so the
        # graphic can never end up dark-on-dark. A media query inside an SVG
        # follows the *browser's* colour scheme, not GitHub's theme switch —
        # anyone whose GitHub theme is set manually against their OS sees the
        # other variant. Transparent looks better; card always stays legible.
        parts.append(
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="6" '
            f'class="card" stroke-width="1"/>'
        )
    parts.append(f'<g transform="translate({PAD},0)">')
    return parts


def text(x, y, s, cls="ink", size=13, weight=400, anchor="start", extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>'
    )


def label(x, y, s) -> str:
    """Small uppercase tracking-wide caption."""
    return (
        f'<text x="{x}" y="{y}" class="muted" font-size="10" letter-spacing="1.4">'
        f"{escape(s.upper())}</text>"
    )


def write(name: str, parts: list[str]) -> None:
    parts.append("</g></svg>")
    path = os.path.join(OUT_DIR, name)
    body = "\n".join(parts) + "\n"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            if fh.read() == body:
                print(f"  = {name} unchanged")
                return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"  → {name}")


# --------------------------------------------------------------------------- #
# stats.svg
# --------------------------------------------------------------------------- #
def draw_stats(user: dict, days: list[tuple[str, int]]) -> None:
    cc = user["contributionsCollection"]
    repos = user["repositories"]["nodes"]
    total = cc["contributionCalendar"]["totalContributions"]
    stars = sum(r["stargazerCount"] for r in repos)

    h = 210
    fonts = inline_font("mono-regular.woff2", "JetBrains Mono", 400) + inline_font(
        "mono-bold.woff2", "JetBrains Mono", 700
    )
    p = svg_open(WIDTH, h, f"{total} contributions in the last 365 days", fonts=fonts)

    p.append(label(0, 14, "contributions · 365 days"))
    p.append(text(0, 68, human(total), cls="ink", size=56, weight=700))

    rows = [
        ("commits", human(cc["totalCommitContributions"])),
        ("pull requests", human(cc["totalPullRequestContributions"])),
        ("public repos", human(user["repositories"]["totalCount"])),
        ("stars earned", human(stars)),
    ]
    y = 22
    for name, value in rows:
        p.append(text(W - 96, y, name, cls="muted", size=12, anchor="end"))
        p.append(text(W, y, value, cls="ink", size=13, weight=700, anchor="end"))
        y += 20

    # Weekly aggregate columns. Daily counts are sparse and discrete — a line
    # through 0,0,11,0 draws values that never happened. Weekly totals are a
    # continuous quantity, and columns keep an empty week visibly empty.
    weeks = [sum(c for _, c in days[i : i + 7]) for i in range(0, len(days), 7)]
    top, base, height = 108, 196, 78
    peak = max(weeks) or 1
    gap = 2.0
    bw = (W + gap) / len(weeks) - gap

    p.append(f'<line x1="0" y1="{base + 0.5}" x2="{W}" y2="{base + 0.5}" class="rule" stroke-width="1"/>')
    p.append('<g class="bar">')
    for i, value in enumerate(weeks):
        bh = max(1.0, value / peak * height)
        x = i * (bw + gap)
        y0 = base - bh
        op = 0.35 + 0.65 * (value / peak)
        p.append(
            f'<rect x="{x:.2f}" y="{y0:.2f}" width="{bw:.2f}" height="{bh:.2f}" '
            f'rx="1" opacity="{op:.2f}">'
            # Grow once and freeze. No loop — a README that pulses forever is
            # a README nobody finishes reading.
            f'<animate attributeName="height" from="0" to="{bh:.2f}" '
            f'begin="{i * 0.012:.3f}s" dur="0.5s" fill="freeze"/>'
            f'<animate attributeName="y" from="{base}" to="{y0:.2f}" '
            f'begin="{i * 0.012:.3f}s" dur="0.5s" fill="freeze"/>'
            "</rect>"
        )
    p.append("</g>")
    p.append(label(0, top - 8, "weekly volume"))
    p.append(text(W, top - 8, f"peak {peak}/wk", cls="muted", size=10, anchor="end"))
    write("stats.svg", p)


# --------------------------------------------------------------------------- #
# streak.svg
# --------------------------------------------------------------------------- #
def draw_streak(st: dict) -> None:
    h = 108
    fonts = inline_font("mono-regular.woff2", "JetBrains Mono", 400) + inline_font(
        "mono-bold.woff2", "JetBrains Mono", 700
    )
    p = svg_open(WIDTH, h, "Contribution streaks", fonts=fonts)

    pct = st["active"] / max(st["total_days"], 1) * 100
    cells = [
        ("current streak", f"{st['current']}", "days",
         f"{pretty(st['current_start'])} → {pretty(st['current_end'])}"),
        ("longest streak", f"{st['longest']}", "days",
         f"{pretty(st['longest_start'])} → {pretty(st['longest_end'])}"),
        ("days with commits", f"{st['active']}", f"/ {st['total_days']}",
         f"{pct:.0f}% of the year"),
    ]
    col = W / 3
    for i, (cap, big, unit, sub) in enumerate(cells):
        x = i * col
        if i:
            p.append(f'<line x1="{x - 24:.0f}" y1="10" x2="{x - 24:.0f}" y2="{h - 10}" class="rule" stroke-width="1"/>')
        p.append(label(x, 16, cap))
        # The unit rides in a <tspan> so it flows after the number instead of
        # being placed at a guessed pixel offset. Never measure a string whose
        # font you do not control.
        p.append(
            f'<text x="{x:.1f}" y="62" class="accent" font-size="38" font-weight="700">'
            f'{escape(big)}<tspan class="muted" font-size="13" font-weight="400" '
            f'dx="6">{escape(unit)}</tspan></text>'
        )
        p.append(text(x, 86, sub, cls="muted", size=11))
    write("streak.svg", p)


# --------------------------------------------------------------------------- #
# langs.svg
# --------------------------------------------------------------------------- #
def draw_langs(by_bytes: list[tuple[str, int]], by_repo: list[tuple[str, int]]) -> None:
    rows = max(len(by_bytes), len(by_repo), 1)
    h = 52 + rows * 26
    fonts = inline_font("mono-regular.woff2", "JetBrains Mono", 400)
    p = svg_open(WIDTH, h, "Language distribution", fonts=fonts)

    colw = W / 2 - 20

    def column(x0: float, caption: str, data: list[tuple[str, int]], suffix: str) -> None:
        p.append(label(x0, 14, caption))
        total = sum(v for _, v in data) or 1
        peak = max((v for _, v in data), default=1)
        y = 40
        for i, (name, value) in enumerate(data):
            share = value / total * 100
            bw = value / peak * (colw - 210)
            p.append(text(x0, y + 10, name, cls="ink", size=12))
            p.append(
                f'<rect x="{x0 + 130:.1f}" y="{y:.1f}" width="{bw:.1f}" height="12" rx="1" '
                f'class="bar" opacity="{0.95 - i * 0.13:.2f}">'
                f'<animate attributeName="width" from="0" to="{bw:.1f}" '
                f'begin="{i * 0.07:.2f}s" dur="0.55s" fill="freeze"/></rect>'
            )
            unit = suffix.rstrip("s") if value == 1 else suffix
            shown = f"{share:.1f}%" if suffix == "%" else f"{value} {unit}"
            p.append(text(x0 + colw, y + 10, shown, cls="muted", size=11, anchor="end"))
            y += 26

    column(0, "by bytes of code", by_bytes, "%")
    column(W / 2 + 20, "by repository", by_repo, "repos")
    p.append(f'<line x1="{W / 2:.0f}" y1="6" x2="{W / 2:.0f}" y2="{h - 6}" class="rule" stroke-width="1"/>')
    write("langs.svg", p)


# --------------------------------------------------------------------------- #
# year.svg
# --------------------------------------------------------------------------- #
def draw_year(days: list[tuple[str, int]]) -> None:
    """
    The last 365 days as a square grid, five intensity levels.

    Thresholds are quartiles of *this* profile's active days, not fractions of
    the maximum. One 40-commit afternoon would otherwise push every ordinary
    day into level 1 and flatten the whole year — the graphic would say more
    about a single outlier than about the habit.
    """
    # 11.5 rather than GitHub's ~13 pitch: at 13 the 53-week grid runs to
    # 721px and pushes the side panel past the width guard, which drops it
    # silently. The squares stay legible; the panel is worth more than 1.5px.
    cell, box, radius = 11.5, 9.5, 2.0
    left, top = 32.0, 40.0

    weeks: list[list[tuple[str, int]]] = []
    first_weekday = datetime.strptime(days[0][0], "%Y-%m-%d").weekday()
    first_weekday = (first_weekday + 1) % 7  # Monday=0 → Sunday=0
    week: list[tuple[str, int]] = [("", -1)] * first_weekday
    for date, count in days:
        week.append((date, count))
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week + [("", -1)] * (7 - len(week)))

    active = sorted(c for _, c in days if c > 0)

    def cut(frac: float) -> int:
        return active[min(int(len(active) * frac), len(active) - 1)] if active else 1

    t1, t2, t3 = cut(0.25), cut(0.55), cut(0.80)

    def level(count: int) -> int:
        if count <= 0:
            return 0
        if count <= t1:
            return 1
        if count <= t2:
            return 2
        if count <= t3:
            return 3
        return 4

    # Opacity steps rather than five different colours: one accent, five
    # weights. Level 0 keeps a faint tile so the grid still reads as a grid
    # through a quiet autumn instead of looking like a failed render.
    OPACITY = {0: 0.07, 1: 0.30, 2: 0.52, 3: 0.76, 4: 1.0}

    grid_right = left + len(weeks) * cell
    h = int(top + 7 * cell + 40)
    fonts = inline_font("mono-regular.woff2", "JetBrains Mono", 400)
    p = svg_open(WIDTH, h, "Contribution calendar for the last 365 days", fonts=fonts)

    # Month ticks at the first week containing that month's opening days.
    seen = set()
    for wi, wk in enumerate(weeks):
        for date, _ in wk:
            if not date:
                continue
            dt = datetime.strptime(date, "%Y-%m-%d")
            key = (dt.year, dt.month)
            if dt.day <= 7 and key not in seen:
                seen.add(key)
                p.append(
                    f'<text x="{left + wi * cell:.1f}" y="{top - 12}" class="muted" '
                    f'font-size="9" letter-spacing="1">{dt.strftime("%b").upper()}</text>'
                )
            break

    names = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label_text in names.items():
        p.append(
            f'<text x="0" y="{top + row * cell + box - 2:.1f}" class="muted" '
            f'font-size="9">{label_text}</text>'
        )

    p.append('<g class="bar">')
    for wi, wk in enumerate(weeks):
        for row, (date, count) in enumerate(wk):
            if not date:
                continue
            x, y = left + wi * cell, top + row * cell
            lvl = level(count)
            p.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{box}" height="{box}" '
                f'rx="{radius}" opacity="{OPACITY[lvl]}">'
                f"<title>{count} on {pretty(date)}</title></rect>"
            )
    p.append("</g>")

    # Right-hand panel: what a square grid alone makes you squint to work out.
    busiest = max(days, key=lambda dc: dc[1])
    quiet_run = run = 0
    for _, c in days:
        run = run + 1 if c == 0 else 0
        quiet_run = max(quiet_run, run)
    median = active[len(active) // 2] if active else 0

    px = grid_right + 34
    if px < W - 150:
        p.append(
            f'<line x1="{px - 18:.0f}" y1="{top - 24:.0f}" x2="{px - 18:.0f}" '
            f'y2="{top + 7 * cell - 4:.0f}" class="rule" stroke-width="1"/>'
        )
        yy = top - 12
        for cap, val in [
            ("busiest day", f"{busiest[1]} on {pretty(busiest[0])[:6]}"),
            ("typical active day", f"{median} contributions"),
            ("longest quiet run", f"{quiet_run} days"),
        ]:
            p.append(label(px, yy, cap))
            p.append(text(px, yy + 17, val, cls="ink", size=12))
            yy += 36

    # Legend, with the thresholds spelled out. A key that says "Less → More"
    # without numbers is decoration; this one tells you what a dark square cost.
    ly = top + 7 * cell + 22
    p.append(text(left, ly + box - 3, "less", cls="muted", size=9))
    lx = left + 34
    p.append('<g class="bar">')
    for lvl in range(5):
        p.append(
            f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{box}" height="{box}" '
            f'rx="{radius}" opacity="{OPACITY[lvl]}"/>'
        )
        lx += cell
    p.append("</g>")
    p.append(text(lx + 4, ly + box - 3, "more", cls="muted", size=9))
    p.append(
        text(
            lx + 46,
            ly + box - 3,
            f"levels at 1, {t1 + 1}, {t2 + 1}, {t3 + 1}+ contributions",
            cls="muted",
            size=9,
        )
    )
    write("year.svg", p)


# --------------------------------------------------------------------------- #
# The README's own text
#
# The graphics are only half of it. These blocks make the prose live too, so
# the page reports what actually happened this week instead of what was true
# the day it was written.
# --------------------------------------------------------------------------- #
def fetch_events() -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/users/{LOGIN}/events/public?per_page=100",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{LOGIN}-profile-generator",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data if isinstance(data, list) else []
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"  ! events unavailable ({exc})")
        return []


def ago(when: str) -> str:
    try:
        dt = datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return ""
    days = max((datetime.now(timezone.utc) - dt).days, 0)
    return " · today" if days == 0 else " · yesterday" if days == 1 else f" · {days}d ago"


def render_activity(events: list[dict], limit: int = 6) -> str:
    lines, seen = [], set()
    for ev in events:
        if len(lines) >= limit:
            break
        kind, repo = ev.get("type"), (ev.get("repo") or {}).get("name", "")
        pl = ev.get("payload") or {}
        if not repo or (kind, repo) in seen:
            continue
        link = f"[`{repo}`](https://github.com/{repo})"
        if kind == "PushEvent":
            n = pl.get("size", 0) or len(pl.get("commits", []))
            what = (
                f"pushed **{n}** commit{'s' if n != 1 else ''} to {link}"
                if n
                else f"pushed to {link}"
            )
        elif kind == "PullRequestEvent":
            pr = pl.get("pull_request") or {}
            act = "merged" if pl.get("action") == "closed" and pr.get("merged") else pl.get("action", "opened")
            num = pr.get("number", "")
            what = f"{act} PR [#{num}](https://github.com/{repo}/pull/{num}) in {link}"
        elif kind == "CreateEvent" and pl.get("ref_type") == "repository":
            what = f"started {link}"
        elif kind == "ReleaseEvent":
            what = f"released `{(pl.get('release') or {}).get('tag_name', '')}` of {link}"
        elif kind == "IssuesEvent" and pl.get("action") == "opened":
            num = (pl.get("issue") or {}).get("number", "")
            what = f"opened issue [#{num}](https://github.com/{repo}/issues/{num}) in {link}"
        else:
            continue
        seen.add((kind, repo))
        lines.append(f"- {what}{ago(ev.get('created_at', ''))}")
    return "\n".join(lines) or "- Quiet week — heads down on something that isn't public yet."


def render_focus(repos: list[dict]) -> str:
    """The three repos touched most recently, in the order they were touched."""
    rows = []
    for repo in repos[:3]:
        desc = (repo.get("description") or "").strip()
        if len(desc) > 96:
            desc = desc[:93].rsplit(" ", 1)[0] + "…"
        lang = (repo.get("primaryLanguage") or {}).get("name", "")
        meta = " · ".join(x for x in (lang, f"{repo['stargazerCount']}★") if x)
        rows.append(
            f"- **[{repo['name']}](https://github.com/{LOGIN}/{repo['name']})**"
            + (f" — {desc}" if desc else "")
            + (f"  <samp>{meta}</samp>" if meta else "")
        )
    return "\n".join(rows)


def splice_readme(blocks: dict[str, str], path: str = "README.md") -> None:
    if not os.path.exists(path):
        print(f"  ! {path} not found, skipping prose")
        return
    with open(path, encoding="utf-8") as fh:
        original = fh.read()
    updated = original
    for name, body in blocks.items():
        start, end = f"<!-- AUTOGEN:{name}:start -->", f"<!-- AUTOGEN:{name}:end -->"
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        if not pattern.search(updated):
            print(f"  ! marker {name!r} missing")
            continue
        updated = pattern.sub(f"{start}\n{body}\n{end}", updated, count=1)
    if updated == original:
        print("  = README.md unchanged")
        return
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(updated)
    print("  → README.md")


# --------------------------------------------------------------------------- #
def main() -> int:
    user = fetch()
    days = days_from(user)
    print(f"· {LOGIN}: {len(days)} days, {len(user['repositories']['nodes'])} public repos")

    draw_stats(user, days)
    draw_streak(streaks(days))
    by_bytes, by_repo = language_stats(user["repositories"]["nodes"])
    draw_langs(by_bytes, by_repo)
    draw_year(days)

    splice_readme(
        {
            "activity": render_activity(fetch_events()),
            "focus": render_focus(user["repositories"]["nodes"]),
        }
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        sys.exit(f"fatal: GitHub API: {exc}")
