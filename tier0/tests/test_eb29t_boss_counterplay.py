"""EB-29t — the pilot reads the promoted Test Subject mechanics (POLICY 6).

R128 landed the boss's real Enrage / Nemesis-Intangible and the C7
instrument read 0.0-3.9% full-HP for every character: the pilot played the
dossier's documented WORST line (skills fed +2 permanent Strength each, and
whole turns were dumped into 1-damage-per-hit Intangible). These pin the two
reads: the Enrage skill tax in `_score` and the Intangible per-hit cap in
`_expected_damage`.
"""

from tier0 import constants as C
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _card(**kw):
    d = dict(id="eb29t_test", name="t", cost=1, type="skill",
             character="klee")
    d.update(kw)
    return Card(**d)


W = {"damage": 1.0, "block": 1.0, "scaling": 1.0, "reaction": 1.0,
     "tempo": 1.0, "cost": 1.0}


def test_skills_are_taxed_under_enrage_and_attacks_are_not():
    st = make_state(enemies=[make_enemy(
        hp=300, intents=[{"kind": "attack", "amount": 10, "times": 3}])])
    skill = _card(type="skill", effects=[{"op": "block", "amount": 6}])
    attack = _card(type="attack", effects=[{"op": "damage", "amount": 6}])

    base_skill = policy._score(st, skill, W)
    base_attack = policy._score(st, attack, W)
    st.enemies[0].powers["enrage"] = 2
    taxed_skill = policy._score(st, skill, W)
    taxed_attack = policy._score(st, attack, W)

    # 2 enrage x 3 hits, over the priced horizon.
    expected = 2 * 3 * policy.ENRAGE_TAX_TURNS * C.PILOT_FUTURE_DAMAGE_DISCOUNT
    assert taxed_skill == base_skill - expected
    assert taxed_attack == base_attack


def test_the_tax_reads_the_intents_ramp():
    st = make_state(enemies=[make_enemy(
        hp=300, intents=[{"kind": "attack", "amount": 10, "times": 3,
                          "times_ramp_per_use": 1}])])
    e = st.enemies[0]
    e.powers["enrage"] = 2
    skill = _card(type="skill", effects=[{"op": "block", "amount": 6}])
    before = policy._score(st, skill, W)
    e.intent_uses[0] = 2                    # Multi-Claw at its third use
    after = policy._score(st, skill, W)
    # Two more hits per turn -> a bigger tax on the same skill.
    assert after < before


def test_intangible_caps_the_priced_damage_per_hit():
    st = make_state(enemies=[make_enemy(hp=300)])
    attack = _card(type="attack",
                   effects=[{"op": "damage", "amount": 9, "times": 2}])
    open_turn = policy._expected_damage(st, attack)
    assert open_turn == 18
    st.enemies[0].powers["intangible"] = 1
    closed_turn = policy._expected_damage(st, attack)
    assert closed_turn == 2 * C.INTANGIBLE_DAMAGE_CAP


def test_intangible_cap_is_per_target_not_global():
    st = make_state(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    st.enemies[0].powers["intangible"] = 1
    aoe = _card(type="attack",
                effects=[{"op": "damage", "amount": 7,
                          "target": "all_enemies"}])
    # One closed target, one open one.
    assert policy._expected_damage(st, aoe) == C.INTANGIBLE_DAMAGE_CAP + 7
