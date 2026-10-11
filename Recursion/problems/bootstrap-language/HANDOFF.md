# Bootstrap-language handoff

## Context

Build on the cold-start runner toward generating simple sites from operator briefs. The example files show three distinct stages:

- `source/operator-brief.txt` is plain-language input for the operator or agent.
- `source/breakfast-blaster.rec` is a YAML-like Recursion site description.
- `output/operator-brief.html` is the expected HTML for the separate operator brief example.

The full site description and the shorter operator brief are separate examples. The compiler's agreed target and exact stage boundaries still need to be specified.

## Plan

Specify a minimal compiler pipeline that can be built in stages. Record how the initial stage produces the next stage and how that stage rebuilds the agreed target. Preserve operator input, Recursion source, commands, HTML output, and comparison evidence in this problem folder.

## Status

Ready; compiler stages and bootstrap evidence have not been implemented yet.
