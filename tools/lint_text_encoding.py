#!/usr/bin/env python3
"""Every text read/write must declare its encoding.

Why this is a gate and not a style nit: Python picks the LOCALE codepage when
`encoding=` is omitted. On Linux CI that is UTF-8 and everything passes; on a
Windows dev box it is cp1252, and a sheet containing `Debut`'s accented `e`
decodes to mojibake IN MEMORY -- so every consumer downstream of the loader
inherits it. That is the exact defect found 2026-07-27: `loader.py` had five
bare `read_text()` calls, the card gallery rendered `Salon DA©but`, and the
generated C# would have shipped mojibake into the mod's Localization strings
had codegen been re-run on Windows. Nothing was committed corrupt, and CI
could never have told us -- the platform that fails is not the platform that
tests.

So the check has to be structural (does the call declare an encoding?) rather
than behavioural (did this file decode correctly?), because the behavioural
version passes on the machine that runs it.

Binary I/O is exempt: `read_bytes`/`write_bytes`, and `open(..., "rb")` --
there is no text decoding to get wrong.

So is `PIL.Image.open`, and that exemption is a REPAIR, not a loosening
(tooling-hardening sprint, 2026-07-29). The `open` arm keyed on the attribute
NAME, so every `Image.open(...)` in the repo counted as an undeclared text
read -- a decoder call that has no `encoding=` parameter to declare and does
binary I/O by definition. There were 20 of them across seven files, and they
were carried on `test_encoding_gate.DEBT` as debt that could only ever be
"paid" by deleting the image pipeline. That is worse than a miscount: the gate
compares a per-file COUNT, so `tools/art_lint.py: 2` was a standing allowance
for two REAL bare `open()` calls to hide behind. Image opens are exempt now
and the debt list carries only offences that can actually be fixed.

  python tools/lint_text_encoding.py            # scan the default roots
  python tools/lint_text_encoding.py path.py    # scan specific files
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_ROOTS = ("tier0", "tier05", "tools")

# Attribute calls that decode/encode text and therefore must say how.
TEXT_METHODS = {"read_text", "write_text"}

# Receivers whose `.open` is a BINARY decoder with no encoding parameter, so
# flagging it can never be acted on. Kept as an explicit, tiny allowlist rather
# than "exempt every attribute-form open": `io.open`, `codecs.open` and
# `gzip.open` all take `encoding=` and must stay in scope.
BINARY_OPEN_RECEIVERS = {"Image", "ImageFile"}     # PIL


def _has_encoding(call: ast.Call) -> bool:
    return any(kw.arg == "encoding" for kw in call.keywords)


def _is_binary_open(call: ast.Call) -> bool:
    """True when the mode argument requests binary I/O."""
    mode = None
    for kw in call.keywords:
        if kw.arg == "mode":
            mode = kw.value
    if mode is None and len(call.args) >= 2:
        mode = call.args[1]
    # open(f) with no mode is text mode -- not exempt.
    return isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
        and "b" in mode.value


def _binary_receiver(fn: ast.Attribute) -> bool:
    """`Image.open(p)` / `PIL.Image.open(p)` -- a binary decoder, not a read."""
    recv = fn.value
    if isinstance(recv, ast.Name):
        return recv.id in BINARY_OPEN_RECEIVERS
    if isinstance(recv, ast.Attribute):
        return recv.attr in BINARY_OPEN_RECEIVERS
    return False


def offences(path: Path) -> list[tuple[int, str]]:
    """[(lineno, call description)] for every undeclared text read/write."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else None)
        if name in TEXT_METHODS:
            if not _has_encoding(node):
                found.append((node.lineno, f"{name}()"))
        elif name == "open":
            if isinstance(fn, ast.Attribute) and _binary_receiver(fn):
                continue
            if not _is_binary_open(node) and not _has_encoding(node):
                found.append((node.lineno, "open()"))
    return found


def scan(paths: list[Path] | None = None) -> dict[str, list[tuple[int, str]]]:
    """{repo-relative path: offences}, only for files that have any."""
    if paths is None:
        paths = [p for root in SCAN_ROOTS
                 for p in sorted((ROOT / root).rglob("*.py"))]
    out = {}
    for p in paths:
        hits = offences(p)
        if hits:
            out[p.relative_to(ROOT).as_posix()] = hits
    return out


def main(argv: list[str]) -> int:
    paths = [Path(a).resolve() for a in argv] or None
    results = scan(paths)
    for rel, hits in sorted(results.items()):
        for lineno, what in hits:
            print(f"{rel}:{lineno}: {what} without encoding=")
    total = sum(len(v) for v in results.values())
    print(f"{total} undeclared text read/write call(s) "
          f"in {len(results)} file(s)")
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
