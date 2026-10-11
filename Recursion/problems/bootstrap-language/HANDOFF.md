# Bootstrap-language handoff

## Context

The bootstrap target is a local generator that turns a small, explicit YAML page description into a complete static HTML page using Bootstrap. The operator's plain-language request is `source/operator-brief.txt`; its normalized YAML is `source/operator-brief.yaml`. `source/site-theme.yaml` exercises a blue dark theme, responsive top navigation, mobile spacing, and a 1080px maximum desktop shell. The separate `source/breakfast-blaster.rec` demonstrates the broader YAML-like Recursion site syntax.

## Stages

1. **Discover and normalize:** read operator intent and express the page using the supported YAML schema. Natural-language interpretation remains an operator/agent step; the generator does not guess intent.
2. **Generate:** `tools/build_page.py` validates the schema and writes a complete static page with escaped content, responsive Bootstrap layout, optional collapsible navbar, heading, and primary button.
3. **Bootstrap proof:** a future compiler stage must generate the next stage and rebuild the agreed target. Record commands, outputs, and a repeatable comparison here when implemented.

## Syntax inventory

The current Recursion example uses reserved syntax words `site`, `theme`, `layout`, `hero`, `title`, `subtitle`, `button`, `section`, and `card`. `print` is reserved for the cold-start smoke program. The normalized YAML page schema also reserves `page`, `max_width`, `navbar`, `brand`, `items`, `label`, and `href`. Theme names such as `blue-dark`, `arcade`, and layout values such as `centered`, `container`, and `wide` are data values, as are display strings such as `Breakfast Blaster` and `Start Game`.

See `../../language/reserved-words.yaml`, `../../language/grammar.md`, and `translation.md` for the versioned vocabulary, grammar notes, and HTML mapping.

## Progress

- Defined the initial vocabulary, restricted YAML shape, deterministic HTML mapping, and local generator.
- Generated the sample standalone page from `source/operator-brief.yaml`.
- Extended the generator for an optional responsive Bootstrap navbar and generated `output/theme-navbar.html` from `source/site-theme.yaml`.
- The self-hosted compiler stages and bootstrap comparison remain incomplete.

## Status

In progress. The YAML-to-static-page stage is implemented; the language compiler bootstrap proof remains open.
