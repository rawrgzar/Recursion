# Orpheus report validation

Run from the repository root with the available Python runtime:

```text
python Recursion/problems/bootstrap-language/abstract-report-interface/tests/verify_orpheus.py
```

The checked-in report was generated with:

```text
python Recursion/problems/bootstrap-language/tools/compile_report.py Recursion/problems/bootstrap-language/abstract-report-interface/source/orpheus-mission.rec Recursion/problems/bootstrap-language/abstract-report-interface/output/orpheus-mission.html
```

## Results

- Compiler parse and render succeeded; a fresh render exactly matches the saved HTML.
- All four overview values, ten subsystem rows, two warning labels, four ordered events, and three milestones with dependencies match the supplied dataset.
- HTML parsing found no duplicate IDs; every in-page navigation link has a target.
- The generated page includes a distinct caution marker on both warning states, search, state filtering, sortable columns, paging, and three expandable context records.
- Semantic section/table labels and reduced-motion CSS are present. The generated script includes the event handlers for search, filtering, sorting, pagination, and disclosure elements.
- A browser preview could not be opened in this session: the browser tool rejected the local `file:` URL as disallowed and explicitly prohibited equivalent workarounds. Desktop and mobile visual appearance and live browser interaction were therefore not visually exercised.

## Language features used

`report`, `nav`/`link`, `heading`, `feature`, `callout`, `metrics`/`metric`, `table` with `search`, `filter`, `page_size`, `column`, `row`, and `detail`, `activity`/`event`, and `footer`.

## Missing capabilities

The language has no dedicated milestone list or semantic alert/status block, no support for more than one table, and no per-row status palette/threshold metadata. This report uses the existing feature for upcoming milestones and a callout for alert interpretation. The smallest reusable next extension would be generic `milestones`/`milestone` entries with date, label, dependency, plus a reusable status style token or state mapping; this would give upcoming plans a semantic section and let `Warning` render distinctly. The current field/value table also cannot assign status-specific colors or assert a reading against a numeric nominal range; threshold checking remains source data rather than computed behavior. Warning rows therefore use an explicit caution glyph while nominal labels remain plain.

## Design decisions

Mission-day context leads the page, followed by the three planned gates and the two unresolved alerts, then a dense sortable/filterable telemetry register and the four-event chronology. The mission dataset has no time-series observations, so no comparison chart was invented. Each warning has a caution glyph and expandable context tying it back to the logged event and relevant milestone.
