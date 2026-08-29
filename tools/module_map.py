"""module_map -- a def-level map of a Python module, for orientation without a read.

    python tools/module_map.py understudy/soak.py
    python tools/module_map.py understudy/            # every .py under it
    python tools/module_map.py understudy/ --grep settle

One line per class / function / method: the line range, the kind, the
dotted name, and the first line of its docstring. Measured on 2026-08-29
across the six understudy modules: the map is 5% of the files' characters
(18k against 385k). The point is the reading order it makes possible --
map first, then `sed -n '<start>,<end>p'` on exactly the one definition
the task needs -- instead of paging a 2,000-line module in ranges to find
where something lives. It is orientation only: to change a definition you
still read it, and its neighbours, in full.

Nothing here imports the module it maps (`ast` only), so it is safe on any
file, including ones whose import would launch a game or load a sheet.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


def _first_doc_line(node: ast.AST) -> str:
    doc = ast.get_docstring(node) or ""
    for line in doc.strip().splitlines():
        line = line.strip()
        if line:
            return line[:72]
    return ""


def map_source(source: str, *, grep: re.Pattern[str] | None = None) -> list[str]:
    """Return the map lines for one module's source text."""
    tree = ast.parse(source)
    rows: list[tuple[int, str]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(child, ast.ClassDef) else "def"
                name = f"{prefix}{child.name}"
                end = getattr(child, "end_lineno", child.lineno)
                if grep is None or grep.search(name):
                    rows.append((child.lineno,
                                 f"{child.lineno:>5}-{end:<5} {kind:<5} {name}"
                                 f"  {_first_doc_line(child)}".rstrip()))
                walk(child, f"{name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    rows.sort()
    return [text for _, text in rows]


def map_path(path: Path, *, grep: re.Pattern[str] | None = None) -> list[str]:
    files = sorted(path.rglob("*.py")) if path.is_dir() else [path]
    out: list[str] = []
    for f in files:
        source = f.read_text(encoding="utf-8")
        lines = map_source(source, grep=grep)
        if grep is not None and not lines:
            continue
        out.append(f"# {f.as_posix()}  ({source.count(chr(10))} lines, {len(source)} chars)")
        out.extend(lines)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", help="a .py file or a directory")
    ap.add_argument("--grep", help="regex on the dotted name; only matching definitions are listed")
    args = ap.parse_args(argv)
    pattern = re.compile(args.grep) if args.grep else None
    path = Path(args.path)
    if not path.exists():
        print(f"module_map: no such path: {path}", file=sys.stderr)
        return 2
    for line in map_path(path, grep=pattern):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
