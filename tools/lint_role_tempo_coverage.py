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
  docs/role-tempo-floors.yaml   canon-derived, percentages only. TWO LAYERS
                                since R91/1c:

      default:   for an archetype with no named anchor. A cell is mandatory
                 when all five canon PACKAGES are non-zero in it; the floor is
                 the minimum of the five, so no canon package can fail it.
      anchored:  for an archetype that names the canon package shaped like it
                 (canon_role_tempo.ARCHETYPE_ANCHORS). The floor is that
                 package's OWN coverage, which it clears with equality and
                 nothing else.

  the three sheets              the LANDED `solve` and `tempo_band` fields.
                                Recomputed through tools/role_tempo.py rather
                                than read off the TSV, because a cell is
                                per-BAND and the TSV's solve is the union.

R91/1c IS WHY THE POPULATION CHANGED. The first run compared a GItS archetype
(11-32 cards, one plan) against a whole canon character (88 cards spread across
everything), so the bar was generous by construction and Furina cleared some
floors by 40-60 points. The comparison population is now the canon PACKAGE --
Silent's poison cards, Defect's orb cards, Necrobinder's summon cards -- which
run 8-41 and are the same kind of object as an archetype.

A-G1 CLOSED 2026-08-04 (R91). The tags this reads are LANDED on the sheets, so
the old "PROVISIONAL, nothing has been written to a sheet" banner is gone. What
has NOT changed: this is a COUNTING TOOL and R90/1a says so out loud. It answers
"does a card for this job exist at this point in the fight?" and nothing more.
Size and timing -- how MUCH a card pays and how fast the meter fills -- are
Track B's, per R90/1b.

`utility`, `support` and `sustain` are never linted. Protected free space
(A0.2(2)); one-seat sim, play-graded only (D4); and R91/2d respectively -- canon
carries 0.0-2.3% sustain under the structural definition, so zero sustain is a
legal identity and a sustain floor would be measuring noise.

--gate AND THE DEBT LIST
------------------------
Per R90/1a the Klee/Kokomi findings are REAL and stay pinned; the lint fails
only on NEW ones. Suite-green at a track boundary is a standing rule and the
house pattern for exactly this is the Silent anchor's.

`--gate` passes while the findings are a subset of `docs/role-tempo-debt.tsv`,
and fails on a new finding OR on a pinned finding that has silently
disappeared. A stale pin is as much a defect as a new gap: it means a cell moved
and nobody said so.

NO FLOOR WAS EVER ADJUSTED TO MAKE THIS PASS, and none may be. The debt list is
deleted the day the Klee and Kokomi reworks address the gaps in it.
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


def coverage() -> dict:
    """{(character, archetype): {cell: percent}} plus the sub-pool sizes.

    Recomputed through the classifier rather than read off the TSV's `solve`
    column, because a cell is per-BAND and the TSV's solve is the union over
    bands. The TSV is the readable rendering; this is the number. The sheets'
    landed tags and this computation cannot drift -- the same classifier wrote
    them, and `suggest_role_tempo_tags.py --check` fails if a hand edit moves
    one.
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
    default = floors["default"]["mandatory"]
    anchored = floors.get("anchored") or {}
    data = coverage()
    cov, sizes = data["coverage"], data["sizes"]

    print("role x tempo coverage -- FLOORS ONLY, no card can fail.")
    print("A COUNTING TOOL (R90/1a): does a card for this job exist at this")
    print("point in the fight? Size and timing are Track B's (R90/1b).")
    print(f"Floors: canon PACKAGES (R91/1c). {len(default)} default-mandatory "
          f"cells; {len(anchored)} archetypes anchored to a named package.")
    print()

    findings, unmeasurable = [], []
    for key in sorted(cov):
        character, archetype = key
        n = sizes[key]
        cells = cov[key]
        if n < MIN_SUBPOOL:
            unmeasurable.append((character, archetype, n))
            continue
        block = anchored.get(f"{character}/{archetype}")
        mandatory = block["mandatory"] if block else default
        source = (f"anchor {block['package']} (n={block['n']})" if block
                  else "default (min over five canon packages)")
        under = [(cell, cells.get(cell, 0.0), floor)
                 for cell, floor in sorted(mandatory.items())
                 if cells.get(cell, 0.0) < floor]
        if not args.quiet:
            print(f"  {character}/{archetype}  ({n} cards)  -- {source}")
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
