# Setup

Roughly 40 minutes, most of it spent picking a photo.

```bash
gh repo create addyvantage --public --clone   # name must equal your username
cd addyvantage
```

Copy in `README.md`, `scripts/`, and `.github/`.

---

## 1. Fonts

Optional but worth it — this is the only way the page gets your typeface
instead of GitHub's. Skipping it just means the SVGs fall back to the
visitor's monospace, and the layout still holds, because nothing in the
generators depends on a measured string width.

The font must be OFL or similar: the file lands in a public repo. JetBrains
Mono, IBM Plex Mono, Fira Code and Source Code Pro all qualify. Commercial
fonts are not an option here.

```bash
pip install fonttools brotli
mkdir -p assets/fonts
# download JetBrains Mono, then:

# 13 ramp glyphs only — for the portrait
pyftsubset JetBrainsMono-Regular.ttf --text=' .`:-=+*cs#%@' \
  --flavor=woff2 --layout-features='' --no-hinting -o assets/fonts/ramp.woff2

# basic latin — for the data graphics
pyftsubset JetBrainsMono-Regular.ttf --unicodes=U+0020-007E \
  --flavor=woff2 --layout-features='' --no-hinting -o assets/fonts/mono-regular.woff2
pyftsubset JetBrainsMono-Bold.ttf --unicodes=U+0020-007E \
  --flavor=woff2 --layout-features='' --no-hinting -o assets/fonts/mono-bold.woff2

# just the heading letters
pyftsubset JetBrainsMono-Medium.ttf --text='whoamibuildngsteryqu' \
  --flavor=woff2 --layout-features='' --no-hinting -o assets/fonts/headings.woff2
```

Commit the OFL licence file next to them. Each SVG inlines its own copy as
base64, because an external font URL cannot work: these files load through an
`<img>` tag and browsers refuse subresource fetches for image documents.
Subsetting is what keeps that from costing megabytes — expect ~1.5 KB for the
ramp and ~4.5 KB per basic-latin weight.

## 2. Portrait

Already done — `portrait-dark.svg` and `portrait-light.svg` are generated from
the headshot you sent. To redo them from another photo:

```bash
pip install pillow numpy opencv-python-headless rembg onnxruntime

python3 scripts/portrait.py photo.jpg -o portrait-dark.svg  --dark \
  --cols 130 --clip 3.5 --gamma 1.0 --stagger 0.05 --dur 0.55 --size 13.3 --char-w 8
python3 scripts/portrait.py photo.jpg -o portrait-light.svg \
  --cols 130 --clip 3.5 --gamma 1.0 --stagger 0.05 --dur 0.55 --size 13.3 --char-w 8
```

**Why two files.** A dense glyph is *more ink*. On a white page that reads as
darker; on a dark page it emits more light and reads as brighter. The same
text is therefore a photographic negative depending on the background — hair
glowing white, skin in shadow. Density is baked into the characters, so no
amount of CSS fixes it after the fact. `--dark` flips the mapping, and the
README swaps between the two with a `<picture>` element, which GitHub keeps.

**Settings for your photo, and why they differ from the guide's defaults.**
Your headshot is evenly-lit studio work against white, which is the opposite
problem to the one the defaults assume. Clip 3.0 and gamma 1.7 on an already
well-exposed face drove the skin to the dark end of the ramp and filled it in
solid. What worked: 130 columns rather than 90 (flat light gives few shadow
edges, so the likeness has to come from resolution), clip 3.5 for local
contrast, and gamma 1.0 — no darkening curve at all.

At 130 columns the natural width is 1040px and it's displayed at 600. Below
about 110 the glasses and eyes stop resolving.

`--no-rembg` is safe for that photo because the background is already white.
For anything else, leave the cut-out on: the script now preserves a background
mask across CLAHE, but it can only mask what was white to begin with.

## 3. Headings and first run

```bash
python3 scripts/generate_headings.py

export GITHUB_TOKEN=$(gh auth token)
export GH_LOGIN=addyvantage
python3 scripts/generate_stats.py
python3 scripts/check_markdown.py     # preflight
```

Then commit, push, and run the workflow once by hand from the Actions tab.

**After that, let CI own `stats.svg`, `streak.svg`, `langs.svg` and
`year.svg`.** Regenerating them locally as well is a reliable way to
manufacture merge conflicts: your token and the workflow's token bucket days
near a week boundary slightly differently, so the two outputs are never
byte-identical.

---

## Gotchas

**Theme mismatch.** A `prefers-color-scheme` query inside an SVG follows the
*browser's* colour scheme, not GitHub's theme switch. Anyone whose GitHub
theme is set manually against their OS sees the other variant. Most people
sync with system, so this is usually invisible — but if you want it airtight,
set `THEME: card` in the workflow and each graphic carries its own background.
It looks slightly boxier and can never be dark-on-dark.

**The type-out runs 4.4s.** 78 rows at 0.05s stagger. Raise `--stagger` if you
want it slower, but past about 6s people scroll away before it lands.

**Screenshots kill SMIL.** Verifying with headless Chrome and `fullPage: true`
produces blank animated SVGs. Use a tall viewport and wait — the portrait
takes about 4–5 s to finish typing.

**Image caching.** GitHub proxies README images and caches them. A push
usually busts it; if a graphic looks stale for a few minutes, that's why, not
the workflow.

**A new profile README is cached too.** If it doesn't show on your profile at
all, edit it once through the web UI to force a refresh.

**Pinned repos and your bio cannot be automated.** No GraphQL mutation exists
and the REST call needs a scope your CLI token won't have. Both stay manual.

**The README outline goes empty.** Image headings have no anchor links. The
`alt` text carries the word for screen readers, but GitHub's table-of-contents
button will show nothing. If you'd rather keep it, use real `##` headings and
drop `generate_headings.py`.

**Nightly commits are normal.** The window is a rolling 365 days, so the year
grid shifts one column every day and the file legitimately changes. What the
whole-day pinning prevents is two runs *on the same day* disagreeing.
