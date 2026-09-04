Status: OPEN (no pick; the defaults in §4 are applied)

# Klee round fourteen: the Spark economy pays for itself, and the cap holds

Written 2026-09-04. One blind Opus seat played the Bomb kit on
`0.2.2564+proto` (rows on `docs/prototype-surface.yaml`), the first build
with the bridge's action cap (`EB-456`), the Bomb badge listing its charges
oldest first (`EB-450`, half), Oz named (`EB-446`) and the map printing gold
and deck (`EB-447`). Record: `review/qa/klee-round-14-2026-09-04/opus-act1.md`.
Prototype stage, Guardrail-7. No pick.

## 1. The run in one paragraph

Seed `SL4V9ZDBZ20G`, Ascension 1. Six fights, six won, floor 8, 32 of 62 HP;
the bridge refused the 121st action on a reward screen with `budget
reached`, the first round the cap held by mechanism. No rest site or shop
was ever on the path, so the deck ended at 16 with nothing removed. Neither
Countdown nor Stoke the Fuse was offered; Quick Fuse was offered once and
passed over, which the seat named its one regret.

## 2. What the round found

**The Spark economy is the quiet star.** Pounding Surprise pays a Spark per
charge popped; Powder Charge and Bang Bang! are Spark-priced; so a
detonation funded the next placement and the next detonator in the same
turn, three kit cards for zero energy, and Bang Bang!'s face flipped from
`CANNOT BE PLAYED` to playable mid-turn. R219's price, read for the third
round as the thing that makes the kit's turns work.

**Hold or pop is the spine, and both branches are computable.** The badge
now prints `Bombs here: 16 / 10 / 8, growing each turn` (`EB-450`'s half);
fight 2 turn 2 held at 22 for a guaranteed 34 one-shot, the round's best
decision, "made entirely off printed numbers". "Kills move it on" walked a
dead toad's Mine onto the survivor and 16 points of Bomb onto the last
slug; Careful Now's "when played" ordering was found from the face alone;
fight 3 turn 3 was a turn where the right play was to play nothing and let
the Mine kill, which the Mine tip (`EB-436`) said in so many words.

**One invisible Mine.** After a Set off on the Gremlin Merc the rider's
Mine did not print on the status block and its 3 damage landed anyway; the
same rider printed in fights 1 and 3 (`EB-457`).

**Hexerei still does not parse.** "Cards of hers pay when you play one",
pay what; the seat skipped Witches' Circle and Coven Errand because it
could not price them (`EB-444` widened). The reaction glossary still
printed a paragraph ending "NO REACTION IS REACHABLE HERE" on every screen
of a mono-Pyro run (`EB-428` widened).

**The page printed the enemy block twice** on five observes (`EB-458`).

**The starter's bottom, a fourth round.** Eight of sixteen cards were
Strike and Defend; fight 6 turn 1 was all-generic, "a turn with no kit in
it". Same finding as rounds 11 to 13; carried to the pool pass.

**Turn one.** A real decision on a card (plant a Bomb with no Set off in
hand, or Strike), the engine on turn 2, real tension on the fourth turn of
the run: "a fast enough ramp".

## 3. What the round did not test

Countdown, Stoke the Fuse, Quick Fuse; a rest site or shop; the boss. One
run. Nothing here is a strength reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-457`, `EB-458` minted; `EB-444`, `EB-428` widened.**
- **The cap held** (`EB-456`): 120 of 120, the refusal read as the stop and
  not as a finding.
