#!/usr/bin/env python3
"""Print ONE register row. The 300-line grep this replaces cost 4k tokens a time.

THE RITUAL. An agent handed "close EB-311" opens `BACKLOG.md` -- 170 lines of
six tables, most rows 400-600 characters -- to read one of them, or greps and
gets a truncated line with no section and no line number. Both put the whole
register in context to answer a question about one row.

    python tools/row.py EB-311             # the row, its four fields unpacked
    python tools/row.py EB-311 --raw       # the row line, verbatim
    python tools/row.py EB-311 --oneline   # id, register:line, section, status
    python tools/row.py M69                # QUEUE rows too; the register is
                                           # found, not asked for

An id that defines no row exits 1 and says so in one line -- which is also the
answer to "is this row still open?", since closed rows leave HEAD.
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import register_io                                        # noqa: E402

#: BACKLOG's declared four, in the order the register states them. Split on
#: the bold openers rather than parsed, because the colon sits inside the bold
#: in some rows and outside it in others and both spellings are in HEAD.
FIELDS = ("Scope", "Next action", "Gate", "Acceptance")
FIELD = re.compile(r"\*\*(" + "|".join(FIELDS) + r")\b:?\*?\*?:?\s*",
                   re.IGNORECASE)


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def unpack(body: str) -> list[tuple[str, str]]:
    """`[(field, text)]` for a BACKLOG body, or `[]` if it carries no fields."""
    hits = list(FIELD.finditer(body))
    if not hits:
        return []
    out = []
    if hits[0].start():
        out.append(("Status", body[:hits[0].start()].strip()))
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        out.append((m.group(1), body[m.end():end].strip()))
    return out


def locate(cid: str):
    """`(register, row, section, line)` for the one register that defines it."""
    for register in ("BACKLOG", "QUEUE"):
        found = register_io.row_text(register, cid)
        if found:
            row, section, line = found
            return register, row, section, line
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("id", help="a register id: `EB-311`, `M69`, `S4-G6`")
    ap.add_argument("--raw", action="store_true",
                    help="the row line verbatim, nothing else")
    ap.add_argument("--oneline", action="store_true",
                    help="id, register:line, section, and the leading status")
    args = ap.parse_args(argv)

    found = locate(args.id)
    if not found:
        print(f"{args.id}: no row in docs/current/BACKLOG.md or QUEUE.md. "
              f"Closed rows leave HEAD (CLAUDE.md Norms) -- if it ever "
              f"existed, it is in git and in "
              f"docs/current/operations/register-ids.md.")
        return 1
    register, row, section, line = found
    rel = register_io.REGISTERS[register]

    if args.raw:
        print(row)
        return 0

    parts = cells(row)
    body = parts[1] if len(parts) > 1 else ""
    fields = unpack(body) if register == "BACKLOG" else []
    if args.oneline:
        lead = (fields[0][1] if fields and fields[0][0] == "Status"
                else (parts[2] if register == "QUEUE" and len(parts) > 2
                      else body[:60]))
        print(f"{args.id}  {rel}:{line}  [{section}]  {lead}")
        return 0

    print(f"{args.id} -- {rel}:{line}")
    print(f"section: {section}")
    if register == "QUEUE":
        labels = ("Decision needed", "Status", "Provenance")
        for label, value in zip(labels, parts[1:]):
            print(f"\n{label}:")
            print(textwrap.indent(textwrap.fill(value, 76), "  "))
        return 0
    for label, value in fields:
        print(f"\n{label}:")
        print(textwrap.indent(textwrap.fill(value, 76), "  "))
    if len(parts) > 2:
        print("\nProvenance:")
        print(textwrap.indent(textwrap.fill(parts[2], 76), "  "))
    if not fields:
        print("\n(this row carries none of BACKLOG's four field markers)")
        print(textwrap.indent(textwrap.fill(body, 76), "  "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
