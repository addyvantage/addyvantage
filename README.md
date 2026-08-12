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

```mermaid
flowchart LR
    A["Long-form<br/>LLM output"] --> B["Claim<br/>extraction"]
    B --> C["Atomic claims"]
    C --> D["Evidence retrieval<br/>Wikidata · Wikipedia"]
    D --> E["Per-claim<br/>verification"]
    E --> F["Risk<br/>aggregation"]
    F --> G["Scored audit<br/>+ append-only log"]
    E -.->|"no evidence found"| H["Flagged as<br/>unverifiable"]
    H --> F
```

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

```mermaid
sequenceDiagram
    participant U as Client
    participant A as FastAPI
    participant Q as Redis queue
    participant W as RQ worker
    U->>A: POST /analyze
    A->>Q: enqueue job
    A-->>U: 202 + job id
    Note over A,U: request path never waits on the model
    Q->>W: dequeue
    W->>W: parse · LLM · bias scoring
    W->>Q: store result
    U->>A: GET /jobs/{id}
    A-->>U: result
```

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

> [!NOTE]
> Everything in this section is written by a scheduled job, not by me. If it's stale, the workflow broke.

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
- opened issue [#44823](https://github.com/timburgan/timburgan/issues/44823) in [`timburgan/timburgan`](https://github.com/timburgan/timburgan) · today
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
