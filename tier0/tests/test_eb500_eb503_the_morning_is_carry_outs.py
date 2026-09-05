"""`EB-500`, `EB-501`, `EB-503`: the morning is CARRY-OUTS, and it says so.

Three findings off one round (Kokomi r17 lane 1) that turn out to be one
number read three ways.

`EB-501`. Well Laid prints "for each Plan the Bake-Kurage carried out this
morning" and counted the Plans WRITTEN: a morning of one Plan under Nereid's
Ascension is carried out twice and paid once. Tide Wall and Tide Chart print
the same words off the same number, so the fix is the number and not the card:
`kk_plans_this_morning` (C# `KokomiOverhaulLedger.PlansThisMorning`) is
`len(due) * carry_out_times`, still read ONCE at the drain so a reader's answer
does not depend on where in the queue it sits.

`EB-500`. "The Bake-Kurage carries out every Plan twice" admits no exception,
and the built rule has one: the doubling is the MORNING's, and The Moon's
now-copy -- the Plan resolved the moment it is written -- is single, as is
Change of Plans' front-copy. The rule stands (D default) and the face and the
tip now name the morning.

`EB-503`. Tide Chart's draw happened inside the morning with no line anywhere:
"the one Plan card the Bake-Kurage block never reports on". The C# pays it
through `Announce`, the block's own door, so it is a beat over the pet and a
row in the same list every carry-out lands in. The sim's twin row is
`tide_chart_paid`, and both now count carry-outs, so a doubled morning draws
twice.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import kokomi_plan
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400


def _row(card_id):
    """One prototype row by id -- `prototype_cards` is the only reader of the
    quarantined sheet, which is the quarantine and not an inconvenience."""
    import copy
    return copy.deepcopy(
        next(c for c in loader.prototype_cards() if c.id == card_id))


def _face(card_id) -> str:
    """The row's PRINTED description off the sheet. `Card` carries no
    description field -- the face is codegen's business -- so the sheet is the
    one place the words live on this side."""
    import yaml
    from pathlib import Path
    sheet = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "docs"
         / "prototype-surface.yaml").read_text(encoding="utf-8"))
    return next(r["description"] for r in sheet if r["id"] == card_id)


@pytest.fixture(autouse=True)
def arm(monkeypatch):
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)


def _state(ascension: bool = False):
    p = loader.build_player("kokomi")
    p.powers["kurage_summon"] = 3
    if ascension:
        p.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(7))


def _plan_card(plan):
    return Card(id="eb501_probe", name="probe", cost=0, type="skill",
                character="kokomi", plan=plan)


def _write(state, plans):
    for plan in plans:
        kokomi_plan.schedule(state, _plan_card([plan]))


# ---- EB-501: the morning's depth ------------------------------------------

def test_a_plain_morning_counts_one_per_written_plan():
    state = _state()
    _write(state, [{"op": "draw", "amount": 1}, {"op": "draw", "amount": 1}])

    kokomi_plan.resolve_all(state)

    assert state.kk_plans_this_morning == 2


def test_a_doubled_morning_counts_the_carry_outs():
    """The row's own case: one Plan, two carry-outs, and every reader that
    says "carried out this morning" sees two."""
    state = _state(ascension=True)
    _write(state, [{"op": "draw", "amount": 1}])

    kokomi_plan.resolve_all(state)

    assert state.kk_plans_this_morning == 2


def test_an_empty_morning_still_reads_zero():
    state = _state(ascension=True)

    kokomi_plan.resolve_all(state)

    assert state.kk_plans_this_morning == 0


def test_the_depth_is_read_once_at_the_drain():
    """SOURCE-READ: the count must not be accumulated inside the loop, or a
    Tide Wall written last would answer a different number from one written
    first."""
    body = kokomi_plan.resolve_all.__code__.co_names

    assert "carry_out_times" in body
    assert body.index("kk_plans_this_morning") < body.index("_resolve_entry")


# ---- EB-501: what Well Laid pays -----------------------------------------

def _well_laid_damage(state) -> int:
    row = _row("proto_kk_well_laid")
    before = state.enemies[0].hp
    from tier0.engine import effects
    effects.resolve_card(state, row)
    return before - state.enemies[0].hp


def test_well_laid_pays_its_floor_on_an_empty_morning():
    state = _state()
    kokomi_plan.resolve_all(state)

    assert _well_laid_damage(state) == 2


def test_well_laid_pays_three_per_carry_out():
    state = _state()
    _write(state, [{"op": "draw", "amount": 1}])
    kokomi_plan.resolve_all(state)

    assert _well_laid_damage(state) == 2 + 3


def test_a_doubled_morning_pays_well_laid_six():
    """The row's acceptance."""
    state = _state(ascension=True)
    _write(state, [{"op": "draw", "amount": 1}])
    kokomi_plan.resolve_all(state)

    assert _well_laid_damage(state) == 2 + 6


def test_well_laids_face_prints_the_live_total_and_nothing_else():
    """`EB-539` (Kokomi r19 lane 2, a D default). The face used to carry the
    rule as well as the number -- "Deal 2 damage, already including 3 for each
    Plan carried out this morning" -- and on a BARE morning the seat read that
    as self-contradictory: 2 cannot already include a 3 that nothing paid. It
    was `EB-441`'s clause working exactly as written, on the one board where
    the fold is zero.

    A card has ONE face and no runtime branch can print two live numbers
    (`CardModel.Description` is not virtual; BaseLib's only runtime swap is
    `{IfUpgraded:show:}`, which asks about the card and not the board), so the
    remedy is the codebase's own for this shape -- Undertow's `ForDebuffRider`
    (`EB-484`), one count over. The FACE prints the live total; the RULE and
    the live count go on the rider tip
    (`KokomiRiderTips.ForMorningDamageRider`)."""
    face = _face("proto_kk_well_laid")

    assert face == "Deal {CalculatedDamage:diff()} damage."
    assert "already including" not in face
    assert "Deals" not in face


# ---- EB-503: Tide Chart --------------------------------------------------

def _tide_chart_paid(state):
    return [row for row in state.log if row["event"] == "tide_chart_paid"]


def test_tide_chart_draws_one_per_carry_out():
    state = _state()
    kokomi_plan.promise_tide_chart(state, per=1, flat=0)
    _write(state, [{"op": "draw", "amount": 1}, {"op": "draw", "amount": 1}])
    kokomi_plan.resolve_all(state)
    kokomi_plan.pay_tide_charts(state)

    assert _tide_chart_paid(state)[0]["cards"] == 2


def test_a_doubled_morning_draws_twice():
    """The row's acceptance: one written Plan, two carry-outs, two cards."""
    state = _state(ascension=True)
    kokomi_plan.promise_tide_chart(state, per=1, flat=0)
    _write(state, [{"op": "draw", "amount": 1}])
    kokomi_plan.resolve_all(state)
    kokomi_plan.pay_tide_charts(state)

    assert _tide_chart_paid(state)[0]["cards"] == 2


def test_the_payment_still_says_what_it_paid():
    """The sim's twin of the C# line: the row that names the draw exists and
    carries the number, which is what the page prints from."""
    state = _state()
    kokomi_plan.promise_tide_chart(state, per=1, flat=1)
    _write(state, [{"op": "draw", "amount": 1}])
    kokomi_plan.resolve_all(state)
    kokomi_plan.pay_tide_charts(state)

    row = _tide_chart_paid(state)[0]
    assert row["cards"] == 2 and row["plans"] == 1


# ---- EB-500: the morning is what doubles ---------------------------------

def test_the_ascension_doubles_the_morning():
    state = _state(ascension=True)
    _write(state, [{"op": "draw", "amount": 1}])
    before = len(state.player.hand)

    kokomi_plan.resolve_all(state)

    assert len(state.player.hand) - before == 2


def test_writing_a_plan_under_the_ascension_carries_nothing_out():
    """`EB-570`. THE MOON OVERLOOKS THE WATERS IS WITHDRAWN, so there is no
    now-copy for the Ascension to be asked about: writing banks the Plan and
    the board waits for the morning, which is rule 2 whole."""
    state = _state(ascension=True)
    before = len(state.player.hand)

    kokomi_plan.schedule(state, _plan_card([{"op": "draw", "amount": 1}]))

    assert len(state.player.hand) - before == 0
    assert len(state.kk_plan_queue) == 1
    assert not hasattr(kokomi_plan, "PLANS_ALSO_NOW")


def test_the_face_and_the_power_tip_both_name_the_morning():
    face = _face("proto_kk_nereids_ascension")
    from pathlib import Path
    gen = (Path(__file__).resolve().parents[2] / "tools"
           / "gen_klee_cards.py").read_text(encoding="utf-8")

    assert face.startswith("At the start of your turn, ")
    assert ('"At the start of your turn, the [gold]Bake-Kurage[/gold] "\n'
            '        "carries out every [gold]Plan[/gold] twice."') in gen
