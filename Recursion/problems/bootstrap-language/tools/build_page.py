#!/usr/bin/env python3
"""Build one static Bootstrap page from Recursion's supported YAML subset."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from design import normalize_style, render_design_css


PROBLEM_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROBLEM_DIR / "source" / "operator-brief.yaml"
DEFAULT_OUTPUT = PROBLEM_DIR / "output" / "operator-brief.html"
BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
BOOTSTRAP_CSS_SRI = (
    "sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
)


def fail(path: Path, line: int, message: str) -> ValueError:
    return ValueError(f"{path}:{line}: {message}")


def parse_scalar(value: str, path: Path, line: int) -> str:
    value = value.strip()
    if not value:
        raise fail(path, line, "expected a text value")
    if value[0] in "\"'":
        quote = value[0]
        if len(value) < 2 or value[-1] != quote:
            raise fail(path, line, "unterminated quoted value")
        inner = value[1:-1]
        if quote == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    if any(token in value for token in (" #", "\t", ": ", "\n")):
        raise fail(path, line, "quote values containing YAML punctuation or whitespace escapes")
    return value


def parse_page(path: Path) -> dict[str, object]:
    page: dict[str, object] = {"hero": {}, "navbar": {"items": []}, "style": {}, "cards": [], "references": []}
    seen_top: set[str] = set()
    seen_hero: set[str] = set()
    seen_nav: set[str] = set()
    seen_style: set[str] = set()
    seen_feature: set[str] = set()
    block: str | None = None
    nav_items_open = False
    current_nav_item: dict[str, str] | None = None
    current_card: dict[str, str] | None = None
    current_reference: dict[str, str] | None = None
    lines = path.read_text(encoding="utf-8").splitlines()

    for number, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("\t"):
            raise fail(path, number, "tabs are not allowed for indentation")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 4 and block == "navbar" and nav_items_open:
            item_match = re.fullmatch(r"    - label:(?:[ ]+(.*))?", raw)
            if not item_match or item_match.group(1) is None:
                raise fail(path, number, "navbar items must start with '- label: text'")
            nav = page["navbar"]
            assert isinstance(nav, dict)
            current_nav_item = {"label": parse_scalar(item_match.group(1), path, number)}
            items = nav["items"]
            assert isinstance(items, list)
            items.append(current_nav_item)
            continue
        if indent == 6 and block == "navbar" and nav_items_open and current_nav_item is not None:
            href_match = re.fullmatch(r"      href:(?:[ ]+(.*))?", raw)
            if not href_match or href_match.group(1) is None:
                raise fail(path, number, "navbar item property must be 'href: #anchor'")
            if "href" in current_nav_item:
                raise fail(path, number, "duplicate navbar item href")
            current_nav_item["href"] = parse_scalar(href_match.group(1), path, number)
            continue
        if indent == 2 and block == "cards":
            card_match = re.fullmatch(r"  - title:(?:[ ]+(.*))?", raw)
            if not card_match or card_match.group(1) is None:
                raise fail(path, number, "cards must start with '- title: text'")
            current_card = {"title": parse_scalar(card_match.group(1), path, number)}
            cards = page["cards"]
            assert isinstance(cards, list)
            cards.append(current_card)
            continue
        if indent == 4 and block == "cards" and current_card is not None:
            card_match = re.fullmatch(r"    text:(?:[ ]+(.*))?", raw)
            if not card_match or card_match.group(1) is None:
                raise fail(path, number, "card property must be 'text: description'")
            if "text" in current_card:
                raise fail(path, number, "duplicate card text")
            current_card["text"] = parse_scalar(card_match.group(1), path, number)
            continue
        if indent == 2 and block == "references":
            reference_match = re.fullmatch(r"  - title:(?:[ ]+(.*))?", raw)
            if not reference_match or reference_match.group(1) is None:
                raise fail(path, number, "references must start with '- title: text'")
            current_reference = {"title": parse_scalar(reference_match.group(1), path, number)}
            refs = page["references"]
            assert isinstance(refs, list)
            refs.append(current_reference)
            continue
        if indent == 4 and block == "references" and current_reference is not None:
            reference_match = re.fullmatch(r"    href:(?:[ ]+(.*))?", raw)
            if not reference_match or reference_match.group(1) is None:
                raise fail(path, number, "reference property must be 'href: https://…'")
            if "href" in current_reference:
                raise fail(path, number, "duplicate reference href")
            current_reference["href"] = parse_scalar(reference_match.group(1), path, number)
            continue

        match = re.fullmatch(r"( *)([A-Za-z][A-Za-z0-9_-]*):(?:[ ]+(.*))?", raw)
        if not match:
            raise fail(path, number, "expected 'key: value', a block key, or a navbar item")
        spaces, key, raw_value = match.groups()
        indent = len(spaces)
        if indent == 0:
            block = None
            nav_items_open = False
            current_nav_item = None
            if key in seen_top:
                raise fail(path, number, f"duplicate key '{key}'")
            seen_top.add(key)
            if key not in {"page", "layout", "max_width", "theme", "hero", "navbar", "style", "feature", "cards", "cards_heading", "references"}:
                raise fail(path, number, f"unknown page key '{key}'")
            if key in {"hero", "navbar", "style", "feature", "cards", "references"}:
                if raw_value is not None:
                    raise fail(path, number, f"'{key}' must be a mapping block")
                block = key
                if key == "feature":
                    page[key] = {}
                if key == "cards":
                    page[key] = []
                if key == "references":
                    page[key] = []
                current_card = None
                current_reference = None
            else:
                if raw_value is None:
                    raise fail(path, number, f"'{key}' must have a text value")
                page[key] = parse_scalar(raw_value, path, number)
        elif indent == 2 and block == "hero":
            hero = page["hero"]
            assert isinstance(hero, dict)
            if key in seen_hero:
                raise fail(path, number, f"duplicate hero key '{key}'")
            seen_hero.add(key)
            if key not in {"title", "subtitle", "button", "button_href", "image", "image_alt"}:
                raise fail(path, number, f"unknown hero key '{key}'")
            if raw_value is None:
                raise fail(path, number, f"'hero.{key}' must have a text value")
            hero[key] = parse_scalar(raw_value, path, number)
        elif indent == 2 and block == "navbar":
            if key in seen_nav:
                raise fail(path, number, f"duplicate navbar key '{key}'")
            seen_nav.add(key)
            if key == "brand":
                if raw_value is None:
                    raise fail(path, number, "'navbar.brand' must have a text value")
                nav = page["navbar"]
                assert isinstance(nav, dict)
                nav["brand"] = parse_scalar(raw_value, path, number)
            elif key == "items":
                if raw_value is not None:
                    raise fail(path, number, "'navbar.items' must be a list block")
                nav_items_open = True
                current_nav_item = None
            else:
                raise fail(path, number, f"unknown navbar key '{key}'")
        elif indent == 2 and block == "style":
            if key in seen_style:
                raise fail(path, number, f"duplicate style setting '{key}'")
            seen_style.add(key)
            if raw_value is None:
                raise fail(path, number, f"'style.{key}' must have a value")
            style = page["style"]
            assert isinstance(style, dict)
            style[key] = parse_scalar(raw_value, path, number)
        elif indent == 2 and block == "feature":
            if key in seen_feature:
                raise fail(path, number, f"duplicate feature key '{key}'")
            seen_feature.add(key)
            if key not in {"title", "text", "image", "image_alt", "id"}:
                raise fail(path, number, f"unknown feature key '{key}'")
            if raw_value is None:
                raise fail(path, number, f"'feature.{key}' must have a value")
            feature = page["feature"]
            assert isinstance(feature, dict)
            feature[key] = parse_scalar(raw_value, path, number)
        else:
            raise fail(path, number, "invalid indentation or property for this block")

    for required in ("page", "hero"):
        if required not in seen_top:
            raise fail(path, 1, f"missing required key '{required}'")
    hero = page["hero"]
    assert isinstance(hero, dict)
    for required in ("title", "button"):
        if required not in hero:
            raise fail(path, 1, f"missing required key 'hero.{required}'")
    layout = page.get("layout", "container")
    if layout not in {"container", "centered", "wide"}:
        line = next((i for i, row in enumerate(lines, 1) if row.startswith("layout:")), 1)
        raise fail(path, line, f"unsupported layout '{layout}' (choose container, centered, or wide)")
    theme = page.get("theme", "light")
    if theme not in {"light", "blue-dark"}:
        line = next((i for i, row in enumerate(lines, 1) if row.startswith("theme:")), 1)
        raise fail(path, line, f"unsupported theme '{theme}' (choose light or blue-dark)")
    page["layout"] = layout
    page["theme"] = theme
    style = page["style"]
    assert isinstance(style, dict)
    try:
        page["style"] = normalize_style(style, str(theme))
    except ValueError as error:
        line = next((i for i, row in enumerate(lines, 1) if row.startswith("style:")), 1)
        raise fail(path, line, str(error)) from error
    page["has_navbar"] = "navbar" in seen_top
    max_width = page.get("max_width", "1080px")
    width_match = re.fullmatch(r"([0-9]{3,4})px", str(max_width))
    if not width_match or not 100 <= int(width_match.group(1)) <= 9999:
        line = next((i for i, row in enumerate(lines, 1) if row.startswith("max_width:")), 1)
        raise fail(path, line, "max_width must be a pixel value from 100px to 9999px")
    page["max_width"] = max_width
    if "navbar" in seen_top:
        nav = page["navbar"]
        assert isinstance(nav, dict)
        if "brand" not in nav:
            raise fail(path, 1, "missing required key 'navbar.brand'")
        items = nav["items"]
        assert isinstance(items, list)
        if not items:
            raise fail(path, 1, "navbar.items must contain at least one item")
        for index, item in enumerate(items, 1):
            if "href" not in item:
                raise fail(path, 1, f"navbar item {index} is missing href")
            if not re.fullmatch(r"#[A-Za-z][A-Za-z0-9_-]*", item["href"]):
                raise fail(path, 1, f"navbar item {index} href must be an in-page #anchor")
    hero_image = hero.get("image")
    if hero_image and not hero.get("image_alt"):
        raise fail(path, 1, "hero.image requires hero.image_alt")
    if "button_href" in hero and not re.fullmatch(r"#[A-Za-z][A-Za-z0-9_-]*", hero["button_href"]):
        raise fail(path, 1, "hero.button_href must be an in-page #anchor")
    for image in [hero_image, (page.get("feature") or {}).get("image")]:
        if image:
            ref = Path(image)
            if ref.is_absolute() or ":" in image or "\\" in image:
                raise fail(path, 1, "image paths must be local project-relative paths")
            resolved = (PROBLEM_DIR / "output" / ref).resolve()
            if not resolved.is_relative_to(PROBLEM_DIR) or not resolved.is_file():
                raise fail(path, 1, f"image asset does not exist inside the problem folder: {image}")
    feature = page.get("feature")
    if feature:
        assert isinstance(feature, dict)
        for required in ("title", "text"):
            if not feature.get(required):
                raise fail(path, 1, f"feature.{required} is required")
        if "id" in feature and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", feature["id"]):
            raise fail(path, 1, "feature.id must be a simple HTML id")
        if feature.get("image") and not feature.get("image_alt"):
            raise fail(path, 1, "feature.image requires feature.image_alt")
    cards = page["cards"]
    assert isinstance(cards, list)
    for index, card in enumerate(cards, 1):
        if "text" not in card:
            raise fail(path, 1, f"card {index} is missing text")
    references = page["references"]
    assert isinstance(references, list)
    for index, reference in enumerate(references, 1):
        if not re.fullmatch(r"https://[^\s\"']+", reference.get("href", "")):
            raise fail(path, 1, f"reference {index} needs an https URL")
    return page


def render(page: dict[str, object]) -> str:
    hero = page["hero"]
    assert isinstance(hero, dict)
    layout_class = "container text-center" if page["layout"] == "centered" else "container"
    shell = 'container-fluid px-3 px-sm-4 recursion-shell' if page["layout"] == "wide" else layout_class
    is_dark = page["theme"] == "blue-dark"
    html_theme = ' data-bs-theme="dark"' if is_dark else ""
    theme_style = render_design_css(page["style"])
    if page["layout"] == "wide":
        theme_style = theme_style.replace(
            "  </style>",
            f'    .recursion-shell {{ max-width: {page["max_width"]}; margin-inline: auto; }}\n  </style>',
        )
    esc = lambda value: html.escape(str(value), quote=True)
    subtitle = ""
    if "subtitle" in hero:
        subtitle = f'\n      <p class="lead mb-4">{esc(hero["subtitle"])}</p>'
    button_href = esc(hero.get("button_href", "#method"))
    hero_copy = f'''<div class="site-hero-copy">
      <h1 class="display-5 fw-bold mb-3">{esc(hero["title"])}</h1>{subtitle}
      <a class="btn btn-primary btn-lg" href="{button_href}">{esc(hero["button"])}</a>
    </div>'''
    hero_image = (
        f'<img class="site-photo" src="{esc(hero["image"])}" alt="{esc(hero["image_alt"])}" fetchpriority="high">'
        if hero.get("image")
        else ""
    )
    hero_class = "site-hero has-image" if hero_image else "site-hero"
    hero_content = f'{hero_copy}\n    {hero_image}' if hero_image else hero_copy
    cards = page["cards"]
    assert isinstance(cards, list)
    cards_html = ""
    if cards:
        items = "\n".join(
            f'        <div class="col"><article class="site-card"><div class="card-body"><h3 class="h5 card-title">{esc(card["title"])}</h3><p class="mb-0 mt-2">{esc(card["text"])}</p></div></article></div>'
            for card in cards
        )
        cards_html = f'''\n    <section id="method" class="py-4" aria-labelledby="cards-heading">
      <h2 id="cards-heading" class="h2 mb-4">{esc(page.get("cards_heading", "A few things to know"))}</h2>
      <div class="row row-cols-1 row-cols-md-3 g-3">
{items}
      </div>
    </section>'''
    feature_html = ""
    feature = page.get("feature")
    if feature:
        assert isinstance(feature, dict)
        feature_image = (
            f'<img class="site-photo" src="{esc(feature["image"])}" alt="{esc(feature["image_alt"])}" loading="lazy">'
            if feature.get("image")
            else ""
        )
        feature_text = f'''<div class="site-feature-copy">
        <h2>{esc(feature["title"])}</h2>
        <p>{esc(feature["text"])}</p>
      </div>'''
        feature_content = f'{feature_image}\n      {feature_text}' if feature_image else feature_text
        feature_html = f'\n    <section id="{esc(feature.get("id", "feature"))}" class="site-feature" aria-label="{esc(feature["title"])}">\n      {feature_content}\n    </section>'
    references = page["references"]
    assert isinstance(references, list)
    references_html = ""
    if references:
        links = "\n".join(
            f'        <li><a href="{esc(reference["href"])}">{esc(reference["title"])}</a></li>'
            for reference in references
        )
        references_html = f'''\n    <footer class="site-references" aria-labelledby="references-heading">
      <h2 id="references-heading" class="h5">Further reading</h2>
      <ul class="mb-0">\n{links}\n      </ul>
    </footer>'''
    navbar = ""
    if page["has_navbar"]:
        nav = page["navbar"]
        assert isinstance(nav, dict)
        links = "\n".join(
            f'          <li class="nav-item"><a class="nav-link" href="{esc(item["href"])}">{esc(item["label"])}</a></li>'
            for item in nav["items"]
        )
        navbar = f'''  <nav class="navbar navbar-expand-lg bg-primary" data-bs-theme="dark" aria-label="Main navigation">
    <div class="{shell}">
      <a class="navbar-brand" href="#home">{esc(nav["brand"])}</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#siteNavigation" aria-controls="siteNavigation" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse justify-content-end" id="siteNavigation">
        <ul class="navbar-nav gap-lg-2">
{links}
        </ul>
      </div>
    </div>
  </nav>
'''
    bootstrap_js = (
        '  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" '
        'integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" '
        'crossorigin="anonymous"></script>'
        if page["has_navbar"]
        else ""
    )
    hero_id = "start" if navbar else "home"
    shell_open = f'<main id="home" class="{shell} py-4 py-lg-5">'
    return f'''<!doctype html>
<html lang="en"{html_theme}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page["page"])}</title>
  <link href="{BOOTSTRAP_CSS}" rel="stylesheet" integrity="{BOOTSTRAP_CSS_SRI}" crossorigin="anonymous">
{theme_style}
</head>
<body class="site-page">
{navbar}  {shell_open}
    <section id="{hero_id}" class="{hero_class} py-4 py-md-5">
      {hero_content}
    </section>{cards_html}{feature_html}{references_html}
  </main>
{bootstrap_js}
</body>
</html>
'''


def main(args: list[str]) -> int:
    if len(args) not in {0, 2}:
        print("usage: build_page.py [input.yaml output.html]", file=sys.stderr)
        return 2
    source = Path(args[0]).resolve() if args else DEFAULT_INPUT
    target = Path(args[1]).resolve() if args else DEFAULT_OUTPUT
    try:
        result = render(parse_page(source))
    except (OSError, UnicodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result, encoding="utf-8", newline="\n")
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
