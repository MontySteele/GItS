# Furina: the Spend caps and the held bank (2026-10-12)

**Why.** [USER], before the wave:

> Our main concern ... is where her damage comes from, with tension regarding Fanfare spend ... if we still have problems, the simplest knob to turn is going to be how big her Drain floor ought to be, and what her Fanfare Spend looks like.

And on the character:

> She's supposed to feel like a character that swings her HP around violently but gets rewarded for it.

Her core loop (Drain, Fanfare, Spend, Repay) is kept as it is; this paper turns only those two knobs. The guest-star style, which this wave barely drafted (guest acts made 3 to 7% of her damage), is the later flavour pass.

**Sources:**
- `review/records/furina-varka-wave-2026-10-12.md`: four Furina seats, 69 fights, 250 turns.
- Fight telemetry fields: `fanfare_turn_start`, `spend_cards_in_hand_turn_start`, `fanfare_spends`, `fanfare_end`, `drain_buffer_left` and `past_lost`.
- The offer logs.
- A Fable review, in the session scratchpad (`fable-review-furina-spend.md`), which corrected this paper's first draft.

## 1. What the wave shows

**Damage is fine.**
- Normal fights, acts 1 to 3: 18.7, 32.8 and 63.8 damage a turn, against the base five's 19.0, 30.2 and 38.6.
- Spend cards made 20, 26 and 30% of it in normal fights.

**The swing is there and pays back.**
- Inside a fight she drops a median 14, 30 and 18% of her HP.
- After the fight she is about 9% down once the drained HP returns. The base five end 8 to 14% down.

**Fanfare goes unspent.**
- **A quarter of the Fanfare she made was never spent.** That is 546 of 2,162, not counting what she made on the last turn of a won fight, which no card could spend.
- **A third of her turns (82 of 250) started with 15 or more Fanfare.** On 32 of those she had no Spend card in hand.
- **A third of the unspent Fanfare is left behind by the caps.** Of the 37 plays of a "Spend up to" card, 20 hit their cap and left 222 Fanfare in the bank:
  - Spirited Aria ("up to 8") hit it on 13 of 18 plays.
  - Crashing Waves ("up to 12") hit it on 6 of 16.

**The deaths are not mainly about having no outlet:**
- **Two came at elites she entered at 19 and 20 HP.** No outlet saves those.
- **One came at the act-3 boss** with Rising Applause, Encore! and Bring the House Down in hand. She spent 46 for damage and died to 45 incoming on 5 Block.
- **One came at the act-3 boss with 34 to 36 banked and no Spend card in hand.** That seat had passed Standing Ovation three times, Encore! twice, and Quick Flourish and Hold the Stage once each. Pooled across both rounds, Standing Ovation was passed 15 of 19 times.

So the no-outlet death is a drafting shape. The outlets are in the pool.

**The Drain floor** (her buffer, a quarter of Max HP, which returns after combat):
- In normal fights she uses 26 to 68% of it.
- Against act-2 elites she uses a median 88%, and against act-3 bosses 83%. HP lost past the line reached 11 in act-3 boss fights.
- It already binds where fights are hardest, so it is not the loose knob.

## 2. The proposal

**1. Raise the three Spend caps that leak.** A capped play should be able to empty a normal fight's bank; her normal-fight peaks are 15 to 27.

| Card | Today | Proposed |
|---|---|---|
| Spirited Aria (C) | "Spend up to 8: deal 1 more for each. Draw 1 for every 4 spent." | up to **12** |
| Crashing Waves (C) | "Spend up to 12: hit once more for every 4." | up to **16** |
| Hold the Stage (U) | "Spend up to 12: gain 1 more Block for each." | up to **16** |

- **Tidal Flourish's 10 is unchanged.** It hits ALL enemies.
- **The rates are unchanged:** each Fanfare still buys what it buys today. The caps came in on 2026-10-10 after she "dominated act 3" in co-op. Her solo act-3 damage is 1.65 times the base five's, so these are raised by a third, not removed.

**2. Packed House becomes the hoard's Block card.** Holding Fanfare is a ruled small style ("the hoard", diversity pass sec.2, component A).

> **Packed House** (Common Skill, 1): Gain 5 [8] Block, plus 1 for every 4 Fanfare you have.

- **Today:** "Deal 4 damage, plus 1 for every 5 Fanfare you have." Taken 1 of 14.
- **What it gives:** 15 Fanfare gives 8 Block, 25 gives 11, and 53 gives 18. It never spends.
- **Why 1 per 4:** Hold the Stage still wins at the banks she usually holds, and The Show Must Go On (Rare, 1 Block per Fanfare) stays the hoard's top card.

**3. Rising Applause: Retain on the upgrade.**

> **Rising Applause+**: Gain 7 Block. Spend all your Fanfare and deal that much Hydro damage. **Retain.**

- **There is a precedent:** Standing Ovation+ gains Retain only on its upgrade.
- **The base card is unchanged.** Starter cards stay bad.
- **The trade-off:** Retain rewards holding the bank, so it lowers how often she Spends mid-fight. On the upgrade alone it costs a smith or a shop, which keeps the "hold, then dump it all" deck a choice rather than the default.

**4. A one-line tip on Rising Applause** (hygiene, no pick): "Its damage is the Fanfare you hold; play it when the bank is worth it." Two seats played it at 0 to 4 damage.

**Unchanged:**
- The Drain floor.
- Every Spend rate.
- The Repay floor.
- The guests.

## 3. Risks

- **Higher caps raise her act-3 damage,** which is already high. Watch act-3 damage a turn against the base five's next round. The rates do not move, so the ceiling only moves where she banks more than the old cap.
- **Packed House plus Prima Donna and Star Turn** is a hoard deck that rarely Spends. At 1 per 4 it is a small component, as ruled.
- **Four seats are a small sample.** The 2026-10-12 round's two Furina seats also left 26% and 33% unspent.

## For [USER]

1. **The Drain floor.**
   - **(a) Default:** unchanged at a quarter of Max HP. It already binds against elites (88% used) and bosses (83%).
   - (b) A third of Max HP. That allows a bigger swing, which she reaches only in hard fights.
   - (c) A fifth. That would bind on most elites from act 2.
2. **The Spend caps.**
   - **(a) Default:** Spirited Aria up to 12, Crashing Waves up to 16, Hold the Stage up to 16.
   - (b) Unchanged.
3. **Packed House.**
   - **(a) Default:** "Gain 5 [8] Block, plus 1 for every 4 Fanfare you have."
   - (b) Keep it as the Attack it is.
4. **Rising Applause** (her starter card).
   - **(a) Default:** Retain on the upgrade only.
   - (b) Retain on the base card too.
   - (c) No change.
