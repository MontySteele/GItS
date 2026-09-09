Status: RULED R270 2026-09-08

# Klee round 25: Spark is a currency with almost nothing to buy; the Spark defence fails on detonator draw and Energy, never on Sparks

Written 2026-09-08, evening. Two blind Opus seats on `0.2.3105+proto` (main
`28d1769b` after #466), the first build after [USER]'s second run
(`review/records/klee-user-run-2-2026-09-08.md`) and the tip trims. Records:
`review/qa/klee-round-25-2026-09-08/opus-lane1-detonator.md` (lane 1,
natural, Countdown granted) and `opus-lane2-spark-defence.md` (lane 2,
assembled: Dodoco Cover, Careful Now, Barbara's Front Row Seat, Coven
Errand, Witches' Circle, Fischl's Oz, Sucrose's Gust). Prototype stage,
Guardrail 7. **Caveat on the instrument:** each seat's brief was the standard
brief with one question appended for this round, (f) below; the brief's own
text was not changed.

## 1. The two hypotheses

**Lane 1** (the comparison pass §4): "a natural lane that holds one
Energy-priced detonator beside its Spark-priced ones reaches a turn where
the Spark price binds without deadlocking, and the seat can say which price
it paid and why." **Lane 2** ([USER]'s run, note 2): "a seat that builds the
Bomb every turn and eats it for Block when the intent says so reaches the
act-1 boss with the Spark bank never at zero on a Block turn; where it
fails, the record names whether the Spark was missing, the Bomb was missing,
or the Block row's condition was false."

**Lane 1:** 120 of 120 acts, floor 11, five fights won including the Terror
Eel elite, the sixth (Phantasmal Gardeners) cut off by the budget; 54 of 72
HP. **Lane 2:** 120 of 120, five fights won, the Bygone Effigy elite in
progress at 56 of 127 with a Bomb 65 on it; 26 of 62. Neither lane stalled
or hit a refusal streak.

## 2. The reads

**1. Lane 1 never bought a Spark-priced card, so the Energy-versus-Spark
choice never arose.** The seat was offered Fwoosh!, Pocket Match and
Fireworks Show and passed on all three, each time because the Energy
detonators it already held (Countdown, Ka-pow!) were doing the job and
something else on the screen looked scarcer. Its Spark bank ended fights on
3, 5 and 5 having spent zero. In its words: "Whatever Spark is meant to be
rationing, it did not ration me — and a resource that only ever accumulates
is not making decisions. The bottleneck was Energy every single turn."

**2. Lane 2's Spark bank never reached zero and peaked at 8 while it was
taking damage.** Four turns needed Block and did not get it. On none was the
Spark missing; on none was the Bomb missing. One (fight 4 turn 3) was a
false condition, and the missing ingredient was a **Set off card**:
Barbara's "whenever a Bomb goes off this turn" is priced in a detonation,
which the deck could supply from 3 of 23 cards. The other three were Energy
spent on setup, a young Bomb, and the Block cards not being in the drawn
hand. The seat's sentence: "Spark is not a constraint on Klee's defence; it
is a currency with almost nothing to buy. The scarce resources in this kit
are Energy and detonator draw, not Spark."

**3. This answers [USER]'s note 2.** The inconsistency of a Hexerei-paid,
Spark-priced defence is not user error and not a Spark shortage. It is
detonator draw and Energy, and the defence rows price in different things:
Careful Now prices in the Bomb (nearly always present once Jumpy Dumpty is
Innate, so it "essentially never failed"), Barbara prices in a detonation
(a third resource her face names but the deck may not hold), Dodoco Cover
prices in nothing. Dig In (8 Block for 1 Spark, no Energy) was lane 2's most
valuable pickup precisely because it converts the surplus into the thing
that is scarce.

**4. The Spark-economy question is now read from all three edges.** Round 23:
never scarce on a natural lane, deadlocked on a deck of Spark cards. Round
25: never scarce on two more lanes, one of them built to spend it. The only
binding case on record is a deck of Spark-priced detonators with no
Energy-priced one, and lane 1 shows why: an Energy detonator in the starter
makes the Spark-priced ones optional. Pounding Surprise pays one Spark per
charge that goes off, so the biggest detonation turns are the turns the bank
grows fastest.

**5. The kit's real decisions read the same on both lanes, and well.** Both
seats named "detonate now or let it grow" as posed on turn one of fight one
and every turn after, with the screens' arithmetic ("Set off here deals 69
Pyro damage after Vulnerable") as the reason it is a decision on numbers and
not on faith. Lane 1 named element ordering (Diona then Bombs Away! is Melt;
the reverse is nothing) as the second real decision; lane 2 named Careful
Now before the detonation that destroys its Bomb, and Chained Reactions
rebuilding the field mid-turn, as the best dilemma in the kit. Both said the
first turn of the first fight presented a decision.

**6. Strike and Defend are dead weight on both lanes.** Lane 1: eight of
nineteen cards it was disappointed to draw; lane 2 paid 75 gold to remove
one Strike and "would have removed four more." This is R242's starter rule
working as [USER] wants it (the basics are supposed to be bad); it is
recorded, not raised.

## 3. Where the screen and the outcome disagreed

- **Mine, "and the hit still lands"** (lane 1, twice; lane 2 once). The
  tip trimmed today dropped `EB-436`'s exception, "unless the Mine kills";
  lane 1 gambled 9 HP on the plain reading and the Mine killed with no hit.
  My regression, fixed on this branch (§6).
- **Kindling on a bare enemy** (lane 2, fight 5). Face: "Each Bomb on an
  enemy whose aura is not Pyro grows by 4." With no aura on either body only
  the largest grew, by 2; with a Hydro aura present both grew by 4. The
  engines read "an aura other than Pyro", Flame Dance's rule (`EB-664`);
  the face says the other thing.
- **Diona's "Apply Cryo twice"** names no target; lane 1 read two bodies,
  the bridge refused the untargeted play, and it is one body twice.
- **Fischl's Oz end-of-turn hit is Electro** and consumed Barbara's Hydro,
  turning a planned Vaporize into Electro-Charged; lane 2 declined its best
  Power three times to protect the multiplier. The reaction rules are
  working; the Oz tip does not say the hit carries Electro.
- **The `Bomb N` header folds a pending Vaporize** while the sizes list
  beside it is raw (`Bomb 18 ... sizes: 12`), lane 2. `EB-559`'s family.
- **`Witches' Circle 3 (buff)`** prints the Bomb size it places where every
  other numbered buff prints its own stacks, lane 2; Chained Reactions the
  same.
- Not defects: Kaeya's Grounded clause meant nothing to a seat holding no
  Grounded card (`EB-576` built it as printed); lane 1 could not tell
  whether later hits of a multi-charge Set off react (the tip says only the
  first takes the aura); Countdown's draw "never once mattered"; both lanes
  held every potion to the end.

## 4. What the round did not test

An act-1 boss. A deck holding both a Spark-priced and an Energy-priced
detonator, since lane 1 declined every Spark-priced one; that is the
finding, not a gap in the design of the round, but it means "which price did
you pay" has still not been answered by a seat that held both.

## 5. Pick

The brief (R213 course-correction, draft 2) makes Spark Klee's second
currency: Hexerei plays and detonations earn it, detonators and sinks spend
it. Four lanes and [USER]'s run now say it does not compete with Energy. The
brief cannot settle what Spark is for, so this is [USER]'s.

1. **What Spark is for (A).** **Default: 1.** (1) A lubricant that buys the
   scarce things: income untouched, and a pool pass adds Spark-priced rows
   that pay Block, draw or Energy (Dig In's shape), read at the doctrine door
   and by a seat round; Spark then makes a spending decision because its
   sinks compete with each other for the bank, and the surplus becomes the
   defence's consistency. (2) A scarce second currency: Pounding Surprise
   pays per detonation instead of per charge and the opening Spark falls,
   so a Spark price binds on a natural lane; a rule change [USER] plays,
   with round 23's deadlock as the known risk. (3) As it is: Spark stays a
   number in the corner, the Spark-priced detonators stay optional, and the
   question closes with this record.

## 6. Rows and defaults

Minted: `EB-719` the Mine tip regression (BUILT on this branch, `EB-436`'s
exception restored); `EB-720` Kindling's face ("an aura other than Pyro",
Flame Dance's wording), Diona's face (the target named) and the Oz tip ("an
Electro hit"), BUILT together; `EB-721` the `Bomb N` header fold (OPEN,
display); `EB-722` the buff-strip number for a placer Power (OPEN, display).

Defaults applied (E): the three face and tip fixes follow the rule each
engine already runs and move no number. Nothing measured; no stamp moves.
Round 26's hypothesis is written from the ruling on §5.

## 7. Ruled (R270, 2026-09-08)

Option 1. Spark's income stays as it is, and the pool gets Spark-priced rows
that pay Block, cards and Energy, priced on Regent's Stars ladder
(`docs/current/research/regent-stars-economy.md`: cheapest sink 1, median 3,
a Rare at 5) and read at the doctrine door before they are built:
`review/records/klee-pool-pass-two-2026-09-08.md`. Round 26 reads the pass.
