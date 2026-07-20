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


def test_max_stacks_caps_power():
    st = make_state()
    card = loader.get_card("explosives_workshop")   # v0.2: amount 2, cap 4
    for _ in range(5):
        effects.resolve_card(st, card)
    assert st.player.powers["bomb_damage_up"] == 4


def test_n_per_detonation_formula():
    st = make_state()
    st.detonations_total = 5
    gf = loader.get_card("grand_finale")            # v0.2: 2 per detonation
    effects.resolve_card(st, gf)
    dmg = [e for e in st.log if e["event"] == "damage"][-1]
    assert dmg["base"] == 10 + 2 * 5


def test_burst_retain_keeps_card_in_hand():
    pilot = make_pilot(loader.pilot_weights("reaction"))
    player = loader.build_player("klee", "reaction_weighted")
    player.draw_pile.insert(0, loader.get_card("sparks_n_splash"))
    state = run_fight(player, loader.build_encounter("attrition"), pilot,
                      seed=3)
    drawn = any(e["event"] == "draw" and e["card"] == "sparks_n_splash"
                for e in state.log)
    discarded_burst = any(c.id == "sparks_n_splash"
                          for c in state.player.discard_pile)
    assert drawn and not discarded_burst    # retained or cast, never cycled


def test_burst_cast_rate_with_retain():
    # Ruling 5 acceptance: cast in the majority of fights that reach a
    # full meter (was ~never before Retain).
    pilot = make_pilot(loader.pilot_weights("reaction"))
    full, cast = 0, 0
    for seed in range(30):
        player = loader.build_player("klee", "reaction_weighted")
        player.draw_pile.append(loader.get_card("sparks_n_splash"))
        state = run_fight(player, loader.build_encounter("attrition"), pilot,
                          seed=seed)
        events = [e["event"] for e in state.log]
        if "burst_cast" in events:
            full += 1
            cast += 1
        elif state.player.burst_energy >= state.player.burst_max:
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


def test_barbara_injection_raises_a4():
    klee = score_config("klee", "barbara_injection", "reaction",
                        FIGHTS, SEED)
    assert klee["scores"]["A4_sustain"] > 0.5
    assert klee["raw"]["A4_sustain"] > 3            # actual healing/fight


def test_a6_ordering_anchor():
    # Ruling 2 sanity: Ironclad-package < Klee on the AoE term.
    pkg = score_config("ref_ironclad", "archetype_package", "generic",
                       FIGHTS, SEED)
    klee = score_config("klee", "demolition_weighted", "demolition",
                        FIGHTS, SEED)
    assert klee["raw"]["A6_aoe"] > pkg["raw"]["A6_aoe"]
    assert klee["scores"]["A6_utility"] > 3.0


def test_a1_gt_a2_constraint_wired():
    # The mechanism, not the verdict: whether v0.2 satisfies A1>A2 at
    # scorecard fight-counts is reported in the pass-2 report. Here we
    # assert the constraint is loaded and, when violated, flagged with
    # both scores in the message.
    assert loader.character_constraints("klee") == [
        "A1_frontload>A2_scaling"]
    klee = score_config("klee", "demolition_weighted", "demolition",
                        FIGHTS, SEED)
    for f in klee["heuristic_flags"]:
        if "CONSTRAINT" in f:
            assert "A1_frontload>A2_scaling" in f and "vs" in f


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
