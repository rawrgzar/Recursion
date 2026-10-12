# Abstract report interface handoff

## Context

This child task adds a visually ambitious example to the bootstrap-language problem. It uses fictional structured information to exercise the language's ability to describe a polished, general-purpose reporting interface. The visual brief is stored in `source/visual-brief.md`.

## Current compiler limits

The stage-zero `.rec` compiler currently supports a site title, theme, centered or container layout, shared design tokens, a hero, sections, and cards. It does not yet express navigation, metric groups, tables, chronological activity, or inspection states. Extend the source grammar and renderer only as needed for this example, and document any syntax changes in the shared language notes.

## Implementation

- Added `source/field-notes.rec`, a reusable report example with navigation, contextual metadata, a feature summary, four metrics, a comparison chart, an eight-row interactive table, a four-event timeline, and a quiet footer.
- Added `tools/compile_report.py`, a deterministic compiler for the report subset. The output is standalone HTML, uses semantic sections and tables, supports narrow screens, reduced motion, row and metric hover/focus states, and compact inspection titles.
- Added the report grammar and vocabulary to the shared language notes. Report syntax deliberately stays separate from `site` syntax; the existing site compiler remains unchanged.
- Analyzed the supplied workload-planner HTML and recorded reusable patterns in `reference-analysis.md`. Extended the report grammar with interpretation callouts, a two-series comparison chart that filters the table by category, multiple table filters, sorting, paging, and expandable row details. The checked-in example uses fictional content and matches the reference palette.
- Generated `output/field-notes.html`.
- Updated the report's visual system to match the supplied planner's navy/slate foundation and cyan, amber, coral, and mint status colors while retaining smooth sans-serif typography.
- Added the optional `professions` and `step` syntax for keyboard-operable profession tabs with skill ranges, craft/gather counts, and row-specific material details. `source/wow-classic-professions.rec` compiles to `output/wow-classic-professions.html` and provides 12 Classic profession tabs.

## Reproduce and verify

From the repository root, run:

```text
python Recursion/problems/bootstrap-language/tools/compile_report.py
```

The compiler reads `source/field-notes.rec` and writes `output/field-notes.html`. It also accepts explicit input and output paths. Verification performed: the checked-in source compiles successfully; the emitted HTML contains the navigation, heading, feature, metrics, record table, activity list, and footer, and the renderer HTML-escapes all source-derived text and attributes. Navigation targets are restricted to local anchors, and each row must match the declared column count.

Screenshot generation is supplemental and was not needed for completion.

The detailed WoW Classic report is built with:

```text
python Recursion/problems/bootstrap-language/tools/compile_report.py Recursion/problems/bootstrap-language/abstract-report-interface/source/wow-classic-professions.rec Recursion/problems/bootstrap-language/abstract-report-interface/output/wow-classic-professions.html
```

Each `profession` declares a tab; its nested `step` entries provide skill range, recipe/action, craft or gather count, and materials/route note. Tabs support mouse and arrow/Home/End keyboard navigation. Route totals summarize Wowhead Classic profession leveling guides; yellow and green recipe outcomes can increase the actual material count.

