Status: RULED R276 2026-09-23

# Klee: a design pass, and a finish line

Written 2026-09-23 by Claude (Opus 5.5), from the brief
(`review/active/klee-brief-2026-09-01.md`), your two runs
(`review/ruled/klee-user-run-1-2026-09-07.md`,
`review/records/klee-user-run-2-2026-09-08.md`), rounds 26 and 27, the
consolidation ruling (R271), and a census of the live build (49 draftable
cards, read off the generated C#).

## 1. My verdict: the kit works, so stop redesigning it

Klee is the best of the three kits, and the evidence is unusually
consistent:

- You called the concept sound on both runs, and on run two named the
  tension ("attack spam go!" against "how do I block?") as the thing that
  works.
- All four seats in round 27 named "set it off now or let it grow" as the
  recurring decision, unprompted. Jumpy Dumpty (Innate) plus Ka-pow!
  (Retained, 0 cost) makes turn one of fight one a real fork.
- Her defences each hang off that one decision. Grounded pays for a turn
  where nothing went off, Run Away! pays for a turn where something did, and
  a Mine is both. This is the best idea in the mod, and it came straight
  from her lore (Jean grounding her, running after the bang, Jumpy Dumpty's
  mines).

What is left is finishing work: a few more Mine cards, a cleaner pool, one
keyword that is not pulling its weight, and a list of text bugs. None of it
needs another rule, and none of it needs 27 more rounds.

## 2. What I would change

**Build the two planned card batches together (four cards) and cut five.**
R271 planned Tripwire ("one of your Bombs becomes a Mine") and Explosive
Frags (a Mine going off applies 2 Vulnerable) as the Mines batch, and Where
Did I Put It? (find a *Set off* card) and Big Bounce (overkill carries to
another enemy) as the next slice. All four are good and fix things seats
kept naming. Mines are her best verb and have only three placers, and "I
can't find a detonator" was the most common complaint. Build all four in
one go. At the same time, cut five of the six cards R271 put on the
lower-value shelf:

- Long Fuse is Ka-pow! at 1 Energy.
- Explosives Workshop: the one seat that drafted it twice could not point
  at a moment it mattered.
- Sugar Rush overlaps Sparkling Burst and was often unplayable at its
  2-Spark price.
- Kindling and Catalytic Converter never found the deck they were for.

Keep Rapid Fire, the one chaotic multi-hit Set off card, which is fun with
Chained Reactions. The pool goes from 49 to 48, and every card left has
been played on purpose by someone.

**Replace Hexerei with "Companion" (the new fact: under the prototype
arm Klee starts with no companion card, so every Hexerei reader waits on
two lucky offers).** Today any companion card printing the word Hexerei
gives her 1 to 3 Sparks, and three of her cards read Hexerei plays. You
said on run one that the tag never came together, and it cannot come
together often. It needs the companion slot to offer a Hexerei card *and*
her reward to offer a reader. Making the same rule read *any* companion
card keeps the idea, which is her friends feeding her explosions, and
removes a keyword and a tooltip. It also makes every companion she drafts
matter to her. The coven stays in the card names (Coven Errand, Witches'
Circle). This is option 3 of R265 pick 2, which you did not take then.
The fact above is why I'm asking again.

**Leave Sparks alone.** I considered capping Sparks at 3, which is canon
(her Boom Badges cap at 3) and would stop the pile-up one seat saw. But your
R266 principle is "no artificial constraints when card design can do
better", and the pile-up only happens in decks that drafted no way to spend
Sparks. The floors 1–3 reward rule already offers one. The opening bank of
1 stays (the held R271 comparison closes as a D default): five cards now
cost 1 Spark, so turn one can spend it.

**Fix the text and residue without asking.** These are hygiene:

- The brief says Bombs grow by 3, but the game uses 4.
- The brief says her Strength boosts explosions, but it doesn't.
- The upgraded relic Dodoco Tales promises 3 opening Sparks the prototype
  turns off.
- Her Ancient card (Jumpy Dumpty Mk.Omega) places an old-rules Bomb.
- Stale comments and one dead file remain.
- Round 27's four display bugs are still open: relic bonuses missing from
  card faces, the Stage glossary leaking onto her screens, Amber printing
  `{Damage}`, and "oldest Bomb" being ambiguous.

## 3. The finish line

Today's "done" test is three calibration answers from you on two builds in
a row. I would replace it with something simpler: **once the batch above is
built and two seats have played it, you play one full run.** If it is fun
through act 3, Klee moves to Balance: her cards go onto the real sheet, the
sim measures her, and numbers get tuned there. If it isn't, your notes say
which part, and we fix that part.

## 4. Picks

**Pick 1: the pool.**
1. **(default)** Build Tripwire, Explosive Frags, Where Did I Put It? and
   Big Bounce together, and cut Long Fuse, Explosives Workshop, Sugar Rush,
   Kindling and Catalytic Converter. The pool becomes 48.
2. Build only the Mines batch now, as R271 staged it, and keep the shelf.
3. Your own list.

**Pick 2: Hexerei.**
1. **(default)** Hexerei becomes "Companion": any companion card gives
   Klee a Spark (1 to 3, as now), and the three readers read any companion
   play. One keyword fewer.
2. Keep Hexerei as it is.
3. Drop the Spark on companion plays entirely. The readers go too.

**Pick 3: the finish line.**
1. **(default)** Two seats, then one full run by you. Fun through act 3
   means Balance.
2. Keep the calibration gate as written in `operations/stage-gate.md`.

## Ruled (R276, 2026-09-23)

All three picks at their defaults, with one correction from [USER]: "Klee's
overall pool is still incomplete (the target for each pool is 78 standard
cards + the ancient rewards + multiplayer cards), which skews the balance
discussion somewhat (small pools are more reliable)." So pick 1's cuts and
four cards land, but 48 is not a finished pool: the pool grows to 78
draftable cards before Klee moves to Balance, and pick 3's full run is read
on a pool that is at or near that size.
