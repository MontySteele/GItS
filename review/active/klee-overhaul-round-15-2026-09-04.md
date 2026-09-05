Status: OPEN (no pick; the defaults in §4 are applied)

# Klee round fifteen, targeted: Stoke the Fuse played five times, and a hedge that cost HP

Written 2026-09-04. One blind Opus seat played the Bomb kit on
`0.2.2577+proto` (rows on `docs/prototype-surface.yaml`) with **Countdown
and Stoke the Fuse granted into the starting deck** (`embark --arm`), the
targeted form the GPT review of 2026-09-04 asked for after six runs drew
neither. The dev grant makes the deck one no generator produced; nothing
here is comparable to another run, and nothing measured. Record:
`review/qa/klee-round-15-2026-09-04/opus-act1.md`. Prototype stage,
Guardrail-7. No pick.

## 1. The run in one paragraph

Seed `Y19ZL7Y606A8`, Ascension 0. Five fights, five won, including the
Skulking Colony elite and a five-turn Haunted Ship; 120 of 120 at the cap
on a map screen, 17 of 62 HP, 190 gold, a 20-card deck. No refusals, no
stalls.

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

**Catalytic Converter: one Spark in five fights**, dead by its own printed
admission in three. A reaction-keyed card in a mono-Pyro deck, `EB-428`'s
family; carried to the pool pass with the Klee r12 reading.

**What read true.** Faces rewrite under Weak and Frail; the Reaction
preview appears on detonators when an aura is live; stacks print their
parts (`12 / 3, including 1 Mine`, `EB-450`); Barbara's face warns that her
play consumes an aura with no hit to multiply. By fight 4 the seat
predicted a 45-damage turn exactly.

## 3. What the round did not test

Grounded with Sparks 'n' Splash (run 2 of this round, in flight); Quick
Fuse; the boss. One run on a granted deck. Nothing here is a strength
reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-461`, `EB-447` reopened** with this seat's evidence beside the
  Kokomi seat's.
- **Countdown and Stoke the Fuse stay in the pool** as built; the targeted
  run answers the audit's question about Stoke and leaves Countdown as a
  filler Common, which the pool pass weighs.
