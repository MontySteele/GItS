#!/usr/bin/env python3
"""Nothing in the engine or the tier 0.5 model may READ a card's `register`.

WHAT THE FIELD IS. Curtain Call (R85) added `register: Optional[str]` to the
SHARED Card schema in tier0/engine/state.py -- the voice a card's NAME speaks
in. Furina's vocabulary is {salon, archon, private}; the column is per-character
and Columbina and every future character inherit it.

WHY IT IS FENCED OFF. It is a NAMING and ART label, not a mechanic. Cell 1 of
the Curtain Call sweep established that empirically: the sweep's renames and
register assignments landed together, and the run came out BYTE-IDENTICAL --
proof that nothing downstream read the new column. That pin is a measurement,
though, and a measurement only speaks for the code that existed when it ran.
This lint converts it into a standing guarantee: the next reader is a lint
failure instead of a silent balance change that the next sim run attributes to
whatever else moved that day.

The cost of getting this wrong is specifically bad. A register-aware engine
would make the sheet's voice labels load-bearing, so a lore edit -- renaming a
card from the salon register to the archon one, which is an ART decision taken
on art grounds -- would silently move win rate. Balance and lore have to be
able to move independently.

EXEMPTIONS, and why each is not a loophole:
  * state.py's own declaration. Somewhere has to define the field.
  * This file, which necessarily names it.
  * tools/ generally is NOT scanned: the sheet lints, the art pipeline and the
    gallery are all legitimate readers -- register guides art selection, which
    is the entire point of having it.

If a ruling ever DOES make the register mechanical, this lint is the thing to
delete, deliberately, with the ruling cited. That is the intended workflow: it
is a tripwire, not a wall.

  python tools/lint_register_isolation.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_ROOTS = ("tier0/engine", "tier05")

# (relative path, why it may name the field)
EXEMPT = {
    "tier0/engine/state.py": "declares the field",
}


def offences(path: Path) -> list[tuple[int, str]]:
    """[(lineno, what)] for every read of a `register` attribute or key."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        # card.register
        if isinstance(node, ast.Attribute) and node.attr == "register":
            found.append((node.lineno, "attribute .register"))
        # card["register"] / card.get("register")
        elif (isinstance(node, ast.Constant) and node.value == "register"):
            found.append((node.lineno, 'literal "register"'))
    return found


def scan(paths: list[Path] | None = None) -> dict[str, list[tuple[int, str]]]:
    """{repo-relative path: offences}, only for files that have any."""
    if paths is None:
        paths = [p for root in SCAN_ROOTS
                 for p in sorted((ROOT / root).rglob("*.py"))]
    out = {}
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXEMPT:
            continue
        hits = offences(p)
        if hits:
            out[rel] = hits
    return out


def main(argv: list[str]) -> int:
    paths = [Path(a).resolve() for a in argv] or None
    results = scan(paths)
    for rel, hits in sorted(results.items()):
        for lineno, what in hits:
            print(f"{rel}:{lineno}: reads the register field ({what})")
    total = sum(len(v) for v in results.values())
    print(f"{total} register read(s) in {len(results)} file(s)")
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
