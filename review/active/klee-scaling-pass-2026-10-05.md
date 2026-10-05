# Klee's scaling pass

Paper, 2026-10-05, main session. Picks open. [USER]: "Yes, agreed - let's
look at Klee's scaling."

**Draft 2**, after GPT's review. What changed from draft 1:
- **A new finding (sec.1):** Klee's damage arrives a turn late, as GPT
  suggested. The telemetry already records it.
- **One fact corrected (sec.2):** Witch's Homework and Half a Mountain do
  not need a Set off card on the same turn.
- **Change A re-shaped (sec.4):** Secret Base now makes each Bomb bigger
  when it is placed, instead of making Bombs grow faster each turn.
- **Change B (Witch's Homework) dropped (sec.4).**
- **Suite 2 measures more (sec.5),** and fatal fights get logged before it
  runs.

Suite 1 (`review/records/klee-suite-1-2026-10-05.md`) showed that Klee falls
behind the base characters as the run goes on. This paper explains why, and
proposes two card changes for `klee-next`. Each change comes with a
prediction, and suite 2 grades the predictions on the same five seeds. Under
the freeze, nothing here touches `main`'s cards (the measurement paper,
sec.6).

## 1. What falls behind

**Her Bombs barely grow over the run.** Damage a turn on the paired seeds,
counting all fights in the suite-1 telemetry:

| Act | Bombs + Mines | Klee's cards | Klee total | Base five total |
|---|---|---|---|---|
| 1 | 11.4 | 12.3 | 23.7 | 23.0 |
| 2 | 14.3 | 20.7 | 35.1 | 39.6 |
| 3 | 14.5 | 22.7 | 37.2 | 52.7 |
| Growth, act 1 to act 3 | ×1.27 | ×1.85 | ×1.57 | ×2.29 |

Big Badda Boom grows (20.9, 34.8 and 36.9 a play), but only because it
copies Bomb damage.

Each base character's main damage source grows over the run. Damage a play
on the same seeds:

| Card | Act 1 | Act 3 |
|---|---|---|
| Ironclad Strike | 7.4 | 21.5 |
| Ironclad Whirlwind | 40.4 | 56.9 |
| Silent Shiv | 5.6 | 11.1 |
| Defect Strike | 5.9 | 11.2 |
| Necrobinder The Scythe | 27.6 | 67.8 |

**Her damage also arrives a turn late.** The fight lines record enemy HP at
the start of every turn (`enemy_pool_by_turn`). This table shows the share
of the enemies' starting HP still alive, in normal fights:

| Act | Klee, turn 2 | Base five, turn 2 | Klee, turn 3 | Base five, turn 3 |
|---|---|---|---|---|
| 1 | 0.76 | 0.61 | 0.37 | 0.26 |
| 2 | 0.92 | 0.66 | 0.54 | 0.39 |
| 3 | 0.90 | 0.57 | 0.66 | 0.32 |

- **Turn 1:** in acts 2 and 3, Klee's first turn removes about a tenth of
  the enemies' HP. A base character's removes a third to two fifths.
- **Turn 2:** her second turn keeps pace (about a quarter, the same as
  theirs).
- **Why it happens:** a Bomb placed on turn 1 deals nothing until a later
  Set off. So her first turn mostly places Bombs, and enemies take an extra
  attack. That fits her longer act-2 fights and her 1.3 to 1.8 times HP
  loss.
- **Why it gets worse by act:** the base five's turn-1 damage grows with
  the run. Hers stays near zero, because turn 1 is the turn she places.
- **Act-3 normal fights:** she loses 18.1 HP a fight, against their 10.8.

The two findings are one problem seen twice. Most of her damage comes from
Bombs, and Bomb damage is both delayed and flat. The fix has to make Bombs
pay sooner, not only bigger. A change that only rewards waiting longer would
make the delay worse.

**Boss-entry HP** (`hp_start`) was fine in acts 1 and 2:
- Klee entered act-1 bosses at 86 to 100% of her HP and act-2 bosses at 54
  to 83%. The base five entered at 54 to 95%.
- Her two act-1 boss deaths were not caused by arriving low.
- They cannot be read yet, because a fatal fight writes no line (sec.5).

## 2. Why her Bombs stay flat and slow

1. **No Uncommon card makes ordinary Bombs better.**
   - A Bomb grows 4 at the start of each of her turns
     (`KleeOverhaulLaw.BombGrowth`), from the first fight to the last.
   - Each base character has 1-cost Uncommon Powers that make its damage
     better for the rest of the fight (`game_ref/*.json`):
     - Ironclad: Inflame.
     - Silent: Accuracy and Noxious Fumes.
     - Defect: Storm, Thunder and Hailstorm.
     - Necrobinder: Friendship and Haunt.
     - Regent: Furnace.
   - Klee has eight Uncommon Powers, and none of them makes her Bombs
     better without a condition:
     - Experiment in Progress pays only on turns she sets nothing off.
     - Klee's Secret Base pays only when no enemy has a Bomb. A seat put it
       on the NEVER AGAIN list.
     - Little Hexenzirkel, Party Poppers and Finders Keepers each place a
       small Bomb when something else happens.
   - Her only steady growth Power is Alice's Recipe, a 2-cost Rare.
2. **Her payoff cards are weak or hard to line up.** They split into two
   kinds, and the difference matters:
   - **Too little payoff.** Witch's Homework (+8 to the largest Bomb) and
     Half a Mountain (double it) grow a Bomb that stays on the board and
     can go off later, with no same-turn condition. The seats passed them.
     Witch's Homework was offered three times in lane 2's act 1 and never
     taken.
   - **Payoff that is hard to reach.** Boom Badge needs 2 Sparks, a big
     Bomb and a Set off card, all on the same turn. Two seats took it and
     never played it: "it never lined up in hand" (lane 1), and "it was in
     the discard whenever the Sparks were" (lane 2).
3. **Nothing carries over between fights.** The base game has cards that
   grow for the rest of the run: The Scythe's damage a play rises 2.5 times
   by act 3. Klee has none. This pass does not add one (sec.4).

A fourth cause is left alone. Klee's Strength does not add to her Bombs
(`EB-343`, R248). Base-game Strength from relics, potions and Bennett
therefore skips her biggest damage source. Changing that is a rule change,
which means you play it. It is pick 4.

## 3. What does not change: her flat numbers

Your first read was "scaling being low and flat numbers being high enough to
somewhat balance it out". The paired seeds back the first half, not the
second:
- In act 1, Klee deals 1.03 times a base character's damage and loses 1.31
  times its HP.
- Two of the five runs died at the act-1 boss.

So her act-1 numbers are level, not high, and her act-1 defence is already
behind. This pass only adds scaling. If suite 2 shows act-1 damage above
1.15 times the base characters', that is a signal to review her flat
numbers, not an automatic cut. A cut would have to weigh her HP losses too.

## 4. The changes

Both changes go on cards the seats skipped or could not use. No card is
added, so the pool stays at 78. Both cards were offered on these seeds in
suite 1, so suite 2 will see them again.

**A. Klee's Secret Base: her Accuracy.**
- The new text: "Your Bombs are placed 3 [4] bigger."
- The rest is unchanged: 1-cost Uncommon Power.
- What counts as placing:
  - A Mine is a Bomb, so every Mine counts, including Jumpy Dumpty's Mine
    on every enemy.
  - Every card that says "place" counts, as do the Bombs from All of My
    Treasures!, Return to Sender and Aftershock.
  - A merge (Exquisite Compound) and a jump are not placing.
- It stacks with copies of itself.
- **Why this shape, not draft 1's "grow 2 more each turn".** Draft 1's
  version paid only on Bombs that survived to her next turn. GPT pointed
  out that Mines going off under an attack, and Bombs placed and set off on
  the same turn, would gain nothing. The timing data in sec.1 makes that
  decisive, because waiting is the problem.
  - **The new shape pays at once.** A Bomb placed and set off on the same
    turn is 3 bigger, so cashing early becomes a fair answer to danger.
  - **Cooking still gains,** because the bigger Bomb also grows 4 a turn.
  - **It grows with how many Bombs her deck places.** Pop!, Booby Trap,
    Jumpy Dumpty Mk.III's three Bombs, Dodoco and Party Poppers are her
    Shivs, and this is the Silent's Accuracy for them. Base Accuracy is a
    1-cost Uncommon too.
- **Prediction:** in runs that play it, Bombs and Mines deal about 3 to 4
  more damage a turn from act 2 on. On top of that, the enemy HP left at
  the start of turn 2 falls from about 0.9 to about 0.8, in the act-2 and
  act-3 fights where it is in play by turn 1.

**C. Boom Badge: Retain.**
- The new text keeps everything (2 Sparks [1], double the next Set off this
  turn) and adds Retain.
- The badge can then wait in hand for the big Bomb. The same-turn
  combination drops from three pieces to two.
- **Prediction:** a run holding it plays it in at least half of its act-2
  and act-3 fights, against 0 plays in suite 1. When played, it adds at
  least 15 damage to that Set off.

**B. Witch's Homework, dropped from this pass.** Draft 1 made it a Bomb that
grows for the rest of the run, like Genetic Algorithm. GPT raised three
points against it, and they hold:
- **Its entry price is weak.** It cost 1 Energy for a Bomb 4, when Pop! is
  a Bomb 5 for 0.
- **Its reward is conditional.** Draft 1's "about 30 by act 3" needed 13
  of its own Bombs to go off, so it depended on how early it was picked and
  how often it was drawn.
- **Its rulings were unsettled:** jumps, merges and copies.

It also adds another waiting period, which is the very thing sec.1 found
costly. It stays as it is. Run-long growth can come back if suite 2 shows
the loop works and still lacks power late.

**Considered and left out:**
- A higher Bomb growth for everyone: it raises damage only for Bombs that
  wait, which is the slow path. It is also a rule change.
- The Big One at a lower cost: it was passed once, which is too little to
  tell.
- Alice's Recipe at 1 cost: it was never offered on these seeds.
- Ka-pow!, her one starting Set off card, has no upgrade. A change to it
  would change her starter, so it is yours to make. This pass does not ask
  for one.

## 5. How suite 2 grades it

Suite 2 uses the same five seeds, the same seats (one Sonnet seat per act,
at A0) and the same report. Klee's suite-1 figures are the starting line.

| Measure | Suite 1 | Predicted |
|---|---|---|
| Enemy HP left at the start of turn 2, act 2 / 3 | 0.92 / 0.90 | about 0.85 / 0.85 overall; 0.8 where A is in play |
| Bombs + Mines damage a turn, act 1 / 2 / 3 | 11.4 / 14.3 / 14.5 | about 12 / 16 / 17 |
| Damage a turn against the base five, act 2 / 3 | 0.91 / 0.72 | about 1.0 / 0.8 |
| HP lost against the base five, act 3 | 1.81 | about 1.5 |
| Boss-entry HP | act 1: 86 to 100%; act 2: 54 to 83% | not lower |
| Runs reaching act 3 | 2 of 5 | 3 of 5 |

**Also recorded:**
- Each changed card: whether it was offered, taken and played, and in which
  fights. This comes from the seat records and the telemetry.
- The turn of her first Set off in each fight.
- **Fatal fights.** A fight the player dies in writes no line today
  (`BACKLOG.md`). This is fixed before suite 2, so boss deaths can be read.

**Read these with care:**
- Five runs is a small sample. Act 3 had 8 normal fights in suite 1.
- If different runs survive to act 3, the act-3 figures compare different
  runs. Each run is therefore also compared with its own suite-1 run, fight
  by fight, up to the floor where the two runs part.
- Runs reaching act 3 is the noisiest line.
- Act 1 should barely move: these cards seldom arrive before the first
  boss.
- If the turn-2 figure improves and act 3 still misses the bar, the next
  pass picks from what is left:
  - stronger payoffs;
  - more reliable access to Set off;
  - better survival while she places;
  - pick 4.

  The failures decide which. They are not assumed to be one scaling
  problem.

The changes are built on `klee-next` and deployed with
`tools/deploy_round.py --staging` as a `+next` build. They reach `main` in one
promotion PR that carries the suite-2 record.

## Picks

1. **The diagnosis.** Klee's Bomb damage is flat across the run and arrives
   a turn late, and no card below Rare improves ordinary Bombs. Default:
   agree.
2. **No flat cuts in this pass.** Act-1 damage above 1.15 times the base
   characters' in suite 2 is a signal to review, not an automatic cut.
   Default: yes.
3. **The changes:** A (Secret Base: "Your Bombs are placed 3 [4] bigger")
   and C (Boom Badge gains Retain), built on `klee-next` and graded by suite
   2. Witch's Homework stays as it is. Default: both.
   - (b) Use draft 1's A instead: "Your Bombs grow 2 [3] more at the start
     of your turn."
4. **Strength adds to Bomb growth.** Hold, and decide after suite 2. GPT
   notes that it multiplies through Bomb count, waiting time and Alice's
   Recipe. Default: hold.
