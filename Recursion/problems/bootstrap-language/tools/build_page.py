#!/usr/bin/env python3
"""Build one static Bootstrap page from Recursion's supported YAML subset."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


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
    page: dict[str, object] = {"hero": {}}
    seen_top: set[str] = set()
    seen_hero: set[str] = set()
    in_hero = False

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise fail(path, number, "tabs are not allowed for indentation")
        match = re.fullmatch(r"( *)([A-Za-z][A-Za-z0-9_-]*):(?:[ ]+(.*))?", raw)
        if not match:
            raise fail(path, number, "expected 'key: value' or a block key followed by ':'")
        spaces, key, raw_value = match.groups()
        indent = len(spaces)
        if indent == 0:
            in_hero = False
            if key in seen_top:
                raise fail(path, number, f"duplicate key '{key}'")
            seen_top.add(key)
            if key not in {"page", "layout", "hero"}:
                raise fail(path, number, f"unknown page key '{key}'")
            if key == "hero":
                if raw_value is not None:
                    raise fail(path, number, "hero must be a mapping block")
                in_hero = True
            else:
                if raw_value is None:
                    raise fail(path, number, f"'{key}' must have a text value")
                page[key] = parse_scalar(raw_value, path, number)
        elif indent == 2 and in_hero:
            hero = page["hero"]
            assert isinstance(hero, dict)
            if key in seen_hero:
                raise fail(path, number, f"duplicate hero key '{key}'")
            seen_hero.add(key)
            if key not in {"title", "subtitle", "button"}:
                raise fail(path, number, f"unknown hero key '{key}'")
            if raw_value is None:
                raise fail(path, number, f"'hero.{key}' must have a text value")
            hero[key] = parse_scalar(raw_value, path, number)
        else:
            raise fail(path, number, "only hero properties may be indented by two spaces")

    for required in ("page", "hero"):
        if required not in seen_top:
            raise fail(path, 1, f"missing required key '{required}'")
    hero = page["hero"]
    assert isinstance(hero, dict)
    for required in ("title", "button"):
        if required not in hero:
            raise fail(path, 1, f"missing required key 'hero.{required}'")
    layout = page.get("layout", "container")
    if layout not in {"container", "centered"}:
        line = next((i for i, row in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if row.startswith("layout:")), 1)
        raise fail(path, line, f"unsupported layout '{layout}' (choose container or centered)")
    page["layout"] = layout
    return page


def render(page: dict[str, object]) -> str:
    hero = page["hero"]
    assert isinstance(hero, dict)
    layout_class = "container text-center" if page["layout"] == "centered" else "container"
    esc = lambda value: html.escape(str(value), quote=True)
    subtitle = ""
    if "subtitle" in hero:
        subtitle = f'\n    <p class="lead">{esc(hero["subtitle"])}</p>'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page["page"])}</title>
  <link href="{BOOTSTRAP_CSS}" rel="stylesheet" integrity="{BOOTSTRAP_CSS_SRI}" crossorigin="anonymous">
</head>
<body>
  <main class="{layout_class}">
    <h1>{esc(hero["title"])}</h1>{subtitle}
    <button type="button" class="btn btn-primary">{esc(hero["button"])}</button>
  </main>
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
