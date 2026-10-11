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
- `theme`: optional; `light` is the default and `blue-dark` selects Bootstrap dark mode with a primary-blue navbar.
- `layout: wide` enables a fluid responsive shell; `max_width` sets its desktop maximum in pixels (defaults to `1080px`).
- `navbar`: optional mapping with a required `brand` and an `items` list. Each item has a `label` and same-page `href` such as `#home`.
- All values are text. Quote a value when YAML punctuation or special characters require it.
- Any other key, duplicate key, invalid indentation, missing required value, or unsupported layout stops generation with a line-specific error.

The responsive blue-dark example is fully specified in [`source/site-theme.yaml`](source/site-theme.yaml).

## Translation rules

The generator implements the small operator-brief schema above plus an optional responsive navbar and blue-dark wide theme. The larger site syntax in `source/breakfast-blaster.rec` is inventoried below as the planned mapping; it is not accepted by `build_page.py` yet. Keeping that boundary explicit lets the generator reject unsupported input instead of silently dropping content.

### Implemented YAML subset

| YAML field/value | Generated HTML |
| --- | --- |
| `page` | Escaped `<title>` text |
| `layout: container` | `<main class="container">` |
| `layout: centered` | `<main class="container text-center">` |
| `hero.title` | Escaped `<h1>` text |
| `hero.subtitle` | Optional escaped `<p class="lead">` |
| `hero.button` | Escaped `<button type="button" class="btn btn-primary">` |
| `theme: blue-dark` | `data-bs-theme="dark"` on `<html>` and primary-blue navbar |
| `layout: wide`, `max_width: 1080px` | Fluid Bootstrap shell with a custom 1080px maximum width and centered margins |
| `navbar.brand` | Escaped `.navbar-brand` text linking to `#home` |
| `navbar.items[]` | Escaped `.nav-link` anchors within a responsive `.navbar-expand-lg` navigation |
| Wide layout spacing | Bootstrap `px-3 px-sm-4`, `py-4 py-lg-5`, and `py-4 py-md-5` responsive spacing utilities |

### Implemented `.rec` site mapping

| Recursion syntax | YAML meaning | Planned Bootstrap HTML |
| --- | --- | --- |
| `site "Name"` | `site: Name` | Document `<title>` text |
| `theme: arcade` | `theme: arcade` | `data-theme="arcade"` on the body and a matching `theme-arcade` class |
| `layout: centered` | `layout: centered` | `.container.text-center` main wrapper |
| `layout: container` | `layout: container` | `.container` main wrapper |
| `hero:` | `hero:` mapping | Semantic `<header>` with responsive spacing inside main |
| `title` | `hero.title` | Escaped `<h1>` |
| `subtitle` | `hero.subtitle` | Escaped `<p class="lead">` |
| `button` | `hero.button` | Escaped primary Bootstrap button |
| `section "Name"` | Item in `sections` with `title: Name` | `<section>` with an `<h2>` |
| `card "Name"` | Item in that section's `cards` list | Bootstrap card inside a responsive row and column |

`tools/compile_site.py` implements this mapping for the current syntax in `source/breakfast-blaster.rec`. It accepts `light`, `arcade`, and `blue-dark` themes and `centered` or `container` layouts. It rejects unknown statements and invalid indentation rather than silently dropping input.

Theme names such as `arcade` remain data values. The compiler must escape all user-provided text and validate theme and layout choices before emitting attributes or classes.

The output is a complete HTML5 page with English language metadata, UTF-8, responsive viewport metadata, and pinned Bootstrap 5.3.8 CSS and JavaScript CDN links with Subresource Integrity. Pages without a navbar do not need the JavaScript bundle. Bootstrap styling and navbar behavior require the CDN to be reachable or the assets to be replaced with local copies. The CDN version and integrity values follow the [official Bootstrap 5.3 quick start](https://getbootstrap.com/docs/5.3/getting-started/introduction/); the `.container` and `.btn` classes follow the official [containers](https://getbootstrap.com/docs/5.3/layout/containers/) and [buttons](https://getbootstrap.com/docs/5.3/components/buttons/) documentation.

The blue-dark page uses Bootstrap's `data-bs-theme="dark"` color mode, `.bg-primary`, and responsive navbar collapse behavior. The 1080px shell is its only custom width rule; its padding, navigation, button, and spacing use Bootstrap classes. These choices follow the official [navbar](https://getbootstrap.com/docs/5.3/components/navbar/), [color modes](https://getbootstrap.com/docs/5.3/customize/color-modes/), and [spacing utilities](https://getbootstrap.com/docs/5.3/utilities/spacing/) documentation.

## Run locally

From the repository root:

```text
python Recursion/problems/bootstrap-language/tools/build_page.py
```

The command reads `source/operator-brief.yaml` and writes `output/operator-brief.html`. Pass input and output paths to process another page:

```text
python Recursion/problems/bootstrap-language/tools/build_page.py input.yaml output.html
```

Compile the Recursion site example from the repository root:

```text
python Recursion/problems/bootstrap-language/tools/compile_site.py
```

This reads `source/breakfast-blaster.rec` and writes `output/breakfast-blaster.html`. Pass input and output paths to compile another `.rec` file:

```text
python Recursion/problems/bootstrap-language/tools/compile_site.py input.rec output.html
```
