# YAML to Bootstrap HTML mapping

The first generator accepts a deliberately small YAML subset, not arbitrary YAML. It uses only Python's standard library and has no network or package-install step. Unknown keys and unsupported values are errors so a typo cannot silently produce a different page.

## Supported schema

```yaml
page: Breakfast Blaster
layout: container
hero:
  title: Ready for breakfast?
  button: Start Game
```

- `page`: required, non-empty text used for the document title.
- `layout`: optional; `container` maps to Bootstrap `.container`, and `centered` maps to `.container.text-center`.
- `hero`: required mapping containing `title` and `button`; `subtitle` is optional.
- All values are text. Quote a value when YAML punctuation or special characters require it.
- Any other key, duplicate key, invalid indentation, missing required value, or unsupported layout stops generation with a line-specific error.

## Translation rules

The initial generator implements the small operator-brief schema above. The larger site syntax in `source/breakfast-blaster.rec` is inventoried below as the planned mapping; it is not accepted by `build_page.py` yet. Keeping that boundary explicit lets the generator reject unsupported input instead of silently dropping content.

### Implemented YAML subset

| YAML field/value | Generated HTML |
| --- | --- |
| `page` | Escaped `<title>` text |
| `layout: container` | `<main class="container">` |
| `layout: centered` | `<main class="container text-center">` |
| `hero.title` | Escaped `<h1>` text |
| `hero.subtitle` | Optional escaped `<p class="lead">` |
| `hero.button` | Escaped `<button type="button" class="btn btn-primary">` |

### Planned full-site mapping

| Recursion syntax | YAML meaning | Planned Bootstrap HTML |
| --- | --- | --- |
| `site "Name"` | `site: Name` | Document `<title>` and visible site heading |
| `theme: arcade` | `theme: arcade` | `data-theme="arcade"` on the body and a matching `theme-arcade` class for optional project CSS |
| `layout: centered` | `layout: centered` | `.container.text-center` main wrapper |
| `layout: container` | `layout: container` | `.container` main wrapper |
| `hero:` | `hero:` mapping | Semantic `<header class="py-5">` inside main |
| `title` | `hero.title` | Escaped `<h1>` |
| `subtitle` | `hero.subtitle` | Escaped `<p class="lead">` |
| `button` | `hero.button` | Escaped primary Bootstrap button |
| `section "Name"` | Item in `sections` with `title: Name` | `<section>` with an `<h2>` |
| `card "Name"` | Item in that section's `cards` list | Bootstrap card inside a responsive row and column |

Theme names such as `arcade` remain data values. The compiler must escape all user-provided text and validate theme and layout choices before emitting attributes or classes.

The output is a complete HTML5 page with English language metadata, UTF-8, responsive viewport metadata, and a pinned Bootstrap 5.3.8 CSS CDN link with Subresource Integrity. No Bootstrap JavaScript is included because this first schema has no interactive components. The page works offline as a static HTML document, but Bootstrap styling requires the CSS CDN to be reachable or replaced with a local copy. The CDN version and integrity value follow the [official Bootstrap 5.3 quick start](https://getbootstrap.com/docs/5.3/getting-started/introduction/); the `.container` and `.btn` classes follow the official [containers](https://getbootstrap.com/docs/5.3/layout/containers/) and [buttons](https://getbootstrap.com/docs/5.3/components/buttons/) documentation.

## Run locally

From the repository root:

```text
python Recursion/problems/bootstrap-language/tools/build_page.py
```

The command reads `source/operator-brief.yaml` and writes `output/operator-brief.html`. Pass input and output paths to process another page:

```text
python Recursion/problems/bootstrap-language/tools/build_page.py input.yaml output.html
```
