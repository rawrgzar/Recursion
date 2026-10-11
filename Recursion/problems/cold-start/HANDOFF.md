# Cold-start handoff

## Context

This is the first executable proof for `language/grammar.md`. The example is `language/examples/hello.rec`; a successful run prints `Hello World` followed by a newline.

## Plan

Choose and document the smallest initial runner that executes the example from a clean checkout. Do not rely on generated compiler outputs. Record prerequisites, exact commands, actual output, and reproducible evidence.

## Claim

- Owner: Codex
- Status: done
- Scope: add a small runner for the documented `print "..."` smoke syntax, run the canonical example, and record reproducible evidence.
- Intended files: `tools/run_recursion.py`, this handoff, and `../index.yaml`.

## Result

- Prerequisite: Python 3.10 or newer; implementation uses only the standard library.
- Reproduction command from the repository root: `python Recursion/problems/cold-start/tools/run_recursion.py Recursion/language/examples/hello.rec`
- Actual executable used here: the workspace's bundled Python 3.12.14 runtime.
- Actual output: `Hello World` followed by a newline.
- Saved output: `output/hello.txt`.
- Exit status: 0.
- Generated compiler outputs: none used; execution read the checked-in `.rec` source only.
- Reproduction instructions: `tests/cold-start.md`.

## Status

Done. The initial smoke program runs from its source file using the small standard-library runner. This proves only the documented `print` form, not the site-language compiler or bootstrap stages.
