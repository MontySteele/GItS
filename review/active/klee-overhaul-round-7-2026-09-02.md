Status: OPEN (round seven, build 0.2.2188+proto: two Opus seats, one run, six fights, dead on floor 9; three picks)

# Klee round seven: what the seats saw on the build with the coven and the stand-ins

Written 2026-09-02, the night the build went in. The build carried R243's
numbers (growth 4, Ka-pow! Retain, the base Strike applying nothing), the
Fable card audit, and the companion layer ruled in R236: Gorou's Personal,
the four coven Personals, four caretaker stand-ins and, one PR behind, the
four Hexerei stand-ins. Two Opus seats played one run on lane 2, blind, in
two sittings: 99 actions to floor 6, then 16 more to a death on floor 9.
Their records are `review/qa/klee-round-7-2026-09-02/opus-act1.md` and
`opus-act1b.md`; every claim below is checkable against a fight in one of
them. The Kokomi seat's round is a separate packet.

## 1. The run in one paragraph

Neow: Arcane Scroll, which handed her Alice's Recipe and never said so. Five
fights won, Sludge Spinner through Fossil Stalker, HP falling 62 to 2 by
floor 6 with no rest site reachable. Five companion offers, all through
Pounding Surprise's fourth slot; the seat drafted Diona's Icy Paws as the
only card in five offers that applied a non-Pyro element. Fight 6, a
Calcified Cultist and a Seapunk, killed her on round 2: the deck's whole
Block output was four Defends and Diona, five plus five plus five plus five
plus six, against 17 incoming.

## 2. What the round found, in the order it matters

**The stand-ins never appeared, and that is a defect, not a draft.** The seat
was handed "Diona — Icy Paws (proto)" as Klee. The ruled structure says Klee
is handed "Diona — Shaken, Not Purred" in its place. The cause is found: the
stand-in rows spell their owner as a one-item list, `personal_pool: [klee]`,
and the C# emitter printed that list's Python spelling, `"['klee']"`, as the
owner, which matches no character, so the hand-off answered "no" at both of
its mouths while the sim, which normalises the spelling, swapped correctly
the whole time. Two engines disagreeing with every test green, because the
C# rule had no headless pin. PR #317 fixed the emitter the same night; the
pin and the live look are `EB-320`. So this round tested none of the
caretaker rows it was built to test, and your run waits for the fix build.

**The reaction layer works the moment a foreign aura exists, and nothing of
Klee's can make one.** Seat one wrote that six of her cards print reaction
riders and none was reachable in five fights. Seat two refuted the
"unreachable" half in one turn: with Diona's Cryo on the Seapunk every Pyro
card in hand grew "Reaction preview: Melt — the triggering hit deals 1.75x
damage", and a 0-cost Ka-pow! took the Seapunk from 44 to 23. What survives
is the sharper form: the layer is gated entirely behind drafting an
off-element companion, and act 1 offered one in five. That is the law as
ruled (the React loop is companion-fed, brief pick 7), and the coven and the
stand-ins are the density answer to it, which is why finding one matters.

**Bank or cash is the kit's real decision, and it reads correctly.** Both
seats named it first: banking won Fight 2 with 28 damage off one Ka-pow!,
cashing at once was right in Fight 3 because Jumpy Dumpty's Mine rider only
fires when the bomb goes off, and the first turn of the first fight already
posed it (Alice's Recipe plus Jumpy Dumpty against Strike-Defend-Defend,
with nothing in hand to set the bomb off). Ka-pow! was both seats' happiest
draw. Alice's Recipe played into an empty board, twice, was the automatic
mistake.

**The badge still does not print what the bomb will hit for.** EB-270 made
the badge one predicted number, and it folds Weak in. It does not fold the
reaction in: "Bomb 10 — Set off here deals 10 Pyro damage" beside "Melt —
1.75x", and the hit dealt 17. Neither screen printed 17. `EB-321`.

**Defend is not the kit.** Both seats, unprompted: four 5-Block Defends
against 11, 12, 15 and 17 are a rounding error, and against Fight 5's Suck 3
a partial block fed the enemy. Half the turns drew the vanilla half of a
16-card deck and presented nothing. R243 ruled the starter four-four-two and
the survival set (Grounded, Run Away!, Sorry, Jean..., Dig In, Mines) the
draft's; the seat saw Sorry, Jean... offered once and took Diona over it.
The new fact for the record is the death: maximum Block two short of the
incoming with the whole survival set undrafted. Taken as an F pick at its
ruled default: the shape stands, and the draft's survival density is what
the next round reads, on a build where the caretakers can actually show up.

**Small things with rows.** Jumpy Dumpty's rider put two Mines on one enemy
off one detonation, `EB-318`. Two of five companion titles print "(proto)"
to the player, `EB-322`. Three purchases were made sight-unseen (an
enchant, a potion and a relic in events, Neow's rare), the buff intent
names no target, and the floor number disagrees with itself, all the blind
page's to print, `EB-323`. A refusal for a random-target Attack named no
working form and cost a potion, `EB-319`.

## 3. What the round did not test

Gorou's Personal is Kokomi's. The four coven Personals (Prune, Sayu, Qiqi,
Yaoyao) share Klee's Personal channel and did not appear in five offers;
three of them have no illustration yet. The Hexerei stand-ins were one PR
behind the build. None of this is a finding against the cards; it is the
round's coverage, and it is why the next round is the one that reads the
companion layer.

## 4. Picks

1. **Your run.** (1) *After the fix build (#317's emitter fix is on main;
   the deploy follows the Kokomi seat), so the run you play is the one with
   the stand-ins in it* [default]. (2) On 0.2.2188+proto now, knowing the
   caretakers cannot appear.
2. **The reaction layer's self-service.** (1) *Stays companion-fed as
   ruled; the fix build's seats read the coven and stand-in offer rate in
   act 1 before anything moves* [default]. (2) Reopen brief pick 7 and give
   Klee one own-kit off-element source, a LAW amendment. The one-line new
   fact, if you take (2): two seats, six fights, one off-element card in
   five offers, and it decided the only fight it appeared in.
3. **The local seat's window** (`EB-324`, the Kokomi run's instrument, not
   Klee's). (1) *A chained-session rule: one thread per act, the sealed
   record and the deck carried forward and declared* [default]. (2) The
   local seat stays an act-and-a-half instrument and the three-act reads
   are Opus's.
