# Klee scaling pass, round 1, 2026-10-05

Round 1 of the ruled scaling pass (`review/active/klee-scaling-pass-2026-10-05.md`,
sec.4-5), on the `klee-next` staging build 0.2.4490+next (draft PR #940).

**What ran.**
- **Three arms on two seeds,** the cards given at embark, A0:

  | Arm | Given at embark |
  |---|---|
  | 1 | A (Secret Base), C (Boom Badge) |
  | 2 | A, B (Witch's Homework II), C |
  | 3 | A, C, the test relic (Pounding Surprise II: a Bomb 6 at combat start) |

- **Seats:** one Sonnet seat (medium effort) per act, with the previous
  act's handoff.
- **Grading:** acts 2 and 3 only, from fight telemetry
  (`enemy_hp_by_turn`, `strength_by_turn` and the `died` line, #938/#939).
- **Comparison runs:** each seed's suite-1 Klee run
  (`review/records/klee-suite-1-2026-10-05.md`) and the base character's
  baseline run on that seed.
- **Raw records** are in the session scratchpad and are gitignored.

## Result: four of five late runs reached the final boss, and one won

| Seed | Run | End |
|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | suite 1 | floor 43, Soul Nexus elite |
| | arm 1 | floor 39, Globe Head (53/148 left) |
| | arm 2 | floor 9, act-1 elite (four Phantasmal Gardeners), reached at 23/70 |
| | arm 3 | floor 48, **final boss**, Test Subject (third form) |
| | base Ironclad | floor 48, Test Subject |
| R41TX5Q0ZQYN (Regent) | suite 1 | floor 42, Mecha Knight elite |
| | arm 1 | floor 48, **final boss**, Aeonglass (178/512 left) |
| | arm 2 | **won** (Aeonglass dead, 11/90 HP) |
| | arm 3 | floor 48, **final boss**, Aeonglass (31/512 left) |
| | base Regent | floor 48, Aeonglass |

- Suite 1 reached the final boss on neither seed. Round 1 reached it in
  four of the five runs that left act 1, and arm 2 won on the Regent seed.
- Arm 2 died in act 1 on the Ironclad seed, which is not graded. It reached
  a forced elite with no rest site or shop on its path. So B has no paired
  read on that seed.
- **Granted cards shape the whole run (GPT).** Leaving act 1 out of the
  grade does not remove their effect on later decks, HP, upgrades and
  routes. These are targeted tests of the changes, not ordinary-draft
  balance results.

## Telemetry: act-2 and act-3 normal fights

Median per fight, except damage a turn, which is the total over all turns.
"Left at turn N" is the share of the enemies' turn-1 HP still standing when
turn N opens; a fight already won counts as 0. Round 1 reads HP alone. Suite
1 and the base runs predate that field, so they read HP plus Block.

**Ironclad seed** (act 2 / act 3):

| Run | Left at turn 2 | Left at turn 3 | Turns | Bomb+Mine a turn | Damage a turn | HP lost, % |
|---|---|---|---|---|---|---|
| suite 1 | 1.00 / 1.00 | 0.46 / 0.89 | 3 / 3.5 | 11.8 / 16.1 | 33.8 / 37.8 | 24.3 / 27.9 |
| arm 1 | 0.87 / 0.71 | 0.26 / 0.40 | 3 / 4 | 13.0 / 14.8 | 36.1 / 35.1 | 11.4 / 24.3 |
| arm 3 | 1.00 / 0.75 | 0.00 / 0.27 | 2 / 3 | 25.9 / 25.8 | 50.2 / 59.0 | 12.9 / 2.9 |
| base Ironclad (two runs) | 0.64-0.76 / 0.63-0.71 | 0.28-0.36 / 0.27-0.29 | 2.5-3 / 3 | — | 40.8-42.3 / 62.4-65.6 | 14.4-15.0 / 18.8-20.0 |

**Regent seed** (act 2 / act 3):

| Run | Left at turn 2 | Left at turn 3 | Turns | Bomb+Mine a turn | Damage a turn | HP lost, % |
|---|---|---|---|---|---|---|
| suite 1 | 0.84 / 0.82 | 0.58 / 0.41 | 3 / 3.5 | 14.7 / 12.9 | 39.0 / 36.6 | 16.9 / 18.4 |
| arm 1 | 1.00 / 0.73 | 0.58 / 0.28 | 3 / 4 | 16.1 / 20.6 | 32.8 / 40.9 | 5.2 / 17.2 |
| arm 2 | 0.85 / 0.92 | 0.66 / 0.91 | 3.5 / 4 | 17.4 / 28.3 | 28.1 / 45.2 | 9.1 / 10.3 |
| arm 3 | 1.00 / 1.00 | 0.61 / 0.21 | 3 / 3 | 25.8 / 32.4 | 35.9 / 51.0 | 7.8 / 10.6 |
| base Regent | 0.68 / 0.66 | 0.59 / 0.44 | 4 / 5 | — | 22.4 / 35.6 | 12.6 / 15.2 |

Each run has 4 to 7 normal fights an act, so a single fight moves a median.

## The predictions

**D, the tempo relic: missed as written, but the clearest gain of the round.**
- **The prediction:** enemy HP left at the start of turn 2 falls from about
  0.9 to about 0.8. It did not fall; arm 3 reads 1.00 in three of four
  act-seeds.
- **Why:** the seats mostly cooked the relic's Bomb on turn 1 and set it
  off on turn 2 or later. The paper offered that choice ("Ka-pow! it now, or cook
  it"), and the seats took the bigger hit.
- **What moved instead:**
  - Arm 3's Bombs and Mines dealt 1.6 to 2.0 times arm 1's damage a turn,
    on both seeds and in both acts.
  - Its total damage a turn was 1.1 to 1.7 times arm 1's. In act 3 it
    matched the base Ironclad (59.0 against 62.4-65.6) and passed the base
    Regent (51.0 against 35.6).
  - Its act-3 HP lost was lower on both seeds (2.9 against 24.3, and 10.6
    against 17.2).
  - Its act-3 turn-3 figure (0.27 and 0.21) was at or below the base
    characters'.
  - Its act-2 HP lost was slightly higher than arm 1's on both seeds (12.9
    against 11.4, and 7.8 against 5.2) (GPT).
- The prediction stays missed. A later gate may ask whether delayed damage
  pays enough, but it does not turn this result into a confirmation of the
  tempo diagnosis (GPT).
- **What it fixed was a cold start, not tempo (Fable).**
  - Every fight began with a Bomb already growing, so her first Set off had
    something to pay. Her first Sparks came a turn earlier: suite 1's
    "Spark-cost cards dead at the start of a fight".
- **The gain is bigger than the relic's face (Fable).**
  - A Bomb 6 that goes off at 10 or 14 adds about 14 damage a fight, but
    arm 3 gained about 40 a fight over arm 1.
  - The rest comes from Badge doublings landing on it, earlier Sparks, and
    two seeds' worth of routes and seat luck.
  - Expect the gap to shrink over more seeds.
- **Verified in game:** the relic's Bomb shows as 10 when Klee first acts
  (lane 3, fight 1: "Relic put Bomb 10 on Toadpole 2 at start").

**C, Boom Badge: met in three of five runs.**
- **The prediction:** played in at least half of act-2 and act-3 fights
  (suite 1: 0).
- **The result:**
  - 13 of 17 fights (Regent arm 3), 11 of 15 (Regent arm 1) and 7 of 11
    (Regent arm 2).
  - 8 of 18 on Ironclad arm 3. Ironclad arm 1 played it only in act 1 (0 of
    13); its act-1 seat called it the card it would never draft again.
- **Was each play useful?** Every turn a Badge was played removed at least
  24 enemy HP plus Block (median about 90; 42 plays). The telemetry cannot
  split out the doubling's share, so "useful" is read loosely. The lane-4
  act-2 seat called the Badge-before-Big-Badda-Boom turn its biggest swing.

**A, Secret Base: not shown.**
- **The prediction:** about 4 more Bomb damage a turn in fights where it is
  played.
- **Bomb+Mine a turn, fights where it was played against fights where it
  was not:**
  - Ironclad arm 1: 13.9 against 13.3.
  - Ironclad arm 3: 25.1 against 27.0.
  - Regent arm 2: 24.2 against 22.8.
  - Regent arm 3: 40.0 against 26.8 (only 9 turns with it).
- Regent arm 1 never played it after act 1. Two seats called it the
  weakest card, and one had it stolen and "never missed it".
- This comparison cannot establish its effect (GPT): a seat chooses which
  fights to play it in. But it shows no steady +4, and the seats do not
  want the card.

**B, Witch's Homework II: no read.**
- Its Ironclad run died in act 1. On the Regent seed it was played in 8 of
  11 late fights, and that run won.
- The size its Bomb reached was not logged. A seat note shows "Homework 25"
  in act 2, but that may include turn growth and Secret Base.
- So the "about 25 by act 3" prediction is ungraded.

**Strength (pick 4's input).** Peak Strength was 0 in every Ironclad-seed
run and 1 (Vajra) in every Regent-seed run. The seats held almost none.

**First Set off.** Median turn 1 to 3, the same as suite 1 (1.5 to 2.5).
Turn 1 is still limited by Set off cards. The relic made turn 1 richer, not
earlier.

## What the seats said

- **Played well:**
  - Boom Badge doubling a cooked Bomb before Big Badda Boom+ or Ka-pow!;
    Big Badda Boom+ dealt 154 to Aeonglass.
  - Durin set to Dark adds 6 to every Pyro hit, so it adds to each Bomb in
    a Set off.
  - Jumpy Dumpty's turn-1 Mine on every enemy.
- **NEVER AGAIN:** Sparkling Burst, Cover Your Ears! (twice; Artifact eats
  it), Blazing Delight, Fireworks Finale, Treasure Map, Pop!, Red Knight.
- **Deaths:** all five losses came at a forced fight entered at a third of HP
  or less, or at a final boss's last turns.
  - In two of those fights the seat misjudged one turn's Block (Globe Head;
    Aeonglass's Wither).

## Screen and text problems

1. **The test relic says "Bomb 6"; the board shows 10 when Klee first acts.**
   One seat could not tell why. The text should name the number she sees.
2. **Boom Badge's Retain reads as if the doubling carries over.** It lasts the
   turn it is played. One seat wasted a play on a turn with no Set off.
3. **Durin's Dark +6 never appears in printed card numbers** (lane 4).
4. **Durin's start-of-turn tick did not fire in one fight** (Fogmog, Regent
   arm 3, act 1) but did elsewhere. Needs a trace.
5. **"Witch's Homework" and "Witch's Homework II" are hard to tell apart in
   hand lists** (lane 5, which had both).
6. **The "Put Mine N on ..." lines after Big Badda Boom** read as five Mines
   from one Bomb (lane 5).
7. The Melt note "nothing to amplify" beside an amplified hit came up again.
   It is already in `BACKLOG.md`.

Items 1 to 6 go to `BACKLOG.md` as one line.

**Instrument gaps** (to `BACKLOG.md`):
- **A boss that comes back in a new form closes its fight line as won** when
  its first form dies.
  - Test Subject wrote `won` after 2 turns in arm 3, though the seat died to
    its third form. Both base Ironclad baseline runs also log a won Test
    Subject.
  - So the deaths and the later forms are missing. Fixed by #942.
- **Witch's Homework II's Bomb size is not logged,** so B cannot be graded.

## Next (revised after GPT's and Fable's reviews)

- **The relic stays off the starter.** [USER] ruled no: "I'm not really a
  fan of that relic redesign."
  - Both reviews agree. It plants for her, which hands over the first move
    of the plan her starter teaches ("plant, wait, boom").
  - It is also a flat gift to every deck, which this pass set out not to
    make. And it leaves the real defect where it was: she has no Bomb
    engine below Rare.
  - The arm stays on record as evidence that more setup helps.
- **The finding kept is the cold start.** The seats' failed turns show it:
  - "a hand of Defends and an unplayable Boom Badge" (Ironclad arm 1, fight
    1, turn 2);
  - "Boom Badge and Blazing Delight sat dead in hand at 1 Spark on four early
    turns" (Ironclad arm 3, act 1).
  - Klee needs a drafted card that puts a Bomb on the table every turn.
- **That card is Secret Base (Fable).** The pass has tried to save it twice,
  and its first text was almost this; the condition is what killed it.
  - **Secret Base v3:** "At the start of your turn, place a Bomb 4 [6] on a
    random enemy." 1-cost Uncommon Power; copies stack. It replaces this
    round's "placed 3 [4] bigger".
  - It is her Noxious Fumes: the base-game shape the paper's census points
    at, a 1-cost Uncommon Power that pays every turn with no card spent.
  - **What it does:**
    - It gives every Set off something to pay.
    - It feeds a Spark for every Bomb that goes off.
    - Its Bombs still grow 4 a turn, so it is both an engine and something
      to cook.
    - A run earns it by drafting it.
  - **Ruling:** the Bomb is placed after her Bombs grow, so it shows 4 when
    she acts.
  - **Loops:** Chained Reactions grows Bombs and places none, and
    Aftershock places at most one a turn, so neither feeds it.
  - **Prediction:** a run holding it plays it in at least half of its act-2
    and act-3 fights. Arm 1's Bomb+Mine damage a turn beats round 1's arm 1
    on both seeds: 13.0 / 14.8 (Ironclad) and 16.1 / 20.6 (Regent), acts 2
    / 3.
- **Before round 2,** both instrument gaps get fixed:
  - the fight line for a boss with several forms;
  - Witch's Homework II's logged size.

## Picks

**RULED 2026-10-05, all four at their defaults** ([USER]: "I agree all
around... let's test this out.").

The paper's pick 5 (the relic on the starter) is ruled no, above.

1. **The gate for suite 2, written down now, before round 2.** The turn-2
   figure did not move, and the missed prediction stays missed.
   - **Default:** in act-2 and act-3 normal fights, Klee's damage a turn
     and HP lost are within the Balance bar (15%, `telemetry_report.py`) of
     the base character's run on the same seed, on both seeds.
   - She must also reach the act-3 boss on both seeds, and boss fights are
     read once their telemetry is fixed.
   - A slow start is fine if the delayed payoff pays for it.
2. **Secret Base v3** ("At the start of your turn, place a Bomb 4 [6] on a
   random enemy") replaces this round's Secret Base on `klee-next`.
   **Default:** yes.
3. **Strength and Bombs** (the paper's pick 4). The seats held at most 1
   Strength. **Default:** defer past this pass. Low Strength makes it a low
   priority; it is not a rejection of the interaction (GPT).
4. **Round 2 before suite 2.** Two seeds, cards given at embark:
   - arm 1: Secret Base v3 and Boom Badge;
   - arm 2: the same plus Witch's Homework II, with its size logged.
   **Default:** yes. Suite 2 runs on whichever build meets pick 1's gate.

Boom Badge (Retain, does not stack) stays on `klee-next`. B stays a staging
grant until it has a logged size and a paired read.
