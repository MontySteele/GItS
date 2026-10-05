# Klee's scaling pass

Paper, 2026-10-05, main session. Picks open. [USER]: "Yes, agreed - let's
look at Klee's scaling."

**Draft 3,** after reviews by GPT and Fable. Both reviews were of draft 1.
What changed:
- **Tempo comes first.** Klee's damage arrives a turn late (sec.1). Both
  reviewers suspected this, and the telemetry confirms it.
- **One fact corrected (sec.2).** Witch's Homework and Half a Mountain do
  not need a Set off card on the same turn. Boom Badge does.
- **A works differently.** Secret Base now makes each Bomb bigger when it
  is placed, instead of making Bombs grow faster each turn.
- **B is revised but not promoted.** Witch's Homework gets Fable's edits
  and goes into a targeted round only. The reviewers split on it (sec.4).
- **C's Badges stop multiplying each other** (Fable).
- **The grading changes (sec.5):** a two-seat round with the cards given at
  embark, then suite 2, with fight length graded and two fresh seeds at
  promotion.
- **Pick 4 changes form.** It now uses Fable's simpler Strength rule.
- **Fatal fights and the player's Strength get logged** before any round.

This paper proposes card changes for `klee-next`. Each change comes with a
prediction, which a round grades. Under the freeze, nothing here touches
`main`'s cards (the measurement paper, sec.6).

## 1. What falls behind

**Her damage arrives a turn late.** The fight lines record enemy HP at the
start of every turn (`enemy_pool_by_turn`). This table shows the share of
the enemies' starting HP still alive, in normal fights, from the suite-1
telemetry on the paired seeds:

| Act | Klee, turn 2 | Base five, turn 2 | Klee, turn 3 | Base five, turn 3 |
|---|---|---|---|---|
| 1 | 0.76 | 0.61 | 0.37 | 0.26 |
| 2 | 0.92 | 0.66 | 0.54 | 0.39 |
| 3 | 0.90 | 0.57 | 0.66 | 0.32 |

- **Turn 1:** in acts 2 and 3, Klee's first turn removes about a tenth of
  the enemies' HP. A base character's removes a third to two fifths.
- **Turn 2:** her second turn keeps pace, at about a quarter.
- **Why it happens:** a Bomb placed on turn 1 deals nothing until a later
  Set off, so enemies get an extra attack.
- **It also answers Fable's act-1 puzzle.** In act 1 she deals as much
  damage a turn as a base character and gains more Block, yet loses 1.31
  times the HP.
- **Act-3 normal fights:** she loses 18.1 HP a fight, against their 10.8.

**Her Bombs barely grow over the run.** Damage a turn, all fights:

| Act | Bombs + Mines | Klee's cards | Klee total | Base five total |
|---|---|---|---|---|
| 1 | 11.4 | 12.3 | 23.7 | 23.0 |
| 2 | 14.3 | 20.7 | 35.1 | 39.6 |
| 3 | 14.5 | 22.7 | 37.2 | 52.7 |
| Growth, act 1 to act 3 | ×1.27 | ×1.85 | ×1.57 | ×2.29 |

- The base five's main cards grow over the run. On the same seeds, damage a
  play from act 1 to act 3:
  - Ironclad Strike: 7.4 to 21.5.
  - Silent Shiv: 5.6 to 11.1.
  - Defect Strike: 5.9 to 11.2.
  - The Scythe: 27.6 to 67.8.
- Big Badda Boom grows only because it copies Bomb damage.

**These are one problem seen twice.** Most of her damage comes from Bombs,
and Bomb damage is both delayed and flat. A fix has to make Bombs pay
sooner, not only bigger. A card that only rewards waiting would add to the
delay.

**Boss-entry HP** (`hp_start`) was fine:
- She entered act-1 bosses at 86 to 100% of her HP and act-2 bosses at 54
  to 83%. The base five entered at 54 to 95%.
- Her two act-1 boss deaths cannot be read yet, because a fatal fight
  writes no line (sec.5).

**Her Strength (Fable's question).** Fable asked how much Strength Klee
holds that does nothing for her Bombs.
- The telemetry does not log the player's Strength. Fable assumed it did.
  It is being added.
- The seat records show very little: Vajra (+1) in two runs, and one
  Strength Potion drunk (lane 1, act-2 boss).
- Her pool has two Strength cards, both companion cards (Bennett, Nicole),
  and no seat played either.
- So unused Strength is not most of the gap today. The Ironclad's Strength
  comes mostly from his own cards, which she does not have. Pick 4 stays a
  rule question, not the main fix.

## 2. Why her Bombs are slow and flat

1. **Every Bomb costs a turn of waiting, and nothing makes cashing early
   pay.**
   - A Bomb starts at its printed size, often 3 to 8. It grows 4 at the
     start of her turn (`KleeOverhaulLaw.BombGrowth`).
   - Setting it off on the turn it is placed gives up the growth and leaves
     a small hit. So seats wait, and enemies attack once more.
2. **No Uncommon card makes ordinary Bombs better.**
   - Each base character has 1-cost Uncommon Powers that make its damage
     better (`game_ref/*.json`):
     - Ironclad: Inflame.
     - Silent: Accuracy and Noxious Fumes.
     - Defect: Storm, Thunder and Hailstorm.
     - Necrobinder: Friendship and Haunt.
     - Regent: Furnace.
   - Klee's eight Uncommon Powers all pay only under a condition:
     - Experiment in Progress: on turns she sets nothing off.
     - Secret Base: when no enemy has a Bomb. A seat put it on the NEVER
       AGAIN list.
     - Little Hexenzirkel, Party Poppers and Finders Keepers: a small Bomb
       when something else happens.
   - Her steady growth Power is Alice's Recipe, a 2-cost Rare.
3. **Her payoff cards are weak or hard to line up.**
   - **Too little payoff:** Witch's Homework (+8 to the largest Bomb) and
     Half a Mountain (double it) grow a Bomb that stays on the board, with
     no same-turn condition. Seats passed them. Witch's Homework was
     offered three times in lane 2's act 1 and never taken.
   - **Hard to reach:** Boom Badge needs 2 Sparks, a big Bomb and a Set off
     card on the same turn. Two seats took it and never played it: "it
     never lined up in hand" (lane 1), and "it was in the discard whenever
     the Sparks were" (lane 2).
4. **Nothing carries over between fights.** The Scythe grows for the whole
   run. Klee has no card like it.

## 3. What does not change, and what the changes aim at

**Her flat numbers stay.**
- In act 1 she deals 1.03 times a base character's damage and loses 1.31
  times its HP.
- Two of five runs died at the act-1 boss.

If a later suite shows act-1 damage above 1.15 times, that is a signal to
review, not an automatic cut. Any cut would have to weigh her HP losses
too.

**Raise her floor before her ceiling** (Fable).
- The bar is set by Sonnet seats. An Opus seat won on seeds where Sonnet
  lost, so part of the gap is how hard she is to pilot.
- Tuning with multipliers until Sonnet reaches par would leave a good human
  well over par.
- So this pass prefers changes that make an ordinary hand work over
  doublers that make a great hand better.

## 4. The changes

No card is added, and the pool stays at 78. Each card below was offered on
these seeds in suite 1.

**A. Klee's Secret Base: her Accuracy.** A floor fix, and the main change.
- The new text: "Your Bombs are placed 3 [4] bigger."
- The rest is unchanged: 1-cost Uncommon Power. It stacks with copies of
  itself.
- What counts as placing:
  - Mines are Bombs (`ProtoBombPower.cs`), so every Mine counts, including
    Jumpy Dumpty's Mine on every enemy.
  - Every card that says "place" counts, as do the Bombs from All of My
    Treasures!, Return to Sender and Aftershock.
  - A merge (Exquisite Compound) and a jump do not count.
- Why this shape, not draft 1's "grow 2 more each turn":
  - Draft 1's version paid only on Bombs that waited a turn. Both reviewers
    named the risk: Mines going off under an attack, and Bombs placed and
    set off on the same turn, would gain nothing. Fable added that it would
    push seats to wait, which lengthens fights.
  - **The new shape pays at once.** A Bomb placed and set off on the same
    turn is 3 bigger, so cashing early is a fair answer to danger.
  - **Cooking still gains,** because the bigger Bomb also grows 4 a turn.
  - **It grows with how many Bombs her deck places.** Pop!, Booby Trap,
    Jumpy Dumpty Mk.III's three Bombs, Dodoco and Party Poppers are her
    Shivs, and this is the Silent's Accuracy for them.
- **Prediction:** with it in play by turn 1, two things change:
  - Bombs and Mines deal about 4 more damage a turn.
  - In act-2 and act-3 normal fights, the enemy HP left at the start of
    turn 2 falls from about 0.9 to about 0.8.

**C. Boom Badge: Retain, and Badges stop multiplying.**
- The new text keeps "2 Sparks [1], double the next Set off this turn".
  Two things are added:
  - Retain;
  - "Does not stack." Today two Badges give ×4 (`KleeExpansionPowers.cs`).
- Retain lets the Badge wait in hand for the big Bomb. The same-turn
  combination drops from three pieces to two. A floor fix.
- **Prediction:** a run holding it plays it in at least half of its act-2
  and act-3 fights, against 0 plays in suite 1. Each play adds at least 15
  damage to that Set off.

**B. Witch's Homework: revised, tried in the targeted round, not yet
promoted.**
- **The reviewers split.**
  - Fable called it "the best idea in the paper", since nothing of hers
    carries between fights.
  - GPT would send it back: it adds another waiting period, and it costs
    more than Pop! for less.
- **Fable's edits fix the price and the rulings.** The new text: "Place a
  Bomb 6. When it goes off, this card's Bomb is 2 [3] larger for the rest
  of the run. Exhaust."
- **Rulings:**
  - It counts whenever its Bomb goes off, including after a jump.
  - If Exquisite Compound merges it, the merged Bomb counts when it goes
    off.
  - A copy (All of My Treasures!) does not count.
  - Exhaust limits it to one growth a fight.
- **GPT's timing point still holds.** Turn 1 is already her slow turn, and
  this is one more Bomb that pays later.
- So it goes into the targeted round (sec.5), where it is given at embark
  and its growth can be read directly. It joins suite 2 only if the round
  shows it paying by act 2.
- **Prediction:** given at embark, it reaches about 6 + 2 × 15 = 36 by act
  3 if it goes off in most fights. A more likely figure is about 25,
  because it is not drawn every fight.

**Considered and left out:**
- **A higher Bomb growth rate:** it pays only Bombs that wait, and it is a
  rule change.
- **The Big One at a lower cost:** it was passed once, too little to tell.
- **Alice's Recipe at 1 cost:** it was never offered on these seeds.
- **A Bomb already placed at the start of each fight** (Fable's tempo idea,
  from the brief's Dodoco row). No current relic does this.
  - It would go on Pounding Surprise, her starter relic, so it is a starter
    change and yours to make. It is pick 5, held until A's turn-2 figure is
    read.
- **Ka-pow!** has no upgrade. A change to it would also change her starter.
- **Sparks:** you never felt short of them, but seats find Spark-cost cards
  dead at the start of a fight. That is not what is killing her, so it
  waits for the pass after this one.

## 5. How it is graded

**Before any round:** fatal fights write their line with `outcome: died`,
and each fight line records the player's Strength at the end of each turn.
Both are being built now.

**Round 1, targeted (Fable's pick 5).**
- Two Sonnet seats on `klee-next`, with A, B and C given at embark.
- Seeds: two of the five baseline seeds, so each run pairs with a base
  character and with its own suite-1 run.
- This reads each card's prediction directly, without waiting for the
  offers to fall right. Fable estimated that over five runs, whether a run
  was offered the cards would drown the effect.

**Suite 2, the kit as a whole.**
- The same five seeds, the same seats (one Sonnet seat per act, at A0) and
  the same report, with only the cards round 1 supported.

| Measure | Suite 1 | Predicted |
|---|---|---|
| Enemy HP left at the start of turn 2, act 2 / 3 | 0.92 / 0.90 | about 0.85 / 0.85 overall |
| Normal-fight length in turns, act 2 / 3 (median) | 4 / 3.5 | 3.5 / 3.5 |
| Bombs + Mines damage a turn, act 1 / 2 / 3 | 11.4 / 14.3 / 14.5 | about 12 / 16 / 16.5 |
| Damage a turn against the base five, act 2 / 3 | 0.91 / 0.72 | about 1.0 / 0.8 |
| HP lost against the base five, act 3 | 1.81 | about 1.6 |
| Boss-entry HP | act 1: 86 to 100%; act 2: 54 to 83% | not lower |
| Runs reaching act 3 | 2 of 5 | 3 of 5 |

**Also recorded:**
- each changed card: offered, taken and played;
- the turn of her first Set off in each fight;
- boss deaths, now that fatal fights are logged.

**Read these with care:**
- **The dose is small** (Fable). Over five runs that mostly will not hold
  these cards, Bomb damage may rise only 2 to 3 a turn. That is why round 1
  reads the cards and suite 2 reads the kit.
- **The act-3 figures may compare different runs.** If different runs
  survive to act 3, each run is also compared with its own suite-1 run, up
  to the floor where the two part.
- **"3 of 5 reach act 3"** depends on the seeds more than on these cards.
- **Act 1 should barely move.**
- **If the turn-2 figure improves but act 3 still misses the bar,** the
  failures choose the next pass, from:
  - stronger payoffs;
  - more Set off cards in hand;
  - survival while she places;
  - pick 4 or pick 5.

**Overfitting** (Fable). Every pass is graded on the same five maps, and
the changes are chosen partly from what those maps offered.
- The promotion suite adds two runs on fresh seeds.
- Those runs have no paired base run, so they are read on how far each run
  gets and on the telemetry against the pooled base five.

The changes are built on `klee-next` and deployed with
`tools/deploy_round.py --staging` as a `+next` build. They reach `main` in one
promotion PR that carries the suite record.

## Picks

1. **The diagnosis.** Klee's Bomb damage arrives a turn late and is flat
   across the run. No card below Rare improves ordinary Bombs. Default:
   agree.
2. **No flat cuts in this pass.** Act-1 damage above 1.15 times the base
   characters' is a signal to review, not an automatic cut. Default: yes.
3. **The changes.** Default: A ("Your Bombs are placed 3 [4] bigger") and C
   (Retain; Badges do not stack) go to `klee-next`. B (Witch's Homework,
   Bomb 6, run-long growth) is tried in round 1 and joins suite 2 only if
   it pays by act 2.
   - (b) B goes straight into suite 2 as well (Fable).
   - (c) B is dropped (GPT).
4. **Strength and Bombs.** If taken, the rule is Fable's simpler form:
   "positive Strength adds to a Bomb when it is placed." It reads like
   Strength on a hit, and negative Strength never shrinks a Bomb. It is a
   rule change, so you would play it. Default: hold. The Strength she
   holds today is small (sec.1), and A already gives this shape through a
   card. Decide after round 1, with the Strength numbers logged.
5. **A Bomb at the start of each fight**, on Pounding Surprise. It is a
   tempo fix and a starter change, so it is yours. Default: hold until
   round 1 reads A's turn-2 effect.
6. **Grading** as in sec.5: round 1 targeted, suite 2 on the five seeds,
   two fresh seeds at promotion. Default: yes.
