"""FOLLOWING CURRENT'S RECEIPT (Kokomi v3 seats, 2026-10-18), the page half.

"Whenever a Plan is carried out, the Bake-Kurage deals 3 Hydro damage." The
hit lands after the Plan's own beat, so it sat outside the beat's measurement
and printed nothing, and seats thought the Power never fired. The mod now puts
the hit on the carry-out's row (`KokomiPlan.NoteAfter`, the wire's `after`)
and the page prints one line under it. C# half:
`klee-mod/KleeTests/Prototype/KokomiV2SeatFindingsTests.cs`.
"""

from __future__ import annotations

from understudy import blindplay


def _page(*rows):
    from tier0.tests.test_understudy_blindplay import (morning_of,
                                                       plans_combat_state)
    blindplay.forget_fight()
    return blindplay.render(blindplay.observation(plans_combat_state(
        morning_of(*rows))))


def _plan(**extra):
    row = {"card": "War Council", "number": 2,
           "line": "Bake-Kurage: War Council, 2", "on_play": False,
           "moved": [], "kind": "energy", "asked": 2}
    row.update(extra)
    return row


def test_following_current_prints_its_hit_under_the_carry_out():
    page = _page(_plan(after=[{"source": "Following Current", "amount": 3,
                               "target": "Louse", "combat_id": ""}]))
    lines = page.splitlines()
    plan = next(i for i, l in enumerate(lines)
                if "Bake-Kurage: War Council, 2" in l)
    after = [l for l in lines[plan + 1:plan + 4]
             if "Following Current" in l]
    assert after == ["    - Following Current: 3 Hydro to Louse"]


def test_one_line_per_carry_out_and_none_without_the_power():
    hit = [{"source": "Following Current", "amount": 4, "target": "Louse",
            "combat_id": ""}]
    page = _page(_plan(after=hit), _plan(after=hit, again="Nereid's Ascension"))
    assert page.count("Following Current: 4 Hydro to Louse") == 2
    assert "Following Current" not in _page(_plan())
    # An older mod sends no `after` key; a zero-damage row prints nothing.
    zero = [{"source": "Following Current", "amount": 0, "target": "Louse",
             "combat_id": ""}]
    assert "Following Current" not in _page(_plan(after=zero))
