# Furina: a diversity pass and act-3 "oomph" (2026-10-11)

**Why.** From the co-op playtest (`review/records/coop-human-playtest-2026-10-11.md`):
- "Furina's core loop is fine, but it didn't have enough 'oomph' - carried in act 1 and 2 when Varka wasn't online yet, fell behind in act 3."
- "We should do a diversity pass on the build to allow for multiple unique playstyles besides the one core loop."

Sources, all in the session scratchpad:
- the census, `furina-diversity-census.md`;
- per-card counts over five seat rounds plus your run, `furina-card-lifetime.md`;
- the round 5 packet, `furina-r5-packet.md`.

## 1. What your run shows

From your co-op telemetry, `play-20261011-161711.jsonl`, seat 1:

- **Damage a turn by act: 21.8, 35.2 and 38.9.** Varka's was 26.4, 48.5 and 94.6.
- **She did not run short of Fanfare.**
  - The act-3 boss fight (Test Subject) peaked and ended at **144 Fanfare**, with 44 spent. All of it went through Hold the Stage (12 a play) and Encore! (4).
  - The act-3 elite fight ended with 82.
  - Rising Applause was played twice in act 3. More generation would not have helped; she had nothing to turn the bank into.
- **Her deck was a guest deck.** Lyney, Clorinde and Lynette dealt **44%** of her damage (1,356 of 3,072). Guest acts are flat: Lynette 3, Wriothesley 4, Clorinde 6, Lyney 8 (`FurinaStageLaw.cs:44-75`). They don't grow, so by act 3 they fall behind.
- **The blind seats never draft that deck.** Over five rounds, the guest support cards were offered 46 times and taken 0 times:
  - Final Bow 0 of 5, Tutti! 0 of 5, Showstopper 0 of 5, Ensemble Cast 0 of 11, Casting Call 0 of 11, Grand Entrance 0 of 8;
  - Lynette 0 of 6, Escoffier 0 of 6, Clorinde 0 of 1, Navia 0 of 5.

  The seats' Furina is a pure Spend deck, and on that deck act 3 is fine: 61 damage a turn in round 5. So seat rounds can't grade this pass; your play has to.
- **On "not enough draw / energy":** the pool has 13 draw cards and 6 energy cards. The base characters have 4 to 10 draw and 3 to 7 energy. The count is not short, but every one of those cards needs a Drain, Repay or Spend first. I propose nothing here and would watch it in the next run.
- **On "Spend All are redundant":** Rising Applause (1 damage a point, 5 Block) and Bravura (6, plus 2 a point) are the same shape: one enemy, cost 1, no rider. Rejoice (ALL) and Bring the House Down (guests act) each do something different.

## 2. The playstyles

Today about 70% of her cards name Spend, Drain, Repay or Fanfare (census sec.6). The pass keeps the loop as the engine and gives it three ways to cash out.

**A. The Spend deck (today's deck).** It spends the bank in bursts. Nothing is added. Bravura is reshaped so it stops repeating the starter:
- **Bravura** (Uncommon, 1): "Spend all your Fanfare. Deal 6 Hydro damage for every 3 spent."
  - The rate is unchanged, 2 damage a point. It loses the flat 6 and becomes many hits.
  - Strength and Vulnerable now apply to every hit, and Neuvillette's "+Hydro damage" line adds to every hit. That gives Furina's three Strength Rares (Regina, Standing Room Only, Hymn of Renewal) a Spend payoff for act 3.
  - At 60 Fanfare and 2 Strength, that is 20 hits for 160 damage. Today it would be 128.

**B. The company (guests that grow).** Your run's deck. The fix is to let the bank feed the guests:
- **Full House** (new, Uncommon Power, 1): "Your guests' acts deal 1 more damage for every 10 Fanfare you have." Upgrade: Innate.
  - With 3 guests and 40 Fanfare, that is +12 damage a turn.
  - With the 144 you ended on, Lyney's act would hit for 22 and the three guests together for about 50 a turn. That turns the act-3 bank into guest damage.
  - It sets up a choice: every Spend lowers your guests' damage.

**C. The hoard (hold, don't Spend).** Prima Donna, Star Turn and The Show Must Go On already reward a big bank, but all three are Rare or Uncommon. A Common gives the style a floor:
- **Packed House** (new, Common Attack, 1): "Deal 5 damage, plus 1 for every 3 Fanfare you have." Upgrade: base 8.
  - At 30 Fanfare it deals 15; at 60, 25. It spends nothing, so it pairs with Full House and Prima Donna.

**Pool size.** The pool stays at 78 (plus 2 basics). Two cards make room, and both were dead in every source: 0 takes from 16 seat offers, and 0 plays in your run.
- **Rising Tide** (Uncommon): "Deal 6 damage, plus 3 for each time you Repaid this turn." 0 of 7 offered, 0 of 9 in shops.
- **Fountain of Lucine** (Uncommon): "For 3 turns, at the start of your turn Repay 2 [3]. Gain 1 Block for any HP it could not Repay." 0 of 9 offered, 0 of 2 in shops.

Repay keeps 13 other cards.

**Not changed:**
- The starter cards.
- Standing Ovation stays at "Spend half" (ruled today).
- The Spend caps (ruled 2026-10-10).
- The Drain line.
- Draw and energy.

## For [USER]

1. **The playstyles.**
   - **(a) Default:** all three as above: Spend, company and hoard.
   - (b) Company only (Full House, plus Bravura's reshape). Leave the hoard to the existing Rares.
2. **Full House's strength.**
   - **(a) Default:** Uncommon, +1 per 10 Fanfare.
   - (b) Rare, +1 per 5 Fanfare: a deck you build around rather than a card you splash.
3. **Bravura.**
   - **(a) Default:** Hydro multi-hit, "6 for every 3 spent".
   - (b) Leave it, and accept the overlap with Rising Applause.
4. **Room in the pool.**
   - **(a) Default:** Rising Tide and Fountain of Lucine out.
   - (b) Grow the pool to 80 for now and cut after your next run.
