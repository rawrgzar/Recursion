# Initial grammar sketch

The cold-start smoke program uses one statement:

```text
print "Hello World"
```

The bootstrap project explores a YAML-like site description. A full example is in `problems/bootstrap-language/source/breakfast-blaster.rec`:

```text
site "Breakfast Blaster"
  theme: blue-dark
  layout: centered

  style:
    background: "#101326"
    surface: "#1b1f37"
    text: "#f7f4ff"
    muted: "#d4d4ec"
    accent: "#ffd166"
    accent_text: "#24152b"
    hero_start: "#282351"
    hero_end: "#144b65"
    radius: 32px

  hero:
    title: "Ready for breakfast?"
    subtitle: "Build. Discover. Repeat."
    button: "Start Exploring"

  section "How it works"
    card "Discover"
    card "Collaborate"
    card "Contribute"
```

Operators may provide a plain-text brief rather than write Recursion source. For example, `problems/bootstrap-language/source/operator-brief.txt` specifies a page title, layout, hero title, and button. The agent translates that brief into Recursion source; the compiler turns Recursion source into HTML. The brief and the full Breakfast Blaster site are separate examples, so their content need not match.

## Initial syntax notes

- A source file contains one `site` declaration and indented properties or blocks.
- Quoted text is used for names and values containing punctuation or spaces.
- `theme` and `layout` are scalar properties in the site block.
- `hero` contains scalar properties such as `title`, `subtitle`, and `button`.
- `style` optionally sets page colors and shape values; unspecified values use neutral defaults.
- A `section` contains zero or more `card` entries.
- The `print` statement remains a tiny cold-start smoke test, not the target site language.
- HTML structure, escaping, unknown keys, and error reporting still need precise definitions and tests.

This is a working sketch, not a settled specification. Record refinements and matching examples or verification updates in the bootstrap-language problem.

## Generic report subset

The abstract reporting example uses a separate `report` document root. Its compiler accepts the following focused, indentation-sensitive grammar:

```text
report "Document title"
  nav "Brand"
    link "Label" -> "#section-id"
  heading
    eyebrow: "Short label"
    title: "Editorial heading"
    subtitle: "Supporting summary"
    meta: "ITEM · DATE · AUDIENCE"
  feature
    label: "FEATURE LABEL"
    title: "Feature title"
    text: "Feature description"
    status: "Current status"
    tooltip: "Inspection detail"
  metrics
    metric "Label" | "Value" | "Note"
  callout
    title: "How to read this report"
    text: "Interpretation and source caveat."
  chart
    title: "Volume over time"
    filter: "Collection"
    series "Planned" | "verdant"
    series "Incoming" | "arcane"
    point "Window one" | "12" | "9"
  table
    title: "Record register"
    search: "Search records"
    filter: "Status"
    page_size: 8
    column "Column name"
    row "Cell" | "Cell"
    detail "First cell key" | "Expandable record context"
  activity
    event "Time" | "Title" | "Detail"
  footer
    text: "Footer note"
```

This subset is compiled by `problems/bootstrap-language/tools/compile_report.py`. It escapes source text, restricts navigation to same-page anchors and chart series to named palette tokens, validates chart values and table row widths, and emits responsive semantic HTML with reduced-motion support. The optional table search, column filters, sorting, pagination, and expandable row details work without a server. A chart's optional `filter` connects clickable categories to the matching table filter; each point label must match a value in that table column. Quoted strings may escape a quote or backslash. The pipe character separates cells in metrics, rows, details, points, and events and therefore is not currently supported inside a cell value. Chart points use one non-negative numeric value for each declared series.

The report example also records lessons from the user-supplied workload-planner reference in `problems/bootstrap-language/abstract-report-interface/reference-analysis.md`. Its useful reusable patterns are represented as generic report components; the reference's domain labels and data are not part of the language example.

The currently reserved vocabulary is listed in [reserved-words.yaml](reserved-words.yaml). Theme names and layout values are data values, not reserved words.
