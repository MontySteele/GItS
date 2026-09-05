"""`EB-599`: the Plan line folds HER Strength, and nothing of the target's.

WHAT THE SEAT SAW (Kokomi r22, natural lane). *Kurage's Oath* printed
"Plan: Deal 10" under the target's Vulnerable, the seat paid for it, and the
morning carried out 7 once that Vulnerable had expired. "For a mechanic sold
on committing a turn early, the committed number moving is the sharpest
contradiction in the kit." Both lanes then read the two lines computing under
two rules: her Strength moved the own line only, and the target's Vulnerable
moved the Plan line only.

THE RULE, taken at the r22 packet's D default (sec.5): the Plan line folds
HERS -- her Strength and her enchantment -- and NOTHING of the target's. Rule
3 says her Strength counts for a carry-out, and a Plan resolves next morning
against whatever the target wears THEN, so the target's terms are exactly the
ones a line written today cannot honestly print.

WHERE IT IS FOLDED: at writing time, beside `EB-580`'s enchantment, so the
number the face previews is the number the queue holds and the number the
morning deals. `kokomi_plan.hers` is the one call; `KokomiPlan.Hers` is its
twin.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from tier0.content import enchantments, loader
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import kokomi_state, overhaul  # noqa: F401

OATH = "proto_kk_kurages_oath"
STRENGTH = 2


def _oath():
    return loader.get_card(OATH)


def _printed_plan(card) -> int:
    return int(card.plan[0]["amount"])


def test_oath_at_strength_two_under_vulnerable_writes_nine(overhaul):
    """THE ROW'S ACCEPTANCE, half one -- the number that goes into the queue.

    The printed 7 plus her Strength 2, and the body's Vulnerable is not in it:
    the old line printed 10 here (7 x 1.5) and the queue held 7.
    """
    enemy = make_enemy(hp=400)
    enemy.powers["vulnerable"] = 2
    state = kokomi_state(enemies=[enemy])
    state.player.powers["strength"] = STRENGTH

    kokomi_plan.schedule(state, _oath())

    assert state.kk_plan_queue[0].clauses[0]["amount"] == (
        _printed_plan(_oath()) + STRENGTH)


def test_and_the_morning_deals_nine_once_the_vulnerable_has_expired(overhaul):
    """THE ROW'S ACCEPTANCE, half two -- and it is the seat's own fight.

    The debuff that raised the old face is gone by the time the jellyfish
    acts, which is the whole reason the target's side cannot be previewed.
    """
    enemy = make_enemy(hp=400)
    enemy.powers["vulnerable"] = 1
    state = kokomi_state(enemies=[enemy])
    state.player.powers["strength"] = STRENGTH
    kokomi_plan.schedule(state, _oath())

    enemy.powers.pop("vulnerable")            # it expired overnight
    kokomi_plan.resolve_all(state)

    assert 400 - enemy.hp == _printed_plan(_oath()) + STRENGTH


def test_her_strength_is_read_when_the_plan_is_written_not_at_the_morning(
        overhaul):
    """A COMMITTED NUMBER DOES NOT MOVE, which is the row's whole complaint.
    A Vajra picked up after the Plan was written pays nothing into it."""
    state = kokomi_state(enemies=[make_enemy(hp=400)])
    kokomi_plan.schedule(state, _oath())

    state.player.powers["strength"] = 5

    assert state.kk_plan_queue[0].clauses[0]["amount"] == _printed_plan(_oath())


def test_the_enchantment_and_the_strength_fold_in_that_order(overhaul):
    """`EB-580`'s rider is still folded, and hers lands after it -- the order
    a card's own damage takes one file over (`enchant_damage`, then
    `modify_damage_dealt`'s Strength)."""
    card = _oath()
    enchantments.apply(card, "sharp", 3)
    card.enchant_damage_mult = 2.0
    state = kokomi_state(enemies=[make_enemy(hp=400)])
    state.player.powers["strength"] = STRENGTH

    kokomi_plan.schedule(state, card)

    assert state.kk_plan_queue[0].clauses[0]["amount"] == (
        int((_printed_plan(_oath()) + 3) * 2.0) + STRENGTH)


def test_her_weak_is_not_folded(overhaul):
    """THE ONE TERM OF HERS THAT STAYS OFF. Round four-c's finding took her
    Weak off a carry-out -- "a Strategic enemy's Weak cut two banked Plans to
    x0.75 the next morning" -- and the r22 default names her Strength and her
    enchantments, not the whole dealer funnel."""
    state = kokomi_state(enemies=[make_enemy(hp=400)])
    state.player.powers["weak"] = 2

    kokomi_plan.schedule(state, _oath())

    assert state.kk_plan_queue[0].clauses[0]["amount"] == _printed_plan(_oath())


def test_a_clause_with_no_printed_number_is_left_alone(overhaul):
    """`EB-580`'s boundary, unmoved: a flat term joins a flat number, and
    neither `damage_quarter_max_hp` nor the per-companion RATE has one."""
    card = _oath()
    card.plan = [{"op": "damage_quarter_max_hp", "target": "enemy"},
                 {"op": "damage_per_companion_last_turn", "amount": 3,
                  "target": "enemy"}]
    state = kokomi_state(enemies=[make_enemy(hp=400)])
    state.player.powers["strength"] = STRENGTH

    kokomi_plan.schedule(state, card)

    assert state.kk_plan_queue[0].clauses[1]["amount"] == 3
