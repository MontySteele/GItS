# Co-op reaction round, 2026-10-07

The paired co-op check in `docs/current/operations/stage-gate.md` ("Solo
first, co-op checked"), agreed at the defaults on 2026-10-06. [USER]: "It's
fine for co-op to be easier, but the characters should not be outright weak
in single player and dependent on reactions in a way that makes co-op
exponentially easier."

**What ran.** Seed `30KMHAVG9SMQ`, A0, the `klee-next` staging build
(0.2.4508+next, then 0.2.4513+next with #948, then 0.2.4516+next with #949).
One blind Sonnet seat (medium) per player over the co-op bridge.

| Pair | Result | Notes |
|---|---|---|
| Klee (host) + Varka | Died at the act-3 boss, Aeonglass, floor 45 (731/1331 left) | Act-1 and act-2 bosses beaten; 21 fights. First attempt abandoned on a desync at floor 24 (#948); the rerun stalled at the floor-28 Crystal Sphere (#949), unstuck by one map vote cast by the coordinator, then two fresh seats played acts 2-3. |
| Ironclad (host) + Silent | Died at an act-1 elite, floor 7 | Four Phantasmal Gardeners on near-starter decks. The Silent seat voted for the rest site; the split vote sent the party to the elite. |

**The comparison does not answer the question.** Both pairs met the same
elite: Klee + Varka on floor 14 with built decks (61 to 50 HP), Ironclad +
Silent on floor 7 with starter decks (both dead). One run a side is routing
noise, not a strength reading.

**What reactions are worth in co-op (Klee + Varka, 28 fights, 115 turns;
`telemetry_report.py --coop --reactions`, #945).**

| | Reactions a turn | Amplifier bonus damage a turn | Reaction debuff stacks a turn |
|---|---|---|---|
| Team | 1.81 | 1.48 (Melt 0.99, Vaporize 0.49) | 1.23 (Weak 0.65, Poison 0.31, Vulnerable 0.24) |
| Klee | 0.51 (Overload 0.38) | 0.30 | 0.37 (Weak 0.35) |
| Varka | 1.30 (Swirl 0.51, Overload 0.32) | 1.18 | 0.87 |

- The free x1.5 / x1.75 is worth about 1.5 damage a turn to the team: not a
  driver.
- The co-op gift is debuffs, about 1.2 stacks a turn, two thirds of them
  from Varka. Klee's own Weak rate (0.35 a turn) is five times the solo
  Sonnet seats' Overload Weak (0.07 a turn, fights since 2026-10-02), which
  fits [USER]'s reading: two decks' Electro feeding one Pyro.

**What played well.** Cross-player reactions fired without coordination; the
Klee seat's Overloads carried most of the team's Weak.

**What did not.** Two bridge defects ended runs (both fixed, below). Seats
cannot coordinate map votes, and a split vote picked the control pair's
death. Three Klee screens ended under the seat when the partner finished the
fight ("you are not in a battle").

**Fixed in the round.**
- #945: reaction telemetry (by type, amplifier bonus, debuffs) and the
  report's `--coop` / `--reactions`.
- #948: the bridge's potion discard was local-only; in co-op it desynced the
  run (StateDivergence, Tiny Mailbox rewards with a full belt). It now
  enqueues the game's `DiscardPotionGameAction`.
- #949: the co-op state reader kept reporting a finished Crystal Sphere under
  the open map; it now reports the map, and `reveal` never loops.

**What to change.** A co-op strength reading needs several seeds a side, or
a fight-level comparison on shared encounters, before it can be read against
the bar; the open pick is in the reply of 2026-10-07.
