# Cold-start proof

## Goal

From a clean checkout, run `language/examples/hello.rec` without generated compiler outputs and observe `Hello World` plus a newline.

## Evidence to record

- Required tools and versions.
- Exact command from the repository root.
- Actual output and exit status.
- Confirmation that the run did not use generated compiler files.

## Reproduce

Prerequisite: Python 3.10 or newer. From the repository root, run:

```console
python Recursion/problems/cold-start/tools/run_recursion.py Recursion/language/examples/hello.rec
```

Expected stdout is `Hello World` followed by a newline, with exit status 0. The runner currently supports exactly one `print "text"` statement; double quotes and backslashes inside the text may be escaped with a backslash. It uses only the Python standard library and the `.rec` input file. No compiler artifacts are required.

The actual execution and environment details are recorded in `problems/cold-start/HANDOFF.md`.
