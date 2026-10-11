"""Shared, input-configurable visual tokens for generated pages."""

from __future__ import annotations

import re


DEFAULTS = {
    "background": "#f4f6fb",
    "surface": "#ffffff",
    "text": "#172033",
    "muted": "#5a667a",
    "accent": "#3157d5",
    "accent_text": "#ffffff",
    "hero_start": "#e6ebff",
    "hero_end": "#f6e6ff",
    "radius": "24px",
}
DARK_DEFAULTS = {
    "background": "#111827",
    "surface": "#1f2937",
    "text": "#f3f4f6",
    "muted": "#c3cad5",
    "accent": "#77a7ff",
    "accent_text": "#10213d",
    "hero_start": "#263b64",
    "hero_end": "#3b2e5f",
    "radius": "24px",
}
COLOR_KEYS = set(DEFAULTS) - {"radius"}


def normalize_style(settings: dict[str, str], theme: str) -> dict[str, str]:
    values = dict(DARK_DEFAULTS if theme == "blue-dark" else DEFAULTS)
    for key, value in settings.items():
        if key not in DEFAULTS:
            raise ValueError(f"unknown style setting '{key}'")
        if key in COLOR_KEYS and not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            raise ValueError(f"style.{key} must be a six-digit hex color")
        if key == "radius" and not re.fullmatch(r"(?:0|[0-9]{1,2})px", value):
            raise ValueError("style.radius must be a pixel value from 0px to 99px")
        values[key] = value.lower() if key in COLOR_KEYS else value
    return values


def render_design_css(settings: dict[str, str]) -> str:
    variables = "\n".join(f"      --site-{key.replace('_', '-')}: {value};" for key, value in settings.items())
    return f'''  <style>
    :root {{
{variables}
    }}
    body.site-page {{ min-height: 100vh; color: var(--site-text); background: var(--site-background); }}
    .site-page main {{ max-width: 1080px; }}
    .site-hero {{
      position: relative; isolation: isolate; overflow: hidden;
      margin-bottom: clamp(2rem, 6vw, 4.5rem);
      padding: clamp(2.5rem, 8vw, 6rem) clamp(1.5rem, 7vw, 5.5rem) !important;
      border: 1px solid color-mix(in srgb, var(--site-text) 12%, transparent);
      border-radius: var(--site-radius);
      background: linear-gradient(125deg, var(--site-hero-start), var(--site-hero-end));
      box-shadow: 0 1.5rem 4rem color-mix(in srgb, var(--site-text) 12%, transparent);
    }}
    .site-hero::after {{
      position: absolute; z-index: -1; top: -8rem; right: -5rem;
      width: clamp(14rem, 40vw, 28rem); aspect-ratio: 1;
      border: 1px solid color-mix(in srgb, var(--site-text) 12%, transparent);
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, color-mix(in srgb, var(--site-accent) 28%, transparent), transparent 70%);
      box-shadow: 0 0 0 2rem color-mix(in srgb, var(--site-text) 3%, transparent);
      content: "";
    }}
    .site-hero h1 {{ max-width: 15ch; margin-inline: auto; font-size: clamp(2.5rem, 7vw, 5rem); line-height: 1; letter-spacing: -.05em; text-wrap: balance; }}
    .site-hero .lead {{ color: var(--site-muted); font-size: clamp(1.1rem, 2vw, 1.35rem); }}
    .site-page .btn-primary {{ padding: .85rem 1.5rem; border: 0; border-radius: 999px; color: var(--site-accent-text); background: var(--site-accent); box-shadow: 0 .6rem 1.5rem color-mix(in srgb, var(--site-accent) 28%, transparent); font-weight: 700; transition: transform .18s ease, box-shadow .18s ease; }}
    .site-page .btn-primary:hover {{ color: var(--site-accent-text); background: color-mix(in srgb, var(--site-accent) 88%, var(--site-text)); transform: translateY(-2px); }}
    .site-page .navbar {{ background: var(--site-accent) !important; color: var(--site-accent-text) !important; }}
    .site-page .navbar .navbar-brand, .site-page .navbar .nav-link {{ color: var(--site-accent-text) !important; }}
    .site-page section > h2 {{ margin-bottom: 1.5rem !important; font-size: clamp(1.6rem, 3vw, 2.15rem); letter-spacing: -.03em; }}
    .site-card {{ height: 100%; overflow: hidden; border: 1px solid color-mix(in srgb, var(--site-text) 12%, transparent); border-radius: var(--site-radius); color: var(--site-text); background: var(--site-surface); box-shadow: 0 .75rem 2rem color-mix(in srgb, var(--site-text) 8%, transparent); text-align: left; transition: transform .18s ease, box-shadow .18s ease; }}
    .site-card::before {{ display: block; height: 3px; background: linear-gradient(90deg, var(--site-accent), var(--site-hero-end)); content: ""; }}
    .site-card:hover {{ box-shadow: 0 1rem 2rem color-mix(in srgb, var(--site-text) 14%, transparent); transform: translateY(-3px); }}
    .site-card .card-body {{ padding: 1.5rem; }}
    @media (prefers-reduced-motion: reduce) {{ .site-page .btn-primary, .site-card {{ transition: none; }} .site-page .btn-primary:hover, .site-card:hover {{ transform: none; }} }}
  </style>'''
