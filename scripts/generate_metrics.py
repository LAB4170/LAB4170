#!/usr/bin/env python3
"""Generate stats.svg and languages.svg from live public GitHub data.

Uses the GitHub GraphQL API with the token supplied by GitHub Actions
(GITHUB_TOKEN). Only public repositories and public contribution counts are
read. Nothing is hardcoded: every figure comes from the API response.

    python scripts/generate_metrics.py                 # live (needs GH_TOKEN)
    python scripts/generate_metrics.py --fixture f.json  # offline layout test

If the API call fails the script exits non-zero and leaves the existing SVG
files untouched, so a service outage never replaces good assets with bad ones.
The SVG deliberately contains no timestamp, so the workflow only produces a
commit when the underlying figures actually change.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from collections import defaultdict
from html import escape
from pathlib import Path

LOGIN = "LAB4170"
OUT = Path(__file__).resolve().parent.parent / "assets" / "generated"

NAVY, PANEL, BORDER = "#0B1220", "#0F1830", "#1E2A44"
WHITE, MUTED, DIM, BLUE = "#F1F5F9", "#94A3B8", "#64748B", "#4F8EF7"
FONT = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-metrics"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise RuntimeError(f"GraphQL error: {payload.get('errors', 'no user data')}")
    return payload["data"]["user"]


def summarise(user: dict) -> dict:
    repos = user["repositories"]["nodes"]
    langs: dict[str, int] = defaultdict(int)
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"].get("weeks", []) for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"])
              for w in cc["contributionCalendar"].get("weeks", [])]
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        elif current == 0 and d is days[-1]:
            continue  # today may not have activity yet; do not break the streak
        else:
            break
    return {
        "weekly": weekly,
        "current_streak": current,
        "longest_streak": longest,
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "languages": sorted(langs.items(), key=lambda kv: kv[1], reverse=True),
    }


def frame(w: int, h: int, title: str, body: str, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
  <rect width="{w}" height="{h}" rx="14" fill="{PANEL}"/>
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="13.5" fill="none" stroke="{BORDER}"/>
  <text x="28" y="40" font-family="{FONT}" font-size="11.5" font-weight="600" fill="{BLUE}" letter-spacing="2">{escape(title.upper())}</text>
{body}
  <text x="28" y="{h-18}" font-family="{FONT}" font-size="11" fill="{DIM}">Public repositories and public activity only</text>
</svg>
"""


def stats_svg(s: dict) -> str:
    items = [
        ("Public repositories", s["repos"]),
        ("Stars received", s["stars"]),
        ("Contributions, last 12 months", s["contributions"]),
        ("Commits", s["commits"]),
        ("Pull requests", s["prs"]),
        ("Issues opened", s["issues"]),
    ]
    rows = []
    for i, (label, value) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = 28 + col * 200, 84 + row * 62
        rows.append(
            f'  <text x="{x}" y="{y}" font-family="{FONT}" font-size="28" font-weight="600" fill="{WHITE}">{value:,}</text>\n'
            f'  <text x="{x}" y="{y + 20}" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{escape(label)}</text>'
        )
    return frame(430, 290, "GitHub activity", "\n".join(rows), "GitHub statistics for " + LOGIN)


def languages_svg(s: dict) -> str:
    langs = s["languages"][:6]
    total = sum(v for _, v in s["languages"]) or 1
    shades = ["#4F8EF7", "#6C9FF5", "#8AB1F3", "#A6C3F1", "#C0D4EF", "#D8E3EE"]
    bar_w = 374
    # stacked bar
    x, segs = 28.0, []
    for (name, size), colour in zip(langs, shades):
        w = bar_w * size / total
        segs.append(f'<rect x="{x:.1f}" y="62" width="{max(w, 1):.1f}" height="10" fill="{colour}"/>')
        x += w
    bar = (f'  <clipPath id="c"><rect x="28" y="62" width="{bar_w}" height="10" rx="5"/></clipPath>\n'
           f'  <g clip-path="url(#c)">{"".join(segs)}</g>')
    legend = []
    for i, ((name, size), colour) in enumerate(zip(langs, shades)):
        col, row = i % 2, i // 2
        lx, ly = 28 + col * 200, 112 + row * 44
        pct = 100 * size / total
        legend.append(
            f'  <circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colour}"/>\n'
            f'  <text x="{lx + 18}" y="{ly}" font-family="{FONT}" font-size="14" fill="{WHITE}">{escape(name)}</text>\n'
            f'  <text x="{lx + 18}" y="{ly + 17}" font-family="{FONT}" font-size="12" fill="{MUTED}">{pct:.1f}%</text>'
        )
    return frame(430, 290, "Language distribution", bar + "\n" + "\n".join(legend),
                 "Language distribution across public repositories of " + LOGIN)


def activity_svg(s: dict) -> str:
    w, h = 890, 290
    weekly = s["weekly"] or [0]
    left, right, top, bottom = 28, w - 28, 150, 236
    peak = max(weekly) or 1
    n = len(weekly)
    step = (right - left) / max(n - 1, 1)
    pts = [(left + i * step, bottom - (bottom - top) * v / peak) for i, v in enumerate(weekly)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{left},{bottom} " + line + f" {right},{bottom}"
    heads = [
        (f"{s['current_streak']:,}", "Current streak, days"),
        (f"{s['longest_streak']:,}", "Longest streak, last 12 months"),
        (f"{s['active_days']:,}", "Active days, last 12 months"),
    ]
    head_svg = "\n".join(
        f'  <text x="{28 + i * 290}" y="84" font-family="{FONT}" font-size="28" font-weight="600" fill="{WHITE}">{v}</text>\n'
        f'  <text x="{28 + i * 290}" y="104" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{escape(lbl)}</text>'
        for i, (v, lbl) in enumerate(heads)
    )
    body = f"""  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0.35"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </linearGradient></defs>
{head_svg}
  <line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{BORDER}"/>
  <polygon points="{area}" fill="url(#g)"/>
  <polyline points="{line}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-linejoin="round"/>
  <text x="{left}" y="{bottom + 18}" font-family="{FONT}" font-size="11" fill="{DIM}">12 months ago</text>
  <text x="{right}" y="{bottom + 18}" font-family="{FONT}" font-size="11" fill="{DIM}" text-anchor="end">This week</text>"""
    return frame(w, h, "Contribution activity", body, "Weekly contribution activity for " + LOGIN).replace(
        f'y="{h-18}"', f'y="{h-18}" opacity="0"')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", help="JSON file shaped like the API user object (layout testing only)")
    ap.add_argument("--out", help="override output directory (layout testing only)")
    args = ap.parse_args()

    try:
        if args.fixture:
            user = json.loads(Path(args.fixture).read_text())
        else:
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if not token:
                print("No GH_TOKEN/GITHUB_TOKEN set; leaving existing assets unchanged.", file=sys.stderr)
                return 1
            user = fetch(token)
        summary = summarise(user)
    except Exception as exc:  # network, auth, rate limit, schema change
        print(f"Metrics refresh failed, keeping existing assets: {exc}", file=sys.stderr)
        return 1

    out = Path(args.out) if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    (out / "stats.svg").write_text(stats_svg(summary), encoding="utf-8")
    (out / "languages.svg").write_text(languages_svg(summary), encoding="utf-8")
    (out / "activity.svg").write_text(activity_svg(summary), encoding="utf-8")
    print(f"Wrote stats.svg, languages.svg and activity.svg to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
