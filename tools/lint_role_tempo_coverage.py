"""Floors-only role x tempo coverage gate for the three GItS pools.

Track A / T4 (docs/track-a-kickoff-brief.md). Fails a pool when one of its
DECLARED archetypes sits under a canon-derived floor in a mandatory cell.

FLOORS ONLY. NO CARD CAN EVER FAIL. (Charter A0.2(1).) This lint has no
opinion about any individual card -- it cannot name one as wrong, it cannot
call one unclassifiable, and it never reports a card id as a finding. The unit
of failure is (character, archetype, cell) and nothing smaller. A pool with a
strange card and full coverage passes; a pool of blameless cards that all
answer the same question fails.

WHAT IT READS
-------------
  docs/role-tempo-floors.yaml   canon-derived, percentages only. A cell is
                                mandatory when all five canon pools are
                                non-zero in it; the floor is the minimum of
                                the five, so no canon character can fail its
                                own floor.
  docs/role-tempo-review.tsv    the PROVISIONAL tags from
                                tools/suggest_role_tempo_tags.py.

THE SECOND INPUT IS PROVISIONAL AND THE OUTPUT SAYS SO ON EVERY RUN. [USER]
gate A-G1 has not closed; no tag here has landed on a sheet. Read this run as
"what the taxonomy says today", not as a verdict on the pools.

`utility` and `support` are never linted. The first is protected free space
(A0.2(2)); the second is graded by play sessions only, because the sim is
one-seat (D4 clause, charter A0).

--gate AND THE DEBT LIST
------------------------
The first run found 30 findings and P1's binding null fired in the same run
(docs/sprint-axis-validity-track-a-log-2026-08-04.md §0), so the taxonomy is
back with design and the findings are real but not yet actionable. Suite-green
at a track boundary is a standing rule, and the house pattern for exactly this
is the Silent anchor's: PIN the known findings and fail only on NEW ones.

`--gate` therefore passes while the findings are a subset of
`docs/role-tempo-debt.tsv`, and fails on a thirty-first finding OR on a pinned
finding that has silently disappeared. A stale pin is as much a defect as a new
gap: it means a cell moved and nobody said so.

NO FLOOR WAS ADJUSTED TO MAKE THIS PASS, and none may be. The debt list is
worthless the day the null is resolved and should be deleted with it.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import role_tempo as rt              # noqa: E402

FLOORS = REPO / "docs" / "role-tempo-floors.yaml"
REVIEW = REPO / "docs" / "role-tempo-review.tsv"
DEBT = REPO / "docs" / "role-tempo-debt.tsv"
DEBT_HEADER = (
    "# Pinned role x tempo coverage gaps -- the debt list `--gate` measures\n"
    "# NEW findings against. Regenerate with --write-debt ONLY when the change\n"
    "# is intended and said out loud; a shrinking list is progress and a\n"
    "# growing one is a regression, and both must be visible in a diff.\n"
    "#\n"
    "# Every line is a COVERAGE GAP in a pool. No line names a card, and none\n"
    "# ever can: this lint is floors-only (charter A0.2(1)).\n"
    "character\tarchetype\tcell\n")

# A sub-pool smaller than this cannot express a percentage floor honestly: one
# card in a three-card archetype is 33%, which clears every floor in the file
# by accident. Reported as UNMEASURABLE rather than passed, so the silence is
# visible.
MIN_SUBPOOL = 8


def load_floors() -> dict:
    return yaml.safe_load(FLOORS.read_text(encoding="utf-8"))


def load_review() -> list[dict]:
    lines = REVIEW.read_text(encoding="utf-8").splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, line.split("\t"))) for line in lines[1:] if line]


def coverage() -> dict:
    """{(character, archetype): {cell: percent}} plus the sub-pool sizes.

    Recomputed from the sheets rather than read off the TSV's `solve_suggested`
    column, because a cell is per-BAND and the TSV's suggested solve is the
    union over bands. The TSV is the reviewable rendering; this is the number.
    """
    out: dict[tuple[str, str], dict[str, float]] = {}
    sizes: dict[tuple[str, str], int] = {}
    for character, path in rt.SHEETS.items():
        rows = rt.load_rows(path)
        scans, _ = rt.classify_pool(rows, character)
        for archetype in rt.declared_archetypes(path):
            sub = [r for r in rows if archetype in (r.get("archetypes") or [])]
            sizes[(character, archetype)] = len(sub)
            if not sub:
                out[(character, archetype)] = {}
                continue
            hits: dict[str, int] = defaultdict(int)
            for row in sub:
                for band, roles in scans[row["id"]]["cells"].items():
                    for role in roles:
                        hits[f"{role}|{band}"] += 1
            out[(character, archetype)] = {
                cell: 100.0 * k / len(sub) for cell, k in hits.items()}
    return {"coverage": out, "sizes": sizes}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true",
                    help="findings only; skip the full table")
    ap.add_argument("--gate", action="store_true",
                    help="pass while findings are a subset of the debt list; "
                         "fail on a NEW finding or a stale pin")
    ap.add_argument("--write-debt", action="store_true",
                    help="rewrite docs/role-tempo-debt.tsv from this run")
    args = ap.parse_args(argv)
    if args.gate:
        args.quiet = True

    floors = load_floors()
    mandatory = floors["mandatory"]
    data = coverage()
    cov, sizes = data["coverage"], data["sizes"]

    print("role x tempo coverage -- FLOORS ONLY, no card can fail.")
    print("Tags are PROVISIONAL: [USER] gate A-G1 has not closed and nothing")
    print("in docs/role-tempo-review.tsv has been written to a sheet.")
    print(f"Floors: {len(mandatory)} mandatory cells, min-of-canon over five "
          "pools.")
    print()

    findings, unmeasurable = [], []
    for key in sorted(cov):
        character, archetype = key
        n = sizes[key]
        cells = cov[key]
        if n < MIN_SUBPOOL:
            unmeasurable.append((character, archetype, n))
            continue
        under = [(cell, cells.get(cell, 0.0), floor)
                 for cell, floor in sorted(mandatory.items())
                 if cells.get(cell, 0.0) < floor]
        if not args.quiet:
            print(f"  {character}/{archetype}  ({n} cards)")
            for cell, floor in sorted(mandatory.items()):
                have = cells.get(cell, 0.0)
                mark = "UNDER" if have < floor else "ok   "
                print(f"      {mark}  {cell:<18} {have:5.1f}%  "
                      f"floor {floor:4.1f}%")
            print()
        for cell, have, floor in under:
            findings.append((character, archetype, cell, have, floor))

    if unmeasurable:
        print("UNMEASURABLE (sub-pool under "
              f"{MIN_SUBPOOL} cards -- a percentage floor cannot be honest "
              "here, so these are reported rather than passed):")
        for character, archetype, n in unmeasurable:
            print(f"    {character}/{archetype}: {n} cards")
        print()

    keys = {(c, a, cell) for c, a, cell, _h, _f in findings}
    if args.write_debt:
        DEBT.write_text(DEBT_HEADER + "".join(
            "\t".join(k) + "\n" for k in sorted(keys)), encoding="utf-8")
        print(f"  wrote {DEBT.relative_to(REPO)} ({len(keys)} pinned gaps)")
        return 0

    if args.gate:
        pinned = {tuple(line.split("\t")) for line in
                  DEBT.read_text(encoding="utf-8").splitlines()
                  if line and not line.startswith(("#", "character\t"))}
        new = sorted(keys - pinned)
        stale = sorted(pinned - keys)
        print(f"gate: {len(keys)} findings against {len(pinned)} pinned.")
        for key in new:
            print("    NEW      " + "/".join(key))
        for key in stale:
            print("    STALE    " + "/".join(key)
                  + "   (pinned, no longer found -- say so and re-pin)")
        if new or stale:
            print("\nA NEW finding is a coverage regression. A STALE pin is a "
                  "cell that\nmoved without anybody saying so. Both fail.")
            return 1
        print("gate ok: findings are exactly the pinned debt list.")
        return 0

    if not findings:
        print("CLEAN: every declared archetype clears every mandatory cell.")
        return 0

    print(f"UNDER FLOOR: {len(findings)} (character, archetype, cell) "
          "findings.")
    print("Each names a COVERAGE GAP in a pool. None names a card.")
    for character, archetype, cell, have, floor in findings:
        print(f"    {character}/{archetype:<10} {cell:<18} "
              f"{have:5.1f}%  <  floor {floor:4.1f}%")
    return 1


if __name__ == "__main__":
    sys.exit(main())
