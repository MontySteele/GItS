# Furina sweep round, 2026-10-14

Ten blind Sonnet seats played Furina at A0 on build 0.2.5460. That build
carries the ruled sweep (#1271: fifteen cuts, fifteen new cards of her own,
`review/active/furina-sweep-2026-10-14.md`) and the tooltip trim (#1269). Each
seat played a whole run on its own seed. The seat records are in the
session scratchpad (`seats/archive/furina-sweep-r1` to `-r10`). Raw
transcripts are not kept.

## Results: 4 wins in 10

| Run | End |
|---|---|
| r1 | Lost to the final boss (Queen), floor 48 |
| r2 | Lost in act 2, floor 24 (Bowlbug Rock, Bowlbug Silk, Slumbering Beetle) |
| r3 | Lost to the act-2 boss (Kaiser Crab), floor 33 |
| r4 | **Won**, floor 48 |
| r5 | **Won**, floor 48 |
| r6 | **Won**, floor 48 (low of 9 HP against the Knowledge Demon) |
| r7 | Lost to the act-2 boss (The Insatiable, 130 of 321 HP left), floor 33 |
| r8 | Lost to the act-2 elite (Entomancer), floor 28 |
| r9 | **Won**, floor 48 (Queen and Torch Head Amalgam, at 3 HP on the last turn) |
| r10 | Lost in act 2, floor 23 (the same Bowlbug room as r2) |

Before the sweep, the same build line went 1 win in 3, counting one Abyss
run. On the 2026-10-05 baseline, base-five seats went 0 for 5 at A0. With 4 in
10 and every loss in act 2 or later, the sweep did not cost her strength.

## What played well

- **Deciding when to bank Fanfare and when to spend it was the main choice
  in every run.** The wins came from building a bank and then spending it
  in one burst: Bravura, Let the People Rejoice, Rising Applause+ and
  Verdict of the Oratrice. In r9, Verdict landed at Fanfare 42 on a Queen at
  14 HP.
- **The new cards were drafted and used.** The Show Must Go On+ carried the
  final turn in r9. Verdict of the Oratrice closed bosses. Ousia / Pneuma
  was played as intended, flipping between damage and Block.
- **Reactions read well.** Seats ordered Hydro and Cryo off the "Reaction
  preview" line. Electro-Charged from guests (Hydro onto an Electro aura,
  giving Poison 32 in r5) carried a win.
- **One Grand Deluge killing two linked enemies at once** beat the Kaiser
  Crab's Crab Rage in r9.

## What did not

- **Three runs (r2, r7 and r10) died with Fanfare banked or undrawn.** In
  r10, Let the People Rejoice+ sat unseen for three turns with 38 Fanfare
  banked, while the seat had 11 Block against 43 incoming. Banking pays off
  only if the spender shows up.
- **The act-2 Bowlbug room** (Rock, Silk and Slumbering Beetle) ended two runs
  on floors 23 and 24. **The Queen** ended one run and nearly ended r9.
- **Weak cards** named by more than one seat: Leading Lady (its numbers were
  ambiguous), Prima Donna, Thunderous Applause and Exterminate. Charlotte and
  Crescendo were called dead in r2.
- **Text and display:**
  - Hold the Stage's "Spend up to 16" spends the whole bank with no chooser
    (r6, r9).
  - Commanding Gaze opens its chooser only at Fanfare 4 or more, which the
    card does not say (r6, r9).
  - Playing Ousia logs as "Pneuma" (r7, r9).
  - Bravura's "Fanfare / 3" was misjudged (r2).
  - Understudy's Debut's "below half", "past your line", and the Surrounded
    and facing cues were unclear.
  - Neuvillette's damage preview counts HP lost to your own Drain, which his
    text does not say.
  - The incoming-damage line ignores Tungsten Rod.
  - Duplicate numbers on the page shift after a play.
- **To check, from one report each:**
  - Corpse Slug still attacked while Stunned (r4).
  - Tender's text prints backwards (r5).
  - The Charlotte keyword never applied (r5).
  - Salon Solitaire's Repay timing at end of turn misled a seat into a lethal
    end turn (r3).
  - Vambrace (once per combat) reads as once per turn (r5).
- **Seat caveat:** several seats filtered observe output with grep (they
  declared it). Their play is still blind to the repo.

## What to change

1. Fix the text and display list above. These are hygiene fixes, with no
   numbers and no pick.
2. Check the five one-report items against the code. Fix any that are real.
3. No number moves on one round. Watch the Bowlbug room and the four
   weak-card names in the next Furina round.
