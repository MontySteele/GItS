# Varka: a Pyro that works one card at a time (2026-10-11)

**Why.** From the co-op playtest (`review/records/coop-human-playtest-2026-10-11.md`), [USER]:

> I used his Cryo and Electro extensively in the last co-op game and they worked quite well! Pyro is the odd one out now; outside the rather good starter card, it felt too niche and self-contained to be good without having the whole package assembled in one go, whereas block / draw power / statuses are individually useful already.

GPT's four-character review (`review/active/four-character-independent-review-2026-10-11.md`) found the same thing in the seat logs: Ember Cleave taken 2 of 14, Stoke the Flames 1 of 8, Ashen Oath 0 of 6.

**Source:** a census of his 78-card pool by element, in the session scratchpad (`varka-element-census.md`). It counts offers and takes over every Varka seat lane to date (`tools/offer_report.py --character Varka`). Card text is from `docs/prototype-surface.yaml`.

## 1. What each element does for him today

| Element | Pool cards | Its job in a deck without the rest of its package | Taken |
|---|---|---|---|
| Anemo | 12 | damage and Swirl, his own element | 28.8% |
| Electro | 10 | draw, Energy, damage to ALL | 19.5% |
| Cryo | 7 | Weak and Vulnerable | 16.9% |
| Pyro | 9 | damage (which Anemo already gives) | 15.8% |
| Hydro | 6 | Block | 12.8% |

Cryo, Electro and Hydro each bring something his Anemo cards lack, so one card of them is worth a slot. Pyro brings damage, which every Anemo Attack already brings. What Pyro has of its own is two closed packages:
- **Exhaust.** Ember Cleave and Stoke the Flames make you Exhaust a card, and Ashen Oath pays Pyro Oath for each Exhaust. Varka has no Statuses or Curses of his own to feed it, so each Exhaust costs one of his own cards. All three are among his least-taken cards.
- **Pyro Oath.** Blazing Charge (5, plus 2 per Pyro Oath; taken 1 of 22) and Wildfire Oath (Rare) read it. Neither is good until Pyro Oath is high.

The Pyro cards that work alone are the ones taken: Kindled Edge (34%) and Diluc: Searing Onslaught (29%). Amber: Precise Shot, his Pyro starter Knight, is the "rather good starter card".

## 2. The proposal: Pyro powers up his Attacks

Varka has **no Strength in his pool** and no card that boosts his next Attack. That is the job Pyro takes, as Bennett and Diluc do in Mondstadt. It is useful in any deck of Attacks, which every Varka deck is. Pyro Oath still scales it, so the package still pays when assembled. The Exhaust lane is retired: the cost comes off the two Commons, and Ashen Oath becomes the Strength card.

| Card | Today | Proposed |
|---|---|---|
| **Ashen Oath** (U Power, 1) | "Exhaust a card. Whenever you Exhaust a card, gain 2 Pyro Oath." [Innate] | "Gain 2 Strength. Gain 2 Pyro Oath." [3 Strength] |
| **Stoke the Flames** (C Skill, 0) | "Exhaust a card. Pyro becomes your current element. Gain 2 Pyro Oath." [3] | "Pyro becomes your current element. Gain 2 Pyro Oath. Your next Attack this turn deals 3 additional damage." [3 Oath, 5 damage] |
| **Ember Cleave** (C Attack, 1) | "Deal 9 Pyro damage. Exhaust a card. Gain 1 Pyro Oath." [12] | "Deal 9 Pyro damage. Gain 1 Pyro Oath." [12] |
| **Blazing Charge** (U Attack, 1) | "Deal 5 Pyro damage, plus 2 for each Pyro Oath." [7] | "Deal 8 Pyro damage, plus 2 for each Pyro Oath." [11] |

Unchanged: Kindled Edge, Diluc: Searing Onslaught, Amber: Sharpshooter, Amber: Baron Bunny, Wildfire Oath and the starter Knight.

Notes:
- **Ashen Oath** is Inflame with 2 Pyro Oath on top. Inflame is an Uncommon at 1 Energy for 2 Strength, so the Oath is the kit's premium for the slot. Strength reaches every hit of Gale Sweep, Storm Surge, Thundering Verdict and Four Winds' Ascension's two hits, which is why it is 2 and not more.
- **Stoke the Flames** keeps its 0 cost and its element switch, and loses the Exhaust. The +3 is Bennett — Passion Overload's template ("Your next Attack this turn deals 4 additional damage").
- **Ember Cleave** loses only the Exhaust; 9 for 1 with an Oath is a Common rate.
- **Blazing Charge** gets the floor every new card is held to: 8 with no setup, which is still under Favonius Cut's rate.
- The Pyro count stays at 9 and the pool at 78; no rarity moves.

## 3. Not in this pass

- **Converging Winds** pays 6 to every enemy for each Swirl, so a card that Swirls three enemies deals 54 more against three, against 6 for one Swirl on one enemy (GPT's review; `VarkaOath.cs:843`). [USER] agreed to check rather than change it. The next Varka round reads its damage by enemy count.
- **Block.** [USER]'s run said he relied on Powers for Block. Rippling Guard and Gleeful Songs got Block floors in #1114, which the same round reads.

## How it is checked

A two-seat Varka round on the built pool. Lines:
- Pyro take rate at least 20% pooled (15.8% today);
- Ashen Oath, Stoke the Flames and Ember Cleave each taken at least once;
- Converging Winds' damage per fight against the number of enemies, read and reported.

## For [USER]

1. **Pyro's job.**
   - **(a) Default:** Pyro powers up his Attacks (Strength and "next Attack" damage), the Exhaust lane is retired, and the four cards in section 2 build as written.
   - (b) The same, but the Exhaust stays as an optional rider ("You may Exhaust a card. If you do, gain 1 more Pyro Oath.").
   - (c) A different job for Pyro (say which).

## Ruled 2026-10-11: pick 1 (b)

[USER]: "I lean towards b) which allows for some tactical use of Exhaust vs status enemies, bit I agree that we need something better as the main engine."

- Ashen Oath and Blazing Charge build as in section 2.
- Stoke the Flames and Ember Cleave build as in section 2, plus the optional rider: "You may Exhaust a card. If you do, gain 1 more Pyro Oath." Choosing no card is allowed, and with an empty hand the rider does nothing.
