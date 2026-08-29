#!/usr/bin/env python3
"""EB-190: recorded authorship on the prototype surface, and the grades it bans.

TWO CHECKS, AND THEY ARE THE SAME RULE READ FROM BOTH ENDS.

  (1) **The field.** Every row on `docs/prototype-surface.yaml` records
      `authored_by:` -- a non-empty list of model FAMILIES from the closed
      AUTHORING set `{claude, gpt}` (`authorship.AUTHORABLE_FAMILIES`). Note
      the qualifier: `authorship.FAMILIES` also carries `local`, the family of
      a model served on this machine, and the two sets are deliberately
      different. `local` may be RECOGNISED, so a reading can be attributed and
      a refusal can name the chair it came from; it may not AUTHOR a row, and
      this check is what makes that true rather than merely intended -- a row
      naming it is a finding, exactly as `mistral` is.
      `tools/gen_prototype_cards.py` already refuses a row
      that fails this, so on a healthy tree check (1) never fires alone; it is
      here because the generator's refusal is a BUILD failure on the dev path
      and this is the lane that runs on every push.

  (2) **The grades.** No committed grade under `review/qa/` for a row whose
      `authored_by` names a CONTRIBUTING family was produced by a grader of
      that family. That is R217 C made checkable after the fact: the seat now
      refuses at run time (`understudy/seat.py`), but a form is a FILE, and a
      file can be written by a hand, an older tool, or a branch that predates
      the door.

WHAT (2) DELIBERATELY DOES NOT ASK, AND WHERE THAT QUESTION LIVES INSTEAD.
`AUTHOR_FAMILY` -- `claude` -- is on every row by construction, because Claude
authors this surface. So "did a Claude grader read a Claude-authored row?" is
answered YES by every second-grader form in every round, and asking it here
would produce sixteen findings that all say one structural thing and would
bury the four that name an actual contribution. That question is the BLINDNESS
of a fresh same-family seat -- R213's first guard rather than R217 C's
separation -- and it is refused at run time by
`understudy.blindplay.check_independent` for the driver, and open for the
second grader. This lint asks the OTHER question: did a family that
contributed TEXT, A NUMBER OR A MODE to a row then grade it? Such a family is
by definition not the standing author, so the check skips `AUTHOR_FAMILY`, and
only that.

WHY (2) IS THE ONE THAT MATTERS. A grade that violates the separation does not
look wrong. It looks like a grade -- same schema, same verdict, same ledger
row -- and the only way to see it is to join the form's grader against the
sheet's author list, which is a join no person does by eye across four rounds
of records.

THE DEBT LIST IS THE FINDING, NOT AN EXEMPTION. Klee slice 1's rounds 1 and 2
graded Rummage and Slow Burn with the family that re-wrote Rummage's text and
picked Slow Burn's number. Those four records ARE the defect this row was
opened for, they are already recorded as provisional in the slice packet's
section 11, and deleting them would be rewriting a published measurement
record (R101b). So they are named here, with the reason, and the lint is green
today and BITES on the next one. The set can only shrink: an entry that has
stopped tripping FAILS, exactly as `lint_register_shape`'s and
`lint_face_defects`' debt sets do, so nobody can leave a stale exemption
behind after the round is re-run.

Run: python tools/lint_prototype_authorship.py
     python tools/lint_prototype_authorship.py --self-test   # prove it bites
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from understudy import authorship            # noqa: E402

QA_DIR = REPO / "review" / "qa"

# Turn ids whose committed grades break rule (2) TODAY, each with the reason
# it is carried rather than fixed. Curated by hand; exact, not a prefix rule.
DEBT: dict[str, str] = {
    "klee-slice1-t04":
        "Klee slice 1 round 1, Rummage (`proto_spark_priced_draw`): the seat "
        "re-authored the card's text and its family then graded the turn. "
        "Provisional; Klee round 3 re-authors the arm. Packet section 11.",
    "klee-slice1-t06":
        "Klee slice 1 round 1, Slow Burn (`proto_spark_burst_conversion`): "
        "the seat chose the printed 10 and its family then graded the turn. "
        "Provisional; Klee round 3 re-authors the arm. Packet section 11.",
    "klee-slice1-r2-t04":
        "Klee slice 1 round 2, Rummage. Same defect as round 1, re-run before "
        "this door existed. Provisional; Klee round 3 re-authors the arm.",
    "klee-slice1-r2-t06":
        "Klee slice 1 round 2, Slow Burn. Same defect as round 1, re-run "
        "before this door existed. Provisional; Klee round 3 re-authors the "
        "arm.",
}


def surface_findings(sheet: Path | None = None) -> list[str]:
    """Check (1): the field, on every row."""
    path = sheet or authorship.SURFACE
    if not path.exists():
        return []
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    out: list[str] = []
    for row in rows:
        if isinstance(row, dict):
            out += authorship.field_findings(row)
    return out


def graded_by(turn_dir: Path) -> list[tuple[str, str]]:
    """`(form file name, grader model)` for every committed form in a turn dir.

    The MODEL is read out of the form rather than off the filename: the
    filename carries the ledger's grouping string, which an operator picks,
    and `grader.model` is the field the wrapper fills from the rollout.
    """
    out: list[tuple[str, str]] = []
    for path in sorted(turn_dir.glob("form-*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):                         # noqa: PERF203
            continue
        grader = blob.get("grader") if isinstance(blob, dict) else None
        if isinstance(grader, dict):
            out.append((path.name, str(grader.get("model") or "")))
    return out


def grade_offenders(qa_dir: Path | None = None,
                    turns: Path | None = None,
                    sheet: Path | None = None) -> dict[str, list[str]]:
    """`{turn id: [one line per offending form]}` for check (2), debt aside."""
    d = qa_dir or QA_DIR
    known = authorship.rows_authorship(sheet)
    index = authorship.turn_index(turns)
    found: dict[str, list[str]] = {}
    if not d.is_dir():
        return found
    for turn_dir in sorted(p for p in d.iterdir() if p.is_dir()):
        rows = index.get(turn_dir.name) or []
        if not rows:
            continue
        lines: list[str] = []
        for form_name, model in graded_by(turn_dir):
            family = authorship.model_family(model)
            # See the module docstring: the standing AUTHOR family is on every
            # row by construction, so it is not evidence of a contribution and
            # is skipped here rather than carried as sixteen debt entries.
            if not family or family == authorship.AUTHOR_FAMILY:
                continue
            for rid in rows:
                if family in (known.get(rid) or []):
                    lines.append(
                        f"{form_name} (model {model!r}, family {family!r}) "
                        f"graded {rid}, whose authored_by is "
                        f"{list(known.get(rid) or [])}")
        if lines:
            found[turn_dir.name] = lines
    return found


def findings(qa_dir: Path | None = None, turns: Path | None = None,
             sheet: Path | None = None,
             debt: dict[str, str] | None = None) -> list[str]:
    carried = DEBT if debt is None else debt
    out = surface_findings(sheet)
    offenders = grade_offenders(qa_dir, turns, sheet)

    for turn_id, lines in sorted(offenders.items()):
        if turn_id in carried:
            continue
        for line in lines:
            out.append(
                f"{turn_id}: {line}. A seat may not grade a row its own model "
                f"family authored (R217 C, EB-190). If this record is a known "
                f"and accepted violation, it belongs in this lint's DEBT with "
                f"its reason -- not deleted (R101b).")

    for turn_id, why in sorted(carried.items()):
        if turn_id not in offenders:
            out.append(
                f"DEBT entry {turn_id} no longer trips this lint, so the "
                f"exemption is stale and must be deleted. Recorded reason: "
                f"{why}")
    return out


def _self_test() -> int:
    """Prove the lint bites, on fixtures, without touching the repo's files."""
    import tempfile

    bad_row = {"id": "proto_x", "character": "kokomi"}
    assert authorship.field_findings(bad_row), "a row with no field must fail"
    assert authorship.field_findings({"id": "proto_x",
                                      "authored_by": ["mistral"]}), \
        "an unknown family must fail"
    # The local GRADER family is recognised by `model_family` and is still not
    # authorable. If this ever passes, the authoring roles have been widened
    # by accident rather than by a ruling.
    assert authorship.field_findings(
        {"id": "proto_x", "authored_by": [authorship.LOCAL_FAMILY]}), \
        "the local family must not be able to author a row"
    assert not authorship.field_findings({"id": "proto_x",
                                          "authored_by": ["claude"]})

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sheet = root / "surface.yaml"
        sheet.write_text(yaml.safe_dump(
            [{"id": "proto_selftest", "authored_by": ["claude", "gpt"]}]),
            encoding="utf-8")
        turns = root / "turns"
        turns.mkdir()
        (turns / "t.yaml").write_text(yaml.safe_dump(
            {"id": "selftest-t01",
             "board": {"hand": ["proto_selftest"]}}), encoding="utf-8")
        qa = root / "qa" / "selftest-t01"
        qa.mkdir(parents=True)
        (qa / "form-codex.json").write_text(json.dumps(
            {"grader": {"model": "gpt-5.6-sol"}}), encoding="utf-8")

        hits = findings(qa.parent, turns, sheet, debt={})
        assert hits and "selftest-t01" in hits[0], hits
        assert not findings(qa.parent, turns, sheet,
                            debt={"selftest-t01": "carried"})
        stale = findings(qa.parent, turns, sheet,
                         debt={"selftest-t01": "carried", "ghost-t01": "why"})
        assert any("ghost-t01" in h for h in stale), stale

        # And the documented exclusion: the STANDING AUTHOR family is on every
        # row by construction, so a claude grader is not what this check is
        # looking for. See the module docstring for where that question lives.
        (qa / "form-codex.json").unlink()
        (qa / "form-opus.json").write_text(json.dumps(
            {"grader": {"model": "claude-opus-5"}}), encoding="utf-8")
        assert not findings(qa.parent, turns, sheet, debt={}), \
            "the standing author family must be skipped, not reported"
    print("lint_prototype_authorship: self-test OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true",
                    help="run the fixtures that prove this lint bites")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()

    hits = findings()
    for line in hits:
        print(line)
    if hits:
        print(f"\n{len(hits)} finding(s).")
        return 1
    print(f"lint_prototype_authorship: OK "
          f"({len(authorship.rows_authorship())} surface row(s), "
          f"{len(DEBT)} carried debt entr(ies))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
