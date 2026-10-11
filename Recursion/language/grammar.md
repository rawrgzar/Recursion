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

The currently reserved vocabulary is listed in [reserved-words.yaml](reserved-words.yaml). Theme names and layout values are data values, not reserved words.
