"""Regression locks for the realistic-loadout calibration instruments."""

import random
from types import SimpleNamespace

from tier0.engine import combat
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy, make_state
from tools import burst_defense, realistic_axis_scores


def test_burst_probe_records_wall_raised_not_only_block_consumed():
    state = make_state(hp=80, enemies=[make_enemy(
        intents=[{"kind": "attack", "amount": 23}])])
    state.player.block = 30

    combat._enemy_turn(state, state.enemies[0])

    hit = next(e for e in state.log if e["event"] == "player_hit")
    assert hit["block_before"] == 30
    assert burst_defense._turn_incoming(state) == {0: (23, 23, 30)}


def test_loadout_uses_elite_context_for_booming_conch():
    run = SimpleNamespace(
        relics=["booming_conch"], potions_end=[], potions_used=[], deck_ids=[])

    _, effects, _, _ = realistic_axis_scores._loadout(run, "klee")
    _, boss_effects, _, _ = realistic_axis_scores._loadout(run, "klee", "B")

    assert {fx["hook"] for fx in effects} == {
        "combat_start_draw", "combat_start_energy"}
    assert boss_effects == []


def test_loaded_gauntlet_carries_potions_and_max_hp_between_stages(
        monkeypatch):
    seen = []

    monkeypatch.setattr(realistic_axis_scores.loader, "encounter_ids",
                        lambda: ["gauntlet"])
    monkeypatch.setattr(realistic_axis_scores.loader, "encounter_stages",
                        lambda encounter: ["stage_1", "stage_2"])
    monkeypatch.setattr(realistic_axis_scores.loader, "build_encounter",
                        lambda stage: [make_enemy()])

    def win_and_spend(player, enemies, pilot, seed):
        seen.append((list(player.potions), player.hp, player.max_hp))
        if player.potions:
            player.potions.pop(0)
        if len(seen) == 1:
            player.max_hp += 3
            player.hp += 3
        for enemy in enemies:
            enemy.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))

    monkeypatch.setattr(realistic_axis_scores, "run_fight", win_and_spend)

    realistic_axis_scores._battery(
        "klee", [], lambda state: None, fights=1, seed=7,
        potions=["blood_potion"], node_kind="elite")

    assert seen == [
        (["blood_potion"], 62, 62),
        ([], 65, 65),
    ]
