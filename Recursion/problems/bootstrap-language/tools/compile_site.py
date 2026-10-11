#!/usr/bin/env python3
"""Compile the documented Recursion site syntax to a standalone Bootstrap page."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


PROBLEM_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROBLEM_DIR / "source" / "breakfast-blaster.rec"
DEFAULT_OUTPUT = PROBLEM_DIR / "output" / "breakfast-blaster.html"
BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
BOOTSTRAP_CSS_SRI = "sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"


def error(path: Path, line: int, message: str) -> ValueError:
    return ValueError(f"{path}:{line}: {message}")


def quoted(value: str, path: Path, line: int) -> str:
    match = re.fullmatch(r'"((?:[^"\\]|\\["\\])*)"', value)
    if not match:
        raise error(path, line, 'expected a quoted string (escape " and \\ with \\)')
    return match.group(1).replace('\\"', '"').replace('\\\\', '\\')


def parse(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    site: dict[str, object] = {"sections": []}
    hero: dict[str, str] = {}
    seen: set[str] = set()
    section: dict[str, object] | None = None
    in_hero = False
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        if "\t" in raw:
            raise error(path, number, "tabs are not allowed for indentation")
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()
        if indent and "site" not in seen:
            raise error(path, number, 'the site declaration must come first: site "Name"')
        if indent == 0:
            match = re.fullmatch(r"site (.+)", text)
            if not match or "site" in seen:
                raise error(path, number, 'expected one site declaration: site "Name"')
            site["title"] = quoted(match.group(1), path, number)
            seen.add("site")
            section = None
            in_hero = False
        elif indent == 2:
            match = re.fullmatch(r"(theme|layout): (.+)", text)
            section_match = re.fullmatch(r"section (.+)", text)
            if match:
                key, value = match.groups()
                if key in seen:
                    raise error(path, number, f"duplicate {key}")
                if key == "theme":
                    site["theme"] = (
                        quoted(value, path, number)
                        if value.startswith('"')
                        else value
                    )
                else:
                    if value not in {"centered", "container"}:
                        raise error(path, number, "layout must be centered or container")
                    site["layout"] = value
                seen.add(key)
                section = None
                in_hero = False
            elif text == "hero:" and "hero" not in seen:
                seen.add("hero")
                in_hero = True
                section = None
            elif section_match:
                section = {"title": quoted(section_match.group(1), path, number), "cards": []}
                sections = site["sections"]
                assert isinstance(sections, list)
                sections.append(section)
                in_hero = False
            else:
                raise error(path, number, "expected theme, layout, hero, or section")
        elif indent == 4 and in_hero:
            match = re.fullmatch(r"(title|subtitle|button): (.+)", text)
            if not match:
                raise error(path, number, "expected hero title, subtitle, or button")
            key, value = match.groups()
            if key in hero:
                raise error(path, number, f"duplicate hero {key}")
            hero[key] = quoted(value, path, number)
        elif indent == 4 and section is not None:
            match = re.fullmatch(r"card (.+)", text)
            if not match:
                raise error(path, number, 'expected card "Name"')
            cards = section["cards"]
            assert isinstance(cards, list)
            cards.append(quoted(match.group(1), path, number))
        else:
            raise error(path, number, "unexpected indentation or statement")

    if "site" not in seen:
        raise error(path, 1, 'missing site declaration: site "Name"')
    if "hero" not in seen:
        raise error(path, 1, "missing hero block")
    for key in ("title", "button"):
        if key not in hero:
            raise error(path, 1, f"missing hero {key}")
    theme = site.get("theme", "light")
    if theme not in {"light", "arcade", "blue-dark"}:
        line = next((n for n, row in enumerate(lines, 1) if row.strip().startswith("theme:")), 1)
        raise error(path, line, f"unsupported theme {theme!r}")
    site["theme"] = theme
    site["layout"] = site.get("layout", "container")
    site["hero"] = hero
    return site


def render(site: dict[str, object]) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    hero = site["hero"]
    assert isinstance(hero, dict)
    layout = "container text-center" if site["layout"] == "centered" else "container"
    theme = str(site["theme"])
    body_attrs = (
        ' data-theme="arcade" class="theme-arcade"'
        if theme == "arcade"
        else f' class="{esc(theme)}"'
    )
    theme_attr = ' data-bs-theme="dark"' if theme == "blue-dark" else ""
    subtitle = f'\n      <p class="lead mb-4">{esc(hero["subtitle"])}</p>' if "subtitle" in hero else ""
    sections = []
    for entry in site["sections"]:
        assert isinstance(entry, dict)
        cards = "\n".join(
            f'        <div class="col"><article class="card h-100"><div class="card-body"><h3 class="h5 card-title">{esc(name)}</h3></div></article></div>'
            for name in entry["cards"]
        )
        sections.append(
            f'    <section class="py-4" aria-labelledby="section-{len(sections) + 1}">\n'
            f'      <h2 id="section-{len(sections) + 1}" class="h3 mb-3">{esc(entry["title"])}</h2>\n'
            f'      <div class="row row-cols-1 row-cols-md-3 g-3">\n{cards}\n      </div>\n    </section>'
        )
    extra = "\n".join(sections)
    if extra:
        extra = "\n" + extra
    return f'''<!doctype html>
<html lang="en"{theme_attr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(site["title"])}</title>
  <link href="{BOOTSTRAP_CSS}" rel="stylesheet" integrity="{BOOTSTRAP_CSS_SRI}" crossorigin="anonymous">
</head>
<body{body_attrs}>
  <main class="{layout} py-4 py-lg-5">
    <header class="py-4 py-md-5">
      <h1 class="display-5 fw-bold mb-3">{esc(hero["title"])}</h1>{subtitle}
      <button type="button" class="btn btn-primary btn-lg">{esc(hero["button"])}</button>
    </header>{extra}
  </main>
</body>
</html>
'''


def main(args: list[str]) -> int:
    if len(args) not in {0, 2}:
        print("usage: compile_site.py [input.rec output.html]", file=sys.stderr)
        return 2
    source = Path(args[0]).resolve() if args else DEFAULT_INPUT
    target = Path(args[1]).resolve() if args else DEFAULT_OUTPUT
    try:
        output = render(parse(source))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8", newline="\n")
    except (OSError, UnicodeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
