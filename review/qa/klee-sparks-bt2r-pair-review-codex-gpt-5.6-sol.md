## Arm: Bag of Tricks

### F1

1. The evidence. On board t01, the deciding reader chose: “Bag of Tricks on Seapunk [mode: Spend 3 Sparks: place 3 Bombs dealing 5.] -> Kaboom! on Seapunk -> Firework Finale on Seapunk.” The reader explained that Kaboom! caused “the Bombs to detonate and restore 3 Sparks” before spending them on Firework Finale. The replay recorded bank 0 after the mode, bank 3 after Kaboom!, and confirmed: “Both 3-Spark uses were PAID and BOTH RESOLVED in the one turn.”

2. Against the threshold. 1 of 1. The line took the priced mode, attacked the same enemy, paid Firework Finale in the same turn, and the wire showed 0 immediately after the mode and 3 immediately after the Attack.

3. Verdict: **PREDICTED**.

4. Judgment: **RETURN**.

### F2

1. The evidence. On board t03, the deciding reader wrote: “It gave up Duck and Cover; the available energy went to the larger block card instead.” However, that form was REFUSED for `no_second_line` and `intent_insensitive`. Under the registered refusal rule, this wording is only an out-of-slot observation. No replay ran, so “the next-turn reading this board was built to buy DOES NOT EXIST.”

2. Against the threshold. The slot has no admissible 1-of-1 observation. The deciding form was refused and there is no next-turn bank reading.

3. Verdict: **UNREACHED**.

4. Judgment: **RETURN**.

### F3

1. The evidence. On board t02, the deciding reader’s chosen line named both priced uses: “Bag of Tricks on Nibbit [mode: Spend 3 Sparks: place 3 Bombs dealing 5.] -> Firework Finale on Nibbit.” Its second answer instead named a different alternative: “I seriously considered replacing Mine Toss with Duck and Cover.” In replay, Bag of Tricks consumed the bank, after which Firework Finale was refused as `BlockedByCardLogic`; therefore exactly one priced use was paid.

2. Against the threshold. 0 of 1. The replay established exactly one paid priced use, but the second answer named neither Bag of Tricks’s priced mode nor Firework Finale as the considered-and-declined line.

3. Verdict: **MISS**. This is the registered instrument finding.

4. Judgment: **RETURN**.

### F4

1. The evidence. All three deciding forms carried complete forecasts:

   - t01: “['0', '3', '0']” — 3 asked, 3 carried.
   - t02: “['3', 'yes', '1']” — 3 asked, 3 carried.
   - t03: “['4', '4', '20']” — 3 asked, 3 carried.

   None was refused for `forecast_missing`.

2. Against the threshold. 3 of 3.

3. Verdict: **PREDICTED**.

4. Judgment: **ADVANCE**.

### F5

1. The evidence. On board t01, whose deciding line took the priced mode, the first two forecast answers were “0” and “3.”

2. Against the threshold. 1 of 1. Both registered forecast values matched.

3. Verdict: **PREDICTED**.

4. Judgment: **ADVANCE**.

## Pre-registered return condition

**FIRED.** F1 is PREDICTED: the bank returned to 3 after the same-turn detonation, and the reader paid for both priced uses. Predicate (a) therefore returns the arm independently of F2. F2 remains UNREACHED and contributes no inference.

The boards did not all do what they were built to do. Board t01 directly obtained the same-turn recycling observation and its forecast-legibility reading. Board t03 did not obtain its next-turn observation because the deciding form was refused. Board t02 exposed an instrument failure: despite the board’s exclusivity claim, its deciding line proposed both priced uses, while live replay established that the second was unpayable.

The local shadow seat decides nothing; its t01 and t03 forms were refused, and its surviving t02 form was not replayed.

**Overall: RETURN.**