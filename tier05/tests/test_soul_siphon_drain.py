"""Lagavulin Matriarch's Soul Siphon -- the PLAYER half (EB-25).

Soul Siphon is one game action that steals: the Matriarch gains 2 Strength
and the player loses 2 Strength and 2 Dexterity. Only her half was authored,
so the sim's second Act-1 boss was the anti-turtle clock in name only -- the
turtle's block and the scaler's damage were never actually touched, which
silently biased the Act-1 boss split against Vantom's burst race.

The player half is authored on the EXISTING general `debuff` intent kind,
which already applies an arbitrary power to `state.player`
(`combat._enemy_turn`, `kind == "debuff"` -> `powers.apply_power(state,
state.player, ...)`). Nothing Lagavulin-shaped was added anywhere: the sheet
names strength/dexterity with negative amounts, exactly as act2/act3 name
weak/vulnerable/frail with positive ones.

WHY THE DRAIN IS PERMANENT: `powers.DECAYING` is
(weak, vulnerable, frail, ceremonial_garment). Strength and Dexterity are not
in it, so nothing ticks them back up -- a drained stack survives to the end of
the fight, which is the sheet's "permanently".

WHY THREE BEATS: the intent grammar is one intent per enemy turn
(`_enemy_turn` calls `advance_intent()` once), so a multi-effect game action
is authored as consecutive beats -- the convention already used by this
enemy's own "Slash's +12 block (beat)" and by Sting's Weak+Frail pair in
act3_pool.yaml. These tests therefore pin the SOUL SIPHON WINDOW (the three
beats that follow the block beat), not a single turn.
"""

import random

from tier0.engine import combat, powers
from tier0.tests.conftest import make_state
from tier05 import acts

# Index of each beat in the authored rotation.
SLASH, DISEMBOWEL, SLASH2, BLOCK, SIPHON_SELF, SIPHON_STR, SIPHON_DEX = range(7)
CYCLE = 7


def _spec():
    return next(b for b in acts.boss_pool(0)
                if b["id"] == "lagavulin_matriarch")


def _boss():
    return acts.spawn(_spec(), random.Random(0))[0]


def _turns(state, boss, n):
    """Take n enemy turns, ignoring sleep (the drain is a rotation fact, not
    a sleep fact -- sleep is exercised by the sheet's `sleep_turns`)."""
    boss.sleep_turns = 0
    for _ in range(n):
        state.turn += 1
        combat._enemy_turn(state, boss)


# --- sheet wiring ----------------------------------------------------------


def test_sheet_wires_both_drain_beats_onto_soul_siphon():
    intents = _spec()["enemies"][0]["intents"]
    assert len(intents) == CYCLE
    assert intents[SIPHON_SELF] == {"kind": "buff", "power": "strength",
                                    "amount": 2}
    assert intents[SIPHON_STR] == {"kind": "debuff", "power": "strength",
                                   "amount": -2}
    assert intents[SIPHON_DEX] == {"kind": "debuff", "power": "dexterity",
                                   "amount": -2}


def test_the_drain_beats_are_the_general_debuff_kind_not_a_new_one():
    """No Lagavulin-special intent kind: every kind she uses is one the rest
    of the pools already use."""
    kinds = {i["kind"] for i in _spec()["enemies"][0]["intents"]}
    assert kinds == {"attack", "block", "buff", "debuff"}


def test_the_sheet_no_longer_claims_the_player_half_is_unimplemented():
    """The UNIMPLEMENTED note must name Plating only (Plating stays in
    SKIP-10.9). A stale skip note is how a fixed thing stays 'known broken'."""
    from pathlib import Path
    text = Path(acts._CONTENT_DIR / "act1_pool.yaml").read_text(
        encoding="utf-8")
    block = text.split("- id: lagavulin_matriarch", 1)[1].split(
        "enemies:", 1)[0]
    assert "UNIMPLEMENTED" in block and "Plating" in block
    assert "stat-drain" not in block


# --- the drain fires -------------------------------------------------------


def test_drain_fires_on_the_soul_siphon_beats_and_nowhere_else():
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    seen = []
    for _ in range(CYCLE):
        _turns(st, boss, 1)
        seen.append((st.player.powers.get("strength", 0),
                     st.player.powers.get("dexterity", 0)))
    # Beats 0-4 (Slash, Disembowel, Slash, Block, her own +2 Str) take
    # nothing from the player; beats 5 and 6 take one stat each.
    assert seen[:SIPHON_STR] == [(0, 0)] * SIPHON_STR
    assert seen[SIPHON_STR] == (-2, 0)
    assert seen[SIPHON_DEX] == (-2, -2)


def test_soul_siphon_is_a_theft_both_halves_on_the_same_window():
    """Her +2 and the player's -2/-2 are one action's worth of Soul Siphon."""
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    _turns(st, boss, SIPHON_SELF)                  # up to the siphon window
    assert boss.powers.get("strength", 0) == 0
    assert st.player.powers.get("strength", 0) == 0
    _turns(st, boss, 3)                            # the whole siphon window
    assert boss.powers["strength"] == 2
    assert st.player.powers["strength"] == -2
    assert st.player.powers["dexterity"] == -2


def test_the_drain_does_not_decay_at_turn_end():
    """Permanent for the fight: strength/dexterity are not in DECAYING."""
    assert "strength" not in powers.DECAYING
    assert "dexterity" not in powers.DECAYING
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    _turns(st, boss, CYCLE)
    drained = (st.player.powers["strength"], st.player.powers["dexterity"])
    for _ in range(5):
        powers.on_turn_end(st, st.player)
    assert (st.player.powers["strength"],
            st.player.powers["dexterity"]) == drained == (-2, -2)


# --- it stacks: the long fight gets strictly worse BOTH ways ---------------


def test_the_drain_stacks_across_cycles():
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    for cycle in range(1, 4):
        _turns(st, boss, CYCLE)
        assert st.player.powers["strength"] == -2 * cycle
        assert st.player.powers["dexterity"] == -2 * cycle
        assert boss.powers["strength"] == 2 * cycle


def test_the_long_fight_gets_strictly_worse_in_both_directions():
    """Her damage strictly rises while the player's damage AND block strictly
    fall. Before EB-25 only the first of the three moved."""
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    hers, player_dmg, player_blk = [], [], []
    for _ in range(4):
        hers.append(powers.modify_damage_dealt(boss, 19))
        player_dmg.append(powers.modify_damage_dealt(st.player, 20))
        player_blk.append(powers.modify_block_gained(st.player, 20))
        _turns(st, boss, CYCLE)
    assert hers == sorted(hers) and len(set(hers)) == 4
    assert player_dmg == sorted(player_dmg, reverse=True)
    assert len(set(player_dmg)) == 4
    assert player_blk == sorted(player_blk, reverse=True)
    assert len(set(player_blk)) == 4
    # Concretely: 19/21/23/25 hers, 20/18/16/14 dealt, 20/18/16/14 blocked.
    assert hers == [19, 21, 23, 25]
    assert player_dmg == [20, 18, 16, 14]
    assert player_blk == [20, 18, 16, 14]


def test_a_card_played_after_the_drain_actually_lands_softer():
    """End-to-end through the card ops, not just the funnels: the drain has to
    reach real damage and real block or it is decoration."""
    from tier0.engine.state import Card
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    st.player.energy = 99
    strike = Card(id="s", name="s", cost=0, type="attack",
                  effects=[{"op": "damage", "amount": 12}])
    guard = Card(id="g", name="g", cost=0, type="skill",
                 effects=[{"op": "block", "amount": 12}])
    st.player.hand = [strike, guard]
    hp0, boss.block = boss.hp, 0
    combat.play_card(st, strike)
    combat.play_card(st, guard)
    dealt_before, blocked_before = hp0 - boss.hp, st.player.block

    _turns(st, boss, CYCLE)
    st.player.block = 0
    st.player.energy = 99
    st.player.hand = [strike, guard]
    hp1, boss.block = boss.hp, 0
    combat.play_card(st, strike)
    combat.play_card(st, guard)
    assert hp1 - boss.hp == dealt_before - 2
    assert st.player.block == blocked_before - 2


# --- clamps: a deep drain must not invert anything -------------------------


def test_a_deep_drain_floors_damage_and_block_at_zero():
    """Many cycles drive Strength/Dexterity well past the printed numbers.
    Neither may go negative: `powers._floor` clamps damage (a negative dmg
    would GIFT the player block through `_enemy_turn`'s
    `blocked = min(block, dmg)`) and `modify_block_gained` clamps the
    additive sum before Frail can invert the multiplier."""
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    _turns(st, boss, CYCLE * 12)                   # -24 Str / -24 Dex
    assert st.player.powers["strength"] == -24
    assert st.player.powers["dexterity"] == -24
    assert powers.modify_damage_dealt(st.player, 6) == 0
    assert powers.modify_block_gained(st.player, 6) == 0
    st.player.powers["frail"] = 2
    assert powers.modify_block_gained(st.player, 6) == 0


def test_a_deep_drain_never_gifts_the_player_block_or_hp():
    """The `_floor` docstring's exact failure: a card that would deal negative
    damage must deal zero, and a fully drained player must not heal an enemy
    or gain block from attacking."""
    from tier0.engine.state import Card
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    _turns(st, boss, CYCLE * 12)
    st.player.energy, st.player.block = 99, 0
    strike = Card(id="s", name="s", cost=0, type="attack",
                  effects=[{"op": "damage", "amount": 6}])
    guard = Card(id="g", name="g", cost=0, type="skill",
                 effects=[{"op": "block", "amount": 6}])
    st.player.hand = [strike, guard]
    hp0, boss.block = boss.hp, 0
    combat.play_card(st, strike)
    combat.play_card(st, guard)
    assert boss.hp == hp0                          # zero, never negative
    assert st.player.block == 0                    # zero, never negative


def test_the_drain_is_not_converted_by_kokomis_strength_guard():
    """Flawless Strategy converts POSITIVE Strength to Charge; a theft is not
    a gain, so Kokomi bleeds Strength like everyone else (the guard's own
    'Negative strength (Mangle-class) is not a gain' comment)."""
    boss = _boss()
    st = make_state(enemies=[boss], hp=5000)
    st.player.relic_hooks = {"tamakushi_casket"}
    _turns(st, boss, CYCLE)
    assert st.player.powers["strength"] == -2
    assert st.player.powers["dexterity"] == -2


# --- the other Act-1 boss is untouched -------------------------------------


def test_vantom_gains_no_drain():
    """EB-25 is a Lagavulin item; the burst-race boss keeps its shape."""
    vantom = next(b for b in acts.boss_pool(0) if b["id"] == "vantom")
    kinds = [i["kind"] for i in vantom["enemies"][0]["intents"]]
    assert "debuff" not in kinds
