Status: OPEN (no pick; the defaults in §5 are applied)

# Klee round ten: the defence shelf read, and the two pre-roster runs beside it

**Read after the fact (R253, 2026-09-04):** the shelf these six runs were
offered had five rows. The charter audit of the same day
(`review/records/card-audit-2026-09-04.md`) withdrew Fire Safety and Safety
Lesson, so the shelf on the surface is Dodoco Cover, Careful Now and
Barbara — Front Row Seat. Nothing below is rewritten; where a run played one
of the two withdrawn rows the record says so and stands as a record.

No pick. Everything is a default, applied and disclosed in §5.

Written 2026-09-04, evening. Six Opus runs on the round-10 build, two of
them before the five defence rows were in the arm's offer roster and four
after. The first build (`0.2.2399+proto`) compiled R252's rows and never
offered them: the roster that hands the reward screen its cards lists the
arm's rows by name and the build's author had added them to the sheet, the
sim and the generated master list and not there. Two runs read it before a
seat that was never offered a new row exposed it; the roster now has the
rows and a lint (`tools/lint_arm_pool_parity.py`) that reads the sheet
against the roster and the sim's mirror, so it cannot recur. The corrected
build (`0.2.2401+proto`) carried runs three to six. All six runs sit at
Ascension 1 with every arm on and the round-9 legibility rows (#362) built.
The records are `review/qa/klee-round-10-2026-09-04/opus-act1.md`,
`opus-act2.md`, `opus-run2-act1.md`, `opus-run2-act2.md` (the pre-roster
pair) and `opus-run3-act1.md`, `opus-run3-act2.md`, `opus-run4-act1.md`,
`opus-run4-act2.md`, `opus-run5-act1.md`, `opus-run5-act2.md`,
`opus-run6-act1.md` and `opus-run6-act2.md`; every claim below names one of
them. This branch also carries R252 and the rows' build (#361), so the
ruling, the rows and their read land together.

## 1. The runs in one paragraph

Pre-roster: run one cleared act 1 at 10 of 62 and died on act-2 floor 25 to
the Hunter Killer holding a Bomb 28 with no detonator (`opus-act2.md`,
fight 4); run two cleared act 1 at 16 of 62 and died on act-2 floor 24 to
the Decimillipede (`opus-run2-act2.md`). On the shelf build: run three
cleared act 1 at 17 of 77 with Dodoco Cover, Run Away! and Careful Now in
the deck and was stopped in act 2 at 53 of 77 by a screen the page cannot
drive, the Crystal Sphere's minigame (`opus-run3-act2.md`, `EB-396`); run four cleared act 1 at 15 of 62 with Careful
Now and Dodoco Cover, a Bomb 66 into Big Badda Boom on the Fogmog, and
died on act-2 floor 31 to an Infested Prism the map offered as the only
node at 9 of 62, after two Elites (`opus-run4-act2.md`). Run five cleared
act 1 at 39 of 83 on Dodoco Cover and Run Away! and died on act-2 floor 31
to the Entomancer, a Big Badda Boom into Thorns having cost it the margin
(`opus-run5-act2.md`); run six cleared act 1 at 36 of 62 and reached The
Insatiable, dying on floor 33 to the boss's Sandpit timer at 30 of 72 with
the boss at 78 (`opus-run6-act2.md`). Six act-1 clears from six runs, where
round 9's one run cleared act 1 at 12 of 69; no run cleared act 2.

## 2. What the round found

**Dodoco Cover is the opening-hand fix and the seats played it every
fight.** Run three called its first turn on it "the turn that sold me the
kit" and led with it in five of eight fights; run four played it on the
turn it named "the whole kit in one turn on 3 energy" (`opus-run3-act1.md`,
fights 4 and 6; `opus-run4-act1.md`, fight 6). Its Block half was dead on
every turn the enemy's intent was Buff, Debuff or Status, about a third of
turns, which is the price the brief sets on every conditional defence and
the seats read it as such (`opus-run3-act1.md` §(b)).

**Careful Now splits the two seats, and the split is the kit's decision.**
Run four stalled three turns behind it, 10 Block a turn off a Bomb that
climbed 20 to 66, then cashed the stack for 54 (`opus-run4-act1.md`, fight
6): the Cook line, exactly as the row was written. Run three never held a
Bomb long enough for it to pay, because that seat cashed early into the
Spark loop, and it called the card "anti-correlated with what you want to
be doing", 6 Block once and 0 the rest (`opus-run3-act1.md` §(b), §(d)). Both
seats found the one thing the face does not say: it reads the largest Bomb
at the moment it is played, so before a detonation it pays 10 and after it
pays 0 (`opus-run4-act1.md` §(c) 4). `EB-394`, default applied: the face
says "when played". The design stands; a defence that pays the cook and not
the spray is the shelf doing what R252 asked.

**Run Away! read as designed.** Taken over Coven Errand for its 0 cost, dead
on non-attack turns, worth 7 on the turn after a cash (`opus-run3-act1.md`,
fight 7 reward and §(b)); run five leaned on it (`opus-run5-act1.md`).
**Safety Lesson was offered once and declined**, its 2 Block per Bomb read
as less than a Defend at the one or two detonations a turn that seat was
seeing (`opus-run5-act1.md`, fight 4 reward); one read, held. **Fire Safety
read as a dead pick in a mono-Pyro deck** (`opus-run6-act1.md` §(b)), which
is the React loop's own condition: every reaction-keyed card in the arm
needs an off-element companion, and a deck without one reads a glossary it
cannot use. The row stands; the pool pass that follows should weigh how
many rows key off a reaction the kit cannot make alone. **Barbara — Front
Row Seat** was offered to no seat in six runs; the stand-in waits on the
companion slot rolling Barbara. Run four's act 2 added the shelf's other cost: Careful
Now's number is unreadable from a badge that prints only the stack's sum
(`opus-run4-act2.md` §(c)), which is `EB-343`'s aggregate line and `EB-394`'s
face between them.

**The Spark loop can close, and three seats sat inside it.** Sparks come
from Bombs going off, two Set off cards are Spark-priced, and a seat holding
Fwoosh! and Bang Bang! at 0 Spark with a fat Bomb on the enemy had no
detonator, once under Vulnerable against a 31 (`opus-run3-act1.md` §(c)).
Ka-pow! is the starter's answer, 0 energy and no Spark, and the seat that
held it never closed the loop; the seat that did had bought two Spark-priced
detonators and drew neither. The pre-roster run one died the same way from
the other side, a Bomb 28 and no detonator of any price (`opus-act2.md`
§(c)). Run six held three Dig Ins on 1 Spark and called it a deadlock
(`opus-run6-act2.md`); run five ended fights holding 4 to 7 Sparks with
nothing to spend them on until Fwoosh! and Dig In arrived, and asked
whether a Spark sink belongs in the starter (`opus-run5-act1.md`). That is
the deck's shape, not a rule: with four placers and three detonators in
twenty-two cards, the hand that has one and not the other is the common
hand, and Spark sits on both sides of it. Noted for the next pool pass as
its first question; nothing moves on this round.

**Hard To Kill and Slippery keep inverting the deck, and the badge keeps
up.** "Capped by Hard To Kill" on the badge made bomb count beat bomb size
for one fight and the seat read it straight off the screen
(`opus-act2.md` §(a)); Vantom's Slippery 8 made a turn "which card do I
waste on the cheap stack" (`opus-run3-act1.md` §(a) 4). The round-9 tip
rewrite read true: "a Bomb is not an Attack" made Flutter navigable
(`opus-run2-act2.md` §(c) 8).

**Three seats hit the Bomb jump, and its tip is still unbuilt.** A dead
host's Bombs on a survivor, "Bombs here: 3" where one was placed, twice
called the biggest hole in the act (`opus-act1.md` finding 1;
`opus-run4-act1.md` §(c) 2; `opus-run2-act1.md`). `EB-361` was applied at
its default in round 8 and never built; it builds with this round's rows.

## 3. What the screens got wrong

Each is a row in `BACKLOG.md` on this packet's branch, or cited to one on
main.

- **Careful Now's face does not say it reads at play** (`EB-394`).
- **Dexterity reaches Dig In and Barbara and not Sorry, Jean...**
  (`EB-390`; `opus-run2-act2.md` §(c) 3).
- **One enemy prints twice; the rest verb refuses once on an open rest**
  (`EB-391`; `opus-act1.md` finding 3; `opus-run3-act1.md`, Identity).
- **Hexerei is unmarked on the companion faces it keys off** (`EB-392`;
  `opus-act1.md` finding 2; `opus-run2-act2.md` §(c) 5).
- **The Clone confirm screen, the Bugslayer event, the redaction line**
  (`EB-393`; `opus-act2.md`).
- **Jumpy Dumpty's Mine rider printed no Mine when its Bomb was stacked
  with a Pop!** (`EB-395`; `opus-run4-act1.md` §(c) 1); and the aggregate
  line's "including 1 Mine" clause is where a Bomb-21 badge paying 21 or 8
  is decided (`opus-run4-act1.md` §(c) 3), `EB-343`'s family.
- **The Bomb jump** (`EB-361`, unbuilt; a fourth seat hit it in run four's
  act 2).
- **The Crystal Sphere strands a seat** (`EB-396`) and **its glossary printed
  Kokomi's Plan tip on a Klee run** (`EB-397`).
- **Tainted defined as itself** on the glossary, its effect printed only on
  the status row after it is paid; it cost run four a losing play at 1 HP
  (`EB-359`; `opus-run4-act2.md`).
- Already rowed: Sharp, Nimble and Goopy undefined on decision screens
  (`EB-377`); Sown at the Sapphire Seed and the Wood Carvings' three
  enchants unglossed (`EB-323`); gold never printed (`EB-350`); enemies
  renumbered mid-turn after a kill (`EB-319`); the Spark line vanishing at
  0 rather than printing 0 (`EB-350`'s family); a shop's removal grid listing
  26 cards and omitting two just acquired (`EB-350`'s 25-row cap;
  `opus-run3-act2.md`); Study's Power never named (`EB-323`); Tangled on the status bar
  against Entangled on the card (`EB-360`'s family).

Seen and not rowed, because they are the base game's: a rest site printing
30% of the old Max HP and healing 30% of the new; Slow charging after the
first card; Grounded switched off by a Mine going off on the enemy's turn,
which is Grounded's own text and the seat's own read of it
(`opus-run2-act1.md`); Intimidating Helmet dead after an upgrade dropped a
cost; Pounding Surprise paying no Spark on two detonations and paying on
the next three in the same turn (`opus-run4-act2.md` §(c)), which the record
cannot reconstruct and the packet does not guess at; the act-boundary heal
that two seats read as a handover mismatch.

## 4. What the round did not test

Act 3 was reached by no run: run three was stopped by the Crystal Sphere,
runs four and five died on floor 31 and run six on the act-2 boss, so the
shelf is read across four act 1s and three and a half act 2s. No seat filled a hand with the shelf: the most any deck held
was three of the five rows. The pre-roster pair read no shelf row at all.
Sparks 'n' Splash was drafted by run one (`opus-act1.md`) and R250's
largest-Bomb rule was read for the first time: the seat held the Splash and
kept detonating, which is the rule's purpose. Act 3 is unplayed on the shelf build.

## 5. Defaults applied (D and E), disclosed

- **E:** your Klee act-1 run is due on `0.2.2401+proto`, which is the
  round-10 build with the shelf in the roster. No rule has changed since
  R248; the shelf is card design inside the brief.
- **D:** `EB-394`, Careful Now's face says "when played".
- **E:** `EB-361`, `EB-394` and `EB-395` build on the round-10 branch beside
  the rows already there; the seats read them on round 11.
- **E:** the pre-roster runs are kept as records and read for the round-9
  legibility rows only; nothing about the shelf is claimed from them.
- **E:** rows `EB-390` to `EB-400` minted on this branch (`EB-398` and
  `EB-399` are Furina round 3's, minted here as the top of the stack);
  twelve seat records committed beside the packet.
- **E:** this branch carries #361 (R252, the rows and their build), so the
  ruling and its read merge as one.
- **E:** the Crystal Sphere's page verb (`EB-396`) builds with this round's
  rows: the wire already carries the screen's proceed action.
