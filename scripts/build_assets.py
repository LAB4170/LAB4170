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


def banner() -> str:
    grid = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="300" stroke="{BORDER}" stroke-opacity="0.55"/>'
        for x in range(720, 1200, 60)
    ) + "".join(
        f'<line x1="720" y1="{y}" x2="1200" y2="{y}" stroke="{BORDER}" stroke-opacity="0.55"/>'
        for y in range(0, 300, 60)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" role="img" aria-labelledby="t d">
  <title id="t">Lewis Abuga Bosire</title>
  <desc id="d">Software Engineer | Full-Stack Development | Business Systems</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NAVY}"/>
      <stop offset="1" stop-color="#14213D"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY}" stop-opacity="1"/>
      <stop offset="0.55" stop-color="{NAVY}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="300" rx="14" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="1199" height="299" rx="13.5" fill="none" stroke="{BORDER}"/>
  <g>{grid}</g>
  <g transform="translate(900 60)" fill="none" stroke="#4F8EF7">
    <rect x="0" y="0" width="180" height="180" rx="10" stroke-opacity="0.9" stroke-width="1.5"/>
    <rect x="30" y="30" width="180" height="180" rx="10" stroke-opacity="0.45"/>
    <rect x="60" y="60" width="180" height="180" rx="10" stroke-opacity="0.2"/>
  </g>
  <rect x="64" y="86" width="44" height="3" rx="1.5" fill="#4F8EF7"/>
  <text x="64" y="150" font-family="{FONT}" font-size="56" font-weight="600" fill="{WHITE}" letter-spacing="-1">Lewis Abuga Bosire</text>
  <text x="64" y="196" font-family="{FONT}" font-size="21" fill="{MUTED}" letter-spacing="0.3" xml:space="preserve">Software Engineer<tspan fill="#4F8EF7">   |   </tspan>Full-Stack Development<tspan fill="#4F8EF7">   |   </tspan>Business Systems</text>
  <text x="64" y="248" font-family="{FONT}" font-size="14" fill="{DIM}" letter-spacing="2">NAIROBI, KENYA</text>
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
    for name, title, w in (("stats.svg", "GitHub activity", 430), ("languages.svg", "Language distribution", 430), ("activity.svg", "Contribution activity", 890)):
        target = ASSETS / "generated" / name
        if not target.exists():  # never overwrite real generated metrics
            target.write_text(placeholder(title, w), encoding="utf-8")
    (ASSETS / "banner.svg").write_text(banner(), encoding="utf-8")
    for p in PROJECTS:
        (ASSETS / "cards" / p["file"]).write_text(card(p), encoding="utf-8")
    print(f"Wrote banner and {len(PROJECTS)} project cards to {ASSETS}")


if __name__ == "__main__":
    main()
