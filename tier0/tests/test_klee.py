"""M4: Klee systems smoke tests — placeholder decks through the frozen
battery with archetype pilots. These validate the SYSTEMS (bombs, sparks,
reactions, instrumentation), not the placeholder card numbers."""

import pytest

from tier0.harness import metrics
from tier0.harness.runner import run_battery

FIGHTS = 100
SEED = 11

DECKS = [("demolition_package", "demolition"),
         ("reaction_package", "reaction"),
         ("spark_package", "spark")]


@pytest.mark.parametrize("deck,pilot", DECKS)
@pytest.mark.parametrize("enc", ["swarm", "punisher", "attrition",
                                 "burst_check", "tank_boss", "gauntlet"])
def test_klee_decks_run_clean(deck, pilot, enc):
    stats = run_battery("klee", deck, enc, pilot, FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert "INFINITE" not in s["flags"], s
    assert "AMP_STACK" not in s["flags"], s


def test_reaction_deck_triggers_reactions():
    stats = run_battery("klee", "reaction_package", "attrition", "reaction",
                        FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert s["reactions_per_fight"] > 2
    assert s["aura_starved_fights"] < 0.05      # spec §8 draft-gating check
    # Spec §4.4 health band: 25-45% in a reaction-weighted deck; >60%
    # means amp numbers carry too hard.
    assert 0.10 < s["reaction_damage_share"] < 0.60


def test_demolition_deck_detonates_and_sparks():
    # Pounding Surprise: +1 Spark per detonation; at 3 sparks an attack
    # is free. Both must actually occur in real fights.
    stats = run_battery("klee", "demolition_package", "punisher",
                        "demolition", FIGHTS, SEED)
    assert all(s.won or s.turns > 1 for s in stats)
    from tier0.content import loader
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee", "demolition_package")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=SEED)
    events = {e["event"] for e in state.log}
    assert "bomb_detonation" in events
    assert "gain_spark" in events


def test_sparks_make_attack_free():
    from tier0.engine.combat import card_cost, play_card
    from tier0.tests.conftest import make_state
    from tier0.content.loader import get_card
    st = make_state()
    st.player.sparks = 3
    st.player.energy = 0
    jab = get_card("pyro_jab")
    st.player.hand.append(jab)
    assert card_cost(st, jab) == 0
    play_card(st, jab)
    assert st.player.sparks == 0        # consumed all 3
    assert st.player.energy == 0


def test_mono_pyro_deck_cannot_react_alone():
    # Design doc Pillar 2: reactions are earned. Demolition (mono-pyro)
    # should trigger ~zero reactions without companions.
    stats = run_battery("klee", "demolition_package", "punisher",
                        "demolition", FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert s["reactions_per_fight"] == 0
    assert s["aura_starved_fights"] == 1.0
