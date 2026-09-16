"""`EB-777`: no player-facing face is silently skipped by the text lint.

THE DEFECT. `tools/lint_text_conventions.py` read `Localization` rows out of
the C# SOURCE with one regex, and that regex's body class was `[^;)\\n]` -- a
face was allowed to contain anything EXCEPT a semicolon. A power whose prose
used one matched NOTHING, produced no row, and was never measured against its
ceiling. Nothing said so: a missing row is silent by construction, which is
the same shape as the missing hover tip `EB-272` was filed on and the empty
tip body `EB-343` was filed on. `ProtoBombPower.cs` even carries a comment
telling authors not to type a semicolon in player-facing prose because of it
-- a lint teaching the tree to dodge its own blind spot.

Ten faces were sitting in that blind spot when this was written: two under the
prototype gate (`PendingPlansPower`'s pair in `KokomiPlan.cs`, plus a
companion row) and eight on the shipped report.

WHY BOTH HALVES ARE PINNED HERE. Widening the matcher fixes the ten faces on
the tree today and nothing about tomorrow's. A ceiling that is never reached
fails nothing, so the gate also has to answer the POSITIVE question -- how
many `Localization` rows exist in the files it scans, and how many did it
measure. `loc_counts()` is that arithmetic and the tests below pin it at zero
unmeasured, with non-vacuous denominators.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import lint_text_conventions as lint          # noqa: E402

#: The matcher as it stood before `EB-777`, kept as the regression witness. A
#: test that only asserts the new behaviour cannot show that the old one was
#: broken, and this is one line.
OLD_MATCHER = re.compile(
    r'\("(description|smartDescription\w*)",'
    r'\s*((?:[^;)\n]|\n|\)(?!,\n))*?)\),\n')


def test_the_old_matcher_could_not_see_a_semicolon_face():
    """The regression witness: the fixture was INVISIBLE, not merely mismeasured."""
    assert not OLD_MATCHER.findall(lint.SEMICOLON_FIXTURE)


def test_a_semicolon_face_is_read_whole_and_measured():
    """It parses, it keeps its semicolons, and it reaches its ceiling."""
    faces = [f for f in lint.loc_bodies(lint.SEMICOLON_FIXTURE)
             if f.status == "row"]
    assert len(faces) == 1
    text = lint.render(lint.csharp_text(faces[0].body))
    # Both of the prose semicolons, and the clause AFTER the second one. A
    # body read to the first semicolon keeps none of that.
    assert text.count(";") == 2, text
    assert text.endswith("goes off at once.6"), text
    row = lint.Row("power", "fx_semicolon", lint.csharp_text(faces[0].body),
                   "fixture")
    found = lint.findings_for([row], {}, gate=False)
    assert any("> 125" in f for f in found), found


def test_a_const_whose_prose_carries_a_semicolon_is_read_whole():
    """`_consts` had the same defect one call down, as an UNDER-measure.

    A clause truncated at the first semicolon still produces a row -- a
    shorter one -- so every face that appends it was measured against a string
    the game never prints. Silent in the other direction, and worth its own
    case.
    """
    src = 'const string Clause = " it is spent; nothing refunds it.";\n'
    assert lint._consts(src)["Clause"] == " it is spent; nothing refunds it."


def test_the_self_test_still_fails_on_its_fixtures():
    """The lint is seen to FAIL, which is what makes a green run mean anything."""
    assert lint.self_test() == []


def _counts_are_whole(rows):
    seen, measured, grid = lint.loc_counts()
    assert seen > 0, "no Localization rows were scanned at all"
    assert measured > 0, "no Localization row was measured at all"
    assert seen == measured + grid, (
        f"{seen - measured - grid} Localization row(s) reached no ceiling; "
        f"{lint.loc_audit_findings()}")
    assert lint.loc_audit_findings() == []
    assert rows, "the surface produced no rows"


def test_every_prototype_localization_row_is_measured():
    """The positive count on the GATE's surfaces."""
    _counts_are_whole(lint.prototype_rows())


def test_every_shipped_localization_row_is_measured():
    """And on the report's, which is where the other eight were hiding."""
    _counts_are_whole(lint.shipped_rows())


def test_the_two_powers_that_were_invisible_are_counted_now():
    """Named, because they are the faces the row was filed on.

    `PendingPlansPower` is the prototype half (its badge says `in order next
    turn; a Dusk Plan at this turn's end`) and `AuraPower` the shipped half.
    Asserted by KEY rather than by count: a count here would have to be edited
    every time a face is added, which is how a pin stops being read.
    """
    proto = {row.ident for row in lint.prototype_rows()}
    assert "PendingPlansPower.description" in proto
    assert "PendingPlansPower.descriptionCapped" in proto
    shipped = {row.ident for row in lint.shipped_rows()}
    assert "AuraPower.description" in shipped
    assert "AuraPower.smartDescription" in shipped
