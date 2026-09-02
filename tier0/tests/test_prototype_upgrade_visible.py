"""EB-283 / EB-277: a staged row's `+` face may not be its base face.

THE DEFECT THIS PINS, in the words of the two rows it closes:

    "an upgraded prototype card was identical to its base: `Coral Bulwark+`
    and `Water's Edge (proto)+` printed and dealt the base numbers, so the
    Light Door's *Upgrade 2 random cards* had no visible effect"  (EB-277)

    "no prototype row upgraded -- Klee's offered no campfire choice at all
    and Kokomi's upgraded into a copy of itself"                  (EB-283)

`EB-283` answered it with `upgrades.prototype_default_delta`, a rule both
engines read. That fixed most of the surface and left TWO holes, and [USER]
found both of them by playing rather than by reading: "'Change of Plans' has
no upgrade?" and "Neither does Rally". Every reading available at the time --
a delta exists, the delta was expressible, a var moved -- was true of cards
that printed identical text, so the check has to be the one thing a player
actually sees: the FACE.

WHAT IS PINNED HERE, and each is a separate failure mode:

  1. the live surface is green under the gate (no row upgrades invisibly that
     is not on the curated `UPGRADE_DEBT` register);
  2. the gate GOES RED on a base-only row, on a row whose declared upgrade the
     face does not print, and on an added-effect upgrade that prints no
     `{IfUpgraded:...}` clause -- red-first, because a gate nobody has watched
     fail is not known to be a gate;
  3. the register cannot rot: an entry for a row that has left the surface,
     and an entry for a row that now passes, are both findings.

The fixtures are dicts and strings, never a row on the shipped surface: R213 B
makes an EMPTY surface the healthy committed state, and a permanent fixture
row would be the second permanent pool that ruling forbids
(`test_prototype_surface.py` makes the same argument at length).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import gen_prototype_cards as gp     # noqa: E402

# A minimal emitted card, in the shape `gen_klee_cards.emit` writes. Held as a
# template rather than generated, so the gate is exercised against the exact
# two strings it reads and a change to either is visible in this file.
_CARD = '''\
public sealed class Fixture : CustomCardModel
{{
    public override List<(string, string)>? Localization => new()
    {{
        ("title", "Fixture"),
        ("description", "{face}"),
    }};

    protected override void OnUpgrade()
    {{
{body}
    }}
}}
'''


def _emitted(face: str, body: str) -> str:
    return _CARD.format(face=face, body=body)


def test_the_live_surface_prints_every_upgrade_it_declares():
    """The gate, run over the committed sheet exactly as the codegen runs it.

    `gen_prototype_cards.main` raises on a finding -- which is what the
    `prototype-codegen` CI lint runs -- and this is the suite's own copy of the
    same read, so a regression is red here as well as at the codegen door.
    """
    built = gp.plan()
    rows = gp._rows()
    deltas = {}
    for row in rows:
        delta = gp.effective_upgrade(dict(row))
        if delta:
            deltas[row["id"]] = delta
    assert gp.upgrade_face_findings(rows, deltas, built.generated) == []


def test_a_row_with_no_upgrade_at_all_is_a_finding():
    # EB-277's own shape: the smith hands back a copy of the card.
    why = gp._upgrade_face_finding({}, _emitted("Deal 7 damage.", ""))
    assert why is not None
    assert "no upgrade at all" in why


def test_a_moved_var_the_face_does_not_print_is_a_finding():
    # The subtler half: a delta that IS expressible, an OnUpgrade that DOES
    # move a number, and a face that never prints it.
    why = gp._upgrade_face_finding(
        {"power_amount": 1},
        _emitted("Whenever you play a card, gain 1 Block.",
                 '        DynamicVars["PowerAmount"].UpgradeValueBy(1m);'))
    assert why is not None
    assert "printed identically to its base" in why


def test_an_appended_effect_with_no_face_clause_is_a_finding():
    # The thirteen-row class this gate found: the Prototype rule's last clause
    # ("otherwise the card draws one more") emits an `IsUpgraded`-gated draw in
    # `OnPlay` and NOTHING in `OnUpgrade`, so before the fix the `+` face was
    # byte-identical to the base one.
    why = gp._upgrade_face_finding(
        {"add": {"op": "draw", "amount": 1}},
        _emitted("Whenever you play a card, the front enemy gains 1 Weak.",
                 "        // add: draw -- expressed at play time."))
    assert why is not None
    assert "does nothing" in why


def test_the_same_row_passes_once_the_face_states_the_added_effect():
    # ... and passes the moment the face says so, which is the fix.
    assert gp._upgrade_face_finding(
        {"add": {"op": "draw", "amount": 1}},
        _emitted("Whenever you play a card, the front enemy gains 1 Weak. "
                 "{IfUpgraded:show:Draw 1 card.|}",
                 "        // add: draw -- expressed at play time.")) is None


def test_the_four_visible_shapes_pass():
    moved = _emitted("Deal {Damage:diff()} damage.",
                     "        DynamicVars.Damage.UpgradeValueBy(3m);")
    keyword = _emitted("Deal 7 damage. Exhaust.",
                       "        RemoveKeyword(CardKeyword.Exhaust);")
    cost = _emitted("Deal 7 damage.", "        EnergyCost.UpgradeBy(-1);")
    # The base game's Calculated* TRIPLE: the upgrade moves `CalculationBase`
    # and the face prints `CalculatedDamage`, which is the same number.
    calculated = _emitted(
        "Deal {CalculatedDamage:diff()} damage.",
        "        DynamicVars.CalculationBase.UpgradeValueBy(3m);")
    for source in (moved, keyword, cost, calculated):
        assert gp._upgrade_face_finding({"damage": 3}, source) is None


def test_a_debt_entry_for_a_row_that_left_the_surface_is_a_finding():
    # R213 B deletes a row WHOLE. An exemption that outlives its row is an
    # exemption nobody can see -- the B6 ledger lesson, one register over.
    findings = gp.upgrade_face_findings([], {}, {})
    assert findings
    assert all("not on the surface" in f for f in findings)
    assert len(findings) == len(gp.UPGRADE_DEBT)


def test_a_debt_entry_for_a_row_that_now_passes_is_a_finding():
    # A paid debt is deleted, never left standing: an entry that no longer
    # excuses anything would quietly excuse the NEXT regression on that id.
    paid = sorted(gp.UPGRADE_DEBT)[0]
    rows = [{"id": paid}]
    generated = {paid: _emitted("Deal {Damage:diff()} damage.",
                                "        DynamicVars.Damage.UpgradeValueBy(3m);")}
    findings = gp.upgrade_face_findings(rows, {paid: {"damage": 3}}, generated)
    assert [f for f in findings
            if f.startswith(f"{paid}: this row is still excused")]


def test_every_debt_entry_states_a_reason():
    for card_id, reason in gp.UPGRADE_DEBT.items():
        assert isinstance(reason, str) and len(reason.split()) >= 8, card_id


# --- `EB-315`: the ROW's own opt-out, and its own anti-rot rule -------------
#
# `no_upgrade:` is where a new exemption goes: it travels with the row under
# R213 B's deletion rule, and both engines read it (the codegen through
# `effective_upgrade`, the sim through `upgrades._prototype_deltas`). The debt
# dict above is what is left of the same idea kept in a file, and it is now the
# Spark arm's alone.

def _about(findings: list[str], card_id: str) -> list[str]:
    """Only the findings about one row.

    A one-row fixture always also reports every `UPGRADE_DEBT` id as "not on
    the surface", which is that register's own rot rule doing its job and is
    not what these three are asking about.
    """
    return [f for f in findings if f.startswith(f"{card_id}: ")]


def test_a_row_that_states_why_it_cannot_upgrade_is_not_a_finding():
    row = {"id": "proto_kk_fixture", "cost": 0, "effects": [],
           "no_upgrade": "the row prints no number the rule may move"}
    generated = {"proto_kk_fixture": _emitted("Draw 1 card.", "")}
    findings = gp.upgrade_face_findings([row], {}, generated)
    assert _about(findings, "proto_kk_fixture") == []


def test_the_same_row_without_the_key_is_a_finding():
    """Red-first: the opt-out is what silences the gate, not the row's shape."""
    row = {"id": "proto_kk_fixture", "cost": 0, "effects": []}
    generated = {"proto_kk_fixture": _emitted("Draw 1 card.", "")}
    findings = _about(gp.upgrade_face_findings([row], {}, generated),
                      "proto_kk_fixture")
    assert findings and "no upgrade at all" in findings[0]


def test_an_opt_out_the_rule_has_caught_up_with_is_a_finding():
    """A paid debt is deleted, one register over.

    The rule reaches a row's `plan:` line since `EB-315`, so an opt-out
    written before that would now be suppressing a real campfire choice --
    silently, which is the whole failure mode this file exists to catch.
    """
    row = {"id": "proto_kk_fixture", "cost": 1,
           "effects": [{"op": "block", "amount": 5}],
           "no_upgrade": "written when the rule could not reach this row"}
    generated = {"proto_kk_fixture": _emitted("Gain 5 [gold]Block[/gold].", "")}
    findings = gp.upgrade_face_findings([row], {}, generated)
    assert [f for f in findings if "the Prototype-stage rule now derives" in f]
