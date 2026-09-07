Status: RULED R265 2026-09-07

# Kokomi, [USER]'s first act-1 run under the overhaul: better than before, the central loop reads as auto-pilot

Written 2026-09-07. [USER] played Kokomi's act 1 on `0.2.2888+proto` (main
`da0e5846`: the Plan kit of R240 and R241, the six now-lines and the aimed
Plan of R250, the tempo shelf of R253, the fixer-T faces of #413). This is
the first read of the kit's rules by [USER] since the R250 rulings, and the
Prototype stage is graded on it. Evidence: [USER]'s notes, quoted in the
commit that carries this packet, and the run's `godot.log`: Ascension 3,
seed `1EQL0MZ0USJN`; the picks Gorou, Arlecchino — Masque of the Red Death,
Vanguard, Nereid's Ascension, Song of Pearls, Mizuki; Mango and Strawberry;
the death to the Terror Eel, the act-1 elite.

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

**Shell Guard sounds wrong, and the Casket is unexplained.** Half right.
The Casket is her relic: whenever she applies a debuff to an enemy it deals
2 Hydro damage to that enemy, and nothing on the screen said so. A Casket
keyword tip now rides every face that names it (`EB-625`, applied). The
window, though, is real and the face keeps "Until your next turn": R246
pick 2 rules that the next turn's Plans applying Weak strike the Casket
before the enemy swings, and both engines close the window one line after
the carry-out to make that true, so the strikes do come after the turn the
card was played on. "This turn" would have printed a smaller window than
the rule has.

**Seen in the log, not in the notes.** The mod's own self-check reported
seven Power descriptions carrying a `[blue]` tag it did not know
(Arlecchino's Masque among them). The build read found the checker wrong
and the strings right: `[blue]` is the base game's own numeral tag in
power and relic text, eighty-three of the mod's powers print it, and the
check's tag list simply lacked it. One entry added, a headless test now
runs the same check over every power, nothing any power says moved
(`EB-626`).

## 3. What the run did not test

The act-1 boss (the run ended at the Terror Eel elite, at Ascension 3);
act 2; the tempo shelf (Tide Chart, Ripple) under a deck that reaches it. Nothing here is a strength
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

## 4b. Three turns from the actual pool, under a carry-out of two

GPT's review of 2026-09-07 asked for these before the rule builds, and it
is the right ask: a queue that only delays rewards is not a decision. The
numbers are the pool's (`docs/prototype-surface.yaml`): Kurage's Oath 1,
deal 3 to ALL, Plan 7 to ALL; Undertow 1, deal 7, or 10 on a debuffed
enemy; Vanguard 0, Exhaust, 1 Vulnerable, Plan 1 Vulnerable and 1 Weak;
Ripple 0, 2 Block, Plan 1 Energy and 4 Block; Coral Bulwark 1, 6 Block,
Plan 8 Block and 1 Weak; Tide Wall 1, 4 Block, Plan 3 Block per Plan
carried out with it; Battle Plan 1, draw 1, Plan 1 Energy and draw 2. The
Casket strikes for 2 on each debuff she applies.

**A safe turn where playing now is right.** The enemy is buffing; one
enemy at 12 HP; hand Oath, Undertow, Vanguard, Ripple, Battle Plan; three
Energy. Oath and Battle Plan are written (7 to ALL, and Energy plus two
cards, next turn); the queue is full. Vanguard's Plan would land the turn
after next, so it is played now instead: 1 Vulnerable, the Casket's 2,
and Undertow's 10 becomes 15, which kills. Under today's rule Vanguard is
written as well, for free, and playing it now is the worse line; under
the cap the immediate play is the good one.

**A dangerous turn where committing is still right.** The enemy attacks
for 14; hand Coral Bulwark, Tide Wall, Ripple, Oath, Undertow; three
Energy. Everything now is 6 + 4 + 2 = 12 Block, two short, and nothing
lands next turn. The other line takes 6: Bulwark now (6 Block) and Ripple
now (2), Oath and Tide Wall written, so next turn opens with 7 to ALL and
Tide Wall's 6 Block before the draw. Six HP for a morning that clears the
hallway and blocks the follow-up is the brief's decision, and the cap does
not remove it.

**A congested queue where the priority changes which card.** Oath is
already written from last turn, so one slot is open; hand Battle Plan,
Ripple, Coral Bulwark, Undertow; the enemy's next intent is an attack for
9. Under today's rule all three Plans are written. Under the cap one is:
Bulwark's Plan (8 Block and Weak, covering the 9 and shrinking the next
swing) if the attack is real, Battle Plan's (Energy and two cards) if the
intent were a buff, Ripple's only if Energy next turn is the constraint.
That is a choice of which, not of order, and it is decided by the intent
line, which is where the brief wanted the price to come from.

**How the player knows when a delayed Plan lands.** The queue is drawn on
the Bake-Kurage in order (the Plan strip), and under the cap each entry
carries its turn: "next turn" on the first two, "in 2 turns" after. The
badge prints "2 of 3". A defensive Plan past the cap is therefore written
knowing it lands a turn late, which is the point.

**What the examples do not settle, and where two of them are wrong.**
GPT's second reading (2026-09-07, evening) corrects two of the three, and
it is right both times. The safe turn: Vanguard into Undertow kills now
under today's rule as well, so that example shows an existing reason to
act now, not one the cap creates. The congested queue: the cap does not
stop the other Plans being written, it delays them, so "one is written"
overstates it; the honest question is whether committing a card to land
in two turns is worse than its now-line or than letting it discard, and
for Ripple's 2 Block it usually is not. Only the dangerous turn stands as
written. So the examples show the decision can exist; they do not show
the cap makes it common, and §7 says what would.

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
   out over two turns. One number (the two) is the sim's to tune. §4b
   shows the three turns; the seat round on the built rule is what says
   whether the choice is met often enough (GPT review 2026-09-07).
2. The player **chooses one Plan** to carry out at the start of each turn;
   the others wait. The sharpest puzzle and the slowest engine: one payout
   a turn, a prompt every turn, and every count-reader changes meaning.
3. Hold the loop as it is and read again after the next seat rounds and
   [USER]'s next run; the seats did not name the problem.

## 7. What Plan is for, and the paths (2026-09-07, evening)

[USER]'s question after the run: is there enough richness and depth
around Plan to make it a design, rather than a one-note "play cards next
turn" loop. GPT's review says keep Plan, and it names the test: does
preparation change the value of the decisions that follow it, the way a
Bomb changes which enemy Klee aims at, whether she waits, and what she
drafts. That is the right test, and by it the current pool is narrow: of
Kokomi's 40 rows, 21 carry a Plan line and nearly all of them are the same
question at a different number, with the brief's own payoff ("three Plans
land at once"), its two readers (Treatise, Song of Pearls) and its Rare
(Nereid's) all pointing the same way: prepare more, collect more.

**What is already there and under-used.** Battle Plan prepares Energy and
draw; Exposed Flank and Slack Water prepare debuffs for ALL; Change of
Plans carries out the first Plan now; Tide Chart reads the count; Moon's
Reflection re-plans an exhausted card. Those are four different uses of
preparation (resources, position, timing, recursion), and the round
records show them drafted as "more Plan", not as different plans.

**Four ways to give the queue a second question, mine.** Each is a pool
change or a small rule, each answers a different half of the complaint,
and none needs the cap.

1. **Order matters: riders that touch the next Plan.** "Plan: 2
   Vulnerable to ALL; the next Plan's damage is doubled." "Plan: the next
   Plan carries out twice." "Plan: gain 6 Block; the next Plan's Block is
   kept through the enemy's turn." With two or three of these in a deck,
   writing on a free turn is a sequencing puzzle in the sense [USER]
   asked for: the order written is the order carried out, and the riders
   make it pay differently. No rule changes.
2. **The queue is a resource to spend, not only to wait on.** Change of
   Plans accelerates; add the other verbs. Cash: "Exhaust. Cancel your
   last Plan; its card returns to your hand and you gain its cost."
   Convert: "Gain 1 Energy for each Plan queued; they still carry out."
   Redirect: "Aim every queued Attack Plan at one enemy." This is the
   Bomb's hold-or-cash tension on the jellyfish, and it is what makes
   "something committed" a reason to do something else this turn.
3. **Timing agency: two moments to land.** Today every Plan lands at the
   start of next turn, after the enemy has hit, which is why a Block Plan
   reads as "for the turn after". Give some Plans a dusk line, carried
   out at the end of this turn before the enemy acts, at a smaller number
   than the dawn line. A defensive Plan then asks "cover this hit for
   less, or the next for more", which is the preparation under
   uncertainty GPT asks for, in one keyword variant rather than a new
   system. If a second word is too many, the narrower form is "Block from
   a Plan is kept through the enemy's turn", which makes dawn Block worth
   writing under an attack.
4. **The queue can be shaken.** Unblocked damage above a threshold on the
   enemy's turn loses the last Plan written. This is what makes dumping
   the hand a bet rather than a habit: on an off-turn it is safe, and
   should be, since free turns are allowed obvious plays; under a
   telegraphed attack it is exposure. It is a rule change to the loop and
   the most invasive of the four; the brief's "enemies cannot touch the
   jellyfish" stands, since it is Kokomi who is hit.

**On the two-Plan cap.** It is a candidate, not the fix. GPT is right
that a fixed allowance is a choice about what Kokomi becomes (fewer,
larger entries; decks of many small Plans pushed out) and that the
examples in §4b were built around the rule. It stays as one lane of the
next round, not as the rule.

**The path.** Pool pass two for Kokomi, authored by Claude through the
audit door: six to eight rows on paths 1 and 2 (two "next Plan" riders on
existing Common shapes, one "carries out twice" Common, the cash card,
the convert card, the redirect card), and the dusk/dawn variant on two
Block Plans as a trial of path 3. Then one round on four lanes: the three
decks GPT's table names (steady defence, concentrated attack,
mostly-immediate with selective Plans) assembled, plus a natural lane,
with the cap on in one assembled lane only. The reads: do the three decks
want different rewards; is a Plan cancelled, converted or accelerated on
purpose; does the order written change on a free turn; does the natural
lane reach any of it. Path 4 waits on that round. The stage holds at
Prototype through it.

## 8. Pick, revised

**Pick 1, the carry-out and the queue** (replaces the pick in §5).

1. **(default)** Pool first: pass two on paths 1 and 2, the dusk/dawn
   trial on two Block Plans, the cap as one lane of the round; the rule
   decided on the round's reads. Nothing in the loop changes before the
   round, so nothing is played by [USER] before it.
2. The two-Plan cap as the rule now, and the pool pass after it.
3. Path 4 (the shaken queue) as the rule now, with pass two.
4. Pivot: Plan stays a supporting mechanic and something else carries the
   character. GPT's own third choice, and only if the round collapses
   into "queue the best values, collect, repeat".

## 6. Defaults applied (D and E), disclosed

- **`EB-623`** "Morning" retired from every printed surface (E).
- **`EB-624`** Undertow in the base game's conditional shape, both numbers
  folded (D).
- **`EB-625`** a Casket tip on every face that names the relic; the face's
  window stands, being the rule's (E).
- **`EB-626`** the self-check's tag list corrected; no power text moved (E).
- No shipped-sheet number moves; no stamp moves; nothing measured.

## 9. Ruled (R265, 2026-09-07)

Pick 1 of §8 at its default, pool first. Pool pass two on paths 1 and 2 of
§7 (order riders, the queue as a resource), the dusk/dawn trial on two Block
Plans, the two-Plan cap as one lane of the next round, and the rule decided
on that round's reads; nothing in the loop changes before it, so nothing is
played by [USER] before it. Built under `EB-643`. The cap of §5 is not the
rule.
