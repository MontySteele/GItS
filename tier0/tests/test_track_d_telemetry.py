"""Last Call, track D: the measurement plumbing, pinned.

Two instruments land here and neither of them is allowed to have an opinion:

D1 -- reactions' share of damage. The audit's finding was that reactions are
"physics that never moved the design in", and the share behind that sentence
had never been computed. It is computed now. Whether the number is high or low
is a design reading; these tests assert that the instrument REPORTS and never
GRADES, the same fence `test_stability_band` holds around the HP trajectory.

D2 -- the per-turn record: HP trajectory and incoming attacks per turn, in the
same per-fight record, one schema.

The load-bearing constraint underneath both: **`reaction_damage` and every
figure derived from it must not move.** It feeds the ratified A6 axis and
`summarize()["reaction_damage_share"]`, and a telemetry track that silently
redefines a ratified metric is a balance change wearing a lab coat.
"""

from __future__ import annotations

from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.harness.runner import run_battery
from tier0.pilot.policy import make_pilot

from .conftest import make_enemy, make_state

# A reaction-heavy arm: Klee's reaction package is the only battery config that
# reliably lights every branch of the D1 decomposition.
REACTIVE = ("klee", "reaction_weighted", "punisher", "generic")


def _battery(fights=40, seed=7):
    return run_battery(*REACTIVE, fights, seed)


# --- D1: the ratified figure does not move -------------------------------

def test_reaction_damage_is_still_exactly_amp_plus_splash():
    """The pre-instrument definition, pinned as an equation.

    If someone later folds the Electro-Charged DoT into `reaction_damage`
    because "it is obviously reaction damage", A6 moves for every reacting
    character and no ruling was asked for. The DoT lives in its own field for
    exactly this reason.
    """
    for s in _battery():
        assert s.reaction_damage == (s.reaction_damage_amp
                                     + s.reaction_damage_splash), s


def test_the_new_share_and_the_old_share_differ_only_by_the_dot():
    stats = _battery()
    old = metrics.summarize(stats)["reaction_damage_share"]
    new = metrics.reaction_share(stats)
    if new["dot"] == 0:
        assert abs(old - new["share"]) < 1e-12
    else:
        # Widened denominator AND widened numerator; the point is only that the
        # DoT is the whole of the difference.
        assert new["damage_all_ops"] == (
            sum(s.total_damage_dealt for s in stats) + new["dot"])
        assert new["damage_from_reactions"] == (
            sum(s.reaction_damage for s in stats) + new["dot"])


# --- D1: the instrument reports, it does not grade -----------------------

def test_the_share_carries_no_verdict():
    r = metrics.reaction_share(_battery(fights=10))
    forbidden = {"ok", "pass", "passed", "fail", "failed", "verdict", "band",
                 "healthy", "acceptable", "within_band", "grade"}
    assert not (forbidden & set(r)), forbidden & set(r)


def test_share_decomposes_and_the_complement_closes():
    stats = _battery()
    r = metrics.reaction_share(stats)
    assert r["damage_from_reactions"] == r["amp"] + r["splash"] + r["dot"]
    assert r["damage_from_base_ops"] + r["damage_from_reactions"] == \
        r["damage_all_ops"]
    assert 0.0 <= r["share"] <= 1.0
    # Pooled and per-fight-mean are different questions and both are offered.
    assert "share" in r and "share_by_fight_mean" in r


def test_empty_battery_and_zero_damage_fight_are_not_a_division():
    assert metrics.reaction_share([]) == {}
    assert metrics.FightStats(
        won=False, turns=0, hp_start=1, hp_end=1, total_damage_dealt=0,
        damage_by_turn={}, energy_by_turn={}, total_block_gained=0,
        damage_blocked=0, energy_spent=0, cards_drawn_extra=0,
        energy_generated_extra=0, healing=0, encore_absorbed=0,
        debuff_stacks_applied=0, debuffed_intents=0, aura_intents=0,
        total_intents=0, reactions=0, reaction_damage=0,
        auras_wasted=0).reaction_share == 0.0


def test_a_non_reacting_reference_deck_reads_a_flat_zero():
    """ref_ironclad applies no elements at all, so its share is 0 by
    construction -- the anchor for anyone reading a nonzero one."""
    r = metrics.reaction_share(
        run_battery("ref_ironclad", "starter", "punisher", "generic", 20, 7))
    assert r["damage_from_reactions"] == 0
    assert r["share"] == 0.0
    assert r["damage_from_base_ops"] == r["damage_all_ops"] > 0


# --- D1: the dot half, driven directly -----------------------------------

def test_enemy_side_dot_is_attributed_and_overkill_clamped():
    """Electro-Charged is the only `dot` an enemy can carry, so an enemy-side
    tick is reaction damage; and a 3-tick into a 1 HP add is 1 point, not 3
    (the EPOCH 1 splash lesson, applied at the second site that had it)."""
    from tier0.engine import powers
    st = make_state(enemies=[make_enemy(hp=1, name="add")])
    add = st.enemies[0]
    add.powers["dot"] = 3
    powers.on_turn_start(st, add)
    tick = [e for e in st.log if e["event"] == "dot_tick"][0]
    assert tick["to_player"] is False
    assert tick["amount"] == 3 and tick["effective"] == 1
    stats = metrics.extract(st, hp_start=st.player.hp)
    assert stats.reaction_damage_dot == 1
    assert stats.reaction_damage == 0          # untouched by the DoT


def test_player_side_dot_is_not_reaction_damage():
    from tier0.engine import powers
    st = make_state()
    st.player.powers["dot"] = 4
    powers.on_turn_start(st, st.player)
    tick = [e for e in st.log if e["event"] == "dot_tick"][0]
    assert tick["to_player"] is True
    assert metrics.extract(st, hp_start=st.player.hp).reaction_damage_dot == 0


# --- D2: the per-turn record ---------------------------------------------

def test_every_player_turn_produces_exactly_one_row_in_order():
    for s in _battery(fights=20):
        turns = [row[0] for row in s.turn_trajectory]
        assert turns == sorted(turns) == list(range(1, len(turns) + 1)), s
        assert len(set(turns)) == len(turns)
        assert all(len(row) == 6 for row in s.turn_trajectory)


def test_hp_at_open_agrees_with_the_fight_it_came_from():
    """Row 1's HP is the fight's starting HP, and no row invents HP the fight
    never had."""
    for s in _battery(fights=20):
        assert s.turn_trajectory[0][1] == s.hp_start
        assert all(0 <= row[1] <= s.hp_start for row in s.turn_trajectory)


def test_incoming_is_pre_mitigation_and_never_below_what_landed():
    """`incoming_damage` is the hit as it ARRIVES. It must dominate HP actually
    lost -- if it ever read the post-block figure this would fail, and the whole
    instrument would be measuring mitigation instead of demand."""
    player = loader.build_player("ref_ironclad", "starter")
    state = run_fight(player, loader.build_encounter("punisher"),
                      make_pilot(loader.pilot_weights("generic")), seed=11)
    stats = metrics.extract(state, hp_start=state.player.hp + 999)
    per_turn_landed: dict[int, int] = {}
    per_turn_hits: dict[int, int] = {}
    for ev in state.log:
        if ev["event"] == "player_hit":
            t = ev["turn"]
            per_turn_landed[t] = (per_turn_landed.get(t, 0)
                                  + ev["amount"] + ev["blocked"])
            per_turn_hits[t] = per_turn_hits.get(t, 0) + 1
    seen = 0
    for turn, _hp, _bo, _be, hits, dmg_in in stats.turn_trajectory:
        assert hits == per_turn_hits.get(turn, 0)
        assert dmg_in >= per_turn_landed.get(turn, 0)
        seen += hits
    assert seen == sum(per_turn_hits.values()) > 0


def test_block_at_end_uses_minus_one_for_a_turn_the_fight_ended_inside():
    """A fight that ends on the player's turn never reaches `turn_close`. The
    missing sample is -1, never 0 -- "the player held no block" and "nobody
    looked" are different facts and a mean over them is different too."""
    stats = _battery(fights=60)
    tails = [s.turn_trajectory[-1][3] for s in stats if s.turn_trajectory]
    assert any(v == -1 for v in tails), (
        "no fight ended inside a player turn in 60 fights -- the sentinel is "
        "untested, not absent")
    # Only ever the LAST row: an interior turn always closes.
    for s in stats:
        for row in s.turn_trajectory[:-1]:
            assert row[3] >= 0, s.turn_trajectory


def test_turn_profile_pools_without_interpolating():
    stats = _battery(fights=30)
    prof = metrics.turn_profile(stats)
    assert prof, "no turns pooled"
    # Every key is a turn some fight actually reached, and the population is
    # non-increasing: fights drop out, they never rejoin.
    counts = [prof[t]["fights"] for t in sorted(prof)]
    assert counts == sorted(counts, reverse=True), counts
    assert sorted(prof) == list(range(1, max(prof) + 1))
    assert prof[1]["fights"] == len(stats)
    # The -1 rows are excluded from the block mean and counted separately.
    for t in prof:
        assert prof[t]["block_end_samples"] <= prof[t]["fights"]
        if prof[t]["block_end_samples"] == 0:
            assert prof[t]["mean_block_at_end"] is None


def test_turn_profile_is_empty_not_exploding_on_no_fights():
    assert metrics.turn_profile([]) == {}


# --- merging staged fights -----------------------------------------------

def test_gauntlet_merge_offsets_turn_rows_and_keeps_the_reaction_split():
    a = run_battery("klee", "reaction_weighted", "gauntlet", "generic", 10, 5)
    for s in a:
        turns = [row[0] for row in s.turn_trajectory]
        assert turns == list(range(1, len(turns) + 1)), (
            "stage-2 turn numbers were concatenated without an offset")
        assert s.reaction_damage == (s.reaction_damage_amp
                                     + s.reaction_damage_splash)


# --- the instrument does not perturb the sim -----------------------------

def test_adding_the_instrument_did_not_move_the_fight():
    """The new emits are log-side only. Two runs at one seed stay identical,
    and -- the real assertion -- the sim's own outcome figures are still a pure
    function of the seed, which is what a telemetry track is allowed to be.
    """
    one = run_battery(*REACTIVE, 25, 99)
    two = run_battery(*REACTIVE, 25, 99)
    assert [(s.won, s.turns, s.hp_end, s.total_damage_dealt) for s in one] == \
           [(s.won, s.turns, s.hp_end, s.total_damage_dealt) for s in two]
