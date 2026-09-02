#!/usr/bin/env python3
"""Read and write the two registers as TABLES, for the tools that mint and quote.

WHY THIS EXISTS. `BACKLOG.md` is ~170 lines of six markdown tables and every
agent that wanted one row out of it grepped, or read the whole file. Every
agent that minted a row hand-wrote the pipe syntax, hand-counted the 600-char
shape limit, and hand-picked the id. Three tools now share this reader --
`tools/mint_row.py`, `tools/row.py` and the id lint's own view of "the next
free number" -- so the parse lives once.

IT IS THE SAME PARSE THE LINTS USE, deliberately. `row_ids` here is
`lint_register_ids.row_ids` imported, not re-implemented: a minting tool that
disagreed with the gate about what a row is would mint rows the gate refuses.
The section / table half is new, because no lint needs it -- a lint reads rows
wherever they are, and only a WRITER has to know which table a row belongs to.

Nothing here writes unless asked (`insert_row`), and the write is the smallest
one that can be made: one line, at the top of one table's body, with the rest
of the file untouched byte for byte. That is what keeps two branches minting
into DIFFERENT sections from conflicting at all, and two branches minting into
the same section down to a one-line conflict.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BACKLOG = "docs/current/BACKLOG.md"
QUEUE = "docs/current/QUEUE.md"
REGISTERS = {"BACKLOG": BACKLOG, "QUEUE": QUEUE}

#: Which series each register mints. The id lint refuses the other direction
#: (an id defined in both registers), so this is the writing half of that rule.
SERIES = {"BACKLOG": "EB", "QUEUE": "M"}

SEPARATOR = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
HEADING = re.compile(r"^(#{2,6})\s+(.*?)\s*$")


def _lint():
    """`tools/lint_register_ids` as a module, loaded by path.

    By path rather than `from tools import ...` because these scripts are run
    as `python tools/x.py` from the repo root, where `tools` is not
    necessarily on `sys.path` -- the same reason `tier0/tests` loads it this
    way.
    """
    path = REPO / "tools" / "lint_register_ids.py"
    spec = importlib.util.spec_from_file_location("lint_register_ids", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("lint_register_ids", mod)
    spec.loader.exec_module(mod)
    return mod


@dataclass(frozen=True)
class Table:
    """One markdown table under one heading, located by line."""

    section: str          # the heading text, without its `##`
    header_line: int      # 1-indexed line of the `| ID | ... |` header
    body_line: int        # 1-indexed line the first data row sits on
    end_line: int         # 1-indexed line AFTER the last data row


def tables(text: str) -> list[Table]:
    """Every heading-plus-table in a register, in document order.

    A table is recognised by its `|---|` separator, and the section it belongs
    to is the nearest heading above it. A register section with no table
    (QUEUE has several -- "2. Shop, pricing, and money" carries prose only)
    contributes nothing, which is correct: there is nowhere to insert a row.
    """
    lines = text.split("\n")
    out: list[Table] = []
    section = ""
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            section = m.group(2)
            continue
        if not SEPARATOR.match(line) or i == 0:
            continue
        if not lines[i - 1].strip().startswith("|"):
            continue
        body = i + 1
        end = body
        while end < len(lines) and lines[end].strip().startswith("|"):
            end += 1
        out.append(Table(section=section, header_line=i,
                         body_line=body + 1, end_line=end + 1))
    return out


def read(register: str) -> str:
    return (REPO / REGISTERS[register]).read_text(encoding="utf-8")


def find_table(text: str, section: str) -> Table:
    """The table whose section heading matches `section`, case-insensitively.

    Matched on a normalised prefix so a caller may pass `tools` for
    `## tools — codegen, lint, scripts, refactors` rather than pasting an
    em-dash. An ambiguous prefix RAISES with every candidate named: guessing
    which table a row belongs in is exactly the mistake a writer must not make
    silently.
    """
    want = section.strip().lower()
    found = tables(text)
    exact = [t for t in found if t.section.lower() == want]
    if len(exact) == 1:
        return exact[0]
    hits = [t for t in found if t.section.lower().startswith(want)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        names = "\n  ".join(t.section for t in found)
        raise KeyError(f"no table under a section starting {section!r}. "
                       f"Sections with tables:\n  {names}")
    names = "\n  ".join(t.section for t in hits)
    raise KeyError(f"{section!r} matches {len(hits)} sections:\n  {names}")


def row_text(register: str, cid: str) -> tuple[str, str, int] | None:
    """`(row line, section, line number)` for one id, or `None`.

    Uses the LINT's definition of "this row defines this id", so a row quoted
    here is a row the gate agrees exists -- compound cells (`EB-33/34/35`) and
    shared cells (`S4-G12` / `CC-G1`) included.
    """
    lint = _lint()
    text = read(register)
    lines = text.split("\n")
    for defined, number in lint.row_ids(text):
        if defined != cid:
            continue
        section = ""
        for i in range(number - 1, -1, -1):
            m = HEADING.match(lines[i])
            if m:
                section = m.group(2)
                break
        return lines[number - 1], section, number
    return None


def defined_ids(register: str) -> dict[str, int]:
    """`{id: line}` for every id this register defines."""
    lint = _lint()
    return {cid: line for cid, line in lint.row_ids(read(register))}


def next_free(register: str) -> tuple[str, int]:
    """`(series, the next number to mint)`, derived — never a literal.

    `max(every id BOTH registers define, every RETIRED number) + 1`. Both
    registers, because the lint refuses an id defined in both and a series
    could in principle be minted from either; RETIRED, because a closed row
    has left HEAD and its number must not come back.
    """
    lint = _lint()
    series = SERIES[register]
    high = max(lint.RETIRED.get(series, frozenset()), default=0)
    for rel in lint.REGISTERS:
        page = REPO / rel
        if not page.exists():
            continue
        for cid, _ in lint.row_ids(page.read_text(encoding="utf-8")):
            found, num = lint.parse(cid)
            if found == series:
                high = max(high, num)
    return series, high + 1


def insert_row(register: str, section: str, row: str) -> int:
    """Write `row` as the first data row of `section`'s table. Returns its line.

    AT THE TOP, not the bottom, because that is where every register in this
    repo puts its newest row and because it keeps the write one line long. The
    file is otherwise untouched: no reflow, no re-sort, no trailing-whitespace
    pass. A minting commit whose diff is one added line is a minting commit
    that merges.
    """
    path = REPO / REGISTERS[register]
    text = path.read_text(encoding="utf-8")
    table = find_table(text, section)
    lines = text.split("\n")
    lines.insert(table.body_line - 1, row)
    path.write_text("\n".join(lines), encoding="utf-8")
    return table.body_line
