#!/usr/bin/env python3
"""EB-127: no id defines two rows. The uniqueness gate the registers never had.

WHY THIS EXISTS. `tools/lint_r_numbers.py` covers R- and D-numbers and nothing
else. The `M`-series in `QUEUE.md`, the `EB`-series in `BACKLOG.md` and every
other series were unchecked: nothing read them and nothing asserted
uniqueness. Two collisions reached review inside two weeks — `EB-119`/`EB-120`,
and `M38` minted twice on 2026-08-24 off the same base — and both were caught
by a human, neither by the suite. A collision that reaches `main` is worse than
a duplicate row: the two branches' provenance chains, rulings and
cross-references silently point at each other's item.

WHAT IS CHECKED, AND WHY EXACTLY THIS. **Row-definition uniqueness, and
nothing else.**

  1. within `QUEUE.md`, no two rows define the same id;
  2. within `BACKLOG.md`, no two rows define the same id;
  3. no id is defined as a row in BOTH registers at once.

A row DEFINES an id when the id sits in the table's first column. Everything
else — a citation in another row's prose, a pointer from `STATE.md`, a
provenance chain naming a closed item — is a REFERENCE and is deliberately out
of scope. References are how these documents work: `EB-136` cites `R208`,
`QUEUE` rows point at `BACKLOG` rows by id, and a lint that treated any
mention as a definition would fire on every healthy cross-reference in the
tree. The row's own words: *citations are fine*.

THE CHOICE THIS ROW LEFT OPEN, AND THE ANSWER TAKEN. `EB-127` named three
candidate homes for a manifest of every id ever ISSUED — a committed ledger, a
derivation from git tags, or a per-series high-water mark — and refused to
settle it. **None of the three is built here, and this lint does not need
one**, because it answers a question HEAD can see: two rows, one id. That is
exactly the shape of both recorded collisions.

WHAT IS THEREFORE NOT COVERED, stated so it is not mistaken for covered:
**re-use of a RETIRED id.** Closed items leave HEAD (CLAUDE.md §Norms), so the
highest live id understates the highest id ever issued, and a branch that
re-mints a number whose row has left HEAD collides with history rather than
with a row — invisible here by construction. That half still wants a manifest,
and it is what keeps `EB-127` open.

Usage:
    python tools/lint_register_ids.py
    python tools/lint_register_ids.py --self-test   # prove it bites

Exit 1 with findings on stdout.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The two ROW registers. Deliberately not every markdown table in the tree:
# `STATE.md`'s tables are stamps and roster rows, `EXPERIMENTS.md`'s are
# registrations — neither mints ids into these series, and scanning them would
# turn a stamp label into a "duplicate id".
REGISTERS = ("docs/current/QUEUE.md", "docs/current/BACKLOG.md")

# One id as the registers spell it: an uppercase series, then hyphen-joined
# parts. Covers `EB-71`, `M14`, `S4-G6`, `CC-G1`, `OT-1` and `SKIP-10.9`.
ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9.]+)*$")

# The compound spelling one row uses for a merged item: `EB-33/34/35` is three
# ids in one cell, not an id containing slashes. Expanded rather than special-
# cased, so a second merged row cannot quietly hide a duplicate inside itself.
COMPOUND = re.compile(r"^(?P<head>.*?)(?P<num>[0-9.]+)(?P<rest>(?:/[0-9.]+)+)$")

# A cell may carry several ids joined by ` / ` (QUEUE's S4-G12 / CC-G1 / CC-G2
# row). Each is a definition; the row is shared, the ids are not.
BACKTICKED = re.compile(r"`([^`]+)`")


def expand(token: str) -> list[str]:
    """One first-column token -> the ids it defines, or [] if it is not one."""
    token = token.strip()
    m = COMPOUND.match(token)
    if m:
        head, num, rest = m.group("head"), m.group("num"), m.group("rest")
        ids = [head + num] + [head + part
                              for part in rest.split("/") if part]
        return ids if all(ID.match(i) for i in ids) else []
    return [token] if ID.match(token) else []


def row_ids(text: str) -> list[tuple[str, int]]:
    """Every (id, line number) a table row DEFINES in this register text.

    Takes TEXT rather than a path so the self-test below exercises this
    function itself. A second copy of the parse living in the test is exactly
    the drift a self-test is supposed to catch.

    The id cell is the first column. A cell that is not entirely backticked
    id tokens is not a definition — that is what keeps `Art debt` and the
    `S8 + S10 galleries` row out, and it is a deliberate REFUSAL rather than
    an oversight: a row without a machine-readable id cannot be checked for
    uniqueness and should not pretend to be.
    """
    out: list[tuple[str, int]] = []
    for n, line in enumerate(text.split("\n"), 1):
        stripped = line.strip().lstrip("> ").strip()
        if not stripped.startswith("|"):
            continue
        cell = stripped.split("|")[1].strip()
        tokens = BACKTICKED.findall(cell)
        if not tokens:
            continue
        # The cell must be ONLY those backticked tokens and the ` / ` between
        # them, or it is prose that happens to open with a code span.
        residue = BACKTICKED.sub("", cell).replace("/", "").strip()
        if residue:
            continue
        for token in tokens:
            out.extend((cid, n) for cid in expand(token))
    return out


def findings(sources: dict[str, str] | None = None
             ) -> tuple[list[str], dict[str, list[tuple[str, int]]]]:
    """Findings, plus the id -> [(register, line)] map for the denominator.

    `sources` overrides the on-disk registers with `{relative path: text}`.
    The self-test feeds it manufactured collisions, so the REPORTING half is
    exercised by the same code path the real run takes — not by a second
    implementation that agrees with this one by coincidence.
    """
    out: list[str] = []
    where: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)
    for rel in (sources or {rel: None for rel in REGISTERS}):
        if sources is not None:
            text = sources[rel]
        else:
            page = REPO / rel
            if not page.exists():
                out.append(f"MISSING REGISTER: {rel} does not exist -- this "
                           f"lint cannot answer the question it claims to "
                           f"answer.")
                continue
            text = page.read_text(encoding="utf-8")
        for cid, line in row_ids(text):
            where[cid].append((rel, line))

    for cid, sites in sorted(where.items()):
        if len(sites) == 1:
            continue
        registers = {rel for rel, _ in sites}
        placed = ", ".join(f"{rel}:{line}" for rel, line in sites)
        if len(registers) > 1:
            out.append(
                f"CROSS-REGISTER: {cid!r} defines a row in {len(registers)} "
                f"registers at once ({placed}). One id, one home: a QUEUE row "
                f"and a BACKLOG row wearing the same id make every "
                f"cross-reference to it ambiguous.")
        else:
            out.append(
                f"DUPLICATE: {cid!r} defines {len(sites)} rows in the same "
                f"register ({placed}). This is the EB-119/EB-120 and M38 "
                f"collision shape — two branches each took 'the next free "
                f"integer' against a HEAD showing neither the other's row.")
    return out, where


def self_test() -> list[str]:
    """Prove the check BITES, on synthetic text rather than on the registers.

    A uniqueness lint that has never seen a duplicate is indistinguishable
    from one that cannot see duplicates, and the registers are (correctly)
    clean — so the only honest evidence is a manufactured collision. Each
    case below is one of the three rules, plus the two shapes that must NOT
    fire.
    """
    bad: list[str] = []

    def ids(text: str) -> list[str]:
        return [cid for cid, _ in row_ids(text)]

    dup = ids("| `EB-9` | a |\n| `EB-9` | b |")
    if dup != ["EB-9", "EB-9"]:
        bad.append(f"self-test: a duplicate id cell did not parse: {dup}")

    compound = ids("| `EB-33/34/35` | x |")
    if compound != ["EB-33", "EB-34", "EB-35"]:
        bad.append(f"self-test: compound expansion is wrong: {compound}")

    shared = ids("| `S4-G12` / `CC-G1` / `CC-G2` | x |")
    if shared != ["S4-G12", "CC-G1", "CC-G2"]:
        bad.append(f"self-test: a shared-row cell is wrong: {shared}")

    prose = ids("| Art debt | x |\n| S8 + S10 galleries | y |\n"
                "| see `EB-71` for why | z |")
    if prose:
        bad.append(f"self-test: a prose cell was read as a definition: {prose}")

    if ids("| ID | Item |\n|---|---|"):
        bad.append("self-test: a header row was read as a definition")

    # --- and the three RULES, through `findings` itself -------------------
    Q, B = REGISTERS

    same, _ = findings({Q: "| `M38` | a |\n| `M38` | b |", B: ""})
    if not any(f.startswith("DUPLICATE:") and "M38" in f for f in same):
        bad.append(f"self-test: rule 1 (same-register duplicate) did not "
                   f"fire: {same}")

    both, _ = findings({Q: "", B: "| `EB-119` | a |\n| `EB-119` | b |"})
    if not any(f.startswith("DUPLICATE:") and "EB-119" in f for f in both):
        bad.append(f"self-test: rule 2 (same-register duplicate) did not "
                   f"fire: {both}")

    cross, _ = findings({Q: "| `EB-9` | a |", B: "| `EB-9` | b |"})
    if not any(f.startswith("CROSS-REGISTER:") for f in cross):
        bad.append(f"self-test: rule 3 (cross-register) did not fire: {cross}")

    clean, seen = findings({Q: "| `M38` | a |", B: "| `EB-119` | b |"})
    if clean or sorted(seen) != ["EB-119", "M38"]:
        bad.append(f"self-test: a CLEAN pair produced findings {clean} / "
                   f"{sorted(seen)} -- the check fires on healthy registers")

    # A compound row must not collide with itself, and MUST collide with a
    # sibling that re-mints one of its members. Both halves, because the
    # expansion is the one place a merged row can hide a duplicate.
    merged, _ = findings({Q: "", B: "| `EB-33/34/35` | a |"})
    if merged:
        bad.append(f"self-test: a merged row collided with itself: {merged}")
    reminted, _ = findings({Q: "", B: "| `EB-33/34/35` | a |\n| `EB-34` | b |"})
    if not any("EB-34" in f for f in reminted):
        bad.append(f"self-test: a re-minted member of a merged row was "
                   f"missed: {reminted}")
    return bad


SELF_TEST_CASES = 11


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: {SELF_TEST_CASES} case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    bad, where = findings()
    for line in bad:
        print(line)
    per_register = collections.Counter(
        rel for sites in where.values() for rel, _ in sites)
    scope = ", ".join(f"{rel} {per_register[rel]}" for rel in REGISTERS)
    print(f"scope: {len(where)} distinct id(s) defined across "
          f"{len(REGISTERS)} register(s) -- {scope}")
    if not where:
        # lint_strict_domination's rule: a sweep that compared nothing must
        # not read like a clean one.
        print("VACUOUS: no row ids were found at all. The registers moved, or "
              "the row shape did; this lint is reporting nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s). One id defines one row. Retired ids "
              f"are NOT covered — closed rows leave HEAD, so re-minting a "
              f"closed number is invisible here (EB-127).")
        return 1
    print("register-ids OK: every row id defines exactly one row, and no id "
          "is defined in both registers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
