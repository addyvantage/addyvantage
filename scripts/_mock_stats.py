"""Feed the stats generator synthetic API data so it can be verified offline."""
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("GITHUB_TOKEN", "mock")
import generate_stats as g

random.seed(7)

today = date.today()
start = today - timedelta(days=364)
weeks, day, streak_left = [], start, 0
cur = []
total = 0
while day <= today:
    # Bursty: quiet stretches punctuated by multi-day pushes, like real work.
    months_in = (day - start).days / 365.0
    busy = 0.12 + 0.55 * max(0.0, (months_in - 0.45) / 0.55)   # ramps up after ~Feb
    if streak_left == 0 and random.random() < busy:
        streak_left = random.randint(2, 8)
    if streak_left > 0:
        count = random.randint(1, 14)
        streak_left -= 1
    else:
        count = 0 if random.random() < 0.80 else random.randint(1, 3)
    total += count
    cur.append({"date": day.isoformat(), "contributionCount": count, "weekday": (day.weekday() + 1) % 7})
    if len(cur) == 7:
        weeks.append({"contributionDays": cur})
        cur = []
    day += timedelta(days=1)
if cur:
    weeks.append({"contributionDays": cur})

REPOS = [
    ("Epistemic-Audit-Engine", 2, "Python", {"Python": 221000, "TypeScript": 88000, "HTML": 5000}),
    ("fairhire-ai", 1, "Python", {"Python": 141000, "TypeScript": 312000, "CSS": 9000}),
    ("DealLens-AI-MA-Screener", 1, "Python", {"Python": 180000, "Jupyter Notebook": 61000}),
    ("dynamic-pricing-decision-simulator", 1, "Python", {"Python": 95000, "TypeScript": 121000}),
    ("PebbleCode", 0, "TypeScript", {"TypeScript": 74000, "Python": 12000}),
    ("pebble-prototype", 0, "Python", {"Python": 33000, "C++": 9000}),
]

g.fetch = lambda: {
    "login": "addyvantage",
    "name": "Aditya Singh",
    "contributionsCollection": {
        "totalCommitContributions": 954,
        "totalPullRequestContributions": 6,
        "totalIssueContributions": 3,
        "totalRepositoriesWithContributedCommits": 25,
        "contributionCalendar": {"totalContributions": total, "weeks": weeks},
    },
    "repositories": {
        "totalCount": 38,
        "nodes": [
            {
                "name": n,
                "stargazerCount": s,
                "forkCount": 0,
                "primaryLanguage": {"name": pl},
                "languages": {"edges": [{"size": v, "node": {"name": k}} for k, v in langs.items()]},
            }
            for n, s, pl, langs in REPOS
        ],
    },
}

g.OUT_DIR = os.environ.get("OUT_DIR", "/tmp/svg")
os.makedirs(g.OUT_DIR, exist_ok=True)
sys.exit(g.main())
