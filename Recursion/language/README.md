# Recursion language sketch

The first language milestone is deliberately small: turn an operator's plain-text request into a readable Recursion source file, then produce a deterministic, inspectable result. The syntax in [grammar.md](grammar.md) is a proposal that the bootstrap-language problem can refine.

`examples/hello.rec` is the canonical cold-start program. The Breakfast Blaster examples in `problems/bootstrap-language/` show the intended site-generation direction: operator brief, generated Recursion source, and expected HTML. The cold-start problem defines how to run the small initial program before compiler artifacts exist.
