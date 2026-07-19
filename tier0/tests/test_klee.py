"""M4/Klee-pass: real card sheet through the frozen battery with archetype
pilots. These validate the SYSTEMS (bombs, sparks, burst, reactions,
instrumentation) and the sheet's parseability — balance is read from
scorecards, not asserted here (except the review's watchlist bounds)."""

import pytest

from tier0.content import loader
from tier0.harness import metrics
from tier0.harness.runner import run_battery

FIGHTS = 100
SEED = 11

DECKS = [("demolition_weighted", "demolition"),
         ("spark_weighted", "spark"),
         ("reaction_weighted", "reaction")]


def test_whole_sheet_parses():
    # Every card in docs/klee-cards.yaml + mondstadt-companions.yaml loads
    # and only uses known ops/predicates/formulas (loader is strict).
    index = loader._card_index()
    assert len([c for c in index.values()
                if c.id not in ("strike", "defend", "bash")]) >= 90


@pytest.mark.parametrize("deck,pilot", DECKS)
@pytest.mark.parametrize("enc", ["swarm", "punisher", "attrition",
                                 "burst_check", "tank_boss", "gauntlet"])
def test_klee_decks_run_clean(deck, pilot, enc):
    stats = run_battery("klee", deck, enc, pilot, FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert "INFINITE" not in s["flags"], s


@pytest.mark.parametrize("deck", ["melt_stack", "barrage_engine",
                                  "loop_density", "dream_team"])
def test_watchlist_configs_run_clean(deck):
    for enc in ("punisher", "tank_boss", "swarm"):
        stats = run_battery("klee", deck, enc, "generic", FIGHTS, SEED)
        s = metrics.summarize(stats)
        assert "INFINITE" not in s["flags"], (deck, enc, s)


def test_reaction_deck_triggers_reactions():
    stats = run_battery("klee", "reaction_weighted", "attrition", "reaction",
                        FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert s["reactions_per_fight"] > 2
    # Character doc §4: target <15% zero-reaction fights in Reaction deck.
    assert s["aura_starved_fights"] < 0.15
    assert 0.05 < s["reaction_damage_share"] < 0.60


def test_demolition_deck_detonates_and_sparks():
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee", "demolition_weighted")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=SEED)
    events = {e["event"] for e in state.log}
    assert "bomb_detonation" in events
    assert "gain_spark" in events           # Pounding Surprise fired


def test_burst_meter_fills_in_reaction_fights():
    # skill_tags + reactions must actually feed the 60 meter to full.
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights("reaction"))
    player = loader.build_player("klee", "reaction_weighted")
    state = run_fight(player, loader.build_encounter("attrition"), pilot,
                      seed=3)
    assert state.player.burst_energy >= state.player.burst_max


def test_burst_card_gated_and_empties_meter():
    from tier0.engine.combat import card_playable, play_card
    from tier0.tests.conftest import make_state
    st = make_state()
    st.player.burst_max = 60
    st.player.energy = 3
    sns = loader.get_card("sparks_n_splash")
    st.player.hand.append(sns)
    st.player.burst_energy = 45
    assert not card_playable(st, sns)       # gated until full
    st.player.burst_energy = 60
    assert card_playable(st, sns)
    play_card(st, sns)
    assert st.player.burst_energy == 0      # casting empties the meter
    assert st.player.powers["sparks_n_splash"] == 3


def test_sparks_make_attack_free():
    from tier0.engine.combat import card_cost, play_card
    from tier0.tests.conftest import make_state
    st = make_state()
    st.player.sparks = 3
    st.player.energy = 0
    kaboom = loader.get_card("kaboom")
    st.player.hand.append(kaboom)
    assert card_cost(st, kaboom) == 0
    play_card(st, kaboom)
    assert st.player.sparks == 0        # consumed all 3
    assert st.player.energy == 0


def test_mono_pyro_deck_cannot_react_alone():
    # Design doc Pillar 2: reactions are earned. Demolition (mono-pyro)
    # should trigger ~zero reactions without companions.
    stats = run_battery("klee", "demolition_weighted", "punisher",
                        "demolition", FIGHTS, SEED)
    s = metrics.summarize(stats)
    assert s["reactions_per_fight"] == 0
    assert s["aura_starved_fights"] == 1.0


def test_amp_cap_holds_on_melt_stack():
    # Review watchlist #1: Vermillion Pact (+25%) + Durin (+30%) + Melt
    # (x1.75) = x2.71 must stay under the 4x provenance cap.
    for enc in ("punisher", "tank_boss"):
        stats = run_battery("klee", "melt_stack", enc, "generic",
                            FIGHTS, SEED)
        s = metrics.summarize(stats)
        assert "AMP_STACK" not in s["flags"], (enc, s)
