Status: OPEN (no pick; the defaults in §4 are applied)

# Furina round six: the reader that never pays, and two nouns that read as one

Written 2026-09-04, the same afternoon as round 5. One blind Opus seat
played the reframe arm on `0.2.2501+proto`, the build with round 5's seven
fixes live (`EB-419` to `EB-423` and the harness's `EB-435`): the face no
longer prints "(reframe)", Duet's second play says why it does not perform,
Guest Cast's tip no longer says "no Fanfare", the Spotlight Spend Boost row
is hidden, Shatter removes Frozen. Record:
`review/qa/furina-reframe-round-6-2026-09-04/opus-act1.md`. Prototype stage,
Guardrail-7. No pick: round 5's pick 1 (the Encore opening) is still
[USER]'s, and this round's new finding is answered by a default in §4.

## 1. The run in one paragraph

Seed `1A3S4GK2ELEL`, Ascension 2, 120 of 120 actions, no refusals, no
stalls: five fights won, the floor-11 elite (Skulking Colony at 7 of 75)
left mid-turn at 25 of 84 when the budget ran out. Aria was played at
Fanfare 3 in the first fight and the 6 line did not pay; Fanfare sat
between 1 and 6 all act, decaying 20% a turn, and neither reader (Aria's
line, the Salon's +1 per 10) fired once. The seat predicted a 32-damage
turn off the printed text and got exactly 32.

## 2. What the round found

**The reader never pays, and the reason is timing.** Three runs across
rounds 5 and 6 played Aria at Fanfare 3 and never at 6. Aria is the first
card played on the turn the engine starts, and Fanfare is minted by
performances that come after it; the bar the rider copies use (6, reached
by a stage that has performed a few times) is one Aria does not stand at
when it is in hand. "I finished the act unable to say what Fanfare is
for." §4 takes the default: the bar on Aria moves to 3, the Fanfare the
records show on an Aria turn, and the offered copies keep theirs.

**Two nouns read as one, and the Spotlight reaches only one of them.**
With Guest Cast up, the log printed Crabaletta's hit at 4, which is 6 at
the dry rate with no 1.5x. The card says "Spotlight every Companion card",
the relic says "once your Companions are lit", and the kit calls members
Companions elsewhere; the seat could not tell a bug from a noun (`EB-437`).
The rule is the reframe's own (Guest Cast reaches Companion cards; members
perform at their own rate); the surfaces say it in one word.

**The fold is excellent and inconsistent.** Card text folds Weak, Frail and
Strength; stored-buff text does not (Sacramental Shower "deal 9" delivered
6 under Weak); the Spotlight rewrites a card's first clause and not its
second (First-Person Shutter printed 4/4, delivered 6/6); Seeker Strike
printed 7 and dealt 6, and a Gremlin Merc lived on 1 HP after arithmetic
that said it was dead (`EB-438`).

**A member's targeting is printed nowhere.** The front member "hits
whatever it likes," splitting damage across two Toadpoles; `EB-430`'s
sentence (the perform follows the card's target) does not match this
board, and `EB-439` reconciles both to the code.

**What read true.** The round-5 fixes where met: the face title, Duet's
line, the Guest Cast tip, no stray status row. The ordering decisions
(Aria then Salon Début, worth 2 damage; grenades after the deploy, worth
about 10) were made from printed text, and the Reaction preview line again
carried the best turns. Turn one of fight one presented a decision.

## 3. What the round did not test

The boss; the Encore opening (round 5 pick 1, unruled); any rider copy.
One run. Nothing here is a strength reading.

## 4. Defaults applied (D and E), disclosed

- **Aria's bar moves from 6 to 3** (D): a number lifted off the records
  (Fanfare on an Aria turn, three runs) rather than picked; the rider
  copies keep 6/6/8/10 because they are drawn later in a fight. Built on a
  branch beneath this packet; [USER] plays the first build of the starter
  card either way, since R254 already made that so.
- **`EB-437`, `EB-438`, `EB-439` minted.**
- **Fanfare's two readouts** ("cards read it and none spends it" against
  "no rule for how it is spent") are one sentence to fix inside `EB-422`'s
  neighbourhood; folded into `EB-437`'s build as the same surface, not a
  row.
