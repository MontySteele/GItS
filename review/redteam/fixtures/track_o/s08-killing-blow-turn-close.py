"""Track O / slice 08 reproducer 2 -- the D2 sentinel and the killing blow.

`metrics.FightStats.turn_trajectory`'s field comment says `block_at_end` is
"the `turn_close` sample, or -1 when the turn never closed because the fight
ended inside it", and `combat._player_turn`'s emit-site comment says "A turn
that ended by killing the last enemy or by the player dying never reaches
here [the turn_close emit]".

Both are false for the killing blow. `_player_turn`'s card loop is
`while not state.over: ...` -- it BREAKS on the kill and then falls through the
whole turn-end tail, including the `turn_close` emit. The only turns that ever
reach the -1 sentinel are those the engine returns from at TURN START
(combat.py's three `if not p.alive or state.over: return` guards).

Consequence: `metrics.turn_profile`'s documented filter -- "skips the -1 rows
... so a mean over two turns is not mistaken for a mean over two hundred" --
removes almost nothing, and every won fight's LAST turn (the turn the player
dumped their hand into a kill, holding whatever block they had) is inside
`mean_block_at_end`.

Run:  PYTHONPATH=. python review/redteam/fixtures/track_o/s08-killing-blow-turn-close.py
"""
from __future__ import annotations

import random

from tier0.engine import combat, effects
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.harness import metrics
from tier0.harness.runner import run_battery


def unit_probe() -> None:
    """One synthetic turn whose last card play kills the last enemy."""
    e = Enemy(hp=6, max_hp=6, name="dummy", intents=[{"kind": "attack",
                                                      "amount": 0}])
    st = CombatState(player=Player(hp=80, max_hp=80), enemies=[e],
                     rng=random.Random(0))
    kill = Card(id="finisher", name="Finisher", type="attack", cost=0,
                effects=[{"op": "damage", "amount": 99, "target": "enemy"}])
    st.player.hand = [kill]
    st.emit("turn_open", hp=80, block=7)
    st.player.block = 7
    combat.play_card(st, kill)
    assert st.over, "fixture must end the fight"
    st.emit("turn_close", block=st.player.block)   # what _player_turn does
    row = metrics.extract(st, hp_start=80).turn_trajectory[0]
    print(f"unit probe: turn_trajectory row = {row}")
    print(f"    block_at_end = {row[3]}   (docstring says -1 on a "
          f"fight-ending turn)")


def battery_probe() -> None:
    stats = run_battery("klee", "reaction_weighted", "punisher", "generic",
                        200, 7)
    rows = [r for s in stats for r in s.turn_trajectory]
    unsampled = [r for r in rows if r[3] == -1]
    won = sum(1 for s in stats if s.won)
    with_traj = sum(1 for s in stats if s.turn_trajectory)
    print(f"\nbattery: 200 fights, {won} won, {with_traj} with a trajectory")
    print(f"    turn rows                 {len(rows)}")
    print(f"    rows carrying the -1      {len(unsampled)}")
    print(f"    fights whose LAST row is -1 "
          f"{sum(1 for s in stats if s.turn_trajectory and s.turn_trajectory[-1][3] == -1)}")
    prof = metrics.turn_profile(stats)
    t = min(prof)
    print(f"    turn_profile[{t}]: fights={prof[t]['fights']} "
          f"block_end_samples={prof[t]['block_end_samples']}")


if __name__ == "__main__":
    unit_probe()
    battery_probe()
