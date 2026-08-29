# Klee slice 1 — the map from turn id to arm

**R213 E2.** Six turns in three matched pairs. The ids are opaque on purpose:
they are printed into the design-blind packet a grader reads, so nothing in one
may say which arm it belongs to. This file is the map, and it is not shown to a
grader.

**A fourth arm was proposed and is not here.** `proto_spark_mode_bombs` / "Bag
of Tricks" is held for [USER] on the independent seat's doctrine verdict, so it
has no rows and no boards. See the packet's "Held for [USER]".

**Nothing here is staged.** Every seed is unpinned and every row reads
`staged: pending`. The prototype halves need a dev build carrying the
quarantined rows (`klee-mod\build\deploy_proto.ps1`); the shipped halves could
be staged on a release build, but the live game and the art-bearing checkout
belong to another session and this branch was built in a worktree.

**The seed rule.** Within a pair, the first half staged rolls a seed and
`stage` records it; the other half must then be staged with `--seed <that
value>`. Two halves on two seeds are two different fights, and the pair has
measured the encounter instead of the card. If the seed's fight telegraphs
anything but an attack, re-roll — the intent is the question here.

## The map

| turn | file | arm | card under test | staged |
|---|---|---|---|---|
| `klee-slice1-t01` | `priced-attack-shipped.yaml` | 1 — the priced Attack | `flame_on_the_wick` (shipped) | pending |
| `klee-slice1-t02` | `priced-attack-prototype.yaml` | 1 — the priced Attack | `proto_spark_priced_strike` | pending |
| `klee-slice1-t03` | `priced-draw-shipped.yaml` | 2 — the priced draw | `eager_to_help` (shipped) | pending |
| `klee-slice1-t04` | `priced-draw-prototype.yaml` | 2 — the priced draw | `proto_spark_priced_draw` | pending |
| `klee-slice1-t05` | `burst-conversion-shipped.yaml` | 3 — the Burst conversion | `clockwork_toy` (shipped) | pending |
| `klee-slice1-t06` | `burst-conversion-prototype.yaml` | 3 — the Burst conversion | `proto_spark_burst_conversion` | pending |

## The boards

Every board: player **42/62**, no Block, **turn 3**, **2 energy**, a **Spark
bank of exactly 3**, one enemy telegraphing an attack, `exact_hand: true`.
Three of the four cards in hand are the same on every board — `kaboom` (1,
Attack, 7), `rapid_fire` (2, Attack, 4 damage four times) and `duck_and_cover`
(1, Skill, 5 Block) — and the fourth is the card under test.

**Why the bank is exactly three on every board, and never four.** Three is the
free Attack's threshold and it is also every prototype's price, so on every
board the bank buys exactly *one* of two things and the player has to pick. At
four or more both could happen and there would be no question left. This is
the opposite of Kokomi slice 2's choice, where the bank deliberately sat above
the price so the shipped readers stayed live on both halves — there the
shipped card *read* the bank, here the shipped rule *takes* it, and a bank that
survives the rule is a bank the rule was not really competing for.

**Why Rapid Fire is on every board.** It is the control, not filler. It is the
board's only *paid* Attack, so it is what the automatic rule spends the bank on
when the player does nothing. Without a paid Attack the free-Attack rule has
nothing to fire on and the arm's question cannot be asked at all.

**Why Duck and Cover, and only Duck and Cover.** It is the one standalone Block
on these boards, in hand everywhere, because a Spark payoff that nothing
competes with is not a decision. A second flat-Block card would make "defend"
the answer by arithmetic rather than by choice.

## The arithmetic that says no line is lethal

Klee has no Strength on these boards and the enemy carries no aura, so every
number below is the printed number. Rapid Fire's four hits all land on the one
enemy. A Bomb is not counted as this turn's damage because it detonates at the
start of the next one.

| turn | enemy HP | largest total damage the board can produce | headroom |
|---|---|---|---|
| `t01` | 48 | Rapid Fire free at bank 3 (**16**) + Kaboom! (**7**) + Flame on the Wick (**6**) = **29** | 19 |
| `t02` | 48 | Second Helping first (**12**, bank → 0) then Rapid Fire at its printed 2 energy (**16**) = **28**; the other order is Rapid Fire free (**16**) + Kaboom! (**7**) = **23** and leaves Second Helping unplayable | 20 |
| `t03` | 40 | Rapid Fire free (**16**) + Kaboom! (**7**) = **23** | 17 |
| `t04` | 40 | Rapid Fire free (**16**) + Kaboom! (**7**) = **23** | 17 |
| `t05` | 44 | Rapid Fire free (**16**) + Kaboom! (**7**) = **23** | 21 |
| `t06` | 44 | Rapid Fire free (**16**) + Kaboom! (**7**) = **23** | 21 |

**The thing this table shows that is the slice itself:** on `t02` the ORDER of
two plays changes the total, and on `t01` it does not. That is the whole of arm
1 in one row.

## The closeness reading

`staged_turn closeness` was run on all six declared boards.
**All six SURVIVE**, against a dominance threshold of 0.5:

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t01` | **0.1695** | 34.800 | 28.900 | 15 |
| `t02` | **0.1076** | 28.800 | 25.700 | 12 |
| `t03` | **0.1667** | 28.800 | 24.000 | 14 |
| `t04` | **0.2049** | 28.800 | 22.900 | 10 |
| `t05` | **0.0062** | 28.980 | 28.800 | 14 |
| `t06` | **0.2049** | 28.800 | 22.900 | 10 |

Per-turn detail is in `review/qa/<turn id>/closeness.json`. Under R215 B this
reading is the one number from a prototype board that may be quoted, because it
reads a *turn* and not a row. It is not a claim that any turn is good; it only
says the falsifier refuses none of them.

**What the reading cannot see, disclosed rather than buried.** On `t04` and
`t06` the card under test appears in **none** of the top lines, and in both
cases the reason is a hole in the pilot rather than a fact about the card:

1. **`t04` — the tier0 mirror has no draw pile.** `Board` carries hp, block,
   energy, turn, resources, hand and enemies, and nothing else, so both halves
   of pair 2 draw from an empty pile and every draw is worth zero. Rummage
   therefore scores as a card that spends 1 energy and 3 Sparks to do nothing.
   The error runs **one way** — the arm is *under*-valued, so it is less likely
   to dominate, and dominance is the only thing the falsifier refuses. The live
   board has a real deck, so the blind packet is unaffected; it is the mirror
   alone that is blind.
2. **`t06` — the pilot does not price Burst Energy.** It has no
   hold-versus-spend term for Sparks either (`powder_charge`'s row says so on
   the shipped sheet), and nothing anywhere in `tier0/pilot/policy.py` values a
   meter that pays out in a future turn. So Slow Burn scores as Duck and
   Cover's 5 Block, one energy, *plus* the loss of a free Rapid Fire — strictly
   worse, correctly, for a pilot that cannot see what it bought. Same one-way
   error direction.

Both are `POLICY_VERSION` changes carrying their own re-baseline, which is
frozen and is not this slice's to make. **The blind seat is the only reading
pairs 2 and 3 have**, and if a human grader cannot separate those halves
either, that is itself the arm's answer.
