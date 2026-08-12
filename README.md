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

<table>
<tr>
<td width="50%" valign="top">

**[Epistemic Audit Engine](https://github.com/addyvantage/Epistemic-Audit-Engine)**

Splits long-form LLM output into atomic claims, retrieves evidence from
Wikidata and Wikipedia, verifies each one, and aggregates the result into a
risk score. Ships with a deterministic eval harness and an append-only
audit log.

<samp>FastAPI · Next.js · retrieval · eval harness</samp>

</td>
<td width="50%" valign="top">

**[FairHire-AI](https://github.com/addyvantage/fairhire-ai)**

Resume intelligence platform that surfaces hiring bias. Document processing
is decoupled from the request path through a worker queue, so the API stays
responsive while the slow work happens elsewhere.

<samp>FastAPI · RQ · PostgreSQL · Redis · Grafana</samp>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**[DealLens AI](https://github.com/addyvantage/DealLens-AI-MA-Screener)**

M&A deal screener automating investment-banking workflows: ratio screening,
NLP over news and filings, synergy detection, backtesting. Hardened with
retries, structured logging and readiness probes.

<samp>Monorepo · Celery · Postgres · observability</samp>

</td>
<td width="50%" valign="top">

**[Dynamic Pricing Simulator](https://github.com/addyvantage/dynamic-pricing-decision-simulator)**

Decision-support system for pricing under demand uncertainty and capacity
constraints, benchmarking policies against static baselines. Measured a
4–5% revenue lift in simulation.

<samp>Simulation runner · policy benchmarking · Next.js</samp>

</td>
</tr>
</table>

<img src="assets/headings/hd-signals.svg" width="860" alt="signals">

<img src="stats.svg" width="860" alt="Contribution totals and weekly volume">

<img src="streak.svg" width="860" alt="Current and longest contribution streaks">

<img src="assets/headings/hd-the-year.svg" width="860" alt="the year">

<img src="year.svg" width="860" alt="The last 365 days, one character per day">

<img src="assets/headings/hd-languages.svg" width="860" alt="languages">

<img src="langs.svg" width="860" alt="Language distribution by bytes and by repository">

<img src="assets/headings/hd-elsewhere.svg" width="860" alt="elsewhere">

<samp>

[linkedin.com/in/addyvantage](https://linkedin.com/in/addyvantage) &nbsp;·&nbsp;
[addy@addyvantage.me](mailto:addy@addyvantage.me) &nbsp;·&nbsp;
New Delhi, India

</samp>

<br>

<sub>

Every graphic on this page is drawn by [`scripts/generate_stats.py`](scripts/generate_stats.py)
inside this repository and committed as a static SVG. Nothing here is fetched from a
third-party card service, so there is no host that can rate-limit it, restyle it, or
go down and leave a broken image on the one page where that costs most. The numbers
come from the GitHub GraphQL API on a whole-day window, which makes a given day's
output a pure function of that day's data.

</sub>
