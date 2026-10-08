# Varka: making the Pyro and Cryo payoffs worth taking, 2026-10-08

Project review 2026-10-08, pick 10, ruled at the default: "Payoffs offered
and passed means fix the cards." The offers round
(`review/records/varka-offers-round-2026-10-08.md`) found exactly that.

- Seats took Pyro cards at 10% of offers, against 18% for all offers and 28%
  for Anemo.
- No Pyro or Cryo payoff went unoffered.
- Even the one Pyro start (lane 4, Amber) passed every Pyro payoff and
  drafted Cryo and Hydro.

This paper adjusts existing cards only: the second step on `stage-gate.md`'s
ladder. Both directions stay as ruled.
- **Pyro's Exhaust engine** is [USER]'s: "Perhaps Pyro cards gain an Exhaust
  engine to compliment Electro's draw engine?" (combo pass, pick 2).
- **Cryo's status payoffs** come from the identities paper ("Cryo deals with
  statuses and has payoffs related to status stacking").

## Why they were passed

1. **Exhaust paid nothing on the turn.** Burning a card was pure cost unless
   Pyre Oath was already down. Seats said "never wanted to exhaust anything",
   and one removed Stoke at a shop.
2. **Pyro Oath had no buyer the seats wanted.** The card they loved most,
   Four Winds' Ascension (3 a hit per Oath of the current element), already
   reads Pyro Oath. Nothing said so: the Pyro cards grew the Oath slowly, and
   only Stoke made Pyro current.
3. **Cryo's payoffs needed debuffs the deck didn't have.** Deep Freeze
   doubles Weak and Vulnerable, and on an enemy with none it is a 1-cost
   "apply Cryo". Icebreaker, which pays on whatever is there, was taken and
   played (11 to 14 a play).
4. **Both rares cost 2**, and seats would not spend a turn on a slow Power.
   The one Absolute Zero drafted was never played.

## The changes

| Card | Now | Becomes | The point |
|---|---|---|---|
| Ember Cleave (C, Attack) | 1: Deal 9 [12] Pyro. Exhaust a card. | 1: Deal 9 [12] Pyro. Exhaust a card. **Gain 1 Pyro Oath.** | The burn pays on the turn. It also makes Pyro current, so the next Ascension reads the Oath it just grew. |
| Stoke the Flames (C, Skill) | **1**: Exhaust a card. Gain 2 [3] Pyro Oath. Pyro becomes current. | **0**: the same | A free switch into Pyro that thins the deck, instead of a turn's tempo. |
| Pyre Oath (U, Power) | 1: Whenever you Exhaust a card, gain 1 Pyro Oath. [Innate] | 1: **Exhaust a card.** Whenever you Exhaust a card, gain 1 Pyro Oath. [Innate] | It pays an Oath on the turn it lands, then keeps Feel No Pain's shape. Built as exactly 1: `exhaust_from` has no "up to" (the fallback below). |
| Wildfire Oath (R, Power) | **2**: applying Pyro deals Pyro Oath to the enemy. [Innate] | **1**: the same | The rare bends, never removed (house rule); the decision is unchanged. |
| Deep Freeze (U, Skill) | 1 [0]: Apply Cryo. Double its Weak and Vulnerable. Retain. | 1 [0]: Apply Cryo **and 1 Vulnerable**. Double its Weak and Vulnerable. Retain. | Never dead: at worst it is 2 Vulnerable and Cryo. |
| Glacial Edict (U, Skill) | +1 Weak and Vulnerable for every **4 [3]** Cryo Oath | every **3 [2]** | The seats' Cryo Oath sat at 7 to 12 in acts 2 and 3: 2 to 4 extra of each instead of 1 to 3. |
| Absolute Zero (R, Power) | **2**: Weak or Vulnerable deals Cryo Oath. [Innate] | **1**: the same | As Wildfire Oath. |

Blazing Charge, Icebreaker, Kindled Edge and the Knights are unchanged.
Kindled Edge+ and Icebreaker already earned their slots in the round.

**Yardsticks.**
- **Ember Cleave** sits above True Grit's "exhaust as a cost". 9 for 1 plus an
  Oath is Vow of the Blade's Oath riding on a Strike+3, paid for by the burned
  card.
- **Stoke at 0** gains Oath, not Energy or draw, so it cannot loop.
- **Pyre Oath** is Feel No Pain's shape plus two exhausts without the draw,
  which is Electro's job. The builder checks Feel No Pain, True Grit and Bash
  against `game_ref` and notes any mismatch.
- **Deep Freeze**'s floor of 2 Vulnerable and an aura for 1 is under Bash's
  8 damage and 2 Vulnerable for 2.

## Readings for the builder

- **Ember Cleave:** the Oath is gained even with no card left to Exhaust.
  Pyro becomes current from its hit, as it does now.
- **Pyre Oath:** the Power goes on first, so its own two Exhausts each pay 1
  Oath. "Up to 2" means the player may choose 0, 1 or 2. If `exhaust_from`
  cannot take "up to", use exactly 1 and say so in the provenance note.
- **Deep Freeze:** the 1 Vulnerable lands before the doubling, so a clean
  enemy ends on 2. Absolute Zero triggers as it does now; this change adds
  one application, the Vulnerable.
- **Glacial Edict:** only the divisor changes (3, upgraded 2).
- Costs are the sheet's `cost`, and upgrades keep their current fields.

## What it should do (graded by the next Varka round)

1. Pyro's take rate rises from 10% to at least the kit's average (18%).
2. Ember Cleave, Pyre Oath and Deep Freeze each get taken at least once in
   five runs, where this round took them 1, 0 and 0 times.
3. At least one run plays a Pyro deck, meaning Pyro current on most of its
   Ascension plays.

No picks: these are card adjustments inside two ruled directions. If a
number is wrong, the next round says so and it moves.
