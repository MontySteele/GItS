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
  4. no defined id is a RETIRED number — one whose row closed and left HEAD,
     which nothing else in the tree remembers;
  5. every number below a series' ceiling either DEFINES a row or is in
     `RETIRED` — a hole is a row that closed without recording its number, and
     the next branch to mint would fall straight into it;
  6. the irregular series (`S4-G*`, `CC-G*`, `SKIP-*`) carry no arithmetic, so
     `OPEN_IRREGULAR` is their explicit manifest in both directions: an id not
     in it is unrecorded, an entry with no row is stale;
  7. no row defines an id in a series another lint owns (`R`, `D`), which
     would land it outside both guards.

A row DEFINES an id when the id sits in the table's first column. Everything
else — a citation in another row's prose, a pointer from `STATE.md`, a
provenance chain naming a closed item — is a REFERENCE and is deliberately out
of scope AS A DEFINITION. References are how these documents work: `EB-136`
cites `R208`, `QUEUE` rows point at `BACKLOG` rows by id, and a lint that
treated any mention as a definition would fire on every healthy
cross-reference in the tree. The row's own words: *citations are fine*.

THE CEILING IS DERIVED, AND THAT IS THE 2026-09-02 CHANGE. It used to be a
hand-bumped literal — `CEILINGS = {"EB": 317, ...}` — that a minting branch had
to edit in the same commit as its row. The rule worked and the line was a
bottleneck: every parallel branch that minted an `EB` row edited the SAME line
of THIS file, and on 2026-09-02 alone four such conflicts were resolved by
hand. So the ceiling is now

    max(every id the registers define, every number in RETIRED)

computed at import. A mint edits its register and nothing here; two branches
minting in parallel merge clean. **Two branches that each take "the next free
number" still take the SAME number** — that hazard did not go away, it MOVED:
it used to surface as a merge conflict in this file, and it now surfaces as
rule 1's `DUPLICATE` finding on the merged tree, in CI, with both rows named.
A gate that fires is a better place for it than a conflict a hand resolves.

WHAT A DERIVED CEILING CANNOT SEE, AND WHAT `RETIRED` IS FOR. Closed rows leave
HEAD (CLAUDE.md §Norms), so a high-water taken from the live rows FOLLOWS a
closed row out of the tree and re-offers its number. `RETIRED` is the record of
those numbers, seeded 2026-09-02 from the literal manifest this replaced —
every id at or below the old frozen ceiling that was not an `OPEN_IDS` entry,
which is exactly the set the old rule refused, number for number. Rule 5 is
what keeps it honest: retire a row without recording its number and the gap it
leaves FAILS this lint, so the retirement is recorded by the act of retiring,
the same self-enforcing shape `OPEN_IDS` had.

WHERE THE NOTES WENT. The per-id narrative that used to live in this file's
comments — every "EB-2xx minted 2026-08-30 by …" and every "LEFT OPEN_IDS with
its row, on its acceptance word for word …" — is
`docs/current/operations/register-ids.md`, moved there verbatim. That page is
also the procedure: how to mint (`tools/mint_row.py`), how to retire, and what
a fresh retirement writes down.

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
# ONE HAND-MAINTAINED SET, and it is touched when a row CLOSES, never when one
# is minted. That asymmetry is the whole 2026-09-02 change: the ceiling used to
# be a literal that every minting branch had to bump, so four branches in one
# sitting collided on the same line of this file. The ceiling is now DERIVED --
# `max(every id the registers define, every number in RETIRED)` -- so a mint
# edits the register and nothing else, and two branches minting in parallel
# merge clean. What the derivation cannot know on its own is the number whose
# row has CLOSED and left HEAD (CLAUDE.md Norms), because a derived high-water
# would follow that row out of the tree and hand the number to the next mint.
# That is what RETIRED carries, and rule 5 below is what forces it to be
# written down.
#
# THE NOTES THAT USED TO LIVE HERE ARE IN `docs/current/operations/register-ids.md`.
# Every "EB-2xx minted by ..." and "LEFT OPEN_IDS with its row" paragraph moved
# there verbatim when this file stopped carrying a hand-bumped ceiling; that
# page is also where a fresh retirement writes its one line.

def _spans(*items: int | tuple[int, int]) -> frozenset[int]:
    """`(1, 11), 13, (16, 31)` -> every integer those INCLUSIVE ranges cover.

    RETIRED is a couple of hundred numbers and a flat list of them would be
    unreadable and unmergeable both. Runs are the shape the data actually has
    -- ids retire in blocks, because a sitting closes several rows at once --
    so a fresh retirement is one number appended to one line, and two branches
    retiring different rows touch different lines.
    """
    out: set[int] = set()
    for item in items:
        if isinstance(item, tuple):
            low, high = item
            out.update(range(low, high + 1))
        else:
            out.add(item)
    return frozenset(out)


# Numbers ISSUED and never to be issued again: their rows closed and left HEAD,
# or they were minted and withdrawn. A number here is refused as a re-mint even
# though nothing else in the tree remembers it -- which is the whole point,
# since the row it belonged to is only in git.
#
# SEEDED 2026-09-02 from the literal `CEILINGS` / `OPEN_IDS` pair this replaced:
# every integer at or below the frozen ceiling (EB 317, M 69) that was not an
# OPEN_IDS entry, which is exactly the set the old rule 5 refused. So the
# guarantee is unchanged by the redesign, number for number.
#
# HOW A ROW RETIRES (the successor to "LEFT OPEN_IDS"). When a row closes and
# leaves HEAD, add its number here IN THE SAME COMMIT and write the one-line
# note in `operations/register-ids.md`. Rule 5 fails until you do: the number
# is then below the derived ceiling, defines no row and is in no set, which is
# precisely the hole a later branch would mint into.
RETIRED: dict[str, frozenset[int]] = {
    "EB": _spans(
        (1, 11), (13, 14), (16, 31), (36, 37), (39, 40), (42, 52), (54, 64),
        (66, 69), (72, 73), (75, 79), (81, 82), (85, 115), (117, 127),
        (129, 153), (155, 158), (162, 179), 182, (184, 190), 192,
        194, (196, 197), (201, 207), (209, 211), (213, 219), (221, 223),
        (225, 233), (236, 240), (242, 246), (249, 250), (252, 254),
        (256, 259), (267, 268), (271, 272), 276, 278, 288, 290,
        (294, 295), 298, (301, 315),
    ),
    "M": _spans((1, 12), (14, 25), (27, 44), (46, 68)),
}

# The irregular half of the same record. These ids carry no arithmetic, so
# nothing about them can be derived and `OPEN_IRREGULAR` below stays an
# explicit list -- a row defining an irregular id nobody recorded is refused by
# that list whether or not it appears here. What this set adds is the RIGHT
# REFUSAL: `S4-G11` was answered in all three parts by R231 and left
# OPEN_IRREGULAR with its row on 2026-08-30, so a row re-taking it is a re-mint
# and should be told so, not told that somebody forgot to record a new id.
RETIRED_IRREGULAR: frozenset[str] = frozenset({"S4-G11"})


# The series whose ids are not a prefix plus an integer: sprint-gate families
# (`S4-G*`, `CC-G*`), one-off tags, and `SKIP-10.9`. No arithmetic is possible
# on these, so there is no ceiling — the set IS the manifest, with the same
# rot semantics as OPEN_IDS. A retired `S4-G7` is therefore refused the same
# way a retired `EB-53` would be: it is simply not in here.
# S4-G11 left this manifest 2026-08-30 with its row, ruled in all three parts
# by R231: Backstroke KEPT, Tengu Flurry KEPT with `chinowa_ward` renamed
# `chinju_ward`, and the EB-82 Grave conversion taking the Liyue / Nameless
# Cairn labels. S4-G6 STAYS -- R231 answered only its MECHANISM.
OPEN_IRREGULAR: frozenset[str] = frozenset({
    "CC-G1", "CC-G2",
    "S4-G6", "S4-G12", "S4-G14", "S4-G17",
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
                      open_irregular: frozenset[str] | set[str],
                      retired: dict[str, frozenset[int] | set[int]] | None = None,
                      retired_irregular: frozenset[str] | set[str] = frozenset(),
                      ) -> list[str]:
    """Rules 4–7: every defined id is a live entry, every entry a live row.

    Takes the manifest as arguments rather than reading the module constants,
    so the self-test can manufacture a retirement without editing the real one.

    `retired` is the DERIVED-CEILING half and is opt-in: pass it and rule 5's
    gap sweep runs (a number below the ceiling that neither defines a row nor
    sits in `RETIRED` is a retirement nobody wrote down). Omit it and this
    behaves exactly as it did under the frozen-literal manifest, which is what
    lets the self-test and `_fitted` keep manufacturing a ceiling and an open
    set that fit each other and nothing else.
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
                held = (f"is in RETIRED[{series!r}]" if retired is not None
                        else f"is not in OPEN_IDS[{series!r}]")
                out.append(
                    f"RE-MINT: {cid!r} defines a row ({placed}), but {num} is "
                    f"at or below the {series} ceiling of {ceiling} and "
                    f"{held}. That number was issued "
                    f"and has retired — its row left HEAD (CLAUDE.md §Norms), "
                    f"so the collision is with HISTORY, not with a row. Take "
                    f"{ceiling + 1} instead; nothing here needs editing for a "
                    f"mint.")
            continue

        seen_irregular.add(cid)
        if cid in retired_irregular:
            out.append(
                f"RE-MINT: {cid!r} defines a row ({placed}), but it is in "
                f"RETIRED_IRREGULAR — that id was issued and its row has "
                f"closed and left HEAD. These series carry no arithmetic, so "
                f"there is no 'next' one: name the new item something the "
                f"family has never worn.")
        elif cid not in open_irregular:
            hint = ("" if series is None else
                    f" (if {series!r} is a new INTEGER series, give it a "
                    f"RETIRED entry rather than listing ids one by one)")
            out.append(
                f"UNRECORDED ID: {cid!r} defines a row ({placed}) and is not "
                f"in OPEN_IRREGULAR. Either it is a fresh id that was minted "
                f"without recording itself, or it re-mints a retired one — "
                f"these series carry no ceiling, so the set cannot tell them "
                f"apart, which is exactly why it is explicit. Add it in the "
                f"minting commit{hint}.")

    # Rule 5, the derived-ceiling half: a HOLE below the ceiling. Under the
    # frozen literal this was rule 6 running the other way -- an OPEN_IDS entry
    # that outlived its row. Derived, the entry is the row, so the thing that
    # can rot is the RETIREMENT: close a row, forget to write its number down,
    # and the number is below the ceiling, defines nothing, and is in no set --
    # which is exactly the hole the next mint falls into.
    if retired is not None:
        for series in sorted(ceilings):
            gaps = sorted(set(range(1, ceilings[series] + 1))
                          - seen_int.get(series, set())
                          - set(retired.get(series, frozenset())))
            for num in gaps:
                out.append(
                    f"UNRECORDED RETIREMENT: {series}-{num} is below the "
                    f"{series} ceiling of {ceilings[series]}, defines no row "
                    f"in {' or '.join(REGISTERS)}, and is not in "
                    f"RETIRED[{series!r}]. A closed row leaves HEAD, so this "
                    f"number is now invisible to everything except this set — "
                    f"add it to RETIRED in the same commit as the close, with "
                    f"its line in docs/current/operations/register-ids.md. "
                    f"Until then the next mint can take it back.")

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


def derive(where: dict[str, list[tuple[str, int]]],
           retired: dict[str, frozenset[int] | set[int]] | None = None,
           ) -> tuple[dict[str, int], dict[str, frozenset[int]]]:
    """`(ceilings, open ids)` for the integer series, off the rows and RETIRED.

    THE CEILING IS `max(defined, RETIRED)` — high enough that no legitimate
    mint is ever above it, because a mint takes the next number ABOVE it and
    a retirement only ever adds to it. The open set is the defined ids MINUS
    the retired ones, so a row wearing a retired number is reported by the
    same `RE-MINT` branch that read the hand-kept `OPEN_IDS`: the rule did not
    change, only where its two inputs come from.

    A series appears here when the registers define one of its ids or when
    `RETIRED` names it — so a series whose every row has closed keeps its
    ceiling, which is the case the whole redesign turns on.
    """
    retired = RETIRED if retired is None else retired
    ceilings: dict[str, int] = {}
    open_ids: dict[str, set[int]] = collections.defaultdict(set)
    for cid in where:
        series, num = parse(cid)
        if series is None or series in FOREIGN_SERIES:
            continue
        ceilings[series] = max(ceilings.get(series, 0), num)
        if num not in retired.get(series, frozenset()):
            open_ids[series].add(num)
    for series, nums in retired.items():
        if nums:
            ceilings[series] = max(ceilings.get(series, 0), max(nums))
    return ceilings, {s: frozenset(n) for s, n in open_ids.items()}


def findings(sources: dict[str, str] | None = None,
             ceilings: dict[str, int] | None = None,
             open_ids: dict[str, frozenset[int] | set[int]] | None = None,
             open_irregular: frozenset[str] | set[str] | None = None,
             retired: dict[str, frozenset[int] | set[int]] | None = None,
             ) -> tuple[list[str], dict[str, list[tuple[str, int]]]]:
    """Findings, plus the id -> [(register, line)] map for the denominator.

    `sources` overrides the on-disk registers with `{relative path: text}`.
    The self-test feeds it manufactured collisions, so the REPORTING half is
    exercised by the same code path the real run takes — not by a second
    implementation that agrees with this one by coincidence.

    THE MANIFEST ARGUMENTS ARE AN OVERRIDE AND A MODE SWITCH. Left None, the
    ceiling and the open set are DERIVED off the rows this call read plus
    `RETIRED`, and rule 5's gap sweep runs — that is the real run. Passed
    explicitly they are used verbatim and the gap sweep is OFF, which is the
    shape the self-test and every manufactured-retirement test wants: a fitted
    ceiling with no claim about what retired below it.
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

    derived = ceilings is None and open_ids is None
    held = RETIRED if retired is None else retired
    fit_c, fit_o = derive(where, held)
    out.extend(manifest_findings(
        where,
        fit_c if ceilings is None else ceilings,
        fit_o if open_ids is None else open_ids,
        OPEN_IRREGULAR if open_irregular is None else open_irregular,
        retired=held if derived else None,
        retired_irregular=RETIRED_IRREGULAR))
    return out, where


def _fitted(sources: dict[str, str]) -> tuple[dict, dict, set]:
    """A manifest that exactly fits `sources`. SELF-TEST SCAFFOLDING ONLY.

    `derive` WITHOUT `RETIRED` — the ceiling taken from the highest id that
    still defines a row and nothing else, which is precisely the
    understatement `RETIRED` exists to correct: a closed row's number survives
    in HEAD only as a citation, so a bare high-water re-offers it. It is here
    so the uniqueness cases below see uniqueness findings and nothing else,
    and it carries the third element (`irregular`) the real derivation has no
    business inventing.
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

    # --- and the DERIVED half: the ceiling follows the rows, RETIRED holds --
    # A mint above every live row and every retired number is the ordinary
    # act this redesign exists to make conflict-free. It must produce nothing.
    two = {"EB": frozenset({1, 2})}
    minted, _ = findings({Q: "", B: "| `EB-4` | fresh |\n| `EB-3` | older |"},
                         open_irregular=set(), retired=two)
    if minted:
        bad.append(f"self-test: a mint at the top of a DERIVED ceiling was "
                   f"refused: {minted}")

    # And the hole a close leaves: 3 defines no row and nothing retired it,
    # which is the number the next mint would fall into.
    holed, _ = findings({Q: "", B: "| `EB-4` | fresh |"},
                        open_irregular=set(), retired=two)
    if not any(f.startswith("UNRECORDED RETIREMENT:") and "EB-3" in f
               for f in holed):
        bad.append(f"self-test: rule 5 (a close that recorded no retirement) "
                   f"did not fire: {holed}")
    return bad


SELF_TEST_CASES = 21


def _committed() -> dict[str, list[tuple[str, int]]]:
    """The id -> sites map for the registers ON DISK, or `{}` if one is gone."""
    where: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)
    for rel in REGISTERS:
        page = REPO / rel
        if not page.exists():
            continue
        for cid, line in row_ids(page.read_text(encoding="utf-8")):
            where[cid].append((rel, line))
    return dict(where)


#: The two names the rest of the tree reads, kept for the readers that had
#: them when they were literals — `main`'s summary line, and the tests that
#: assert the manifest's shape. DERIVED now, at import, off the committed
#: registers and `RETIRED`; nothing bumps them by hand and a mint moves
#: `CEILINGS` by writing its row.
CEILINGS, OPEN_IDS = derive(_committed())


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
    ceilings, open_ids = derive(where)
    manifest = "; ".join(
        f"{series} ceiling {ceilings[series]} (derived), "
        f"{len(open_ids.get(series, ()))} open, "
        f"{len(RETIRED.get(series, ()))} retired"
        for series in sorted(ceilings))
    print(f"manifest: {manifest}; {len(OPEN_IRREGULAR)} irregular id(s)")
    if not where:
        # lint_strict_domination's rule: a sweep that compared nothing must
        # not read like a clean one.
        print("VACUOUS: no row ids were found at all. The registers moved, or "
              "the row shape did; this lint is reporting nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s). One id defines one row, once ever: "
              f"the ceiling is derived, so a mint needs no edit here — but a "
              f"number in RETIRED is a row that closed and left HEAD, and "
              f"nothing else in the tree would have caught you re-taking it.")
        return 1
    print("register-ids OK: every row id defines exactly one row, no id is "
          "defined in both registers, no RETIRED number is re-minted, and "
          "every number below each derived ceiling is either a live row or a "
          "recorded retirement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
