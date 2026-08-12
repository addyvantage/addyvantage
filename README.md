<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="portrait-dark.svg">
  <img src="portrait-light.svg" width="600" alt="ASCII portrait of Aditya Singh, typing itself out">
</picture>

</div>

> **Aditya Singh** — applied AI systems engineer in New Delhi.<br>
> I work on the unglamorous half of GenAI: whether an output can be<br>
> trusted, traced and shipped. Final year, B.Tech CS at KIIT.

<img src="assets/headings/hd-whoami.svg" width="860" alt="whoami">

Most of what I build sits *around* the model rather than inside it —<br>
claim-level verification, evidence linkage, bias auditing, async<br>
workloads that stay upright when the LLM call takes nine seconds.<br>
The interesting failures live in the plumbing.

<samp>Python · TypeScript · FastAPI · Next.js · PostgreSQL · Redis · Docker · Prometheus</samp>

<samp>Previously: Data Analytics @ National University of Singapore · Data Science @ Sukrit Technologies</samp>

<img src="assets/headings/hd-building.svg" width="860" alt="building">

<details open>
<summary><b>🛡️ Epistemic Audit Engine</b> — can you trust what the model just told you?</summary>

<br>

Long-form LLM output gets graded as one blob, or not at all. This splits it
into atomic claims, retrieves evidence for each from Wikidata and Wikipedia,
verifies them independently, and aggregates the result into a risk score you
can act on — so "this paragraph is probably fine" becomes "these two sentences
are the problem."

The hard part isn't the checking, it's making the checking reproducible: a
deterministic eval harness and an append-only audit log, because a reliability
score you can't reproduce is just a vibe.

<samp>FastAPI · Next.js · retrieval · deterministic eval harness</samp> &nbsp;
[**repo →**](https://github.com/addyvantage/Epistemic-Audit-Engine)

</details>

<details>
<summary><b>⚖️ FairHire-AI</b> — resume screening that audits itself for bias</summary>

<br>

Resume intelligence platform that surfaces hiring bias rather than quietly
encoding it. The architectural point: LLM document processing is decoupled
from the request path through a worker queue, so a nine-second model call
never becomes a nine-second API response.

Instrumented end to end — if a worker is falling behind, the dashboard says so
before a user does.

<samp>FastAPI · RQ workers · PostgreSQL · Redis · Prometheus + Grafana</samp> &nbsp;
[**repo →**](https://github.com/addyvantage/fairhire-ai)

</details>

<details>
<summary><b>🔍 DealLens AI</b> — M&A screening, minus the analyst's weekend</summary>

<br>

Automates the first pass of investment-banking deal screening: financial ratio
filters, NLP over news and filings, synergy detection, and backtesting to check
whether the screen would actually have caught the deals that mattered.

Built as a monorepo and hardened for the boring realities — retries, structured
logging, health and readiness probes.

<samp>Monorepo · Celery · PostgreSQL · observability</samp> &nbsp;
[**repo →**](https://github.com/addyvantage/DealLens-AI-MA-Screener)

</details>

<details>
<summary><b>📈 Dynamic Pricing Simulator</b> — what a pricing policy is worth before you ship it</summary>

<br>

Decision-support system for pricing under demand uncertainty and capacity
constraints. Runs candidate policies against simulated demand and benchmarks
them on the same footing, which surfaced a 4–5% revenue lift over static
pricing in simulation.

<samp>Simulation runner · policy benchmarking · Next.js dashboard</samp> &nbsp;
[**repo →**](https://github.com/addyvantage/dynamic-pricing-decision-simulator)

</details>

<img src="assets/headings/hd-signals.svg" width="860" alt="signals">

<img src="stats.svg" width="860" alt="Contribution totals and weekly volume">

<img src="streak.svg" width="860" alt="Current and longest contribution streaks">

<img src="assets/headings/hd-the-year.svg" width="860" alt="the year">

<img src="year.svg" width="860" alt="The last 365 days, one character per day">

<img src="assets/headings/hd-now.svg" width="860" alt="now">

**Where the commits are actually landing** — the three repositories I touched most recently.

<!-- AUTOGEN:focus:start -->
- **[addyvantage](https://github.com/addyvantage/addyvantage)**  <samp>Python · 0★</samp>
- **[TracePack](https://github.com/addyvantage/TracePack)**  <samp>TypeScript · 0★</samp>
- **[smoke-break](https://github.com/addyvantage/smoke-break)**  <samp>Python · 0★</samp>
<!-- AUTOGEN:focus:end -->

<details>
<summary><b>Recent public activity</b></summary>

<br>

<!-- AUTOGEN:activity:start -->
- pushed to [`addyvantage/addyvantage`](https://github.com/addyvantage/addyvantage) · today
<!-- AUTOGEN:activity:end -->

</details>

<img src="assets/headings/hd-languages.svg" width="860" alt="languages">

<img src="langs.svg" width="860" alt="Language distribution by bytes and by repository">

<img src="assets/headings/hd-elsewhere.svg" width="860" alt="elsewhere">

<samp>

[linkedin.com/in/addyvantage](https://linkedin.com/in/addyvantage) &nbsp;·&nbsp;
[addy@addyvantage.me](mailto:addy@addyvantage.me) &nbsp;·&nbsp;
New Delhi, India

</samp>

<details>
<summary><samp>how this page builds itself</samp></summary>

<br>

Every graphic here is drawn by [`scripts/generate_stats.py`](scripts/generate_stats.py) inside this
repository and committed as a static SVG — no third-party card service, so there is no host that
can rate-limit it, restyle it, or go down and leave a broken image on the one page where that
costs most. The prose regenerates too: the focus list and activity feed above are spliced into
this file by the same script.

Three decisions worth stealing:

- **Whole-UTC-day query window.** Left alone, `contributionsCollection` measures a year back from
  the instant of the request, so two runs minutes apart bucket boundary days differently and the
  output churns forever. Pinning to `00:00:00Z` makes a day's output a pure function of that day's
  data.
- **Every glyph in the portrait carries an explicit `x`.** Relying on the font's 0.600em advance
  means a visitor who falls back to Consolas (~0.55em) sees the whole thing 7% narrow and sheared.
- **Two portraits, not one.** A dense glyph is *more ink* — darker on white, brighter on black. The
  same ASCII is a photographic negative depending on theme, and density is baked into the
  characters, so no CSS can fix it after the fact. A `<picture>` element does the swapping.

<samp>[generate_stats.py](scripts/generate_stats.py) · [portrait.py](scripts/portrait.py) · [the workflow](.github/workflows/refresh-stats.yml)</samp>

</details>
