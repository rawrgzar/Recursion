# Bootstrap-language handoff

## Context

The bootstrap target is a local generator that turns a small, explicit YAML page description into a complete static HTML page using Bootstrap CSS. The operator's plain-language request is `source/operator-brief.txt`; its normalized YAML is `source/operator-brief.yaml`. The separate `source/breakfast-blaster.rec` demonstrates the broader YAML-like Recursion site syntax.

## Stages

1. **Discover and normalize:** read operator intent and express the page using the supported YAML schema. Natural-language interpretation remains an operator/agent step; the generator does not guess intent.
2. **Generate:** `tools/build_page.py` validates the schema and writes a complete static page with escaped content, a responsive Bootstrap container, heading, and primary button.
3. **Bootstrap proof:** a future compiler stage must generate the next stage and rebuild the agreed target. Record commands, outputs, and a repeatable comparison here when implemented.

## Syntax inventory

The current Recursion example uses reserved syntax words `site`, `theme`, `layout`, `hero`, `title`, `subtitle`, `button`, `section`, and `card`. `print` is reserved for the cold-start smoke program. In the normalized YAML page schema, allowed keys are `page`, `layout`, and `hero` with `title` and `button` inside `hero`. These are names, not ordinary content; text such as `Breakfast Blaster`, `arcade`, `centered`, `container`, and `Start Game` is data.

See `../../language/reserved-words.yaml`, `../../language/grammar.md`, and `translation.md` for the versioned vocabulary, grammar notes, and HTML mapping.

## Progress

- Defined the initial vocabulary, restricted YAML shape, deterministic HTML mapping, and local generator.
- Generated the sample standalone page from `source/operator-brief.yaml`.
- The self-hosted compiler stages and bootstrap comparison remain incomplete.

## Status

In progress. The YAML-to-static-page stage is implemented; the language compiler bootstrap proof remains open.
