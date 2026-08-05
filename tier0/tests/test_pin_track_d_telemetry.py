"""Pins for the Track D telemetry surfaces that a mutation round found bare.

Track D landed `metrics.reaction_share` / `metrics.turn_profile`, the D1
three-way reaction split, and the D2 per-turn record. `test_track_d_telemetry`
pins what those instruments PRODUCE on a real battery. This file pins the
DEFINITIONS underneath them -- the denominators, the sentinels, the routing of
one event into one bucket -- each of which a mutation round (track K,
2026-08-05) showed could be changed without a single test going red.

Every pin here cites a source of truth that already existed before the pin:
the field's own docstring in `tier0/harness/metrics.py`, the emit-site comment
in `tier0/engine/combat.py` / `powers.py`, or `tier05/reaction_telemetry.py`'s
metric-definitions header. Nothing here decides anything new.
"""

from __future__ import annotations

from tier0.engine import powers
from tier0.harness import metrics
from tier0.harness.runner import run_battery

from .conftest import make_enemy, make_state

REACTIVE = ("klee", "reaction_weighted", "punisher", "generic")


def _stats(**kw) -> metrics.FightStats:
    """A zeroed FightStats; callers set only the fields their pin reads."""
    base = dict(won=True, turns=1, hp_start=80, hp_end=80,
                total_damage_dealt=0, damage_by_turn={}, energy_by_turn={},
                total_block_gained=0, damage_blocked=0, energy_spent=0,
                cards_drawn_extra=0, energy_generated_extra=0, healing=0,
                encore_absorbed=0, debuff_stacks_applied=0,
                debuffed_intents=0, aura_intents=0, total_intents=0,
                reactions=0, reaction_damage=0, auras_wasted=0)
    base.update(kw)
    return metrics.FightStats(**base)


# --- D1: the denominator is the WIDENED one, on both derived figures ------

def test_the_d1_denominator_is_widened_by_the_dot_on_every_derived_figure():
    """`damage_all_ops` is the D1 denominator and its docstring says why: the
    Electro-Charged DoT is damage the player put on an enemy that the `damage`
    event stream never carried, so `total_damage_dealt` is short by exactly
    that much. Both figures DERIVED from the denominator have to use the
    widened one -- `damage_from_base_ops` (the complement) and
    `reaction_share` (the quotient). Using `total_damage_dealt` in either
    still type-checks, still returns a plausible fraction, and is wrong by the
    DoT: the complement stops closing and the share reads high.
    """
    s = _stats(total_damage_dealt=10, reaction_damage_dot=6)

    assert s.damage_all_ops == 16
    assert s.damage_from_reactions == 6
    # The complement CLOSES against the widened denominator, not the narrow one.
    assert s.damage_from_base_ops == 10
    assert s.damage_from_base_ops + s.damage_from_reactions == s.damage_all_ops
    # And the share is over the same 16. Over `total_damage_dealt` it would
    # read 0.6 -- half again as high, from the same fight.
    assert s.reaction_share == 6 / 16


def test_a_splash_event_lands_in_the_splash_bucket_and_nowhere_else():
    """The D1 comment enumerates three ways a reaction puts damage on the
    board and keeps them apart on purpose: `amp` is the Vaporize/Melt
    multiplier's DELTA, `splash` is Overload's explosion, `dot` is
    Electro-Charged ticking on an enemy. A splash credited to `amp` leaves
    every total identical -- `reaction_damage`, `damage_from_reactions` and
    the share all agree -- and silently reports an explosion as a multiplier.
    """
    st = make_state()
    st.emit("damage", amount=7, source="reaction_splash")
    st.emit("damage", amount=4, source="attack")

    s = metrics.extract(st, hp_start=st.player.hp)
    assert s.reaction_damage_splash == 7
    assert s.reaction_damage_amp == 0
    assert s.reaction_damage_dot == 0
    # ...and the ratified figure is unmoved either way, which is why the split
    # needs its own pin: the equation it satisfies cannot see the swap.
    assert s.reaction_damage == 7


def test_an_enemy_named_player_still_takes_enemy_side_dot():
    """The emit site says it in as many words: `to_player` is explicit rather
    than inferred from `target`, because "an enemy may legitimately be named
    'player' in a fixture". Routing on the name instead reads identically on
    the whole roster and misfiles every tick in exactly the fixture the
    comment names.
    """
    st = make_state(enemies=[make_enemy(hp=9, name="player")])
    add = st.enemies[0]
    add.powers["dot"] = 3
    powers.on_turn_start(st, add)

    tick = [e for e in st.log if e["event"] == "dot_tick"][0]
    assert tick["target"] == "player"
    assert tick["to_player"] is False
    assert metrics.extract(st, hp_start=st.player.hp).reaction_damage_dot == 3


# --- D2: the per-turn record's counters and sentinel ----------------------

def test_two_hits_in_one_turn_are_two_hits():
    """`hits_in` is a COUNT of the attack hits that landed in the enemy phase
    following a player turn -- the field comment's words are "how many attack
    hits landed". A multi-hit intent is the ordinary case, so an assignment
    where an increment belongs reads 1 for a turn that took four hits and the
    incoming-attacks-per-turn instrument flattens to a boolean.
    """
    st = make_state()
    st.emit("turn_open", hp=80, block=0)
    st.emit("player_hit", amount=3, blocked=0, block_before=0, incoming=3)
    st.emit("player_hit", amount=2, blocked=1, block_before=1, incoming=3)
    st.emit("turn_close", block=0)

    rows = metrics.extract(st, hp_start=80).turn_trajectory
    assert len(rows) == 1
    _turn, _hp, _bo, _be, hits, damage_in = rows[0]
    assert hits == 2
    assert damage_in == 6


def test_zero_block_at_close_is_a_sample_and_minus_one_is_not():
    """metrics.py states the rule for this column twice: -1 "marks a turn the
    fight ended inside -- an unsampled value, never a zero", and
    `turn_profile` "skips the -1 rows". A turn that CLOSED holding no block is
    a measurement of zero and belongs in the mean; the two facts are different
    and a filter at `> 0` merges them.
    """
    closed_empty = _stats(turn_trajectory=[[1, 80, 0, 0, 0, 0]])
    prof = metrics.turn_profile([closed_empty])
    assert prof[1]["block_end_samples"] == 1
    assert prof[1]["mean_block_at_end"] == 0.0


def test_a_turn_nobody_closed_reports_no_mean_rather_than_zero():
    """The complement of the pin above, and the same sentence carries it: an
    unsampled value is never a zero. A turn whose only row ended inside the
    fight has NO block-at-end sample, and `mean_block_at_end` is None there.
    Reporting 0.0 would put "the player held no block" into a table that means
    "nobody looked".
    """
    unclosed = _stats(turn_trajectory=[[1, 80, 0, -1, 0, 0]])
    prof = metrics.turn_profile([unclosed])
    assert prof[1]["block_end_samples"] == 0
    assert prof[1]["mean_block_at_end"] is None


def test_the_block_mean_divides_by_its_own_samples_and_the_rest_do_not():
    """`turn_profile`'s docstring fixes both denominators in one sentence:
    every figure is "a mean over the fights that REACHED that turn", and
    `block_at_end` alone "skips the -1 rows ... so a mean over two turns is
    not mistaken for a mean over two hundred". So the block mean divides by
    `block_end_samples` and every other mean divides by `fights`. Swap either
    and the table stays well-formed while two of its columns change meaning.
    """
    closed = _stats(turn_trajectory=[[1, 80, 0, 4, 3, 12]])
    unclosed = _stats(turn_trajectory=[[1, 70, 0, -1, 1, 5]])
    prof = metrics.turn_profile([closed, unclosed])[1]

    assert prof["fights"] == 2 and prof["block_end_samples"] == 1
    # Block: over the ONE sample that survived the filter, not over both rows.
    assert prof["mean_block_at_end"] == 4.0
    # Hits and damage: over BOTH rows, including the turn the fight ended in.
    assert prof["mean_incoming_hits"] == 2.0
    assert prof["mean_incoming_damage"] == 8.5


# --- D1/D2: merging staged fights keeps the split and the dot -------------

def test_merging_stages_keeps_all_three_reaction_buckets_apart():
    """A gauntlet's stages are merged into one record, and the merge has to
    carry each of the three D1 buckets into its OWN sibling. Crossing amp and
    splash preserves every total; dropping the DoT preserves
    `reaction_damage` (which is amp + splash by definition) and quietly
    shrinks the widened denominator that exists for it.
    """
    a = _stats(turns=2, reaction_damage=3, reaction_damage_amp=3,
               reaction_damage_splash=0, reaction_damage_dot=5)
    b = _stats(turns=3, reaction_damage=7, reaction_damage_amp=0,
               reaction_damage_splash=7, reaction_damage_dot=2)

    merged = metrics.merge_stages([a, b])
    assert merged.reaction_damage_amp == 3
    assert merged.reaction_damage_splash == 7
    assert merged.reaction_damage_dot == 7
    assert merged.reaction_damage == merged.reaction_damage_amp + \
        merged.reaction_damage_splash


# --- D1 aggregate: pooled is not the per-fight mean -----------------------

def test_the_battery_share_is_pooled_and_the_mean_is_the_other_column():
    """`reaction_share`'s docstring is explicit and gives the reason:
    "POOLED, not averaged over fights: sum(reaction) / sum(all), so a
    6-damage fight does not weigh as much as a 300-damage one",
    with `share_by_fight_mean` offered alongside "because the two answer
    different questions". On a cohort of unequal weight the two numbers are
    far apart, so publishing the mean under the name `share` is a different
    claim wearing the ratified word.
    """
    tiny_all_reaction = _stats(total_damage_dealt=6, reaction_damage=6,
                               reaction_damage_amp=6)
    big_no_reaction = _stats(total_damage_dealt=300)

    r = metrics.reaction_share([tiny_all_reaction, big_no_reaction])
    assert r["share"] == 6 / 306
    assert r["share_by_fight_mean"] == 0.5
    assert r["share"] < r["share_by_fight_mean"]


def test_a_reaction_that_dealt_no_damage_is_not_a_fight_with_reaction_damage():
    """The key is named `fights_with_any_reaction_damage`, and the D1 header
    in `tier05/reaction_telemetry.py` says why the distinction is load-bearing:
    Superconduct's Vulnerable, Frozen's halved action and Crystallize's block
    are reactions that put NO damage on the board, and "a reaction with a 0%
    damage share can still be the reason a fight was won". Counting `reactions`
    here would make the column a reaction counter under a damage name.
    """
    all_control = _stats(reactions=3, reaction_damage=0, total_damage_dealt=40)
    r = metrics.reaction_share([all_control])
    assert r["damage_from_reactions"] == 0
    assert r["fights_with_any_reaction_damage"] == 0


# --- D2: the two block columns are two different quantities ---------------

def test_block_at_open_is_the_leftover_and_block_at_end_is_what_was_built():
    """The emit sites name the difference and say it is the point: the
    `turn_open` sample is taken above the block clear, so it is "the block
    that SURVIVED the enemy", while `turn_close` is "the block standing when
    the player hands the turn over ... which is the quantity a demand curve is
    read against". Zero either column out and the record still has six fields
    per row and still passes every shape test in the suite.
    """
    stats = run_battery(*REACTIVE, 40, 7)
    rows = [row for s in stats for row in s.turn_trajectory]
    assert rows

    # Turn 1 has nothing before it, so nothing survived into it.
    assert all(s.turn_trajectory[0][2] == 0 for s in stats if s.turn_trajectory)
    # Later turns do inherit leftover block -- the column is not constant-zero.
    assert any(row[2] > 0 for row in rows), "no turn opened on leftover block"
    # And the close column carries block the player built and kept.
    assert any(row[3] > 0 for row in rows), "no turn closed holding block"
    # They are genuinely two columns: some turn's leftover differs from what
    # it closed holding.
    assert any(row[2] != row[3] for row in rows if row[3] >= 0)
