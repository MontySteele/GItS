#!/usr/bin/env python3
"""EB-127: one id, one row, once ever. The uniqueness gate the registers never had.

WHY THIS EXISTS. `tools/lint_r_numbers.py` covers R- and D-numbers and nothing
else. The `M`-series in `QUEUE.md`, the `EB`-series in `BACKLOG.md` and every
other series were unchecked: nothing read them and nothing asserted
uniqueness. Two collisions reached review inside two weeks — `EB-119`/`EB-120`,
and `M38` minted twice on 2026-08-24 off the same base — and both were caught
by a human, neither by the suite. A collision that reaches `main` is worse than
a duplicate row: the two branches' provenance chains, rulings and
cross-references silently point at each other's item.

WHAT IS CHECKED, AND WHY EXACTLY THIS.

  1. within `QUEUE.md`, no two rows define the same id;
  2. within `BACKLOG.md`, no two rows define the same id;
  3. no id is defined as a row in BOTH registers at once;
  4. every defined id sits at or below its series' frozen CEILING — a number
     above it is a mint whose ceiling bump never landed;
  5. every defined id at or below the ceiling is a live entry in the manifest
     below — anything else is a RETIRED number being re-minted;
  6. every manifest entry still defines a row — an entry that outlives its row
     is STALE and fails, which is what keeps the manifest from rotting into
     cover for the next real collision;
  7. no row defines an id in a series another lint owns (`R`, `D`), which
     would land it outside both guards.

A row DEFINES an id when the id sits in the table's first column. Everything
else — a citation in another row's prose, a pointer from `STATE.md`, a
provenance chain naming a closed item — is a REFERENCE and is deliberately out
of scope AS A DEFINITION. References are how these documents work: `EB-136`
cites `R208`, `QUEUE` rows point at `BACKLOG` rows by id, and a lint that
treated any mention as a definition would fire on every healthy
cross-reference in the tree. The row's own words: *citations are fine*.

WHERE THE MANIFEST LIVES, AND WHY HERE. `EB-127` named three candidate homes
for the record of every id ever ISSUED — a committed ledger under `docs/`, a
derivation from git tags, or a per-series high-water mark — and refused to
settle it. The answer taken is the third, **as constants in this file**:

  * **Git derivation is not available.** CI checks out a depth-1 clone with no
    tags fetched (CLAUDE.md's history-retrieval section exists precisely
    because history is NOT in HEAD). A lint that needs `git log` to decide
    whether a number was ever issued cannot run in the lane that matters.
  * **`lint_r_numbers.py` set the precedent and it has held.** `R_CEILING` and
    `D_CEILING` are hand-bumped integers in the tool that reads them, for the
    same reason, and two branches taking "the next number" collide on that
    constant instead of silently sharing it. A second mechanism for a second
    pair of series would be a second thing to keep true.
  * **A `docs/` ledger would be a fourth register to maintain by hand** with
    nothing enforcing it, and CLAUDE.md's read-order budget is the thing this
    repo defends hardest. The manifest is machine data, not prose; it belongs
    next to the code that reads it.
  * **Rule 6 makes the whole thing self-enforcing.** Close a row, drop its id
    from `OPEN_IDS` in the same commit, and that number is permanently
    un-re-mintable — the retirement is recorded by the act of retiring. No
    separate discipline to remember, because forgetting fails the lint.

HOW THE CEILINGS WERE FIRST SET. Not from the highest LIVE row — closed items
leave HEAD, so that number understates the truth by exactly the ids this rule
exists to protect. Each ceiling is the highest id of its series **defined or
cited anywhere under `docs/current/`**, scanned on 2026-08-25: a retired id
survives in HEAD as a citation long after its row is gone (`EB-131` and
`EB-133` are cited by live rows and define none). That is a floor on "ever
issued", not a proof of one — but it only ever moves forward, and every mint
above it must record itself here, so the floor becomes exact from this commit
on.

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

# An INTEGER id: a series prefix and a number, hyphen optional (`EB-137`,
# `M26`). `S4-G6`, `CC-G1` and `SKIP-10.9` deliberately do not match — their
# tails are not integers, so they get the explicit-set treatment below.
SERIES_NUM = re.compile(r"^(?P<series>[A-Z][A-Z0-9]*?)-?(?P<num>\d+)$")


# --- THE ISSUED-ID MANIFEST ------------------------------------------------
# Hand-maintained, deliberately. Nothing derives these at runtime: a constant
# that recomputes itself from the thing it is checking guards nothing.

# Highest id ever issued in each integer series minted by these registers.
# Bump in the SAME commit as the row that mints past it. R and D are NOT here
# — `tools/lint_r_numbers.py` owns those two series and one namespace must not
# have two ceilings; rule 7 below refuses a row that tries to define one.
CEILINGS: dict[str, int] = {
    "EB": 137,   # docs/current/ cites EB-137 (defined); EB-131/EB-133 retired
    "M": 40,     # M40 cited by atlas/tier0-pilot-roster.md, closed under R204
}

# Every id AT OR BELOW its ceiling that legitimately defines a row. Frozen by
# a scan of the two registers on 2026-08-25 (the grandfather census) and
# maintained by hand since: a fresh mint joins it in the same commit as the
# ceiling bump, and a closed row's id LEAVES it in the same commit as the row.
# That second half is the whole mechanism — see rule 6 in the docstring.
OPEN_IDS: dict[str, frozenset[int]] = {
    "EB": frozenset({
        1, 12, 15, 28, 32, 33, 34, 35, 36, 38, 40, 41, 53, 65, 67, 70, 71,
        74, 76, 78, 80, 83, 84, 85, 88, 89, 90, 94, 105, 106, 107, 109, 115,
        116, 117, 118, 121, 122, 128, 129, 130, 136, 137,
    }),
    "M": frozenset({10, 13, 14, 16, 17, 19, 26}),
}

# The series whose ids are not a prefix plus an integer: sprint-gate families
# (`S4-G*`, `CC-G*`), one-off tags, and `SKIP-10.9`. No arithmetic is possible
# on these, so there is no ceiling — the set IS the manifest, with the same
# rot semantics as OPEN_IDS. A retired `S4-G7` is therefore refused the same
# way a retired `EB-53` would be: it is simply not in here.
OPEN_IRREGULAR: frozenset[str] = frozenset({
    "CC-G1", "CC-G2",
    "S4-G6", "S4-G11", "S4-G12", "S4-G13", "S4-G14", "S4-G17",
    "SKIP-10.9",
})

# Series another lint already owns. A register row defining one of these would
# sit outside both guards: `lint_r_numbers` checks `## R<n>` HEADINGS in
# docs/current/, never table cells, so a `| `R209` |` row would be namespaced
# by neither tool.
FOREIGN_SERIES: dict[str, str] = {
    "R": "tools/lint_r_numbers.py",
    "D": "tools/lint_r_numbers.py",
}


def parse(cid: str) -> tuple[str | None, int | None]:
    """`'EB-137'` -> `('EB', 137)`; `'S4-G6'` -> `(None, None)`."""
    m = SERIES_NUM.match(cid)
    if not m:
        return None, None
    return m.group("series"), int(m.group("num"))


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


def manifest_findings(where: dict[str, list[tuple[str, int]]],
                      ceilings: dict[str, int],
                      open_ids: dict[str, frozenset[int] | set[int]],
                      open_irregular: frozenset[str] | set[str]) -> list[str]:
    """Rules 4–7: every defined id is a live entry, every entry a live row.

    Takes the manifest as arguments rather than reading the module constants,
    so the self-test can manufacture a retirement without editing the real one.
    """
    out: list[str] = []
    seen_int: dict[str, set[int]] = collections.defaultdict(set)
    seen_irregular: set[str] = set()

    for cid, sites in sorted(where.items()):
        placed = ", ".join(f"{rel}:{line}" for rel, line in sites)
        series, num = parse(cid)

        if series in FOREIGN_SERIES:
            out.append(
                f"FOREIGN SERIES: {cid!r} defines a row ({placed}), but the "
                f"{series}-series is owned by {FOREIGN_SERIES[series]}, which "
                f"reads `## {series}<n>` headings and never table cells. A row "
                f"wearing that number is namespaced by neither tool.")
            continue

        if series is not None and series in ceilings:
            seen_int[series].add(num)
            ceiling = ceilings[series]
            if num > ceiling:
                also = ("" if num in open_ids.get(series, frozenset())
                        else f", and add {num} to OPEN_IDS[{series!r}]")
                out.append(
                    f"UNRECORDED MINT: {cid!r} defines a row ({placed}) above "
                    f"the frozen {series} ceiling of {ceiling}. Bump "
                    f"CEILINGS[{series!r}] to {num}{also} in the minting "
                    f"commit — two branches each taking 'the next free number' "
                    f"then collide on this constant instead of on main.")
            elif num not in open_ids.get(series, frozenset()):
                out.append(
                    f"RE-MINT: {cid!r} defines a row ({placed}), but {num} is "
                    f"at or below the frozen {series} ceiling of {ceiling} and "
                    f"is not in OPEN_IDS[{series!r}]. That number was issued "
                    f"and has retired — its row left HEAD (CLAUDE.md §Norms), "
                    f"so the collision is with HISTORY, not with a row. Take "
                    f"{ceiling + 1} instead and bump the ceiling with it.")
            continue

        seen_irregular.add(cid)
        if cid not in open_irregular:
            hint = ("" if series is None else
                    f" (if {series!r} is a new INTEGER series, give it a "
                    f"CEILINGS entry rather than listing ids one by one)")
            out.append(
                f"UNRECORDED ID: {cid!r} defines a row ({placed}) and is not "
                f"in OPEN_IRREGULAR. Either it is a fresh id that was minted "
                f"without recording itself, or it re-mints a retired one — "
                f"these series carry no ceiling, so the set cannot tell them "
                f"apart, which is exactly why it is explicit. Add it in the "
                f"minting commit{hint}.")

    for series in sorted(open_ids):
        for num in sorted(set(open_ids[series]) - seen_int.get(series, set())):
            out.append(
                f"STALE MANIFEST ENTRY: OPEN_IDS[{series!r}] lists {num}, but "
                f"no row in {' or '.join(REGISTERS)} defines {series}-{num} "
                f"any more. Delete it here in the same commit as the row: that "
                f"deletion is what makes the number permanently un-re-mintable, "
                f"and an entry that outlives its row is cover for the next "
                f"branch that re-takes it.")
    for cid in sorted(set(open_irregular) - seen_irregular):
        out.append(
            f"STALE MANIFEST ENTRY: OPEN_IRREGULAR lists {cid!r}, but no row "
            f"defines it any more. Delete it here in the same commit as the "
            f"row — that deletion is what retires the id.")
    return out


def findings(sources: dict[str, str] | None = None,
             ceilings: dict[str, int] | None = None,
             open_ids: dict[str, frozenset[int] | set[int]] | None = None,
             open_irregular: frozenset[str] | set[str] | None = None,
             ) -> tuple[list[str], dict[str, list[tuple[str, int]]]]:
    """Findings, plus the id -> [(register, line)] map for the denominator.

    `sources` overrides the on-disk registers with `{relative path: text}`.
    The self-test feeds it manufactured collisions, so the REPORTING half is
    exercised by the same code path the real run takes — not by a second
    implementation that agrees with this one by coincidence. The three
    manifest arguments override the frozen constants the same way.
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

    out.extend(manifest_findings(
        where,
        CEILINGS if ceilings is None else ceilings,
        OPEN_IDS if open_ids is None else open_ids,
        OPEN_IRREGULAR if open_irregular is None else open_irregular))
    return out, where


def _fitted(sources: dict[str, str]) -> tuple[dict, dict, set]:
    """A manifest that exactly fits `sources`. SELF-TEST SCAFFOLDING ONLY.

    NOT a source of truth, and never called by the real run: it derives each
    ceiling from the highest id that still DEFINES a row, which is precisely
    the understatement the frozen constants exist to correct — a retired id's
    number survives in HEAD only as a citation. It is here so the uniqueness
    cases below see uniqueness findings and nothing else.
    """
    ceilings: dict[str, int] = {}
    open_ids: dict[str, set[int]] = collections.defaultdict(set)
    irregular: set[str] = set()
    for text in sources.values():
        for cid, _ in row_ids(text):
            series, num = parse(cid)
            if series is None or series in FOREIGN_SERIES:
                irregular.add(cid)
                continue
            ceilings[series] = max(ceilings.get(series, 0), num)
            open_ids[series].add(num)
    return ceilings, dict(open_ids), irregular


def _run(sources: dict[str, str], ceilings=None, open_ids=None,
         open_irregular=None) -> list[str]:
    """`findings` over synthetic registers, defaulting to a fitted manifest."""
    fit_c, fit_o, fit_i = _fitted(sources)
    bad, _ = findings(sources,
                      fit_c if ceilings is None else ceilings,
                      fit_o if open_ids is None else open_ids,
                      fit_i if open_irregular is None else open_irregular)
    return bad


def self_test() -> list[str]:
    """Prove the check BITES, on synthetic text rather than on the registers.

    A uniqueness lint that has never seen a duplicate is indistinguishable
    from one that cannot see duplicates, and the registers are (correctly)
    clean — so the only honest evidence is a manufactured collision. Each
    case below is one of the rules, plus the shapes that must NOT fire.
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

    # --- and the three UNIQUENESS rules, through `findings` itself ---------
    Q, B = REGISTERS

    same = _run({Q: "| `M38` | a |\n| `M38` | b |", B: ""})
    if not any(f.startswith("DUPLICATE:") and "M38" in f for f in same):
        bad.append(f"self-test: rule 1 (same-register duplicate) did not "
                   f"fire: {same}")

    both = _run({Q: "", B: "| `EB-119` | a |\n| `EB-119` | b |"})
    if not any(f.startswith("DUPLICATE:") and "EB-119" in f for f in both):
        bad.append(f"self-test: rule 2 (same-register duplicate) did not "
                   f"fire: {both}")

    cross = _run({Q: "| `EB-9` | a |", B: "| `EB-9` | b |"})
    if not any(f.startswith("CROSS-REGISTER:") for f in cross):
        bad.append(f"self-test: rule 3 (cross-register) did not fire: {cross}")

    clean, seen = findings({Q: "| `M38` | a |", B: "| `EB-119` | b |"},
                           *_fitted({Q: "| `M38` | a |",
                                     B: "| `EB-119` | b |"}))
    if clean or sorted(seen) != ["EB-119", "M38"]:
        bad.append(f"self-test: a CLEAN pair produced findings {clean} / "
                   f"{sorted(seen)} -- the check fires on healthy registers")

    # A compound row must not collide with itself, and MUST collide with a
    # sibling that re-mints one of its members. Both halves, because the
    # expansion is the one place a merged row can hide a duplicate.
    merged = _run({Q: "", B: "| `EB-33/34/35` | a |"})
    if merged:
        bad.append(f"self-test: a merged row collided with itself: {merged}")
    reminted = _run({Q: "", B: "| `EB-33/34/35` | a |\n| `EB-34` | b |"})
    if not any("EB-34" in f for f in reminted):
        bad.append(f"self-test: a re-minted member of a merged row was "
                   f"missed: {reminted}")

    # --- and the MANIFEST rules, each against a manufactured retirement ----
    # The shape that motivated the row: EB-53's row has closed and left HEAD,
    # so a branch re-taking 53 sees no collision anywhere in the tree.
    retired = _run({Q: "", B: "| `EB-53` | re-taken |"},
                   ceilings={"EB": 137}, open_ids={"EB": set()},
                   open_irregular=set())
    if not any(f.startswith("RE-MINT:") and "EB-53" in f for f in retired):
        bad.append(f"self-test: rule 5 (re-minted RETIRED id) did not fire — "
                   f"this is the failure EB-127 was filed about: {retired}")

    unbumped = _run({Q: "", B: "| `EB-138` | fresh |"},
                    ceilings={"EB": 137}, open_ids={"EB": {138}},
                    open_irregular=set())
    if not any(f.startswith("UNRECORDED MINT:") for f in unbumped):
        bad.append(f"self-test: rule 4 (mint above an un-bumped ceiling) did "
                   f"not fire: {unbumped}")

    bumped = _run({Q: "", B: "| `EB-138` | fresh |"},
                  ceilings={"EB": 138}, open_ids={"EB": {138}},
                  open_irregular=set())
    if bumped:
        bad.append(f"self-test: a fresh mint WITH its ceiling bump and its "
                   f"manifest entry was refused: {bumped}")

    stale = _run({Q: "", B: "| `EB-138` | fresh |"},
                 ceilings={"EB": 138}, open_ids={"EB": {99, 138}},
                 open_irregular=set())
    if not any(f.startswith("STALE MANIFEST ENTRY:") and "99" in f
               for f in stale):
        bad.append(f"self-test: rule 6 (a manifest entry that outlived its "
                   f"row) did not fire: {stale}")

    irregular = _run({Q: "| `S4-G6` | live |\n| `S4-G7` | re-taken |", B: ""},
                     ceilings={}, open_ids={}, open_irregular={"S4-G6"})
    if not any(f.startswith("UNRECORDED ID:") and "S4-G7" in f
               for f in irregular):
        bad.append(f"self-test: an unrecorded irregular id was accepted: "
                   f"{irregular}")

    irregular_stale = _run({Q: "| `S4-G6` | live |", B: ""},
                           ceilings={}, open_ids={},
                           open_irregular={"S4-G6", "S4-G7"})
    if not any(f.startswith("STALE MANIFEST ENTRY:") and "S4-G7" in f
               for f in irregular_stale):
        bad.append(f"self-test: a stale irregular entry was accepted: "
                   f"{irregular_stale}")

    foreign = _run({Q: "", B: "| `R209` | a ruling as a row |"},
                   ceilings={}, open_ids={}, open_irregular=set())
    if not any(f.startswith("FOREIGN SERIES:") for f in foreign):
        bad.append(f"self-test: a row defining an R-number — guarded by "
                   f"neither this lint nor lint_r_numbers — was accepted: "
                   f"{foreign}")

    fitting = _run({Q: "| `M10` | a |",
                    B: "| `EB-1` | b |\n| `S4-G6` | c |"})
    if fitting:
        bad.append(f"self-test: a manifest that exactly fits its registers "
                   f"produced findings: {fitting}")
    return bad


SELF_TEST_CASES = 19


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
    manifest = "; ".join(
        f"{series} ceiling {CEILINGS[series]}, "
        f"{len(OPEN_IDS.get(series, ()))} open"
        for series in sorted(CEILINGS))
    print(f"manifest: {manifest}; {len(OPEN_IRREGULAR)} irregular id(s)")
    if not where:
        # lint_strict_domination's rule: a sweep that compared nothing must
        # not read like a clean one.
        print("VACUOUS: no row ids were found at all. The registers moved, or "
              "the row shape did; this lint is reporting nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s). One id defines one row, once ever: "
              f"a number at or below its ceiling that is not in the manifest "
              f"has RETIRED, and closed rows leave HEAD, so nothing else in "
              f"the tree would have caught you re-taking it.")
        return 1
    print("register-ids OK: every row id defines exactly one row, no id is "
          "defined in both registers, and every defined id is a live entry in "
          "the issued-id manifest — no retired number re-minted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
