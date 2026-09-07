"""`EB-603`: Gorou's Block is half the damage actually removed, kill included.

WHAT THE SEAT SAW (Furina r16, assembled lane). *Gorou - Inuzaka All-Round
Defense* printed "Deal 12 damage. Gain Block equal to half the damage dealt",
took a 12-HP body off the board, and gave 0 Block. "Both times I played Gorou
this run it was a killing blow, so I cannot separate 'the clause is broken'
from 'the clause does not fire on a kill'. It needs one non-lethal test."

WHAT THE READ FOUND, and it is two things rather than one.

FIRST, THE NUMBER WAS THE SWING AND NOT THE LOSS. `deal_damage_to_enemy`
handed the arm's reader `hp_dmg` -- damage past Block, overkill and all --
while the function's own `damage` event has always printed the clamped figure
and this reader's docstring has always promised "damage that reached HP, not
the swing". So a killing blow paid Block for damage no body took. The C# read
`DamageResult.UnblockedDamage` and had the same gap; `DamageResult` carries
`OverkillDamage` as its own field, so subtracting it is a read rather than a
second definition. Both engines now count what the body lost.

SECOND, A CREATURE WITH NO COMBAT COULD WIPE THE LEDGER.
`CompanionOverhaulLedger.For` drops the whole table whenever the combat it is
handed differs from the last one, and a card whose owner is off the board --
a compendium copy, a reward-screen copy, a deck view -- answers `null`. Two
speculative call sites can be handed exactly that (a face's multiplier lambda
and a smart-description getter that runs "on every tooltip read"), and a wipe
between the hit and the Block is a 0 on a beat that dealt damage. Guarded.
That half is C#-only; this engine keeps the total on the state.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.tests.conftest import make_enemy, make_state

GOROU = "proto_mi_gorou_inuzaka"


@pytest.fixture
def arm(monkeypatch):
    """The Inazuma companion overhaul on, and the loader's caches cleared on
    the way in and out -- `test_inazuma_companion_overhaul`'s own fixture."""
    loader.reset_arm_caches()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    loader.reset_arm_caches()


def _state(enemy):
    st = make_state(enemies=[enemy], hp=80)
    st.player.character_id = "klee"
    st.in_player_turn = True
    return st


def test_gorou_killing_an_eight_hp_body_gains_four(arm):
    """THE ROW'S ACCEPTANCE. The printed 8 kills a body that had exactly 8 to
    give, so 8 was removed and half of 8 is 4 -- and it arrives on the kill."""
    enemy = make_enemy(hp=8)
    state = _state(enemy)

    effects.resolve_card(state, loader.get_card(GOROU))

    assert not enemy.alive
    assert state.player.block == 4


def test_the_overkill_is_not_paid_for(arm):
    """A 1-HP body pays 0, not 4: what a body did not lose is not damage
    dealt to it. R212's one-way rule -- the doubt pays LESS Block."""
    enemy = make_enemy(hp=1)
    state = _state(enemy)

    effects.resolve_card(state, loader.get_card(GOROU))

    assert not enemy.alive
    assert state.player.block == 0


def test_a_survivor_still_pays_half_the_whole_hit(arm):
    """The non-lethal read the seat could not take. Nothing about the clause
    changed where no body dies: the printed 8 lands whole and pays 4."""
    enemy = make_enemy(hp=40)
    state = _state(enemy)

    effects.resolve_card(state, loader.get_card(GOROU))

    assert enemy.alive and enemy.hp == 32
    assert state.player.block == 4


def test_block_absorbs_before_the_half_is_taken(arm):
    """Block the hit never got past is not damage dealt either, and that half
    of the reading is unchanged: 6 Block off an 8 leaves 2 on HP and 1 Block
    for Gorou."""
    enemy = make_enemy(hp=40)
    enemy.block = 6
    state = _state(enemy)

    effects.resolve_card(state, loader.get_card(GOROU))

    assert state.player.block == 1
