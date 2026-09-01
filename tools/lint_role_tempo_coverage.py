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
                                since R90/1c:

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

R90/1c IS WHY THE POPULATION CHANGED. (Citation repaired 2026-08-06 per Q15 /
R117 -- this file carried F14's misattribution three times over; clause 1c is
R90's, not R91's.) The first run compared a GItS archetype (one plan, a few
dozen cards) against a whole canon character (nearly a hundred, spread across
everything), so the bar was generous by construction and Furina cleared some
floors by 40-60 points. The comparison population is now the canon PACKAGE --
Silent's poison cards, Defect's orb cards, Necrobinder's summon cards -- which
are the same order of size as an archetype, and the same kind of object. The
two spans are not written down here: they move with the DLL and with the
sheets, and sec. 5 of docs/role-tempo-baseline.md derives and prints both.

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
    "# is intended and said out loud; a shrinking list is USUALLY progress and\n"
    "# a growing one is a regression, and both must be visible in a diff.\n"
    "#\n"
    "# USUALLY, and the exception already happened. This list went 30 -> 19 on\n"
    "# 2026-08-04 and NOT ONE GAP WAS FIXED: R90/1c changed the comparison\n"
    "# POPULATION from whole canon pools to canon packages, so some cells\n"
    "# stopped being under-floor because the floor moved and some archetypes\n"
    "# stopped being measured at all. The itemised delta is in\n"
    "# docs/sprint-axis-validity-track-a-log-2026-08-04.md. A shrink is only\n"
    "# progress when the tags moved; when the INSTRUMENT moved it is a change\n"
    "# of subject, and reading it as progress is the mistake this comment\n"
    "# exists to prevent.\n"
    "#\n"
    "# SAID OUT LOUD, 2026-08-07 (L4q / R129): 19 -> 18. The cell that left is\n"
    "# kokomi/priest frontload|late, and it left for the SECOND kind of reason\n"
    "# -- the INSTRUMENT moved, not the pool. R129 adopted\n"
    "# effect_walk.printed_floor for the pays_at_zero tag, so the three kokomi\n"
    "# pile-readers that print a base (pearl_barrage 5+, undertow 4+,\n"
    "# depths_judgment 10+) now carry `frontload` alongside `scaling`. Nobody\n"
    "# wrote a card. The cell is covered because the tag rule stopped\n"
    "# disagreeing with the sheets' own comments; read it as a re-measurement,\n"
    "# not as progress.\n"
    "#\n"
    "# SAID OUT LOUD, 2026-08-24 (EB-118 sec.5.2): 16 -> 17. The cell that\n"
    "# ARRIVES is furina/spotlight frontload|late. A growing list is what this\n"
    "# header calls a regression, so read what happened before reading it as\n"
    "# one: nobody deleted a frontload card. Five spotlight Powers covered\n"
    "# that cell by TOUCHING THE FANFARE METER -- a card that touches a meter\n"
    "# inherits the solves of that meter's payoff set -- and what they touched\n"
    "# it with was the incidental `raise_fanfare_cap` rider EB-118 sec.5.2\n"
    "# removed. The coverage was inherited from a printed line the packet\n"
    "# measured as close to inert, so this is a DISCLOSURE of a gap the pool\n"
    "# already had in play, not one the batch opened. Filling it is Phase 3's\n"
    "# business (Spotlight content). No floor moved to absorb it; none may.\n"
    "#\n"
    "#\n"
    "# SAID OUT LOUD HERE, 2026-08-25 (EB-118 Phase-3 Window 1): 17 -> 18. The\n"
    "# cell that ARRIVES is furina/spotlight frontload|mid, and it is the SAME\n"
    "# SHAPE as the entry above -- inherited coverage, disclosed rather than\n"
    "# opened. Rain of Roses lost its `spotlight` tag in the label pass because\n"
    "# it reads no Spotlight state of any kind; before, the spotlight sub-pool\n"
    "# held 18 cards of which 5 covered the cell (27.8% against a floor of\n"
    "# 25.0%), and after it holds 17 of which 4 do (23.5%). Nobody deleted a\n"
    "# frontload card and nothing was lost: a card that was never doing the job\n"
    "# stopped being counted as though it were. The measurement and its\n"
    "# arithmetic are published at review/records/eb118-w1-postread-2026-08-25.txt\n"
    "# (the pre-registration's build-time fact (b)); this note is the register\n"
    "# carrying it, which the header above requires and W1's landing missed.\n"
    "# Window 2 (2026-08-25) moved this list by NOTHING: tighten_the_cords went\n"
    "# [generic]/glue -> [priest]/payoff and the gate stayed at 18 against 18.\n"
    "#\n"
    "# SAID OUT LOUD HERE, 2026-08-25 (EB-118 Phase-3 Window 3, R211): 18 -> 17,\n"
    "# and this one IS progress rather than a change of subject. The cell that\n"
    "# LEAVES is furina/spotlight frontload|mid -- the entry the note directly\n"
    "# above disclosed at Window 1 -- and it leaves because a card was WRITTEN\n"
    "# for it. `take_it_from_the_top` is a spotlight-tagged Uncommon whose\n"
    "# derived tags are solve [block, frontload] and fight band [mid], so the\n"
    "# sub-pool goes from 17 cards of which 4 covered the cell to 18 of which 5\n"
    "# do. No floor moved and no instrument moved; the tags were derived by\n"
    "# `suggest_role_tempo_tags.py --land`, exactly as every other row's are.\n"
    "# Window 3's other five rows move this list by NOTHING: the three Klee\n"
    "# sinks derive solves against cells klee already covers, and all three\n"
    "# Kokomi rows are rewrites inside pools whose gaps are elsewhere.\n"
    "#\n"
    "# SAID OUT LOUD HERE, 2026-08-30 (EB-192 / R231): 17 -> 18, and it is a\n"
    "# change of SUBJECT rather than a regression. The canon anchor that\n"
    "# klee/spark and kokomi/commander are measured against was REBUILT:\n"
    "# `regent_forge` was a regex union of Regent's Stars with the unrelated\n"
    "# Forge card and ran about half Forge-only, and `regent_stars` replaces it\n"
    "# with the decompile-sourced census (generators, spenders, readers). The\n"
    "# package goes 19 -> 35 members, every one of its cells moves, and four\n"
    "# cells it used to sit at zero in stop being identity exemptions. Three\n"
    "# rows move: klee/spark block|mid LEAVES (its floor fell 10.5 -> 5.7 and\n"
    "# klee/spark already covered it), while klee/spark frontload|early and\n"
    "# klee/generic scaling|mid ARRIVE (the anchor's frontload|early demand\n"
    "# rose 21.1 -> 37.1; the DEFAULT floor set gained scaling|mid once the\n"
    "# Regent package stopped being zero there). Nobody wrote or deleted a\n"
    "# card.\n"
    "#\n"
    "# SAID OUT LOUD HERE, 2026-08-31 (EB-252): 18 -> 20, and both arrivals\n"
    "# are canon-POPULATION moves, not pool regressions. The local sts2.dll\n"
    "# went 0.107.1 -> 0.111.0 and every canon pool gained three cards\n"
    "# (87/88 -> 90/91), so all five packages were recounted: silent_poison\n"
    "# 12 -> 13, defect_orbs 41 -> 42, ironclad_strength 8 -> 10, regent_stars\n"
    "# 35 -> 36. Not one Klee number moved by a tenth; the floors moved under\n"
    "# them.\n"
    "#\n"
    "# klee/generic block|late ARRIVES because the cell had never been\n"
    "# MEASURED. ironclad_strength sat at 0.0% there, which made `block|late`\n"
    "# an identity exemption in the DEFAULT set; one of that package's two new\n"
    "# members blocks in the late band (10.0%), so all five are non-zero and\n"
    "# the cell becomes mandatory at 7.7% -- silent_poison's 1-of-13, the\n"
    "# minimum. What it then measures is real sheet shape and not an\n"
    "# instrument fault: ten of the twenty klee/generic cards carry `block`\n"
    "# and nine of them are early-band only, so ONE card still blocks late\n"
    "# (5.0%). Klee's generic defence is front-loaded and expires; the\n"
    "# instrument simply started asking.\n"
    "#\n"
    "# klee/spark scaling|early ARRIVES on a raised anchor. The Regent package\n"
    "# gained a second early-band scaler, so the demand went 2.9% (1-of-35) ->\n"
    "# 5.6% (2-of-36) while klee/spark stayed at one card (4.2%, 1-of-24). It\n"
    "# was clearing a ONE-CARD canon floor by 1.3 points and now misses a\n"
    "# two-card one -- a thin pass that was always one canon card from\n"
    "# failing, now disclosed rather than opened.\n"
    "#\n"
    "# Nobody wrote or deleted a card for either line, and no floor was moved\n"
    "# to absorb them; none may be. Both are offered to [USER] as DEBT at the\n"
    "# PR, and merging accepts them as debt.\n"
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
    print(f"Floors: canon PACKAGES (R90/1c). {len(default)} default-mandatory "
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
