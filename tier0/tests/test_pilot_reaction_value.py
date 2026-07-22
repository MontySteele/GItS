"""Focused guards for the pilot's elemental-reaction valuation."""

import pytest

from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _pyro_attack(target="enemy", times=1):
    return Card(
        id="probe", name="Probe", cost=1, type="attack", element="pyro",
        effects=[{"op": "damage", "amount": 5, "target": target,
                  "times": times, "applies_element": True}],
    )


def test_single_target_does_not_claim_another_enemys_aura():
    low = make_enemy(hp=10, name="aimed")
    high = make_enemy(hp=20, name="other")
    high.aura = "hydro"
    st = make_state([low, high])

    assert policy._reaction_value(st, _pyro_attack()) == 2.0


def test_all_enemy_trigger_values_each_available_reaction():
    first = make_enemy(name="first")
    second = make_enemy(name="second")
    first.aura = "hydro"
    second.aura = "cryo"
    st = make_state([first, second])

    assert policy._reaction_value(st, _pyro_attack("all_enemies")) == 12.0


def test_apply_only_effect_uses_its_own_element():
    enemy = make_enemy()
    enemy.aura = "pyro"
    st = make_state([enemy])
    card = Card(
        id="hydro_probe", name="Hydro Probe", cost=1, type="skill",
        effects=[{"op": "apply_aura", "element": "hydro", "target": "enemy"}],
    )

    assert policy._reaction_value(st, card) == 6.0


def test_random_multihit_uses_expected_distinct_reactable_targets():
    aura = make_enemy(name="aura")
    blank = make_enemy(name="blank")
    aura.aura = "hydro"
    st = make_state([aura, blank])

    # One reactable target among two, hit twice: P(hit at least once)=0.75.
    assert policy._reaction_value(
        st, _pyro_attack("random_enemy", times=2)) == pytest.approx(4.5)
