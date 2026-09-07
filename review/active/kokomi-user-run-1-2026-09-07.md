Status: OPEN (one pick, §5; three E and D defaults applied, §6)

# Kokomi, [USER]'s first act-1 run under the overhaul: better than before, the central loop reads as auto-pilot

Written 2026-09-07. [USER] played Kokomi's act 1 on `0.2.2888+proto` (main
`da0e5846`: the Plan kit of R240 and R241, the six now-lines and the aimed
Plan of R250, the tempo shelf of R253, the fixer-T faces of #413). This is
the first read of the kit's rules by [USER] since the R250 rulings, and the
Prototype stage is graded on it. Evidence: [USER]'s notes, quoted in the
commit that carries this packet, and the run's `godot.log` (the picks:
Arlecchino — Masque of the Red Death, Vanguard, Nereid's Ascension, Song of
Pearls; Happy Flower, Mango, Strawberry).

## 1. The verdict

**"Not bad, better than before, but the central loop feels too auto-pilot"
and needs design work.** The mechanic works. What fails is the decision on
an enemy off-turn: because every Plan written is carried out next turn, a
turn with no incoming damage collapses to "play all my Plan cards", and
there is nothing to sequence. The brief's decision (§3: now, or next turn
for more, priced by the enemy's intent) is real only while the enemy is
attacking; the moment the price is zero the loop has no question in it.
[USER] also struggled, possibly by taking Arlecchino's Rare Power early and
underestimating its chip damage; that is a play, not a finding. **The
stage holds at Prototype**, and the loop goes back to design (pick 1).

## 2. The notes, one at a time

**Plans playing the whole stack makes an off-turn a no-brainer.** The seats
had touched the edge of this without naming it: round 18's lane 1 called
turn one of fight one "no decision at all" and its best turn "two Plans
written on a free turn, 27 damage plus 4 Block"; round 22's lane 2 named
"dump into a telegraphed Block" as one of its three plays. The seats read
it as strength; [USER] read it as the absence of a puzzle, which is the
fun read and the one the stage is graded on. Design, pick 1.

**"Morning" should be retired.** Right: the word was a name for "the start
of your next turn, before you draw" so tips and the page could say it in
one word, and to a player it reads as a second term for the phrase it
stands for. It is printed on one face (Tide Wall's count), two tips and the
blind page. Hygiene, `EB-623`, applied.

**Undertow is written strangely.** "Deal 10 damage, already including 3 if
the enemy has a debuff" is the shape `EB-598` chose so the printed number
is the delivered one; it is honest and it is not English a card speaks.
The base game's shape carries the same truth: "Deal 7 damage. If the enemy
has a debuff, deal 10 instead", each number the folded live total.
D default, `EB-624`, applied.

**Shell Guard sounds wrong, and the Casket is unexplained.** Both right.
"Until your next turn, whenever the Tamakushi Casket strikes" says when the
window closes and not what opens it: the Casket is her relic, and it
strikes whenever she applies a debuff to an enemy, which she does on her
own turn after playing the card. The face becomes "This turn, whenever the
Tamakushi Casket strikes, gain 3 more Block", and a Casket keyword tip rides
every face that names it. Hygiene, `EB-625`, applied.

**Seen in the log, not in the notes.** The mod's own self-check reported
seven Power descriptions carrying a `[blue]` tag the game's renderer does
not know (Arlecchino's Masque among them, which [USER] held), so their
numbers may render with raw tags. `EB-626`, a defect, minted.

## 3. What the run did not test

The act-1 boss's outcome is not in the notes; act 2; the tempo shelf (Tide
Chart, Ripple) under a deck that reaches it. Nothing here is a strength
reading.

## 4. What the loop question is, in one paragraph

Every character in the base game has free turns, and on a free turn every
character sets up. Kokomi's setup is her whole engine, and her engine has
no cap and no cost past the card's own, so a free turn is not "set up
something" but "write everything you hold", and the next turn pays it all
out in the order written. Two things could put the question back: a limit
on how much the Bake-Kurage carries out in one turn, so that writing more
than it can carry is a sequencing choice and a hold; or a choice at the
carry-out, so that the player decides each turn which Plan lands. The
seats have already read the Plan badge's number as a capacity three times
(`EB-330`, `EB-563`), which is a sign the first shape is the one a player
expects.

## 5. Pick

**Pick 1 — the carry-out.** A rule change to the loop, so [USER] plays it
once it is built and the seats have read it.

1. **(default)** The Bake-Kurage carries out **up to two Plans** each turn,
   in the order written; the rest wait, in order, for the next turn.
   Nereid's Ascension doubles the two it carries out. The Plan badge prints
   "2 of 5" so the queue is visible. Writing a third Plan on a free turn is
   a real choice (it lands a turn later, and its order matters), a
   telegraphed attack turn still asks now-or-later, and Tide Wall and Tide
   Chart keep counting carry-outs. The cost is pace: a four-Plan deck pays
   out over two turns. One number (the two) is the sim's to tune.
2. The player **chooses one Plan** to carry out at the start of each turn;
   the others wait. The sharpest puzzle and the slowest engine: one payout
   a turn, a prompt every turn, and every count-reader changes meaning.
3. Hold the loop as it is and read again after the next seat rounds and
   [USER]'s next run; the seats did not name the problem.

## 6. Defaults applied (D and E), disclosed

- **`EB-623`** "Morning" retired from every printed surface (E).
- **`EB-624`** Undertow in the base game's conditional shape, both numbers
  folded (D).
- **`EB-625`** Shell Guard's window stated as the turn it is, and a Casket
  tip on every face that names the relic (E).
- **`EB-626`** the `[blue]` self-check defect, minted, not yet built (E).
- No shipped-sheet number moves; no stamp moves; nothing measured.
