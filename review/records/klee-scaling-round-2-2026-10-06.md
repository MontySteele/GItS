# Klee scaling pass, round 2, 2026-10-06

Round 2 of the ruled scaling pass (`review/active/klee-scaling-pass-2026-10-05.md`,
sec.5, "Gate changed after round 1"), on the `klee-next` staging build
0.2.4494+next (draft PR #940, commit 41c4b495).

**What ran.**
- **Two arms on the round-1 seeds,** the cards given at embark, A0, the
  starter relic unchanged:

  | Arm | Given at embark |
  |---|---|
  | 1 | Secret Base v3 ("At the start of your turn, place a Bomb 4 [6] on a random enemy."), Boom Badge |
  | 2 | the same, plus Witch's Homework II |

- **Seats:** one Sonnet seat (medium effort) per act, with the previous
  act's handoff; prompts word for word as round 1's.
- **Grading:** acts 2 and 3, from fight telemetry. The gate is read with the
  Balance bar's own measures (`tools/telemetry_report.py`: median per fight,
  act by act, normal fights, `|ratio - 1| <= 0.15`).
- **Comparison runs:** the base character's run on each seed. The Ironclad
  seed has two base runs; both are shown.
- **Seat conduct:** three seats filtered the screen with `grep` at least
  once, against the brief, and declared it. Raw records are in the session
  scratchpad and gitignored.

## Result: three of four runs reached the final boss, one won; the gate was missed

| Seed | Run | End |
|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | round 1, arm 1 | floor 39, Globe Head |
| | **arm 1** | floor 48, **final boss**, Test Subject (third form 275/300 left) |
| | **arm 2** | floor 43, Soul Nexus elite (about 15/234 left) |
| | base Ironclad | floor 48, Test Subject |
| R41TX5Q0ZQYN (Regent) | round 1, arm 1 | floor 48, Aeonglass (178/512 left) |
| | **arm 1** | **won** (Aeonglass dead, 22/95 HP) |
| | **arm 2** | floor 48, **final boss**, Aeonglass (326/512 left) |
| | base Regent | floor 48, Aeonglass |

- All four runs cleared act 1 (round 1 lost one there).
- **All three losses were a Block-short deck at low HP.** Arm 2 Ironclad went
  into its last four fights at 17, 14, 8 and 29 HP (no rest site until
  floor 42) and died at 1 HP with 18 Block against 20. The two boss deaths
  had 10 and 12 Block against the killing hit. The lane-2 and lane-4 seats
  called the deck thin on Block.
- Test Subject's three forms now log as one fight that she lost (#942
  works).

## The gate (written before the round)

"In act-2 and act-3 normal fights, Klee's damage a turn and HP lost are
within 15% of the base character's run on the same seed, on both seeds, and
she reaches the act-3 boss on both."

**Arm 1** (ratio = Klee / base; a cell passes if both ratios are within 0.85-1.15):

| Seed, act | Fights (Klee/base) | Damage a turn | HP lost % | Bar |
|---|---|---|---|---|
| Ironclad, act 2 | 7 / 7 and 6 | 39.5 vs 43.0 and 41.3 = **0.92, 0.96** | 14.3 vs 15.0 and 14.4 = **0.95, 0.99** | within |
| Ironclad, act 3 | 7 / 7 | 49.3 vs 54.0 and 61.7 = **0.91, 0.80** | 11.4 vs 20.0 and 18.8 = **0.57, 0.61** | outside: less HP lost |
| Regent, act 2 | 3 / 3 | 26.3 vs 21.8 = **1.21** | 12.5 vs 12.6 = **0.99** | outside: more damage |
| Regent, act 3 | 5 / 5 | 44.0 vs 38.2 = **1.15** (1.152) | 15.5 vs 15.2 = **1.02** | outside by 0.002 |

**Arm 2:** outside in every cell. Ironclad damage is 0.78-0.92 of base.
Regent act 3 is 0.85 on damage and 1.68 on HP lost. It also did not reach the
Ironclad boss.

**Verdict: missed as written, by both arms.** Arm 1 met the "reaches the
act-3 boss" half on both seeds and was within the bar on Ironclad act 2. Its
misses lean her way: Regent damage 1.15-1.21, and Ironclad act-3 HP lost
0.57-0.61. The exception is Ironclad act-3 damage against the second base run
(0.80).

- The bar is two-sided as coded, so above par is a miss too.
- Each cell has 3 to 7 fights, and the two base Ironclad runs on the same
  seed differ by 0.11 on act-3 damage. Two seeds cannot resolve a 15% bar
  this finely. That is the case for pick 1, not a reason to call it met.

## The other predictions

**Secret Base v3 is played: met.**
- **The prediction:** a run holding it plays it in at least half of its
  act-2 and act-3 fights.
- **The result:** 11 of 17 fights (Ironclad arm 1), 10 of 14 (Ironclad
  arm 2), 8 of 12 (Regent arm 1) and 7 of 13 (Regent arm 2).
- The seats play it on turn 1 as routine ("Automatic: Secret Base and DD on
  turn 1", lane 2, act 3). Round 1's version was called the weakest card
  twice.
- One seat drafted a second copy on its own (a Future of Potions event).

**Arm 1's Bomb+Mine damage a turn beats round 1's arm 1: met in three of four
act-seeds, a tie in the fourth.**

| Seed | Round 1, act 2 / act 3 | Round 2, act 2 / act 3 |
|---|---|---|
| Ironclad | 13.0 / 14.8 | **21.3 / 24.8** |
| Regent | 16.1 / 20.6 | **16.5 / 25.2** |

- Regent act 2 is a tie (3 fights).
- In fights where it was played, Bomb+Mine a turn ran 2.3 to 5.1 higher
  than in fights where it was not, in all four runs. The seat chooses when
  to play it, so this does not establish its effect.

**Witch's Homework II grows to about 25 by act 3: met.**
- The logged size (`homework_bomb_size`) entered act 3 at 24 (Ironclad) and
  23 (Regent), and ended at 30 and 32.
- **No gain from carrying it.** Arm 2 did no better than arm 1 on either
  seed; it did worse on survival and on Regent act-3 HP. Two runs, so this
  is no proof against it either.

**Boom Badge** was played in at least half of late fights in 3 of 4 runs.
Ironclad arm 1 played it in 7 of 17. One act-1 seat called it its weakest
card ("dead early, needs a set-off in hand"). The biggest turns in lanes 1,
2 and 3 were Boom Badge into a Set off (a 144 pile killed Aeonglass; 157 off
The Insatiable in one turn).

**Not graded, per the ruling:**
- The turn-2 prediction stays missed. HP left at turn 2 read 0.87 to 1.00
  again; the seats still cook their Bombs.
- Peak Strength was 0-1, as in round 1.

## Screen and text problems

1. **The printed Bomb number leaves out Durin's Dark, Boom Badge's doubling
   and Weak** (lanes 1, 3, 4). Round 1 logged the Durin part. In lane 3,
   fight 4, the page printed 12 and 4, and 18 and 10 landed.
2. **Treasure Map does not say it needs a Set off card in the discard**
   (lane 4, boss turn 6: played into an empty discard).
3. **"Sorry, Jean..." removes the oldest Bomb with no choice,** and the
   text does not say so (lane 1; it cost an 11 Bomb against Soul Nexus).
4. **Ka-pow! "Set off the enemy" seemed to set off only the oldest Bomb** on
   one elite turn (lane 2). This needs a check against the code.
5. **Whether Boom Badge doubles Big Badda Boom's "damage equal to what your
   Bombs dealt"** is unclear (lane 1).
6. **The Bomb number ignores Skulking Colony's Hardened Shell cap of 20 a
   turn** (lane 2).
7. **Bridge:**
   - Jumpy Dumpty is refused without a named target, though it hits all
     enemies (lane 3).
   - A Durin chooser twice answered "still opening" (lane 3).
   - An enemy (Mawler) died at the end of the turn with no printed cause
     (lane 4).

Items 1 to 7 go to `BACKLOG.md` as one line.

## Picks

1. **Suite 2 despite the missed gate.**
   - **Default: run suite 2 on `klee-next` as built** (Secret Base v3 and
     Boom Badge in the pool), with this record saying plainly that the gate
     was missed.
   - **Why:**
     - Arm 1 reached the final boss on both seeds and won one.
     - Its six readings sit at 0.80 to 1.21, mostly on her side.
     - A third two-seed round cannot resolve a 15% bar at 3 to 7 fights a
       cell.
     - The five-seed suite is the instrument the bar was written for. Its
       base runs already exist, so a suite costs Klee seats only (about
       12M tokens).
   - **Alternative:** the gate stands and round 3 changes something first.
     The only fault the round points at is Block in act 3; it does not point
     at damage.
   - This sets aside a gate you ruled, after its result, which is why it is
     your pick.
2. **Witch's Homework II stays a staging grant, out of the suite's pool.**
   **Default:** yes. It grows as predicted, and the arm that carried it did
   no better on either seed.

Boom Badge stays on `klee-next`. The installed build is 0.2.4494+next;
release play needs `python tools/deploy_round.py` from `main`.
