"""The Stage retires Furina's shipped Burst (2026-09-26).

The Stage retired Burst along with Encore and Fanfare. The reframe's Burst
guard left with the reframe (`EB-726`) and nothing replaced it, so under the
Stage a reaction fed her shipped meter again -- in the mod and here -- and a
full run on 0.2.3820+proto was granted and played the shipped Let the People
Rejoice at 70. The guard is `resources.stage_retires_the_shipped_meters`, at
the income funnel (`resources.gain_burst`) and at the grant
(`combat.grant_charged_kit`). The C# twin's pins are in
`klee-mod/KleeTests/Prototype/FurinaStageUiCleanupTests.cs`.
"""
from __future__ import annotations

import random

import pytest

from tier0.engine import combat, furina_stage, reactions, resources
from tier0.engine.state import Card, CombatState, Enemy, Player


@pytest.fixture(params=[True, False], ids=["arm_on", "arm_off"])
def arm(request, monkeypatch):
    monkeypatch.setattr(furina_stage, "FURINA_STAGE", request.param)
    return request.param


def _kit():
    return Card(id="let_the_people_rejoice", name="Let the People Rejoice",
                cost=0, type="attack", rarity="special", effects=[],
                kit_card=True)


def _state():
    player = Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina",
                    burst_max=70, kit_cards=[_kit()])
    enemy = Enemy(hp=500, max_hp=500, name="paper",
                  intents=[{"kind": "block", "amount": 0}])
    return CombatState(player=player, enemies=[enemy], rng=random.Random(0))


def test_a_reaction_pays_burst_only_with_the_arm_off(arm):
    state = _state()
    enemy = state.enemies[0]
    reactions.apply_aura(state, enemy, "hydro")
    reactions.resolve_hit(state, enemy, "anemo", 5)   # Swirl
    assert state.reactions_this_turn == 1
    if arm:
        assert state.player.burst_energy == 0
    else:
        assert state.player.burst_energy > 0


def test_the_funnel_itself_refuses_under_the_arm(arm):
    state = _state()
    resources.gain_burst(state, 5, "probe")
    assert state.player.burst_energy == (0 if arm else 5)


def test_the_kit_card_is_never_granted_under_the_arm(arm):
    state = _state()
    # A meter already at its max (a save, or anything outside the funnel):
    # the grant asks the arm itself.
    state.player.burst_energy = state.player.burst_max
    combat.grant_charged_kit(state)
    granted = [c.id for c in state.player.hand]
    assert granted == ([] if arm else ["let_the_people_rejoice"])
