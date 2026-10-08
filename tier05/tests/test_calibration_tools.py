"""Regression locks for the realistic-loadout calibration instruments."""

import random
from types import SimpleNamespace

from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tools import realistic_axis_scores


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
        (["blood_potion"], 70, 70),       # Klee 70 HP since 2026-10-02
        ([], 73, 73),
    ]
