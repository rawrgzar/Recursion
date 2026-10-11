#!/usr/bin/env python3
"""Run the initial one-line Recursion print statement."""

from __future__ import annotations

import re
import sys
from pathlib import Path


STATEMENT = re.compile(r'print "((?:[^"\\]|\\["\\])*)"\Z')


def main(args: list[str]) -> int:
    if len(args) != 1:
        print("usage: run_recursion.py SOURCE.rec", file=sys.stderr)
        return 2

    source = Path(args[0])
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        print(f"{source}: {error}", file=sys.stderr)
        return 1

    if len(lines) != 1:
        print(f"{source}:1: expected exactly one print statement", file=sys.stderr)
        return 1

    match = STATEMENT.fullmatch(lines[0])
    if match is None:
        print(f'{source}:1: expected print "text" (escape quotes or backslashes with \\)', file=sys.stderr)
        return 1

    output = re.sub(r'\\(["\\])', r'\1', match.group(1))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
