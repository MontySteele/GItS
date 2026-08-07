"""EB-20: the Encore economy census (the instrument for the D8 lever).

The requirement, as the EB-20 BACKLOG row filed it (the row has since
retired into `EB-20w` -- run-layer wiring -- and the census itself
corrected the filed counts to 18/82 granting, 5 spending; see QUEUE
`D8-def`):

    Instrumentation for D8 (Encore economy census) -- measurement open
    though the lever is ruled-direction, unpicked.

D8's DIRECTION is ruled and its VALUE is [USER]'s to pick. Nothing in this
file, in `metrics.encore_census_profile` or in `report.print_encore_census`
picks it, and the tests below assert that absence as hard as they assert the
counters -- the track D/H/EB-17 fence, restated for a lever that is still open.

The LAW this census is measured against (docs/current/LAW.md, Furina section;
furina kickoff §4):

    Encore is an unbounded per-combat buffer absorbing after Block and before
    HP (overdraw drains true HP); Encore absorption credits A4, never A3.

    Fanfare ... generation is activity-based, never passive. Live legs: HP
    lost / Encore spent / Encore absorbed / Spotlighted card played.

and, from the Track A rework (2026-07-28, RULED), the sentence the last two
tests in section 4 exist for: **Fanfare prints when Encore goes DOWN, never
when it goes up.**

Everything here is log-side. The engine change EB-20 carries is provenance
only -- `source` and `card` keys on `gain_encore` / `encore_spent` /
`encore_overdraw`, `source` on `encore_absorb` -- and section 0 pins that the
fight is bit-identical with them in place.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.engine import combat, resources
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.harness import metrics
from tier0.harness.runner import run_battery

from .conftest import make_enemy, make_state

# The battery the invariant and aggregate sections read. Furina, because
# Encore is hers alone in content -- a Klee cohort would exercise every branch
# below against an empty log and prove nothing.
FURINA = ("furina", "salon_weighted", "punisher", "salon")


def _battery(fights=25, seed=11):
    return run_battery(*FURINA, fights, seed)


def _encore_player(hp=200, fanfare_cap=99, **kw):
    """A player who HAS the Encore/Fanfare resource pair.

    `fanfare_cap` is the marker the engine itself gates the Furina-only
    telemetry on (`fanfare_turn`, `encore_end`), so a fixture without it is a
    fixture the census is deliberately blind to -- which is a fact worth
    building on, and section 5 does."""
    return Player(hp=hp, max_hp=hp, fanfare_cap=fanfare_cap, **kw)


def _card(cid, cost=0, damage=None, effects=None, **kw):
    fx = effects if effects is not None else (
        [{"op": "damage", "amount": damage, "target": "enemy"}]
        if damage is not None else [])
    return Card(id=cid, name=cid.title(), cost=cost,
                type="attack" if damage is not None else "skill",
                effects=fx, **kw)


def _grant(cid, amount):
    return _card(cid, effects=[{"op": "gain_encore", "amount": amount}])


def _spend(cid, amount):
    return _card(cid, effects=[{"op": "spend_encore", "amount": amount}])


def _fight(deck, enemy_hp=200, plays=((),), seed=1, player=None,
           intents=None):
    """Run one player turn per entry in `plays`, on a hand-built deck.

    Lifted from `test_eb17_card_flow_telemetry._fight` and kept
    field-for-field: `plays[t]` is the card ids the pilot plays on turn t+1 in
    order, the draw pile is used IN ORDER because this drives `_player_turn`
    rather than `run_fight`, and the enemy blocks for 0 by default so nothing
    can end the fight early by accident.

    The one addition is `player`, so a fixture can bring an Encore buffer or a
    Fanfare cap with it, and `intents`, so a fixture can be hit."""
    player = player if player is not None else _encore_player()
    player.draw_pile = list(deck)
    enemy = Enemy(hp=enemy_hp, max_hp=enemy_hp, name="wall",
                  intents=intents or [{"kind": "block", "amount": 0}])
    state = CombatState(player=player, enemies=[enemy],
                        rng=random.Random(seed))
    wanted: list[str] = []

    def pilot(s):
        for cid in list(wanted):
            for c in s.player.hand:
                if c.id == cid and combat.card_playable(s, c):
                    wanted.remove(cid)
                    return c
        return None

    for turn_plays in plays:
        wanted[:] = list(turn_plays)
        combat._player_turn(state, pilot)
    return state


def _stats(state):
    return metrics.extract(state, state.player.max_hp)


# --- 0: the instrument does not move the fight ---------------------------

def test_the_census_did_not_move_the_fight():
    """The load-bearing one, on track H's and EB-17's pattern. The engine side
    of EB-20 is four added event KEYS and nothing else; the outcome figures
    stay a pure function of the seed."""
    one = run_battery(*FURINA, 25, 99)
    two = run_battery(*FURINA, 25, 99)
    assert [(s.won, s.turns, s.hp_end, s.total_damage_dealt, s.cards_played)
            for s in one] == \
           [(s.won, s.turns, s.hp_end, s.total_damage_dealt, s.cards_played)
            for s in two]


def test_the_census_field_names_exist_on_the_record():
    """Pin the names, on EB-17's precedent, so the item cannot silently
    reopen by a rename. Constructed positionally from the pre-EB-20 field
    list, which also pins that every EB-20 field carries a default."""
    s = metrics.FightStats(won=False, turns=0, hp_start=1, hp_end=1,
                           total_damage_dealt=0, damage_by_turn={},
                           energy_by_turn={}, total_block_gained=0,
                           damage_blocked=0, energy_spent=0,
                           cards_drawn_extra=0, energy_generated_extra=0,
                           healing=0, encore_absorbed=0,
                           debuff_stacks_applied=0, debuffed_intents=0,
                           aura_intents=0, total_intents=0, reactions=0,
                           reaction_damage=0, auras_wasted=0)
    assert s.encore_granted == 0
    assert s.encore_spent == 0
    assert s.encore_overdrawn == 0
    assert s.encore_residual == 0
    assert s.encore_residual_samples == 0
    assert s.encore_peak == 0
    assert s.encore_zero_turns == 0
    assert s.encore_turns_sampled == 0
    assert s.encore_granted_by_card == {}
    assert s.encore_granted_by_source == {}
    assert s.encore_spent_by_card == {}
    assert s.encore_spent_by_source == {}
    assert s.encore_absorbed_by_source == {}
    assert s.encore_at_turn == {}
    assert s.fanfare_by_leg == {}
    assert s.fanfare_wasted_by_leg == {}
    assert s.encore_drained == 0


# --- 1: grants -----------------------------------------------------------

def test_a_grant_is_counted_and_attributed_to_the_card_that_made_it():
    st = _fight([_grant("hearts_swelling", 4)], plays=[["hearts_swelling"]])
    s = _stats(st)
    assert s.encore_granted == 4
    assert s.encore_granted_by_card == {"hearts_swelling": 4}
    assert s.encore_granted_by_source == {"gain_encore_op": 4}


def test_a_card_that_grants_nothing_is_absent_from_the_grant_table():
    """The negative direction. A non-flow is not a zero row: absent and zero
    are different findings and the whole census turns on keeping them apart
    (the payoff_profile rule)."""
    st = _fight([_card("poke", damage=3)], plays=[["poke"]])
    s = _stats(st)
    assert s.encore_granted == 0
    assert "poke" not in s.encore_granted_by_card
    assert s.encore_granted_by_card == {}


def test_a_grant_with_no_card_behind_it_is_sourced_but_not_carded():
    """The Salon bow grants Encore with no card resolving. It must count in
    the totals and in the by-SOURCE table, and must never invent a card id --
    a fake key here would corrupt exactly the "19 of 78 grant" reading the
    census exists to take."""
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.fanfare_cap = 99
    resources.gain_encore(st, 3, "salon_final_bow")
    s = _stats(st)
    assert s.encore_granted == 3
    assert s.encore_granted_by_source == {"salon_final_bow": 3}
    assert s.encore_granted_by_card == {}


def test_two_grants_from_one_card_id_accumulate_on_one_row():
    st = _fight([_grant("aria", 2), _grant("aria", 5)],
                plays=[["aria", "aria"]])
    s = _stats(st)
    assert s.encore_granted == 7
    assert s.encore_granted_by_card == {"aria": 7}


# --- 2: spends, and the HP an overdraw costs -----------------------------

def test_a_spend_is_counted_and_attributed_to_the_card_that_spent_it():
    st = _fight([_grant("well", 6), _spend("graceful_retreat", 4)],
                plays=[["well", "graceful_retreat"]])
    s = _stats(st)
    assert s.encore_spent == 4
    assert s.encore_spent_by_card == {"graceful_retreat": 4}
    assert s.encore_spent_by_source == {"spend_encore_op": 4}
    assert s.encore_overdrawn == 0


def test_an_overdraw_pays_hp_and_is_never_pooled_into_the_spend():
    """"Spend 4" against a buffer of 1 drains 1 Encore and 3 TRUE HP. The 3
    is not Encore and must not appear as Encore -- pooling it would inflate
    the sink and make the gain/drain ratio read as healthier than it is."""
    st = _fight([_grant("well", 1), _spend("graceful_retreat", 4)],
                plays=[["well", "graceful_retreat"]])
    s = _stats(st)
    assert s.encore_granted == 1
    assert s.encore_spent == 1
    assert s.encore_overdrawn == 3
    assert s.encore_spent_by_card == {"graceful_retreat": 1}
    assert st.player.hp == st.player.max_hp - 3


def test_a_spend_against_a_dry_buffer_counts_no_spend_at_all():
    """Nothing was drained, so nothing is a spend. The whole cost landed on
    HP and is reported there."""
    st = _fight([_spend("graceful_retreat", 2)], plays=[["graceful_retreat"]])
    s = _stats(st)
    assert s.encore_spent == 0
    assert s.encore_spent_by_card == {}
    assert s.encore_overdrawn == 2


def test_the_encore_cost_gate_is_a_separate_sink_from_the_spend_op():
    """"Spend N Encore:" is a playability GATE, not the overdraw op, and the
    two are different design objects (LAW/kickoff §4). The census keeps them
    apart by source while pooling them in the total, because D8's "1 spends"
    sentence is about cards and both of these are cards."""
    st = _fight([_grant("well", 5), _card("gated", damage=3, encore_cost=2)],
                plays=[["well", "gated"]])
    s = _stats(st)
    assert s.encore_spent == 2
    assert s.encore_spent_by_source == {"encore_cost": 2}
    assert s.encore_spent_by_card == {"gated": 2}


# --- 3: the automatic sink -----------------------------------------------

def test_absorption_is_counted_by_source_and_carries_no_card():
    """Absorption is automatic -- one of D8's three stated facts. No card
    causes it, so there is no card table for it, and the split that does
    exist is over what the buffer ATE."""
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.fanfare_cap = 99
    resources.gain_encore(st, 10, "gain_encore_op", "well")
    reached_hp = resources.absorb_into_encore(st, 4, "enemy_hit")
    s = _stats(st)
    assert reached_hp == 0
    assert s.encore_absorbed == 4
    assert s.encore_absorbed_by_source == {"enemy_hit": 4}
    assert not hasattr(s, "encore_absorbed_by_card")


def test_absorption_over_the_buffer_absorbs_only_what_was_there():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.fanfare_cap = 99
    resources.gain_encore(st, 2, "gain_encore_op", "well")
    reached_hp = resources.absorb_into_encore(st, 7, "enemy_hit")
    s = _stats(st)
    assert reached_hp == 5
    assert s.encore_absorbed == 2
    assert s.encore_absorbed_by_source == {"enemy_hit": 2}


def test_the_preexisting_a4_absorption_figure_did_not_move():
    """`encore_absorbed` feeds the ratified A4 axis. EB-20 adds a split BESIDE
    it and must not have changed it: the by-source table sums to exactly the
    old number, fight by fight, across a real battery."""
    for s in _battery():
        assert sum(s.encore_absorbed_by_source.values()) == s.encore_absorbed


# --- 4: the Fanfare legs, and the LAW they are read against --------------

def test_a_spend_prints_fanfare_on_the_encore_spent_leg():
    st = _fight([_grant("well", 6), _spend("graceful_retreat", 4)],
                plays=[["well", "graceful_retreat"]])
    s = _stats(st)
    assert (s.fanfare_by_leg["encore_spent"]
            == 4 * C.FANFARE_PER_ENCORE_SPENT)


def test_absorption_prints_fanfare_on_the_encore_absorbed_leg():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.fanfare_cap = 99
    resources.gain_encore(st, 10, "gain_encore_op", "well")
    resources.absorb_into_encore(st, 4, "enemy_hit")
    s = _stats(st)
    assert (s.fanfare_by_leg["encore_absorbed"]
            == 4 * C.FANFARE_PER_ENCORE_ABSORBED)


def test_a_grant_prints_no_fanfare_at_all():
    """LAW, Track A RULED 2026-07-28: Fanfare prints when Encore goes DOWN,
    never when it goes up. The retired leg was called `encore_gained`; if it
    ever comes back this is where it surfaces."""
    st = _fight([_grant("hearts_swelling", 9)], plays=[["hearts_swelling"]])
    s = _stats(st)
    assert s.encore_granted == 9
    assert "encore_gained" not in s.fanfare_by_leg
    assert s.fanfare_by_leg.get("encore_spent", 0) == 0
    assert s.fanfare_by_leg.get("encore_absorbed", 0) == 0


def test_no_battery_fight_ever_prints_an_unregistered_fanfare_leg():
    """The same rule over a real cohort rather than a fixture. Every leg the
    engine emits is one of the four LAW lists -- an `encore_gained` row, or
    any leg nobody registered, fails here."""
    for s in _battery():
        assert set(s.fanfare_by_leg) <= set(metrics.FANFARE_LEGS)
        assert set(s.fanfare_wasted_by_leg) <= set(metrics.FANFARE_LEGS)


def test_the_encore_legs_never_out_print_the_points_that_left_the_buffer():
    """Every point past Block prints exactly 1 Fanfare (LAW), so the two
    Encore legs are bounded above by the points that actually left the buffer
    -- below it only where the meter saturated at its cap, which is why this
    is an inequality and `fanfare_wasted_by_leg` exists to explain the gap."""
    for s in _battery():
        applied = sum(s.fanfare_by_leg.get(leg, 0)
                      for leg in metrics.ENCORE_FANFARE_LEGS)
        wasted = sum(s.fanfare_wasted_by_leg.get(leg, 0)
                     for leg in metrics.ENCORE_FANFARE_LEGS)
        assert applied <= s.encore_drained
        assert applied + wasted == s.encore_drained * C.FANFARE_PER_ENCORE_SPENT


# --- 5: held, peak, empty turns, residual --------------------------------

def test_peak_is_the_high_water_mark_and_not_the_final_level():
    st = _fight([_grant("well", 9), _spend("graceful_retreat", 7)],
                plays=[["well", "graceful_retreat"]])
    s = _stats(st)
    assert s.encore_peak == 9
    assert s.encore_granted == 9
    assert s.encore_spent == 7


def test_the_reconstructed_buffer_agrees_with_the_engines_own_end_row():
    """The census walks the log to rebuild the buffer. `encore_end` is the
    engine reporting the same number directly, so the two agreeing is the
    proof that the walk covers every mutation site -- and the alarm if a
    fourth one is ever added without an emit."""
    stats = _battery()
    checked = 0
    for s in stats:
        for stage in (s.stages or [s]):
            if not stage.encore_residual_samples:
                continue
            checked += 1
            assert (stage.encore_granted - stage.encore_spent
                    - stage.encore_absorbed) == stage.encore_residual
            assert stage.encore_peak >= stage.encore_residual
    assert checked, "the Furina battery produced no encore_end rows"


def test_an_empty_turn_snapshot_is_counted_and_a_stocked_one_is_not():
    """Both directions in one fixture pair. Turn 1 opens dry; the grant lands
    during turn 1, so turn 2's snapshot finds the buffer stocked."""
    st = _fight([_grant("well", 5), _card("filler", damage=1, retain=True)],
                plays=[["well"], []])
    s = _stats(st)
    assert s.encore_turns_sampled == 2
    assert s.encore_zero_turns == 1
    assert s.encore_at_turn == {1: 0, 2: 5}


def test_a_character_without_the_resource_is_sampled_zero_times():
    """A player with no Fanfare cap has no Encore resource, so the engine
    emits neither `fanfare_turn` nor `encore_end` and the census reports NO
    SAMPLES rather than a turn spent at zero. That is the difference between
    "she was empty" and "there was nothing to be empty"."""
    st = _fight([_card("poke", damage=3)], plays=[["poke"]],
                player=Player(hp=200, max_hp=200))
    s = _stats(st)
    assert s.encore_turns_sampled == 0
    assert s.encore_zero_turns == 0
    assert s.encore_residual_samples == 0
    assert s.encore_at_turn == {}


def test_the_residual_sample_is_a_zero_or_one_per_combat():
    for s in metrics.per_combat(_battery()):
        assert s.encore_residual_samples in (0, 1)


# --- 6: merge (O-1) ------------------------------------------------------

def test_a_gauntlet_sums_the_counts_and_maxes_the_peak():
    """O-1: a `gauntlet` is one record and two combats, and the buffer RESETS
    between them. Counts and residuals sum -- both stages wasted their own --
    but two stages that each reached 9 did not reach 18."""
    a = _stats(_fight([_grant("well", 9), _spend("gr", 3)],
                      plays=[["well", "gr"]]))
    b = _stats(_fight([_grant("well", 9), _spend("gr", 3)],
                      plays=[["well", "gr"]]))
    merged = metrics.merge_stages([a, b])
    assert merged.encore_granted == 18
    assert merged.encore_spent == 6
    assert merged.encore_peak == 9
    assert merged.encore_granted_by_card == {"well": 18}
    assert merged.encore_spent_by_card == {"gr": 6}
    assert merged.stages == [a, b]


def test_a_gauntlet_offsets_the_turn_keyed_trajectory():
    a = _stats(_fight([_grant("well", 4), _card("f", damage=1, retain=True)],
                      plays=[["well"], []]))
    b = _stats(_fight([_grant("well", 4), _card("f", damage=1, retain=True)],
                      plays=[["well"], []]))
    merged = metrics.merge_stages([a, b])
    assert a.encore_at_turn == {1: 0, 2: 4}
    assert merged.encore_at_turn == {1: 0, 2: 4, 3: 0, 4: 4}
    assert merged.encore_turns_sampled == 4
    assert merged.encore_zero_turns == 2


def _residual_stage():
    """One real `run_fight` that grants 2 Encore, never spends it, and wins --
    so the `encore_end` row exists and carries a residual that is not zero."""
    def pilot(s):
        # Grant BEFORE the kill: the finisher ends the combat, and a pilot
        # that scanned the hand in hand order would sometimes swing first and
        # leave the grant unplayed.
        for cid in ("w", "finisher"):
            for c in s.player.hand:
                if c.id == cid and combat.card_playable(s, c):
                    return c
        return None

    state = combat.run_fight(
        _encore_player(draw_pile=[_grant("w", 2), _card("finisher",
                                                        damage=50)]),
        [Enemy(hp=5, max_hp=5, name="paper",
               intents=[{"kind": "block", "amount": 0}])],
        pilot, seed=1)
    return metrics.extract(state, 200)


def test_a_gauntlet_sums_the_residual_and_its_sample_count_together():
    """So that the MEAN stays per combat: two stages each leaving 2 behind is
    a residual of 4 over 2 samples, not 4 over 1."""
    a, b = _residual_stage(), _residual_stage()
    assert a.encore_granted == 2 and a.encore_spent == 0
    assert a.encore_residual == 2            # generated and never needed
    assert a.encore_residual_samples == 1
    merged = metrics.merge_stages([a, b])
    assert merged.encore_residual == 4
    assert merged.encore_residual_samples == 2


# --- 7: invariants over a real battery -----------------------------------

def test_grants_and_spends_by_card_never_exceed_their_totals():
    for s in _battery():
        assert sum(s.encore_granted_by_card.values()) <= s.encore_granted
        assert sum(s.encore_granted_by_source.values()) == s.encore_granted
        assert sum(s.encore_spent_by_card.values()) <= s.encore_spent
        assert sum(s.encore_spent_by_source.values()) == s.encore_spent


def test_nothing_in_the_battery_falls_into_the_unattributed_bucket():
    """`UNATTRIBUTED` is the bucket a call site lands in when it hands the
    buffer points without saying where from. Every engine call site names
    itself, so a real battery must never fill it -- and a new unsourced site
    fails here instead of silently joining a total."""
    for s in _battery():
        assert resources.UNATTRIBUTED not in s.encore_granted_by_source
        assert resources.UNATTRIBUTED not in s.encore_spent_by_source
        assert resources.UNATTRIBUTED not in s.encore_absorbed_by_source


def test_the_buffer_never_goes_negative_anywhere_in_the_reconstruction():
    for s in metrics.per_combat(_battery()):
        assert s.encore_residual >= 0
        assert s.encore_peak >= 0
        for turn, held in s.encore_at_turn.items():
            assert held >= 0, turn


def test_the_zero_turn_count_never_exceeds_the_samples_it_came_from():
    for s in _battery():
        assert s.encore_zero_turns <= s.encore_turns_sampled
        assert len(s.encore_at_turn) == s.encore_turns_sampled


# --- 8: the aggregate hook ------------------------------------------------

def test_encore_census_profile_pools_and_reports_no_verdict():
    stats = _battery()
    prof = metrics.encore_census_profile(stats)
    live = [s for s in metrics.per_combat(stats)
            if s.encore_granted or s.encore_absorbed
            or s.encore_residual_samples]
    assert prof["encore_combats"] == len(live)
    assert prof["granted"] == sum(s.encore_granted for s in live)
    assert prof["spent"] == sum(s.encore_spent for s in live)
    assert prof["absorbed"] == sum(s.encore_absorbed for s in live)
    assert prof["drained"] == prof["spent"] + prof["absorbed"]
    # No grade, no band, no pass/fail, and above all no PICK -- D8's value is
    # [USER]'s. The track D/H/EB-17 fence, restated for an open lever.
    for key in ("verdict", "grade", "ok", "healthy", "band", "target",
                "saturated", "recommendation", "lever", "d8"):
        assert key not in prof


def test_encore_census_profile_is_empty_not_exploding_on_no_fights():
    assert metrics.encore_census_profile([]) == {}


def test_encore_census_profile_is_empty_on_a_cohort_with_no_encore():
    """Klee has no Encore. A row of zeroes wearing Furina's vocabulary is
    noise pretending to be data (the engine's own words at the `encore_end`
    emit); the honest answer is nothing at all."""
    klee = run_battery("klee", "reaction_weighted", "punisher", "reaction",
                       10, 5)
    assert metrics.encore_census_profile(klee) == {}


def test_encore_census_profile_keeps_an_undefined_ratio_out_of_the_numbers():
    """None, not 0.0. A buffer that filled and was never drained is the most
    saturated case there is, and printing it as a ratio's minimum reports the
    strongest finding as the weakest number."""
    st = _fight([_grant("well", 5)], plays=[["well"]])
    prof = metrics.encore_census_profile([_stats(st)])
    assert prof["granted"] == 5
    assert prof["drained"] == 0
    assert prof["gain_drain_ratio"] is None


def test_encore_census_profile_denominates_over_encore_live_combats():
    stats = _battery()
    prof = metrics.encore_census_profile(stats)
    assert prof["combats"] == len(metrics.per_combat(stats))
    assert prof["encore_combats"] <= prof["combats"]
    assert prof["granted_per_combat"] == prof["granted"] / prof["encore_combats"]
    for cid, row in prof["by_card"].items():
        assert (row["granted_per_combat"]
                == row["granted"] / prof["encore_combats"]), cid


def test_the_per_card_table_holds_only_cards_that_moved_a_point():
    """"19 of 78 grant" is a sheet count; what a battery can say is which of
    them a fight actually saw. A card that never moved a point is ABSENT."""
    stats = _battery()
    prof = metrics.encore_census_profile(stats)
    assert prof["by_card"], "the Furina battery moved no Encore at all"
    for cid, row in prof["by_card"].items():
        assert row["granted"] or row["spent"], cid
        assert row["combats_granting"] <= prof["encore_combats"], cid
        assert row["combats_spending"] <= prof["encore_combats"], cid


def test_the_fanfare_leg_table_separates_absent_from_zero():
    stats = _battery()
    prof = metrics.encore_census_profile(stats)
    assert prof["legs_unexpected"] == []
    for leg in metrics.FANFARE_LEGS:
        assert (leg in prof["fanfare_by_leg"]) != (leg in prof["legs_absent"])
    assert (prof["fanfare_from_encore"]
            == sum(prof["fanfare_by_leg"].get(leg, {}).get("applied", 0)
                   for leg in metrics.ENCORE_FANFARE_LEGS))


# --- 9: the printed surface ----------------------------------------------

def test_print_encore_census_is_silent_on_an_empty_profile(capsys):
    from tier0.harness import report
    report.print_encore_census("nothing", {})
    assert capsys.readouterr().out == ""


def test_print_encore_census_prints_the_counters_and_no_verdict(capsys):
    from tier0.harness import report
    report.print_encore_census("punisher",
                               metrics.encore_census_profile(_battery()))
    out = capsys.readouterr().out
    assert "encore" in out
    for word in ("granted", "spent", "absorbed", "residual", "peak",
                 "fanfare leg"):
        assert word in out
    for word in ("VERDICT", "FAIL", "saturated", "redesign", "should be",
                 "too high", "too low"):
        assert word not in out


RUNNER_ARGS = ["--character", "furina", "--deck", "salon_weighted",
               "--pilot", "salon", "--encounter", "punisher",
               "--fights", "3", "--seed", "4"]


def test_the_runner_flag_prints_the_census(capsys):
    from tier0.harness import runner
    assert runner.main(RUNNER_ARGS + ["--encore-census"]) == 0
    out = capsys.readouterr().out
    assert "encore      [punisher]" in out
    assert "fanfare leg [punisher]" in out


def test_the_runner_flag_is_off_by_default(capsys):
    """Opt-in, like every other aggregate surface: a flag that printed by
    default would put a Furina-only table under every run in the battery."""
    from tier0.harness import runner
    assert runner.main(RUNNER_ARGS) == 0
    out = capsys.readouterr().out
    assert "encore      [punisher]" not in out
    assert "win " in out                     # the ordinary summary still ran
