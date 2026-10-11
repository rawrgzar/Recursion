# Bootstrap-language handoff

## Context

The bootstrap target is a local generator that turns a small, explicit YAML page description into a complete static HTML page using Bootstrap. The operator's plain-language request is `source/operator-brief.txt`; its normalized YAML is `source/operator-brief.yaml`. `source/site-theme.yaml` exercises a blue dark theme, responsive top navigation, mobile spacing, and a 1080px maximum desktop shell. The separate `source/breakfast-blaster.rec` demonstrates the broader YAML-like Recursion site syntax.

## Stages

1. **Discover and normalize:** read operator intent and express the page using the supported YAML schema. Natural-language interpretation remains an operator/agent step; the generator does not guess intent.
2. **Generate:** `tools/build_page.py` validates the schema and writes a complete static page with escaped content, responsive Bootstrap layout, optional collapsible navbar, heading, and primary button.
3. **Bootstrap proof:** a future compiler stage must generate the next stage and rebuild the agreed target. Record commands, outputs, and a repeatable comparison here when implemented.

The first `.rec` compiler is `tools/compile_site.py`. It implements the current `site`, `theme`, `layout`, `hero`, `section`, and `card` example syntax and emits standalone Bootstrap HTML. It is a Python stage-zero compiler; it does not yet generate or rebuild itself.

## Syntax inventory

The current Recursion example uses reserved syntax words `site`, `theme`, `layout`, `style`, `hero`, `title`, `subtitle`, `button`, `section`, and `card`. `print` is reserved for the cold-start smoke program. The normalized YAML page schema also reserves `page`, `max_width`, `navbar`, `brand`, `items`, `label`, `href`, and the style design-token names. Theme names such as `blue-dark` and layout values such as `centered`, `container`, and `wide` are data values, as are display strings such as `Breakfast Blaster` and `Start Game`.

See `../../language/reserved-words.yaml`, `../../language/grammar.md`, and `translation.md` for the versioned vocabulary, grammar notes, and HTML mapping.

## Progress

- Defined the initial vocabulary, restricted YAML shape, deterministic HTML mapping, and local generator.
- Generated the sample standalone page from `source/operator-brief.yaml`.
- Extended the generator for an optional responsive Bootstrap navbar and generated `output/theme-navbar.html` from `source/site-theme.yaml`.
- Added a compiler for `source/breakfast-blaster.rec`; its generated page is `output/breakfast-blaster.html`.
- Added shared design tokens in `tools/design.py` and responsive hero, button, and card styling. Both YAML and `.rec` inputs can set background, surface, text, muted text, accent, hero gradient colors, and corner radius; unspecified settings use neutral light or dark defaults. Motion effects honor reduced-motion preferences.
- Extended the YAML page schema with local hero/feature images, information cards, and a further-reading list. Added the generated pancake guide at `output/pancake-guide.html` using two project-local photos and documented sources.
- The self-hosted compiler stages and bootstrap comparison remain incomplete.

## Reproduce the `.rec` compilation

From the repository root, run:

```text
python Recursion/problems/bootstrap-language/tools/compile_site.py
```

The command reads `source/breakfast-blaster.rec` and writes `output/breakfast-blaster.html`. The compiler accepts optional input and output paths as two arguments. It was run here with Python 3.12.14 and completed successfully. The output preserves the site title, configured dark palette, centered layout, hero content, section, and three cards. This is evidence for the initial compiler stage only; it is not a self-hosting or bootstrap-equivalence proof.

The YAML generator uses the same design tokens. `source/site-theme.yaml` demonstrates a separately configured dark blue palette; `source/operator-brief.yaml` omits the style block and uses the neutral defaults. Both generated pages were rebuilt successfully after the shared styling change.

The pancake information site is reproducible with the command in `translation.md`. Its photos are stored in `assets/`; source and license notes are in `assets/credits.md`. The page includes cooking technique guidance, regional context, and further-reading links.

## Status

In progress. Both the YAML-to-static-page generator and the initial `.rec` compiler are implemented. The language compiler bootstrap proof remains open.
