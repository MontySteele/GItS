"""Pass-2 ruling verification (docs/pass1-rulings-round2.md)."""

import pytest

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_config
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_state

FIGHTS = 100
SEED = 11


def test_duplicate_klee_powers_stack_without_arbitrary_caps():
    st = make_state()
    card = loader.get_card("explosives_workshop")
    for _ in range(5):
        effects.resolve_card(st, card)
    assert st.player.powers["bomb_damage_up"] == 10

    spark_style = loader.get_card("spark_knight_style")
    for _ in range(3):
        effects.resolve_card(st, spark_style)
    assert st.player.powers["zero_cost_attacks_up"] == 6

    playtime = loader.get_card("playtime_forever")
    for _ in range(2):
        effects.resolve_card(st, playtime)
    assert st.player.powers["bomb_and_spark_per_turn"] == 2


def test_live_playtest_card_patch_is_loaded():
    assert loader.get_card("chained_reactions").cost == 0
    assert loader.get_card("barbara_shining_idol").cost == 1
    assert loader.get_card("sparks_n_splash").cost == 0

    warm = loader.get_card("warm_glow")
    assert warm.effects[0] == {"op": "block", "amount": 6}

    bright = loader.get_card("bright_idea")
    assert bright.effects[-1] == {"op": "energy", "amount": 1}

    no_holding = loader.get_card("no_holding_back")
    assert no_holding.cost == 1
    assert not any(fx.get("target") == "self" for fx in no_holding.effects)


def test_n_per_detonation_formula():
    st = make_state()
    st.detonations_total = 5
    gf = loader.get_card("grand_finale")            # v0.2: 2 per detonation
    effects.resolve_card(st, gf)
    dmg = [e for e in st.log if e["event"] == "damage"][-1]
    assert dmg["base"] == 10 + 2 * 5


def test_burst_arrives_by_grant_and_never_cycles():
    # v1.9: the Burst is kit -- granted to hand when the meter fills (no
    # card is seeded into the deck), retained across turns (v1.4), and
    # returned to the kit on cast. It must never appear in ANY pile: not
    # discarded (Retain), not exhausted (kit, not deck contents).
    pilot = make_pilot(loader.pilot_weights("reaction"))
    granted = 0
    for seed in range(10):
        player = loader.build_player("klee", "reaction_weighted")
        state = run_fight(player, loader.build_encounter("attrition"), pilot,
                          seed=seed)
        if any(e["event"] == "kit_burst_granted" for e in state.log):
            granted += 1
        for pile in (state.player.discard_pile, state.player.exhaust_pile,
                     state.player.draw_pile):
            assert not any(c.id == "sparks_n_splash" for c in pile)
    assert granted > 0


def test_burst_cast_rate_with_retain():
    # Ruling 5 acceptance: cast in the majority of fights that reach a
    # full meter (was ~never before Retain). v1.9 makes the reach-full
    # condition observable as the grant event.
    pilot = make_pilot(loader.pilot_weights("reaction"))
    full, cast = 0, 0
    for seed in range(30):
        player = loader.build_player("klee", "reaction_weighted")
        state = run_fight(player, loader.build_encounter("attrition"), pilot,
                          seed=seed)
        events = [e["event"] for e in state.log]
        if "burst_cast" in events:
            full += 1
            cast += 1
        elif "kit_burst_granted" in events:
            full += 1
    assert full > 0
    assert cast / full > 0.5


def test_a4_baseline_heals_and_klee_floors():
    base = score_config("ref_ironclad", "starter", "generic", FIGHTS, SEED)
    assert base["raw"]["A4_sustain"] > 0            # Burning Blood anchor
    assert base["scores"]["A4_sustain"] == pytest.approx(3.0)
    klee = score_config("klee", "demolition_weighted", "demolition",
                        FIGHTS, SEED)
    assert klee["scores"]["A4_sustain"] == 0.5      # zero-healing floor


def test_sustain_probe_raises_a4():
    """R8: the barbara_injection instrument died with the conjunctive
    healing law (its heals converted to block/meter). The A4 probe now
    borrows the anchor's exempt relic trickle (heal_after_won_fight via
    package_relic_hooks) -- instrument class change flagged in the M8
    report; the axis must still respond to healing when it exists."""
    klee = score_config("klee", "sustain_probe", "reaction",
                        FIGHTS, SEED)
    assert klee["scores"]["A4_sustain"] > 0.5
    assert klee["raw"]["A4_sustain"] > 3            # actual healing/fight
    # And the probe hook must not leak outside its package:
    from tier0.content import loader
    assert "heal_after_won_fight" not in loader.build_player(
        "klee", "reaction_weighted").relic_hooks


def test_a6_ordering_anchor():
    # Ruling 2 sanity: Ironclad-package < Klee on the AoE term.
    pkg = score_config("ref_ironclad", "archetype_package", "generic",
                       FIGHTS, SEED)
    klee = score_config("klee", "demolition_weighted", "demolition",
                        FIGHTS, SEED)
    assert klee["raw"]["A6_aoe"] > pkg["raw"]["A6_aoe"]
    assert klee["scores"]["A6_utility"] > 3.0


def test_a1_gt_a2_constraint_wired():
    # Round-3 restructure: hard on starter/median, warning on packages.
    assert loader.character_constraints("klee") == [
        "A1_frontload>A2_scaling"]
    klee = score_config("klee", "demolition_weighted", "demolition",
                        FIGHTS, SEED)
    for f in klee["heuristic_flags"]:
        assert "CONSTRAINT VIOLATED" not in f    # packages warn, not fail
        if "warn" in f:
            assert "A1_frontload>A2_scaling" in f


def test_pilot_regret_reported():
    stats = run_battery("klee", "demolition_weighted", "punisher",
                        "demolition", FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert "pilot_regret_rate" in s
    assert s["pilot_regret_rate"] < 0.25    # sanity bound, not a target


def test_enemy_intends_attack_predicate():
    from tier0.tests.conftest import make_enemy
    st = make_state(enemies=[make_enemy(intents=[{"kind": "block",
                                                  "amount": 5}])])
    assert not effects._predicate(st, "enemy_intends_attack")
    st2 = make_state()                       # default intent: attack
    assert effects._predicate(st2, "enemy_intends_attack")
