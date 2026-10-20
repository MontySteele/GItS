# Furina: making her HP legible, 2026-10-19

Furina is at Balance. This pass changes what the screen says, not any number
or rule. STATE's Furina "Next" asks for three things: which HP comes back
after the fight, which Drain stays a cost, and why Repay gives Block below
full HP. Tonight's UI check (`review/records/furina-ui-check-2026-10-19.md`,
two seats, release build) shows where the screen fails at each.

## What the screen does now

- **The Drained counter** above the Fanfare gauge shows the HP drained. Its
  hover gives the buffer left, the rule ("Drain inside it returns after
  combat; past it, only Repay returns") and the part past her line
  (`Vfx/Prototype/DrainedCounter.cs`).
- **A card in hand** is tagged "(Past your Drain buffer)" only when its Drain
  would go past the line (`FurinaStageBowPreview.cs`). A Drain inside the
  buffer carries no tag.
- **The refund** is announced after the fight ("Drained 22 HP returned").

## What both seats missed

1. **What comes back.** Nothing shows the after-combat refund before the
   fight ends. Lane 2 read "you would be at 0/85" on a turn it would have
   survived 22 HP higher, and played two fights more cautiously than it had
   to.
2. **What a card costs.** A Drain inside the buffer carries no tag, so the
   seats could not tell a refunded Drain from a real cost until after
   paying. Only Grand Deluge and Coup de Théâtre were ever tagged.
3. **The turn's total.** Guests and powers Drain at the end or start of a
   turn (Lyney 2, Regina 3), and no total shows before End Turn.
4. **Facade.** "Gain Block equal to the HP you have lost this combat, up to
   12" counts every HP lost, Drains included, and is card Block, so Frail
   cuts it (`FurinaStageCards.Facade`). The seat saw 3, then 12, and could
   not say why.
5. **Fanfare's source.** "For each HP you lose or Repay" does not say a Drain
   counts as HP lost; lane 1 found out by watching.

Seat-page only (no player change): the "HP A -> B" line nets Drain against
Repay and start-of-turn drains. That is a bridge fix and needs no pick.

## The changes

1. **A returning segment on her HP bar.** The HP that will come back after
   combat shows as a pale segment beyond her current HP, the way the base
   game's bar shows Block over HP. The Drained counter's hover gains one line:
   "Returns after combat: N". With A Five-Century Act, past-line Drain counts
   too.
2. **Every Drain card says where its Drain lands.** In combat, a card that
   Drains carries one tag:
   - "(Returns after combat)" if it stays inside the buffer;
   - "(Past your line: lost unless you Repay)" if it all goes past;
   - "(N returns, M past your line)" if it splits.

   These replace today's "(Past your Drain buffer)".
3. **The turn's coming drains.** The Drained counter's hover gains "At end of
   turn: guests Drain N" and "Next turn: Regina Drains 3", when they apply.
4. **Facade shows its count.** In combat its face adds "(Lost this combat:
   N)". The text becomes "Gain Block equal to the HP you have lost this
   combat, Drain included, up to 12."
5. **Fanfare's tip** becomes "Gain 1 for each HP you lose (Drain included)
   or Repay."

None of these moves a number, so they can land on `main` under the Balance
freeze (text-only fixes are allowed there).

**Repay's Block** is the third question in STATE. Neither seat was confused
by it. Hymn+ and Pneuma "sometimes just gave Block", and the Repay keyword
tip already says "HP a Repay cannot return becomes Block". Change 1 covers
the rest: with the returning segment on the bar, the player sees there is
nothing left to repay.

## Picks

Ruled 2026-10-19, all (a): [USER], "Otherwise agreed on the defaults." On
the starter: "I keep coming back to how her starter card drains the whole
bank. I really can't tell if this is a problem or not." Left as it is for
now; the build adds one telemetry field, a Rising Applause Spend made while
another Spend card is in hand, so the next Furina round can say whether it
drains banks a payoff would have used.

1. **The returning HP.**
   - **(a, default)** A segment on the HP bar plus the hover line.
   - (b) The hover line only (cheaper; the number is one hover away).
2. **The Drain tags (change 2).**
   - **(a, default)** Every Drain card tagged, three forms.
   - (b) Tag only the past-line case, as now, plus the hover total.
3. **Her starter, Rising Applause** ("Gain 5 Block. Spend all your Fanfare
   and deal that much Hydro damage"). It made 117 of 268 Spends
   (`furina-next-2-2026-10-16.md`); this pass was where the question came
   back.
   - **(a, default)** Leave it. Starter cards stay plain, and the pool's Spend
     cards (Bravura, Bring the House Down) now cap and compete.
   - (b) Cap it: "Spend up to 15 Fanfare", so big banks go to the pool's
     payoffs. That is a starter change, so a suite run follows.
