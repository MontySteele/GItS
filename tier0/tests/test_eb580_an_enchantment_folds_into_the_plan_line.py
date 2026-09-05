"""`EB-580`: a card's own enchantment folds into its Plan line's number.

WHAT THE SEAT SAW (Kokomi r21, natural lane, (c) 3). A Sharp 2 raised
*Riptide*'s now-line from 9 to 11 and left its Plan line printing 13. Nothing
on the screen said which of the two lines the enchantment had bought, so the
pair read as a fact about the card: the Plan premium had shrunk from 4 to 2
and the now-line was the better half. It "silently reversed the right play on
my best card".

THE RULE, taken at the r21 packet's D default: a card's own enchantment
applies to BOTH its lines, since both are the card's.

WHY IT WAS MISSING RATHER THAN REFUSED. The rider is folded where a CARD deals
damage -- `effects` reads `enchant_damage` inside its `type == "attack"`
branch, and the mod folds it inside `Hook.ModifyDamage` off the play's
`cardSource` -- and a planned clause is not a card being played (`EB-538`), so
nothing on the path from the queue to the board had the card in its hand to
ask. `kokomi_plan._enchanted` asks it once, at writing time, which is Crystal
Collapse's and Flank's rule: what the player was looking at when they decided
to write the Plan.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import pytest

from tier0.content import enchantments, loader
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import kokomi_state, overhaul  # noqa: F401

RIPTIDE = "proto_kk_riptide"
SHARP = 2


def _riptide(sharp: int = 0):
    card = loader.get_card(RIPTIDE)
    if sharp:
        enchantments.apply(card, "sharp", sharp)
    return card


def _printed_plan(card) -> int:
    return int(card.plan[0]["amount"])


def test_riptide_under_sharp_two_writes_the_folded_plan_number(overhaul):
    """THE ROW'S ACCEPTANCE, half one: the number that goes into the queue."""
    plain = _printed_plan(_riptide())
    state = kokomi_state(enemies=[make_enemy(hp=400)])

    kokomi_plan.schedule(state, _riptide(sharp=SHARP))

    entry = state.kk_plan_queue[0]
    assert entry.clauses[0]["amount"] == plain + SHARP


def test_and_the_morning_deals_it(overhaul):
    """THE ROW'S ACCEPTANCE, half two: what the jellyfish actually does with
    it. The clause is `all_enemies`, so one body is the whole read."""
    plain = _printed_plan(_riptide())
    enemy = make_enemy(hp=400)
    state = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(state, _riptide(sharp=SHARP))

    kokomi_plan.resolve_all(state)

    assert 400 - enemy.hp == plain + SHARP


def test_an_unenchanted_copy_in_the_same_hand_is_untouched(overhaul):
    """THE RIDER RIDES THE INSTANCE, which is R82's whole shape and the reason
    the fold is a fact about the CARD and not about the row."""
    plain = _printed_plan(_riptide())
    state = kokomi_state(enemies=[make_enemy(hp=400)])

    kokomi_plan.schedule(state, _riptide())
    kokomi_plan.schedule(state, _riptide(sharp=SHARP))

    assert [e.clauses[0]["amount"] for e in state.kk_plan_queue] == [
        plain, plain + SHARP]


def test_the_multiplier_folds_after_the_flat_rider(overhaul):
    """Corrupted's x1.5 multiplies the SUM, which is the order the card's own
    damage takes one file over -- and it is the order `KokomiPlan.Enchanted`
    asks the base game's two calls in."""
    card = _riptide(sharp=SHARP)
    card.enchant_damage_mult = 1.5
    plain = _printed_plan(_riptide())
    state = kokomi_state(enemies=[make_enemy(hp=400)])

    kokomi_plan.schedule(state, card)

    assert state.kk_plan_queue[0].clauses[0]["amount"] == int(
        (plain + SHARP) * 1.5)


def test_the_first_play_rider_is_not_folded(overhaul):
    """VIGOROUS IS THE ONE RIDER A PLAN CANNOT CARRY. "The first time this card
    is PLAYED" is spent by the play that wrote the Plan, so folding it again at
    the morning would pay one printed rider twice."""
    card = _riptide()
    card.enchant_first_play_damage = 5
    plain = _printed_plan(card)
    state = kokomi_state(enemies=[make_enemy(hp=400)])

    kokomi_plan.schedule(state, card)

    assert state.kk_plan_queue[0].clauses[0]["amount"] == plain


def test_a_clause_with_no_printed_number_is_left_alone(overhaul):
    """A flat rider joins a flat number. `damage_per_companion_last_turn` is a
    RATE -- a flat add there would be paid once per body counted -- and
    `damage_quarter_max_hp` prints no number at all, so there is nothing on
    either face the fold could be about."""
    card = _riptide(sharp=SHARP)
    card.plan = [{"op": "damage_quarter_max_hp", "target": "enemy"},
                 {"op": "damage_per_companion_last_turn", "amount": 3,
                  "target": "enemy"}]
    state = kokomi_state(enemies=[make_enemy(hp=400)])

    kokomi_plan.schedule(state, card)

    assert state.kk_plan_queue[0].clauses[1]["amount"] == 3
