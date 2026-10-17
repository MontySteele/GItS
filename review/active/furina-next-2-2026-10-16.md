# furina-next paper 2, 2026-10-16: spending the bank

Furina is a Balance kit. These changes go on `furina-next`, which keeps
Crescendo, Standing Room Only and Prima Donna from paper 1
(`review/active/furina-next-2026-10-15.md`), and reach `main` only through a
promotion PR with a suite record graded against the predictions below.

**Why.** Suite 2 (`review/records/furina-suite-2-2026-10-16.md`, ruled "do not
promote"): the bank now grows (act 3 production 10.6 a turn, above act 2's
8.8), and it goes unspent. [USER]'s read: "1) not enough ways to spend it big
in act 3 2) too many spenders are "spend all" which you realistically don't
want more than a couple of, and the starter already competes for that role
anyway ... we need to limit the "spend all" effects so they don't brick
everything else (possibly revisit the starter) but come up with other, capped
spender effects that can still scale with powers."

## 1. What the numbers say

Both suites, ten runs, 169 fights (scratch `furina-gap/hand.py`):

- **A big bank usually has nowhere to go.** Of the turns that started with 20
  or more Fanfare, 54 to 59% had no spend-all card in hand, and 37 to 41% had
  no Fanfare spender of any kind.
- **The capped spenders are too small to matter.** In acts 2 and 3 the bank
  held more than the card's limit for 77% to 95% of capped Spends, and the
  average capped Spend was 5 to 7 Fanfare. Spend-all cards made about half
  the Spends (36% in act 3 to 76% in act 1) but used 65% to 88% of the
  Fanfare.
- **One card does half the spending.** Rising Applause made 117 of 268 Spends.
  Of the pool's three other spend-all cards, Let the People Rejoice was taken
  6 times in 11 offers, Bring the House Down 1 in 5, Bravura 0 in 4. The seats
  pass over a second or third spend-all, as you said they would.
- **Fanfare is still in the bank when act 3 fights end.** In fights she won,
  the median left over was 12 in suite 1 and 18 in suite 2.

So your read holds, with one adjustment: decks rarely stack spend-all cards,
because the seats already pass them over. What actually fails is the turn
when the bank is full and only small spenders are in hand.

## 2. The changes

One spend-all in the starter, one in the pool. The other two become capped
spenders whose cap or hit count grows, and a Power raises every cap.

| Card | Today | furina-next |
|---|---|---|
| **Rising Applause** (starter) | Gain 5 Block. Spend all your Fanfare and deal that much Hydro damage. | Unchanged (pick 2). |
| **Let the People Rejoice** (Rare Attack, 2) | Spend all. Deal 2 damage to ALL enemies per point. | Unchanged: the pool's one big act 3 spend. |
| **Bravura** (Uncommon Attack, 1) | Spend all. Deal 7 [9] Hydro damage for every 3 spent. | Spend up to 18, all you can. Deal 7 [9] Hydro damage for every 3 spent. |
| **Bring the House Down** (Rare Attack, 2) | Spend all. Deal that much damage. Each guest acts. | Spend up to 10 for each guest on stage, all you can. Deal that much damage. Each guest acts. |
| **Bis!** → **Extended Run** (Rare Power, 1) | Whenever a card Spends all your Fanfare, keep half of it. (1 of 9 taken) | Attacks and Skills that Spend up to a number can Spend 8 [12] more. |

- **Bravura keeps its damage.** It already hit once per 3 spent, so
  Strength already multiplied across its hits; the cap alone is the change.
  What it gains is the Fanfare left over for the next card, and Extended
  Run's larger cap. (The first draft also cut it to 6 [8]; GPT's review
  pointed out nothing justified both cuts at once.)
- **Bring the House Down grows with her stage.** With three guests it spends
  up to 30, and each guest also acts.
- **Extended Run** takes Bis!'s slot. Bis! only rewarded spend-all cards,
  which are now two in a deck. Its scope, pinned by C# tests as #1350 did for
  Standing Room Only:
  - It adds to a played card's whole cap once: Bring the House Down with
    three guests and one Extended Run spends up to 38 (30 + 8), in one Spend.
  - It touches the five capped Attacks and Skills: Soloist's Solicitation
    and Hold the Stage 16 to 24, Tidal Flourish 10 to 18, Bravura 18 to 26,
    and Bring the House Down.
  - It does **not** touch Full House (a Power whose guest-act payments are
    automatic), Navia's and Freminet's fractional Spends, or fixed costs such
    as Quick Flourish.
  - Worked example: Bravura on a 200 bank with two **upgraded** Extended
    Runs spends 42, 14 hits of 7; with two unupgraded copies it spends 34,
    11 hits.
- Prima Donna (0 of 2 taken) and Standing Room Only (played twice) are not
  changed; neither has had a fair test yet.

The pool stays at 78, and the rarity counts do not change.

## 3. Predictions (written before suite 3)

Same five seeds, one Sonnet seat per lane, on the `furina-next` staging build.

1. The average capped Spend in act 3 rises from 5 to 6 Fanfare to at least 9.
2. Turns starting at 20+ Fanfare where a spender is in hand but none can
   spend at least 10 fall below a third of such turns. The record reports
   these turns in three groups, kept apart: no spender in hand at all;
   a spender in hand but too small; a useful spender in hand but
   unaffordable or wrong for the threat. Higher caps only help the second
   group. If the first group stays near today's 37 to 41%, the next change
   is access (Retain on a capped spender, or a way to fetch one), not
   bigger caps.
3. Bravura, Bring the House Down and Extended Run together are taken in at
   least a quarter of their offers.
4. Act 3 normal-fight damage is at least 0.85 of base (suite 2: 0.68).
5. At least three of five runs reach act 3 (suite 2: one).
6. Net HP lost per fight is not above suite 1 in any act (1.65 / 1.05 / 1.53
   of base).

## Picks (ruled 2026-10-16)

[USER]: "Agreed on both picks. I still think that we should eventually
change the starter, but for now it's fine." (After GPT's review, which
backed an amended 1(a) and 2(a); the amendments are in section 2.)

1. **The change set: (a).** The four rows above on `furina-next`, then
   suite 3.
2. **The starter: (a).** Rising Applause stays as it is for this test. A
   starter change stays open for later: suite 3's three-way split of
   full-bank turns is the evidence for it.
