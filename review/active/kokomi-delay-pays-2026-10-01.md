# Kokomi: a Plan stays open (2026-10-01)

**Ruled 2026-10-01.** [USER]: "Interesting idea! Yes, I think this makes
sense. We'd want to make sure that the UX is reasonably snappy so players
don't have to spend forever on their turns, but it sounds doable." So: a Plan
stays open until it is carried out (§2), with the one-screen chooser in §3.
The first draft's shield (2 Block per Energy paid for waiting Plans) is
withdrawn. [USER] on it: "just giving Kokomi 2 block per plan is patching a
structural problem with a numbers crutch... it does not feel very elegant."
Open the Casket keeps its Exhaust.

[USER], earlier the same day: "that's the recurring challenge of Kokomi - we
have an interesting idea, but how do we make it 'worth' it without just
making the numbers OP."

## 1. What the seats say

Four Sonnet seats on her 78-card build on 2026-10-01: two on the 0.2.4112 pool
and two on 0.2.4162 (status batch, "Or plan:", Riptide Ruin). **All four died to
the act-1 boss.** On the same builds and the same seat type, every other run
cleared act 1: base Ironclad, base Silent, three Varka lanes and two Furina
lanes. Records: `review/records/kokomi-pool-round-2026-10-01.md`,
`review/records/base-sonnet-baseline-2026-10-01.md`; the 0.2.4162 pair is in
the session scratchpad (`w9-lane1/`, `w9-lane2/`) until its record lands.
Earlier builds did reach later acts (`kokomi-feed-round-2026-09-29.md`), so
this does not show that Plan cannot work. It does make early survival the
priority.

- **Plans never answer the attack she is facing.** "Plans land at the start of
  the next turn, so they never answer the attack I am facing ... most turns
  were 'plan, then spend the rest on Strike or Defend'," with about 10 HP lost
  per fight.
- **The Matriarch's Dexterity −4** took a deck of flat 5 to 6 Block cards to "1
  Block, Oath 2 and Barbara 2."

**The structural reading.** A Plan commits to its effect when she knows least:
before the next intent and the next hand. A Block Plan is a guess, so seats plan
damage and defend with flat Block. Damage Plans are not safe either: Soul Fysh's
Intangible turn voided two of them (the 0.2.4112 record). The delay charges a
draw, Energy, a turn of lag and uncertainty, and pays back only in size.

GPT's review (2026-10-01) corrected three claims in the first draft:
- her starter holds only two Plan cards, so a per-Energy shield would have
  helped the expensive late decks more than the dying early ones;
- Kurage Canopy's Power Block already goes through Dexterity and Frail
  (`KokomiExpansion.cs:228`), so "the jellyfish's Block" was not exempt by
  calling it that;
- damage Plans can be wasted too.

## 2. The rule: a Plan stays open

> When the Bake-Kurage carries out a Plan, you choose which line it is: its
> **Plan** line, or its **now** line.

- **Kurage's Oath, planned,** lands next turn as either "Gain 6 Block" or "Deal
  7 damage to ALL enemies," chosen after the new intents and the new hand are
  showing.
- **Defence stops being a guess.** Block chosen at the start of her turn covers
  that turn's enemy attack, with full information.
- **The Intangible turn stops voiding Plans:** take the Block line instead.
- **The head start buys information.** This is the brief's rule ("the Plan line
  buys something only a head start can buy"), applied by the kit as a whole
  rather than by a few intent-reading cards that must be drawn.
- **No number changes.** It is a power increase, and GPT is right to call it
  one: flexibility bought by waiting, which is her identity. She still pays
  Energy a turn early, a draw, and turn 1 with nothing landing.

**Which Plans it touches.**
- **Two-line cards** (a now line and a Plan line): the choice applies.
- **Plan-only cards** (Nip, Bubble Ward, Brine Sting and the rest) have nothing
  to choose; they carry out as today.
- **Dusk Plans** carry out at the end of her turn, before the enemy acts. They
  already answer the turn they are written, so they are left as they are.
- **Carry-out effects that copy or double a Plan** (Second Wave, Nereid's
  Ascension, Change of Plans, Spring Tide, Moon's Reflection) carry out the line
  she chooses. Each copy offers the same choice; the default is the line chosen
  for the first.
- **Plan payoffs** (the Casket, Sango Isshin, Feint, Kurage Canopy) count a Plan
  carried out either way. The Casket's count does not depend on which line.
- **The now line is printed size,** not Plan size; the Plan line keeps its
  premium.

## 3. Keeping the turn snappy

[USER]'s condition. The chooser is one screen per turn, not one per Plan:

- **It appears only if a two-line Plan is due.** Turns with only Plan-only or
  Dusk Plans show nothing new.
- **Every open Plan is listed with its Plan line already selected.** One click
  confirms, so a player who wants the default spends one click a turn.
- **Clicking a Plan flips it** to its now line, and clicking again flips it
  back. The forecast numbers update as you flip.
- **The bridge gets one verb:** `flip "<card>"` then `confirm`, or `confirm`
  alone.
- **The Plan strip shows both lines** while a Plan waits, so the choice is
  readable a turn early.

## 4. What the round records

GPT's list, adopted: how often each line is chosen; damage the chosen Block
prevented; whether a now line was ever the better choice; and, for every death,
whether defensive cards were missing, declined or misplayed. A central rule
changed, so two seats, then [USER] plays.

## 5. Considered and set aside

- **The shield** (2 Block per Energy paid for waiting Plans): withdrawn as a
  numbers crutch (above).
- **More intent-reading Plans** (Tide Wall, Flank): still good cards, but a
  batch needs the right draw. The rule makes every two-line card adaptive.
- **Open the Casket without Exhaust:** permanent Strength for every Plan she
  ever carried out; one variable at a time. Re-read after this round.
