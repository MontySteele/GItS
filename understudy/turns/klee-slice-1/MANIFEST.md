# Klee slice 1 — the map from turn id to arm

**R213 E2.** Six turns in three matched pairs. The ids are opaque on purpose:
they are printed into the design-blind packet a grader reads, so nothing in one
may say which arm it belongs to. This file is the map, and it is not shown to a
grader.

**A fourth arm was proposed and is not here.** `proto_spark_mode_bombs` / "Bag
of Tricks" is held for [USER] on the independent seat's doctrine verdict, so it
has no rows and no boards. See the packet's "Held for [USER]".

**All six are staged.** They were staged live on **`0.2.1314+proto`** (built
by `deploy_proto.ps1` on the art-bearing main checkout, game closed,
`validate.ps1` OK) against game v0.111.0 / buildid 24724944 / `public-beta` /
BaseLib 3.4.5.0 -- the pin, re-read off disk before any live work and unmoved.
Each pair's seed is pinned into both of its files and into the table below.

**The seed rule.** Within a pair, the first half staged rolls a seed and
`stage` records it; the other half must then be staged with `--seed <that
value>`. Two halves on two seeds are two different fights, and the pair has
measured the encounter instead of the card. If the seed's fight telegraphs
anything but an attack, re-roll — the intent is the question here.

## The map

| turn | file | arm | card under test | seed |
|---|---|---|---|---|
| `klee-slice1-t01` | `priced-attack-shipped.yaml` | 1 — the priced Attack | `flame_on_the_wick` (shipped) | `N6PCA0C9GCFG` |
| `klee-slice1-t02` | `priced-attack-prototype.yaml` | 1 — the priced Attack | `proto_spark_priced_strike` | `N6PCA0C9GCFG` |
| `klee-slice1-t03` | `priced-draw-shipped.yaml` | 2 — the priced draw | `eager_to_help` (shipped) | `LUMNB3D9GFKD` |
| `klee-slice1-t04` | `priced-draw-prototype.yaml` | 2 — the priced draw | `proto_spark_priced_draw` | `LUMNB3D9GFKD` |
| `klee-slice1-t05` | `burst-conversion-shipped.yaml` | 3 — the Burst conversion | `clockwork_toy` (shipped) | `PQUR2MZ6Z1KF` |
| `klee-slice1-t06` | `burst-conversion-prototype.yaml` | 3 — the Burst conversion | `proto_spark_burst_conversion` | `PQUR2MZ6Z1KF` |

## The staging, and the eleven rolls it took

Each pair's seed was discovered by staging the SHIPPED half, then pinned onto
both halves -- in each file's own `seed:` key and in the table above. Eleven
rolls in total. The packet asks for ONE enemy telegraphing an ATTACK, and most
Act-1 first fights are two or three bodies, a debuff, or an attack too small for
the defensive half of the board to mean anything.

| pair | rolls | seed | the body it settled on |
|---|---|---|---|
| 1 -- the priced Attack | 4 | `N6PCA0C9GCFG` | Seapunk 45/45, attacks for 11 |
| 2 -- the priced draw | 4 | `LUMNB3D9GFKD` | Nibbit 40/43, attacks for 12 |
| 3 -- the Burst conversion | 3 | `PQUR2MZ6Z1KF` | Nibbit 43/43, attacks for 12 |

**Every board settled BELOW its designed telegraph, and the operator kept
rolling rather than take the first attack it saw.** The design asked for 14, 16
and 18; the rolls delivered 11, 12 and 12. The first roll of pair 1 was a Sludge
Spinner telegraphing **8**, and it was rejected for the same reason Kokomi slice
2 rejected a 4: Duck and Cover is the deliberate defensive competitor on every
one of these boards, and against a small hit it is not a competitor at all. Of
the eleven rolls, four were bodies telegraphing 4, one was a pure debuff, and
two were multi-body encounters -- the three kept are the three largest
single-body attacks the eleven produced.

**Two boards lost HP to the clamp, and it is `set_hp`'s documented behaviour
rather than a surprise.** `set_hp` clamps at a creature's maximum. Pair 1 asked
for 48 and Seapunk's maximum is 45; pair 3 asked for 44 and this Nibbit's
maximum is 43. Pair 2 asked for 40 and got exactly 40. Each file now declares
the LIVE body rather than the design's placeholder, and the staging step was
moved to the achieved figure so a re-stage is exact rather than silently
clamped.

**Every stated property of every board still holds at the live figures:** one
enemy, an attack telegraphed, a Spark bank of exactly 3, 2 energy, 42/62 HP, no
Block, the declared four-card hand, and **no lethal line** -- the largest total
each board can produce is 29 against 45, 28 against 45, 23 against 40 twice and
23 against 43 twice.

**The observed board was checked against the declared one on all six before any
grade**, and the only divergences are the two clamped HP figures and the three
telegraph amounts recorded above. Spark 3, energy 2, Block 0, HP 42/62 and the
exact four-card hand read back live on every one of the six.

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

`staged_turn closeness` was run on all six boards **twice** -- once on the
DECLARED board and once on the live `--observed` board. **All twelve readings
SURVIVE**, against a dominance threshold of 0.5.

| turn | declared gap | declared top / runner-up | observed gap | observed top / runner-up |
|---|---|---|---|---|
| `t01` | **0.1695** | 34.800 / 28.900 | 0.1376 | 21.800 / 18.800 |
| `t02` | **0.1076** | 28.800 / 25.700 | 0.1899 | 15.800 / 12.800 |
| `t03` | **0.1667** | 28.800 / 24.000 | 0.1899 | 15.800 / 12.800 |
| `t04` | **0.2049** | 28.800 / 22.900 | 0.1899 | 15.800 / 12.800 |
| `t05` | **0.0062** | 28.980 / 28.800 | 0.1785 | 15.800 / 12.980 |
| `t06` | **0.2049** | 28.800 / 22.900 | 0.1899 | 15.800 / 12.800 |

`closeness.json` holds the **declared** reading and `closeness-observed.json`
the observed one, and that is the opposite of Kokomi slice 2's choice. The
reason is a defect the run found, stated here rather than buried.

**THE OBSERVED READING CANNOT SEE THE SPARK BANK AT ALL (`EB-185`).** Every one
of the six observed readings reports `unmapped_statuses: ["spark"]`. Klee holds
Sparks as a POWER on the wire (`SPARK_POWER`), the observed mapper's
`WIRE_RESOURCES` table covers registered RESOURCES only (Charge, Encore,
Fanfare, the three Burst meters), and `understudy/adapter.py`'s `STATUS_MAP` has
no `spark` row -- while the sim holds the bank in a separate `Player.sparks`
field that neither table reaches. So **every observed reading of a Klee board
scores a bank of ZERO**, and on this slice the bank is the entire question. It
shows in the numbers: on `t02`, `t04` and `t06` the line count collapses from
12/10/10 to **4**, because at a bank of zero the prototype cannot pay its own
price and drops out of every line; and on `t01` the top line falls from 34.8 to
21.8 because Rapid Fire is not free.

The declared reading is therefore the faithful one HERE, and it is the one
committed. The observed reading is kept beside it as the receipt for `EB-185`
rather than as a reading of these boards. Both SURVIVE, so the falsifier refuses
nothing either way, and under R213 F a SURVIVE is a refusal that did not fire
and never a rating.

**Two further things the DECLARED reading cannot do, unchanged from the design
and disclosed rather than buried.**

1. **On `t04` the mirror has no draw pile.** The tier0 `Board` carries hp,
   block, energy, turn, resources, hand and enemies and nothing else, so both
   halves of pair 2 draw from an empty pile and every draw is worth zero.
   Rummage scores as a card that spends 1 energy and 3 Sparks to do nothing, and
   it appears in none of the top lines. The LIVE board has a real deck, so the
   blind packet is unaffected; the mirror alone is blind.
2. **On `t06` the pilot does not price Burst Energy.** Nothing in
   `tier0/pilot/policy.py` values a meter that pays out in a future turn, and it
   has no Spark hold-versus-spend term either. Slow Burn scores as Duck and
   Cover's 5 Block minus a free Rapid Fire -- strictly worse, correctly, for a
   pilot that cannot see what it bought.

Both errors run **one way**: the arm is *under*-valued, so less likely to
dominate, and dominance is the only thing the falsifier refuses. A SURVIVE here
is the conservative direction. Both fixes are `POLICY_VERSION` changes carrying
their own re-baseline, which is frozen and not this slice's to make. **The blind
graders are the only reading pairs 2 and 3 have.**

**One number the declared reading did NOT move.** Every declared gap, top line
and runner-up above is byte-identical to the pre-run reading taken on the design
placeholder boards, even though two enemies lost HP to the clamp and all three
telegraphs came in below the design. That is not luck: no line on any board is
lethal and no telegraph crosses a threshold Duck and Cover's 5 Block could meet,
so the pilot's ordering over the lines is untouched by the difference.
