# Workload-planner reference analysis

The supplied `ADJ_Rule_Workload.html` was reviewed as an example of report structure and behavior. Its business-specific labels and records are not reused in the Recursion example.

## Reusable patterns

- A compact identity bar gives the report a clear home and marks the data snapshot.
- Summary metrics orient the reader before the detailed data.
- A short interpretation note explains how measures relate and where the source data stops.
- A paired horizontal bar chart compares two measures across shared categories without implying that the measures are interchangeable.
- Directory tables benefit from in-place search, categorical filters, sortable columns, paging, and expandable record context.
- Status colors, visible counts, empty states, keyboard focus, and responsive controls help readers understand and operate dense data.
- Source and uncertainty notes make the report's evidence limits visible in the page itself.

## Recursion representation

The report subset now supports metric entries, optional callout notes, a two-series horizontal comparison chart, configurable table search and category filtering, column sorting, page size, per-row detail disclosures, activity entries, and same-page navigation. The included `.rec` uses fictional records and neutral labels to demonstrate those features.

The HTML reference also contains a donut chart, several separate directories, and sticky filter bars. Those are useful future language extensions, but this implementation keeps one report table and one comparison chart as a reusable stage-zero foundation. Selecting a chart category filters matching table rows; selecting it again clears that chart filter. The generated page uses the reference's midnight navy and slate base with cyan, amber, coral, and mint accents.
