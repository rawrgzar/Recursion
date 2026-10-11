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
- `hero.image` and `hero.image_alt`: optional local image and descriptive alt text; `button_href` may point to an in-page anchor.
- `cards_heading` and `cards`: optional heading and list of titled information cards with short text.
- `feature`: optional image-led information section with a title, text, and optional image/alt text.
- `references`: optional list of titled HTTPS links rendered as further reading.
- `theme`: optional; `light` is the default and `blue-dark` selects Bootstrap dark mode with a primary-blue navbar.
- `style`: optional visual tokens for background, surface, text, muted text, accent colors, hero gradient colors, and corner radius. Neutral light or dark defaults are used for unspecified values. Each color accepts a six-digit hex value; radius accepts pixels.
- `layout: wide` enables a fluid responsive shell; `max_width` sets its desktop maximum in pixels (defaults to `1080px`).
- `navbar`: optional mapping with a required `brand` and an `items` list. Each item has a `label` and same-page `href` such as `#home`.
- All values are text. Quote a value when YAML punctuation or special characters require it.
- Any other key, duplicate key, invalid indentation, missing required value, or unsupported layout stops generation with a line-specific error.

The responsive blue-dark example is fully specified in [`source/site-theme.yaml`](source/site-theme.yaml).

## Translation rules

The YAML generator implements the small operator-brief schema above plus an optional responsive navbar, theme mode, wide layout, and configurable design tokens. The separate `.rec` compiler implements the larger site syntax below.

### Implemented YAML subset

| YAML field/value | Generated HTML |
| --- | --- |
| `page` | Escaped `<title>` text |
| `layout: container` | `<main class="container">` |
| `layout: centered` | `<main class="container text-center">` |
| `hero.title` | Escaped `<h1>` text |
| `hero.subtitle` | Optional escaped `<p class="lead">` |
| `hero.button` | Escaped `<button type="button" class="btn btn-primary">` |
| `theme: blue-dark` | `data-bs-theme="dark"` on `<html>` |
| `style` | CSS design tokens used by the shared page, hero, button, and card styles |
| `layout: wide`, `max_width: 1080px` | Fluid Bootstrap shell with a custom 1080px maximum width and centered margins |
| `navbar.brand` | Escaped `.navbar-brand` text linking to `#home` |
| `navbar.items[]` | Escaped `.nav-link` anchors within a responsive `.navbar-expand-lg` navigation |
| `hero.image` / `feature.image` | Responsive locally referenced images with required descriptive alt text |
| `cards[]` | Responsive grid of escaped information cards |
| `references[]` | Escaped, clickable further-reading links |
| Wide layout spacing | Bootstrap `px-3 px-sm-4`, `py-4 py-lg-5`, and `py-4 py-md-5` responsive spacing utilities |

### Implemented `.rec` site mapping

| Recursion syntax | YAML meaning | Planned Bootstrap HTML |
| --- | --- | --- |
| `site "Name"` | `site: Name` | Document `<title>` text |
| `style:` and its color/shape properties | CSS design tokens | Shared layout styling uses the supplied palette and radius; the compiler does not infer a style from the site's subject |
| `layout: centered` | `layout: centered` | `.container.text-center` main wrapper |
| `layout: container` | `layout: container` | `.container` main wrapper |
| `hero:` | `hero:` mapping | Semantic `<header>` with responsive spacing inside main |
| `title` | `hero.title` | Escaped `<h1>` |
| `subtitle` | `hero.subtitle` | Escaped `<p class="lead">` |
| `button` | `hero.button` | Escaped primary Bootstrap button |
| `section "Name"` | Item in `sections` with `title: Name` | `<section>` with an `<h2>` |
| `card "Name"` | Item in that section's `cards` list | Bootstrap card inside a responsive row and column |

`tools/compile_site.py` implements this mapping for the current syntax in `source/breakfast-blaster.rec`. It accepts `light` and `blue-dark` base modes and `centered` or `container` layouts. The visual design comes from the optional style settings in the source; without them, a neutral palette is used. It rejects unknown statements and invalid indentation rather than silently dropping input.

`source/pancake-guide.yaml` demonstrates the extended YAML content schema with locally stored photos in `assets/`, technique cards, an image-led section, and source links. Rebuild it from the repository root with:

```text
python Recursion/problems/bootstrap-language/tools/build_page.py Recursion/problems/bootstrap-language/source/pancake-guide.yaml Recursion/problems/bootstrap-language/output/pancake-guide.html
```

The compiler escapes user-provided text and validates theme, layout, color, and radius values before emitting attributes, classes, or CSS.

The output is a complete HTML5 page with English language metadata, UTF-8, responsive viewport metadata, and pinned Bootstrap 5.3.8 CSS and JavaScript CDN links with Subresource Integrity. Pages without a navbar do not need the JavaScript bundle. Bootstrap styling and navbar behavior require the CDN to be reachable or the assets to be replaced with local copies. The CDN version and integrity values follow the [official Bootstrap 5.3 quick start](https://getbootstrap.com/docs/5.3/getting-started/introduction/); the `.container` and `.btn` classes follow the official [containers](https://getbootstrap.com/docs/5.3/layout/containers/) and [buttons](https://getbootstrap.com/docs/5.3/components/buttons/) documentation.

The blue-dark page uses Bootstrap's `data-bs-theme="dark"` color mode. Responsive layout and navbar behavior use Bootstrap classes; the shared design tokens control page-specific colors and corner radius. These choices follow the official [navbar](https://getbootstrap.com/docs/5.3/components/navbar/), [color modes](https://getbootstrap.com/docs/5.3/customize/color-modes/), and [spacing utilities](https://getbootstrap.com/docs/5.3/utilities/spacing/) documentation.

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
