#!/usr/bin/env python3
"""Build the static SVG assets used by README.md (banner and project cards).

Every asset is generated from the data below so spacing, type and colour stay
consistent. Run from the repository root:

    python scripts/build_assets.py

Output is deterministic; re-running without changes produces identical files.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Palette: deep navy, charcoal, white, muted grey, restrained blue accents.
NAVY = "#0B1220"
PANEL = "#0F1830"
BORDER = "#1E2A44"
WHITE = "#F1F5F9"
MUTED = "#94A3B8"
DIM = "#64748B"
FONT = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'Cascadia Code', Consolas, 'Liberation Mono', monospace"

STATUS_COLOURS = {
    "Active": "#4F8EF7",
    "Experimental": "#A5B4FC",
    "Completed": "#7DD3C0",
}


PHRASES = ["Building business systems", "Automating workflows", "Shipping full-stack products"]
CHAR_W = 10.8  # advance of the 18px monospace line; textLength below pins it across fonts
CYCLE = 15  # seconds for the full rotation (5s per phrase)


def banner() -> str:
    grid = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="300" stroke="{BORDER}" stroke-opacity="0.55"/>'
        for x in range(720, 1200, 60)
    ) + "".join(
        f'<line x1="720" y1="{y}" x2="1200" y2="{y}" stroke="{BORDER}" stroke-opacity="0.55"/>'
        for y in range(0, 300, 60)
    )
    css, typed = [], []
    for i, text in enumerate(PHRASES):
        w = round(len(text) * CHAR_W, 1)
        delay = i * CYCLE / len(PHRASES)
        # type in (0-8%), hold (to 28%), erase (to 32%), idle for the rest of the cycle
        css.append(
            f"@keyframes ty{i}{{0%{{width:0}}8%{{width:{w}px}}28%{{width:{w}px}}32%{{width:0}}100%{{width:0}}}}"
            f"@keyframes cr{i}{{0%{{opacity:0;transform:translateX(0)}}0.5%{{opacity:1}}8%{{transform:translateX({w}px)}}"
            f"28%{{transform:translateX({w}px)}}32%{{transform:translateX(0);opacity:1}}33%{{opacity:0}}100%{{opacity:0}}}}"
            f".r{i}{{animation:ty{i} {CYCLE}s steps(24,end) {delay}s infinite both}}"
            f".c{i}{{animation:cr{i} {CYCLE}s steps(24,end) {delay}s infinite both}}"
        )
        first = w if i == 0 else 0  # static fallback shows the first phrase only
        typed.append(
            f'<clipPath id="k{i}"><rect class="r{i}" x="94" y="214" width="{first}" height="30"/></clipPath>'
            f'<text clip-path="url(#k{i})" x="94" y="234" font-family="{MONO}" font-size="18" fill="#8AB1F3" '
            f'textLength="{w}" lengthAdjust="spacing">{escape(text)}</text>'
            f'<rect class="c{i}" x="94" y="217" width="2" height="22" fill="#4F8EF7" opacity="0"/>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" role="img" aria-labelledby="t d">
  <title id="t">Lewis Abuga Bosire</title>
  <desc id="d">Software Engineer | Full-Stack Development | Business Systems</desc>
  <style>
    @keyframes drift{{from{{transform:translateY(0)}}to{{transform:translateY(-7px)}}}}
    @keyframes breathe{{from{{opacity:0.45}}to{{opacity:1}}}}
    .g{{animation:breathe 7s ease-in-out infinite alternate}}
    .s0{{animation:drift 8s ease-in-out infinite alternate}}
    .s1{{animation:drift 8s ease-in-out -2.5s infinite alternate}}
    .s2{{animation:drift 8s ease-in-out -5s infinite alternate}}
    {"".join(css)}
    @media (prefers-reduced-motion: reduce){{*{{animation:none !important}}}}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NAVY}"/>
      <stop offset="1" stop-color="#14213D"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="300" rx="14" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="1199" height="299" rx="13.5" fill="none" stroke="{BORDER}"/>
  <g class="g">{grid}</g>
  <g fill="none" stroke="#4F8EF7">
    <rect class="s0" x="900" y="60" width="180" height="180" rx="10" stroke-opacity="0.9" stroke-width="1.5"/>
    <rect class="s1" x="930" y="90" width="180" height="180" rx="10" stroke-opacity="0.45"/>
    <rect class="s2" x="960" y="120" width="180" height="180" rx="10" stroke-opacity="0.2"/>
  </g>
  <rect x="64" y="64" width="44" height="3" rx="1.5" fill="#4F8EF7"/>
  <text x="122" y="71" font-family="{FONT}" font-size="12.5" fill="{DIM}" letter-spacing="2.5">NAIROBI, KENYA</text>
  <text x="64" y="138" font-family="{FONT}" font-size="56" font-weight="600" fill="{WHITE}" letter-spacing="-1">Lewis Abuga Bosire</text>
  <text x="64" y="182" font-family="{FONT}" font-size="21" fill="{MUTED}" letter-spacing="0.3" xml:space="preserve">Software Engineer<tspan fill="#4F8EF7">   |   </tspan>Full-Stack Development<tspan fill="#4F8EF7">   |   </tspan>Business Systems</text>
  <text x="64" y="234" font-family="{MONO}" font-size="18" fill="#4F8EF7">&gt;</text>
  {"".join(typed)}
</svg>
"""


def glyph(kind: str, colour: str) -> str:
    """Small geometric mark per project (top-right of the card)."""
    common = f'fill="none" stroke="{colour}" stroke-width="1.5"'
    if kind == "group":  # linked circles
        return (
            f'<circle cx="0" cy="12" r="9" {common}/><circle cx="18" cy="12" r="9" {common}/>'
            f'<circle cx="9" cy="-2" r="9" {common}/>'
        )
    if kind == "grid":  # register / cell grid
        return "".join(
            f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" {common}/>'
            for x in (-6, 9) for y in (-6, 9)
        )
    if kind == "bars":  # chart
        return (
            f'<rect x="-6" y="10" width="8" height="12" rx="1.5" {common}/>'
            f'<rect x="6" y="2" width="8" height="20" rx="1.5" {common}/>'
            f'<rect x="18" y="-8" width="8" height="30" rx="1.5" {common}/>'
        )
    # "rings" - concentric
    return (
        f'<circle cx="10" cy="10" r="16" {common}/><circle cx="10" cy="10" r="10" {common} stroke-opacity="0.6"/>'
        f'<circle cx="10" cy="10" r="4" {common} stroke-opacity="0.35"/>'
    )


def card(p: dict) -> str:
    w, h = 560, 232
    accent = p["accent"]
    status_colour = STATUS_COLOURS[p["status"]]
    desc = "".join(
        f'<text x="32" y="{118 + i * 22}" font-family="{FONT}" font-size="14.5" fill="{MUTED}">{escape(line)}</text>'
        for i, line in enumerate(p["lines"])
    )
    pill_w = 22 + 7.6 * len(p["status"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{escape(p['title'])}</title>
  <desc id="d">{escape(p['category'])}. {escape(' '.join(p['lines']))} Status: {p['status']}.</desc>
  <rect width="{w}" height="{h}" rx="14" fill="{PANEL}"/>
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="13.5" fill="none" stroke="{BORDER}"/>
  <path d="M14 0.5 H{w-14}" stroke="{accent}" stroke-opacity="0.9" stroke-width="2"/>
  <text x="32" y="46" font-family="{FONT}" font-size="11.5" font-weight="600" fill="{accent}" letter-spacing="2">{escape(p['category'].upper())}</text>
  <text x="32" y="82" font-family="{FONT}" font-size="26" font-weight="600" fill="{WHITE}" letter-spacing="-0.3">{escape(p['title'])}</text>
  <g transform="translate({w-70} 40)">{glyph(p['glyph'], accent)}</g>
  {desc}
  <line x1="32" y1="176" x2="{w-32}" y2="176" stroke="{BORDER}"/>
  <text x="32" y="204" font-family="{MONO}" font-size="12" fill="{DIM}">{escape(p['stack'])}</text>
  <g transform="translate({w-32-pill_w} 190)">
    <rect width="{pill_w}" height="22" rx="11" fill="none" stroke="{status_colour}" stroke-opacity="0.55"/>
    <circle cx="12" cy="11" r="3" fill="{status_colour}"/>
    <text x="20" y="15" font-family="{FONT}" font-size="11.5" font-weight="600" fill="{status_colour}">{p['status']}</text>
  </g>
</svg>
"""


PROJECTS = [
    {
        "file": "chamasmart.svg",
        "title": "ChamaSmart",
        "category": "Savings group platform",
        "lines": [
            "Memberships, contributions, loans and ledgers for",
            "chama savings groups, with M-Pesa Daraja integration.",
        ],
        "stack": "Java 17 / Spring Boot 3 / React / PostgreSQL",
        "status": "Active",
        "accent": "#4F8EF7",
        "glyph": "group",
    },
    {
        "file": "nexus-pos.svg",
        "title": "Nexus POS",
        "category": "Retail operations",
        "lines": [
            "Sales, inventory, expenses and customer debts for",
            "multiple businesses, with tenant-scoped data.",
        ],
        "stack": "Node.js / Express / React / PostgreSQL",
        "status": "Active",
        "accent": "#38A3D8",
        "glyph": "grid",
    },
    {
        "file": "pssf-dashboard.svg",
        "title": "PSSF Dashboard",
        "category": "Operations dashboard",
        "lines": [
            "Membership, contributions and claims views, backed by a",
            "FastAPI service that currently serves mock data.",
        ],
        "stack": "React / TypeScript / Tailwind / FastAPI",
        "status": "Experimental",
        "accent": "#8B9CF0",
        "glyph": "bars",
    },
    {
        "file": "esg-watchtower.svg",
        "title": "ESG Watchtower",
        "category": "ESG monitoring and reporting",
        "lines": [
            "Angular application for ESG monitoring and reports,",
            "with Firebase backend and Stripe subscription billing.",
        ],
        "stack": "Angular 17 / Firebase / TypeScript / Stripe",
        "status": "Completed",
        "accent": "#5BB5C4",
        "glyph": "rings",
    },
]


def placeholder(title: str, w: int = 430) -> str:
    """Neutral card shown until the metrics workflow first runs. Contains no figures."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="290" viewBox="0 0 {w} 290" role="img" aria-label="{title} (generated by workflow)">
  <rect width="{w}" height="290" rx="14" fill="{PANEL}"/>
  <rect x="0.5" y="0.5" width="{w-1}" height="289" rx="13.5" fill="none" stroke="{BORDER}"/>
  <text x="28" y="40" font-family="{FONT}" font-size="11.5" font-weight="600" fill="#4F8EF7" letter-spacing="2">{title.upper()}</text>
  <text x="28" y="150" font-family="{FONT}" font-size="14" fill="{MUTED}">Generated by the Profile metrics workflow.</text>
  <text x="28" y="172" font-family="{FONT}" font-size="12.5" fill="{DIM}">This card fills in after the first workflow run.</text>
</svg>
"""


def main() -> None:
    (ASSETS / "cards").mkdir(parents=True, exist_ok=True)
    (ASSETS / "generated").mkdir(parents=True, exist_ok=True)
    for name, title, w in (("stats.svg", "GitHub activity", 430), ("languages.svg", "Language distribution", 430), ("activity.svg", "Contribution activity", 890), ("latest.svg", "Latest work", 890), ("snake.svg", "Contribution snake", 890)):
        target = ASSETS / "generated" / name
        if not target.exists():  # never overwrite real generated metrics
            target.write_text(placeholder(title, w), encoding="utf-8")
    (ASSETS / "banner.svg").write_text(banner(), encoding="utf-8")
    for p in PROJECTS:
        (ASSETS / "cards" / p["file"]).write_text(card(p), encoding="utf-8")
    print(f"Wrote banner and {len(PROJECTS)} project cards to {ASSETS}")


if __name__ == "__main__":
    main()
