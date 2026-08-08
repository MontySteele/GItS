"""EB-57: the reaction amp counter reports REALIZED uplift.

`reactions._react` can only see `out - damage` -- the amplifier's delta at the
moment the aura is consumed, which sits ABOVE every multiplier that then scales
the amplified hit (Vulnerable and its refpowers relatives, the Slow term) and
above block and the overkill clamp. The instrument published that number as
"the reaction's contribution", so an amped hit into a Vulnerable body
under-reported its own uplift -- and Superconduct applies Vulnerable, so
reaction decks manufactured their own under-read.

The ledger fixture (`review/redteam/fixtures/track_o/s08-amp-before-multipliers.py`)
is the shape pinned here: a 20-damage Pyro hit into a Hydro aura reported
amp = 10 in both arms, where the true uplift is 10 clean and 15 into
Vulnerable 2. The honest quantity is the difference in damage that ACTUALLY
LANDED, so an amp whose whole contribution was overkill contributes 0.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.engine import effects, powers, reactions
from tier0.engine.state import CombatState, Enemy, Player
from tier0.harness import metrics

BASE = 20


def _state(hp: int = 10_000) -> CombatState:
    return CombatState(
        player=Player(hp=80, max_hp=80),
        enemies=[Enemy(hp=hp, max_hp=hp, name="dummy",
                       intents=[{"kind": "attack", "amount": 0}])],
        rng=random.Random(0))


def _vaporize(vulnerable: int = 0, hp: int = 10_000, block: int = 0) -> dict:
    """One 20-damage Pyro attack into a standing Hydro aura."""
    st = _state(hp)
    e = st.enemies[0]
    e.block = block
    reactions.apply_aura(st, e, "hydro")
    if vulnerable:
        powers.apply_power(st, e, "vulnerable", vulnerable)
    effects.deal_damage_to_enemy(st, e, BASE, element="pyro", source="attack")
    s = metrics.extract(st, hp_start=80)
    return {"amp": s.reaction_damage_amp, "all": s.damage_all_ops,
            "base_ops": s.damage_from_base_ops}


def _no_aura(vulnerable: int = 0, hp: int = 10_000, block: int = 0) -> int:
    """The counterfactual: the same hit with nothing to react with."""
    st = _state(hp)
    e = st.enemies[0]
    e.block = block
    if vulnerable:
        powers.apply_power(st, e, "vulnerable", vulnerable)
    effects.deal_damage_to_enemy(st, e, BASE, element="pyro", source="attack")
    return metrics.extract(st, hp_start=80).damage_all_ops


def test_clean_amp_reports_its_own_delta():
    """The undisturbed case, unchanged by the fix: 20 -> 30 is an uplift of 10."""
    got = _vaporize()
    assert got["all"] == int(BASE * C.VAPORIZE_MULT) == 30
    assert got["amp"] == 10 == got["all"] - _no_aura()


def test_amp_into_vulnerable_reports_15_not_10():
    """THE FIXTURE. Vulnerable scales the amplified hit too, and that uplift is
    the reaction's: 45 landed where 30 would have. The pre-fix instrument said
    10 -- the raw multiplier delta, sampled before Vulnerable ran."""
    got = _vaporize(vulnerable=2)
    assert got["all"] == 45 and _no_aura(vulnerable=2) == 30
    assert got["amp"] == 15                      # was 10
    # the derived splits move with it: the base op gets its own 30, no more
    assert got["base_ops"] == 30                 # was 35


def test_amp_is_clamped_by_overkill():
    """An amp that only added overkill added nothing. 20 into a 25 HP body
    vaporizes to 30, of which 25 lands; the unamplified 20 would all have
    landed, so the realized uplift is 5, not the raw 10."""
    got = _vaporize(hp=25)
    assert got["all"] == 25 and _no_aura(hp=25) == 20
    assert got["amp"] == 5

    # and when the body dies to the unamplified hit anyway, the amp is worth 0
    dead = _vaporize(hp=15)
    assert dead["all"] == 15 and _no_aura(hp=15) == 15
    assert dead["amp"] == 0


def test_amp_is_clamped_by_block():
    """Block eats the bottom of the hit, so the uplift is measured on what
    reached HP: 30 - 24 = 6 landed, against 0 for the unamplified 20."""
    got = _vaporize(block=24)
    assert got["all"] == 6 and _no_aura(block=24) == 0
    assert got["amp"] == 6


def test_a_non_amplifying_reaction_still_reports_zero_amp():
    """Superconduct deals no amp damage; the settle pass must not invent one."""
    st = _state()
    e = st.enemies[0]
    reactions.apply_aura(st, e, "cryo")
    effects.deal_damage_to_enemy(st, e, BASE, element="electro", source="attack")
    rows = [ev for ev in st.log if ev["event"] == "reaction"]
    assert len(rows) == 1 and rows[0]["reaction"] == "superconduct"
    assert rows[0]["amp_delta"] == 0
    assert metrics.extract(st, hp_start=80).reaction_damage_amp == 0
