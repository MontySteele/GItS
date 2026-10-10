# Furina: giving Fanfare somewhere to go, 2026-10-10

The Block-card round's open question (`review/records/furina-block-round-2026-10-10.md`):
Fanfare piles up with nothing to spend it on. [USER]'s direction, 2026-10-10:

> "we can make some Spend-payoff Guest Stars Spend a percentage of your current Fanfare instead of
> a flat amount, which encourages stockpiling and spending large amounts. We don't need to print a
> ton of 'Spend X' cards, but we could have Spend act as 'spend up to X' with partial effects, and
> then make the X larger, but keep an eye on the size of the payoff, since more frequent Spend might
> act as a buff if she was previously not Spending all Fanfare."

Numbers below come from the census (`scratchpad/spend-census.md`, 71 quoted cash-outs over six
seat rounds, mixed builds).

## What the seats show

- **Fanfare in hand mid-fight is 12 to 45**, and it peaked unspent at 57, 59 and 81 when seats died.
  28 fights record Fanfare stranded.
- **Fixed Spends are small.** There are 11, at a median of 4 (range 3 to 6). One Spend 4 barely
  dents a 30 bank.
- **Only 5 cards Spend all**, and one is the starter Rising Applause. A spend-all cash-out has a
  median of 24 and a maximum of 76.
- **The seats name one cause:** the spenders are not drawn. "The kit's payoff is a draw lottery"
  (furina-line-r3 L1). "Fanfare 81 felt pointless" (furina-block-r1 L5). Two seats were happy with
  the bank because Applause was always there for lethal.
- **Conversion rates now:** Rising Applause and Standing Ovation pay 1 damage per point. Bravura and
  Let the People Rejoice pay 2. Fixed Spends pay 1 to 2.75 per point (Quick Flourish: Spend 4 for
  11).

## The rule: Spend up to X

**"Spend up to X"** spends X Fanfare, or all you have if that is less. It never fails, and the card
says what each point buys. It counts as a Spend (for Thunderous Applause, Crescendo and Chevreuse)
only if at least 1 Fanfare was spent. It is not a spend-all, so Bis! and Standing Room Only ignore
it. Navia's discount makes the first 2 points of your first Spend each turn free.

Fixed "Spend N" stays on the cards where a threshold is the point: Quick Flourish, Encore!, Sold
Out, Interval Bell, Bubble Aria, Commanding Gaze and Showstopper. The seats liked Quick Flourish as a
sink, so it stays.

**Sizing.** Every up-to card pays **1 per point**: Rising Applause's rate, and below the 2 of
Bravura and Rejoice. So the best use of a big bank is still a spend-all, and stockpiling keeps its
payoff. What is new is that a card that only *topped up* now drains a real share of the bank, so
less of it is wasted.

## The cards (base, upgraded in brackets)

| Card | Now | Proposed |
|---|---|---|
| Tidal Flourish (U, Attack 1) | Deal 5 Hydro to ALL. Spend 6: 12 instead. [8 / 13] | Deal 5 [8] Hydro damage to ALL enemies. Spend up to 10: deal 1 more for each. (max 15 [18]) |
| Spirited Aria (C, Attack 1) | Deal 8. Spend 5: 13 and draw 2. [11 / 14] | Deal 8 [11] damage. Spend up to 8: deal 1 more for each. Draw 1 for every 4 spent. (max 16 and draw 2) |
| Crashing Waves (C, Attack 1) | 4 Hydro twice. Spend 4: three times. [5] | Deal 4 [5] Hydro damage twice. Spend up to 12: hit once more for every 4. (max 5 hits) |
| Hold the Stage (U, Skill 1) | 6 Block. Spend 6: 16. [8 / 18] | Gain 6 [8] Block. Spend up to 12: gain 1 more for each. (max 18 [20]) |

Tidal Flourish and Hold the Stage get a little *worse* at the old 6 (11 and 12 against 12 and 16)
and better past it. Spirited Aria is level at 5 (13, draw 1 where it drew 2) and better past it.

**Two guests Spend a share of the bank** each time they act. A guest acts every turn, so this is a
sink that does not depend on the draw.

| Guest | Now | Proposed |
|---|---|---|
| Navia (Rare) | Line: your first Spend each turn costs 2 [3] less. Act: Geo damage equal to the Fanfare spent this turn. | Line unchanged. **Act: Spend half your Fanfare (rounded down). Deal that much Geo damage to a random enemy.** |
| Freminet (Uncommon) | Line: gain Block equal to every Drain. Act: 5 [8] Cryo to a random enemy, gain 6 [9] Block. | Line unchanged. **Act: Gain 3 [6] Block. Spend half your Fanfare (rounded down): gain that much more Block.** |

**Why half, and why the payoff is bounded.** Once a guest Spends half the bank each turn, the bank
settles where her income equals the Spend. The act then pays about what she earned that turn, around
8 for a typical turn, which is in line with other acts (4 to 8). A big bank pays once, then it is
gone. Half also empties the bank fast enough that it never reaches 81. Navia and Freminet together
split the same bank, oldest first. Showstopper makes them act twice, so each takes half again.

## What this risks

- **It is a buff.** Today 12 to 45 Fanfare is wasted in hard fights. At 1 per point, 10 to 30 more
  damage or Block reaches the board in a fight where she holds the cards. She has 3 wins in 8 on the
  quarter line, against 0 in 5 for the base five, so she may overshoot. The caps (10, 8, 12, 12) are
  the dial: if the round reads high, they come down first.
- **Thunderous Applause fires more often** (3 to ALL per Spend). It is one Uncommon Power. Watch it;
  no change now.
- **Stockpiling can lose to the guests.** With Navia or Freminet on stage, the bank halves every
  turn, so a big Bravura needs the spender drawn the same turn. That is the trade [USER] named: big
  Spends from a big bank, but the bank does not wait forever.

## How it is tested

Two steps, each read on its own, like the line and the Block cards were:
1. The four up-to cards plus the two guests, on the same five seeds (four Furina, one Ironclad
   control), compared with `furina-block-round-2026-10-10.md`. That record asks two things: does
   unspent Fanfare at death drop below about 20, and does her win rate move past about half?
2. [USER]'s own Furina run. "Spend up to X" is a keyword rule change, so it ships after his play.

## Picks

1. **The rule: "Spend up to X" at 1 per point, on the four cards above.** Fixed Spends stay
   elsewhere. **Default: yes.**
   - Alternative: also convert Quick Flourish (Spend up to 8: 2 damage for each, max 16).
2. **The guests: Navia and Freminet Spend half the bank when they act.** **Default: yes, both.**
   - Alternative (a): Navia only.
   - Alternative (b): a quarter, not half. This keeps more bank for spend-all cards but drains the
     81-type pile more slowly.
3. **Overshoot response.** **Default:** if the round reads clearly stronger than the Block round,
   lower the four caps by a third before touching the guests.
4. **Overnight.** **Default:** build picks 1 to 3 at their defaults tonight. Run the Furina round
   (four seeds plus the control), then the Varka payoff round (`varka-payoff-fix-2026-10-08.md`, the
   offers round's five seeds with offers logged). Both records ready in the morning.
