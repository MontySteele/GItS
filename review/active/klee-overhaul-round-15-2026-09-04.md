Status: OPEN (no pick; the defaults in §4 are applied)

# Klee round fifteen, targeted: Stoke the Fuse played five times, Sparks 'n' Splash never, and a hedge that cost HP

Written 2026-09-04. Two blind Opus seats played the Bomb kit on
`0.2.2577+proto` (rows on `docs/prototype-surface.yaml`): run 1 with
**Countdown and Stoke the Fuse granted into the starting deck**
(`embark --arm`), run 2 with **Grounded and Sparks 'n' Splash granted**, the
targeted forms the GPT review of 2026-09-04 asked for (six runs had drawn
neither of the first pair; the review wanted the second pair watched). The dev grant makes the deck one no generator produced; nothing
here is comparable to another run, and nothing measured. Record:
`review/qa/klee-round-15-2026-09-04/opus-act1.md` and `opus-run2-act1.md`.
Prototype stage, Guardrail-7. No pick.

## 1. The run in one paragraph

Run 1 (seed `Y19ZL7Y606A8`, Ascension 0): five fights, five won,
including the Skulking Colony elite and a five-turn Haunted Ship; 120 of
120 at the cap on a map screen, 17 of 62 HP, 190 gold, a 20-card deck. Run
2 (seed `XEN2USFZBJZ1`, Ascension 1): six fights, six won, the Bygone
Effigy elite killed at 2 HP on a pre-computed five-card lethal; stopped at
117 of 120 above the second elite, 2 of 62 HP. No refusals, no stalls.

## 2. What the round found

**Stoke the Fuse is a real card with a real ordering rule.** Played five
times, always before the detonator: "Stoke must come before the detonator,
because after the detonator there is no bomb left to grow. Nothing on
either card says so; you have to work it out." Fight 1's 27-HP slug fell to
Stoke (12 to 18) then Countdown's +3 then Ka-pow!; fight 2's kill cost one
energy for the whole line; the elite's turn 4 took a Bomb 4 to 19 on five
Sparks. Once it was discarded unplayed with no Bomb on the board. The
audit's C3 concern (value follows the Bomb) reads as intended: the card is
nothing without a placer and everything with one.

**Sparks 'n' Splash is a dead card in its own deck.** In hand in four
fights of run 2, played zero times, correctly each time: it needs a Bomb
alive at the end of the turn, and every other card in the kit wants that
Bomb set off now; with no Bomb on the field it is two energy for nothing.
Grounded, played turn 2 of fight 1 as a compounding Power, states the same
anti-synergy on its face ("if none of your Bombs went off last turn"). The
GPT review's hypothesis, that the pair makes waiting the best damage,
defence and resource plan, did not reach the table: the seat never found
a turn where waiting was right. A reading for the pool pass: the Rare
Power asks for a board the kit is built to empty.

**Countdown is quiet.** Played once for its +3 into a Set off; rejected
once as "draw 1 with no energy"; otherwise carried. A Common Skill that
does what it says and rarely changes a turn. Not a defect; a reading for
the pool pass.

**The intent hedge cost HP, a second seat.** `EB-461`'s label ("the damage
part of a multi-part telegraph has repeatedly not landed") was wrong both
times it mattered: the Sludge Spinner's 8 and the Haunted Ship's five
Status cards landed in full. The Kokomi seat of the same round met three
such telegraphs and all three landed. `EB-461` is reopened with neutral
wording and a request to the bridge mod for the resolving part.

**The map's deck list is not the deck.** It listed Dazed ×5 (combat-only)
and dropped Catalytic Converter after it was played as a Power, errors in
both directions on the screen used for drafting (`EB-447` reopened).

**"Hold or fire" needs something that Retains.** With Ka-pow! not drawn
until fight 1's third turn and the drafted detonators (Perfect Timing,
Fwoosh!, Stoke) discarding at end of turn, "hold the Bomb" meant "throw the
detonator away" for most of the run; a 55-gold event enchantment (Steady on
Perfect Timing) "opened more decision-space than any card I drafted". Round
14 read the same choice as the kit's spine because Ka-pow! was in hand from
turn 2. Design reading for the pool pass: the Retain density of detonators
decides whether the spine exists, and Ka-pow! is one card.

**The elite inverted the kit, and that was good.** Hardened Shell's 20 per
turn turned the deck from burst into "source the 20 from 0-cost cards and
put all energy into Block"; the seat called the coherent second mode a real
strength, and the counter counting down to 0 useful (contrast the Kokomi
seat, `EB-467`).

**Run 2's legibility rows.** Lisa's "apply 1 Vulnerable" fires at the end
of your turn and falls off at the end of the enemy's, so no player card
ever sees it and a 74-gold card's second clause is invisible (`EB-470`); a
Mine fires at its base size before the growth tick and nothing says so
(`EB-471`); Superconduct's Vulnerable lands before the triggering hit, a
4-point swing found from HP (`EB-472`); an elite relic never reprinted its text
(`EB-473`). Hexerei was unpriceable a second time: Witches' Circle skipped
twice because no card in the deck printed the word (`EB-444`).

**Catalytic Converter: one Spark in five fights**, dead by its own printed
admission in three. A reaction-keyed card in a mono-Pyro deck, `EB-428`'s
family; carried to the pool pass with the Klee r12 reading.

**What read true.** Faces rewrite under Weak and Frail; the Reaction
preview appears on detonators when an aura is live; stacks print their
parts (`12 / 3, including 1 Mine`, `EB-450`); Barbara's face warns that her
play consumes an aura with no hit to multiply. By fight 4 the seat
predicted a 45-damage turn exactly.

## 3. What the round did not test

Quick Fuse; the boss; Sparks 'n' Splash played (it never was). Two runs
on granted decks. Nothing here is a strength
reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-461`, `EB-447` reopened** with run 1's evidence beside the Kokomi
  seat's; **`EB-470` to `EB-473` minted** from run 2, Lisa's tick moving to the
  start of your turn as a D default.
- **Sparks 'n' Splash and Grounded stay as built**; the reading goes to the
  pool pass, not to a number.
- **Countdown and Stoke the Fuse stay in the pool** as built; the targeted
  run answers the audit's question about Stoke and leaves Countdown as a
  filler Common, which the pool pass weighs.
