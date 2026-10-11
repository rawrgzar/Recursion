# Build outputs

Keep generated static pages and bootstrap build outputs here. `operator-brief.html` and `theme-navbar.html` are generated from their matching YAML files by `tools/build_page.py`; `breakfast-blaster.html` is generated from `source/breakfast-blaster.rec` by `tools/compile_site.py`. Both generators use shared configurable design tokens from `tools/design.py`. `operator-brief.fragment.html` preserves the original body-fragment example. Record reproduction steps in the problem's `HANDOFF.md`.
