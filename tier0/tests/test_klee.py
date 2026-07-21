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
    # skill_tags + reactions must feed the 60 meter to full (or to a
    # cast, which resets it) in most long fights.
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights("reaction"))
    filled = 0
    for seed in range(20):
        player = loader.build_player("klee", "reaction_weighted")
        state = run_fight(player, loader.build_encounter("attrition"), pilot,
                          seed=seed)
        if (state.player.burst_energy >= state.player.burst_max
                or any(e["event"] == "burst_cast" for e in state.log)):
            filled += 1
    assert filled >= 10, filled


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
    # v1.9: kit returns to the kit, not to a pile (a power would have
    # exhausted before this).
    assert not st.player.exhaust_pile and not st.player.discard_pile


def test_kit_burst_grant_and_regrant():
    from tier0.engine.combat import grant_charged_kit, play_card
    from tier0.tests.conftest import make_state
    st = make_state()
    st.player.burst_max = 60
    st.player.energy = 6
    st.player.kit_cards = [loader.get_card("sparks_n_splash")]
    grant_charged_kit(st)
    assert not st.player.hand               # meter not full: nothing yet
    st.player.burst_energy = 60
    grant_charged_kit(st)
    assert [c.id for c in st.player.hand] == ["sparks_n_splash"]
    grant_charged_kit(st)
    assert len(st.player.hand) == 1         # no duplicate grant
    play_card(st, st.player.hand[0])
    assert st.player.burst_energy == 0
    st.player.burst_energy = 60             # refill re-grants
    grant_charged_kit(st)
    assert [c.id for c in st.player.hand] == ["sparks_n_splash"]


def test_random_discard_cannot_touch_the_kit_burst():
    """Review-workflow regression: Bright Idea's random discard moved the
    granted Burst into discard, it recirculated as loot, and the grant
    dedup (hand-only) then aliased a second copy. Kit cards are exempt
    from discard and exhaust-from-hand victim pools."""
    from tier0.engine import effects
    from tier0.tests.conftest import make_state
    st = make_state()
    st.player.burst_max = 60
    st.player.burst_energy = 60
    sns = loader.get_card("sparks_n_splash")
    filler = loader.get_card("kaboom")
    st.player.hand = [sns, filler]
    effects._op_discard(st, {"op": "discard", "amount": 2}, filler)
    assert sns in st.player.hand            # only the filler discarded
    assert not any(c.kit_card for c in st.player.discard_pile)
    effects._op_exhaust_from(st, {"op": "exhaust_from", "zone": "hand",
                                  "amount": 2}, filler)
    assert sns in st.player.hand
    assert not any(c.kit_card for c in st.player.exhaust_pile)


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


def test_crackle_spark_is_priced_by_the_discard():
    # R36 (user-ratified): "Discard 1: add a Spark". The Spark is priced BY
    # the discard -- empty hand = no fodder = no Spark; kit cards are never
    # fodder; short hand discards what it can and pays Sparks to match.
    from tier0.engine import effects
    from tier0.tests.conftest import make_state
    fx = {"op": "discard_for_sparks", "amount": 1, "sparks": 1}
    crackle = loader.get_card("crackle")
    assert fx in crackle.effects            # sheet carries the redesign

    st = make_state()
    st.player.hand = []                     # empty hand: no free Spark
    effects._op_discard_for_sparks(st, fx, crackle)
    assert st.player.sparks == 0

    filler = loader.get_card("kaboom")
    st.player.hand = [filler]               # fodder: discard pays the Spark
    effects._op_discard_for_sparks(st, fx, crackle)
    assert st.player.sparks == 1
    assert st.player.hand == []
    assert filler in st.player.discard_pile

    sns = loader.get_card("sparks_n_splash")
    st.player.hand = [sns]                  # kit card: exempt fodder
    effects._op_discard_for_sparks(st, fx, crackle)
    assert st.player.sparks == 1            # unchanged
    assert sns in st.player.hand

    st.player.hand = [loader.get_card("kaboom")]
    fx2 = {"op": "discard_for_sparks", "amount": 2, "sparks": 2}
    effects._op_discard_for_sparks(st, fx2, crackle)   # upgraded, short hand
    assert st.player.sparks == 2            # +1: one card, one Spark


def test_crackle_upgrade_applies_r36_deltas():
    up = loader.get_card("crackle+")
    fx = next(f for f in up.effects if f["op"] == "discard_for_sparks")
    assert fx["amount"] == 2 and fx["sparks"] == 2
    dmg = next(f for f in up.effects if f["op"] == "damage")
    assert dmg["amount"] == 3               # damage delta died with R10


def test_innate_card_starts_in_the_opening_hand():
    # R37: catalytic_conversion+ is Innate -- top of the shuffled draw
    # pile, so the first hand contains it, every fight.
    from tier0.engine.combat import surface_innate
    ccu = loader.get_card("catalytic_conversion+")
    assert ccu.innate is True
    assert loader.get_card("catalytic_conversion").innate is False

    player = loader.build_player("klee", "catalytic_cell_innate")
    import random
    random.Random(7).shuffle(player.draw_pile)
    surface_innate(player.draw_pile)
    assert player.draw_pile[0].id == "catalytic_conversion+"
    # sparks_n_splash's innate-on-charge is its own mechanism: the kit
    # card is not in the draw pile at all.
    assert not any(c.kit_card for c in player.draw_pile)


def test_x_cost_attack_never_spends_sparks():
    # R34 (user-ratified): a Spark-freed X card would resolve at X = 0, so
    # X-cost cards are exempt from spark spend. Without the exemption, an X
    # attack at 0 energy trips the spend predicate (paid 0, printed != 0)
    # and whiffs the whole spark bank.
    import dataclasses
    from tier0.engine.combat import card_cost, play_card
    from tier0.tests.conftest import make_state
    st = make_state()
    st.player.sparks = 3
    st.player.energy = 0
    x_attack = dataclasses.replace(
        loader.get_card("kaboom"), id="x_probe", cost="X")
    st.player.hand.append(x_attack)
    assert card_cost(st, x_attack) == 0     # X = current energy, not sparks
    play_card(st, x_attack)
    assert st.player.sparks == 3            # bank untouched
    assert st.current_x == 0                # resolved at X = 0


def test_beetle_swarm_bonus_reads_live_bomb_state_per_hit():
    """Playtest finding 2026-07-20 (QUEUED for user ruling -- this is the
    LAW as simulated, not a bug): bonus_vs_bombed is read per hit at damage
    time, and the first hit's HP damage detonates that enemy's bombs early,
    so vs a single bombed enemy only hit 1 is ever buffed. The C# mirrors
    this exactly (ModifyDamageAdditive reads live state). If the user
    re-rules (e.g. snapshot bombed-state at cast), this test changes WITH
    the sheet -- until then it pins what both engines do."""
    from tier0.engine.combat import play_card
    from tier0.engine.state import Bomb
    from tier0.tests.conftest import make_state
    st = make_state()
    st.enemies[0].bombs.append(Bomb(damage=5, turn_placed=0))
    st.player.energy = 3
    kbs = loader.get_card("kaboom_beetle_swarm")
    st.player.hand.append(kbs)
    play_card(st, kbs)
    hits = [e["base"] for e in st.log
            if e["event"] == "damage" and e["source"] == "attack"]
    assert hits == [8, 5, 5]                # +3 on hit 1 only
    assert any(e["event"] == "bomb_detonation" for e in st.log)


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
