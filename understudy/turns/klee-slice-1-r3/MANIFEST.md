# Klee slice 1 — ROUND 3 turn manifest

Four turns in two matched pairs, run 2026-08-29 on the dev build
`0.2.1353+proto`. The game pin was read off disk before any live work and had
not moved: **v0.111.0**, commit `41cef1ea`, Steam buildid `24724944`, branch
`public-beta`, BaseLib **3.4.5.0**.

**Round 3 exists for one reason and it is not a card.** Rounds 1 and 2 ran
Rummage and Slow Burn on content the doctrine seat supplied — its re-authoring
of arm 2's text, its pick of arm 4's printed Burst figure — and the same model
family then graded and pair-read both, so both outcomes were **provisional**
(packet §11). Both rows are re-derived Claude-side from the clause the seat
named, their `authored_by:` is `[claude]` again, and this round re-runs the two
arms with the seat's text and number discarded. **Arm 1 (Second Helping) is not
in this round**: its row was never touched by the seat and its round-2 ADVANCE
is already clean.

## The map from opaque id to arm

The turn ids are deliberately opaque, because they are printed into the
design-blind packet. The filenames name the arm; only the tooling and the
packet-writer read filenames.

| turn | file | half | card under test | seed |
|---|---|---|---|---|
| `klee-slice1-r3-t03` | `priced-draw-shipped.yaml` | shipped | Eager to Help | `8D3369V27Z55` |
| `klee-slice1-r3-t04` | `priced-draw-prototype.yaml` | prototype | **Rummage** (`proto_spark_priced_draw`) | `8D3369V27Z55` |
| `klee-slice1-r3-t05` | `burst-conversion-shipped.yaml` | shipped | Imaginary Friend | `PQUR2MZ6Z1KF` |
| `klee-slice1-r3-t06` | `burst-conversion-prototype.yaml` | prototype | **Slow Burn** (`proto_spark_burst_conversion`) | `PQUR2MZ6Z1KF` |

## Pair 3 — the Burst conversion. UNCHANGED, and deliberately so.

`t05`/`t06` are the round-2 files byte-identical but for the turn id and the
header, on round 2's own pinned seed `PQUR2MZ6Z1KF`. Round 2 already ADVANCED
this arm on a repaired board with a clean replay; what made that outcome
provisional was **who derived the printed Burst figure**, not the board. The
figure is re-derived Claude-side and lands on the same number, so re-boarding
would have changed a second thing and made the round unattributable.

Board: 42/62 HP, no Block, **2 energy**, Spark bank 3, Burst meter 20 of 40,
Nibbit 43/43 telegraphing an attack for 12. Hand of four: the card under test,
Kaboom!, Rapid Fire, Duck and Cover. Largest total at true values 23 against
43 — **no lethal line**.

## Pair 2 — the priced draw. RE-SET, and the reviewer set it.

Round 2 RETURNED this arm with a named repair:

> *"The board prices the prototype against 16 guaranteed damage and defense
> while offering three unknown, mostly unaffordable draws, and one grader
> consequently constructed an illegal comparison. This arm needs a board that
> can expose a real draw destination before whole-fight testing."*

Three changes, all of them that repair and nothing else.

1. **Energy 4, not 2.** Playing the card under test leaves **three energy
   standing** after it resolves, where round 2 left one.
2. **A hand of three, not four.** Kaboom! is off the board: the hand alone
   could otherwise absorb every point of energy and the drawn cards would have
   had nothing to be played with. Both cards that make the decision live stay —
   **Rapid Fire**, the paid Attack the automatic rule would take the bank for,
   and **Duck and Cover**, the one standalone Block.
3. **A declared draw pile.** Three copies of Kaboom! (1 energy, 7 damage) are
   granted to the draw pile before the turn, and an assumption line states that
   the pile is real, that they are in it, and that nothing in it costs more than
   2 energy.

**The live pile, read off `observed.json` after staging, and identical on both
halves — 13 cards:** 3× Duck and Cover (1), Jumpy Dumpty (2), **6× Kaboom!**
(1, three of them the grant), Pop! (0), Kaeya — Frostgnaw (1), Prune — Little
Witch's Hunt (1). Nothing in it costs more than 2, so the assumption line is
true as staged. *(Several print at `Cost: 0` on the wire because the bank is
3 and the free-Attack rule zeroes Attacks; the figures above are the PRINTED
costs.)*

Board: 42/62 HP, no Block, **4 energy**, Spark bank 3, **Seapunk 46/46**
telegraphing an attack for 11.

### The seed, and the nine rolls

The seed was discovered on the shipped half and pinned onto both. It took
**nine staging attempts**, and the honest account of them is:

| roll | outcome | why it was not taken |
|---|---|---|
| 1 | Fuzzy Wurm Crawler 48/57, attack **4** | **operator error, not a roll:** a `seed: PENDING` placeholder left in the file was accepted as a literal seed, so nothing was rolled. The key was removed. |
| 2 | Fuzzy Wurm Crawler 48/55, attack **4** | telegraph too small — Duck and Cover is the deliberate defensive competitor, and against a 4 it is not a competitor at all |
| 3 | Seapunk 45/45, attack 11 | usable telegraph, but 45 HP sits at the board's damage ceiling once the delayed Bomb is counted |
| 4 | Seapunk 44/44, attack 11 | same, and lower |
| 5 | Sludge Spinner 38/38, attack 8 | telegraph too small (round 1 rejected an 8 for the same reason); run seed also read back `None` (`EB-191`) |
| 6 | Seapunk 44/44, attack 11 | run seed read back `None` (`EB-191`), so nothing could be pinned |
| 7 | Nibbit 43/43, attack 12 | usable telegraph, HP under the ceiling |
| 8 | Leaf Slime (S) 13/13, attack 3 | far too small on both counts |
| 9 | **Seapunk 46/46, attack 11** | **TAKEN** — `8D3369V27Z55` |

### The arithmetic — no line on this board is lethal

The ceiling has to count what the **draw** can reach, which is new this round.
The most damaging cards the pile holds are Jumpy Dumpty (printed 2 energy: 8
damage twice = **16** immediate, plus a Bomb dealing **6** that lands later) and
Kaboom! (printed 1: **7**).

**Shipped half (`t03`), the larger of the two.** The bank makes the first Attack
free, so:

| play | energy | immediate damage |
|---|---|---|
| Rapid Fire (printed 2, free at bank 3) | 0 | 16 |
| Eager to Help (1) → draw 2 | 1 | — |
| drawn Jumpy Dumpty (2) | 2 | 16 |
| drawn Kaboom! (1) | 1 | 7 |
| **total** | **4 of 4** | **39** |

39 immediate against **46**, and **45** even counting the delayed Bomb.

**Prototype half (`t04`).** Rummage takes the bank, so Rapid Fire costs its
printed 2: Rummage (1) → draw 3, then the best 3 energy of Attacks is Jumpy
Dumpty (2) + Kaboom! (1) = 23, or Rapid Fire (2) + Kaboom! (1) = 23. **23**
against 46.

"Just kill it" never ends this turn on either half.

### What the re-set could not fix, disclosed rather than buried

The tier0 mirror `Board` carries hp, block, energy, turn, resources, hand and
enemies and **no draw pile**, so in the mirror both halves still draw from an
empty pile and every draw scores zero. Rummage still appears in none of the
mirror's top lines. The error runs **one way** — the arm is *under*-valued, so
less likely to dominate, and dominance is the only thing the falsifier refuses
— so a SURVIVE here stays the conservative direction. The fix is a `Board`
field plus a line in `_state_from_board`, owed and unbuilt. The **live** board
has the real deck, so the blind packet and the replay are unaffected; it is the
mirror alone that is blind, and **what the draw actually reached is recorded at
replay** in the packet's §13.

## The closeness reading

`staged_turn closeness` was run **both ways** on all four turns. **All eight
SURVIVE**, against a dominance threshold of 0.5, and declared and observed are
byte-identical on every one — `EB-185` is closed, so the observed board now
carries the Spark bank and the two mirrors agree.

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t03` | 0.0478 | 23.000 | 21.900 | 7 |
| `t04` | 0.0274 | 21.900 | 21.300 | 7 |
| `t05` | 0.0062 | 28.980 | 28.800 | 14 |
| `t06` | 0.2049 | 28.800 | 22.900 | 10 |

`closeness.json` per turn holds the DECLARED reading and `closeness-observed.json`
the live one. SURVIVES means **not yet falsified**; it is never a rating, and
the numbers are not comparable between two rows (R213 F).
