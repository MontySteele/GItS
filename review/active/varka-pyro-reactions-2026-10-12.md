# Varka: Pyro is the hit that cashes the reactions (2026-10-12)

**Why.** After the Pyro pass (`varka-pyro-pass-2026-10-11.md`), [USER] said his Pyro core "is still 'up for grabs' if we can't make the Strength / Exhaust ideas work out". That pass ruled pick 1 (b): Strength on Ashen Oath, "next Attack" on Stoke the Flames, and the Exhaust kept as an optional rider.

Two seat rounds have now played the pass:
- `review/records/furina-varka-round-2026-10-12.md`: two Varka seats.
- `review/records/furina-varka-wave-2026-10-12.md`: six Varka seats, three of them forced to start on Pyro.

**Sources:**
- Offers: `tools/offer_report.py --character Varka --element pyro --since 2026-10-11T12:00`.
- Lane telemetry, read by `varka_wave.py` in the session scratchpad.
- A Fable review of this paper's first draft, `fable-review-pyro.md` in the scratchpad, which changed its diagnosis and both cards.

## 1. What the two rounds show

**Strength works; the Exhaust Commons do not.**
- Ashen Oath (2 Strength) is the best-taken Pyro card: 3 of 8. The one run that drafted it, the Cryo win, peaked at 5 to 15 Strength in 9 fights.
- Ember Cleave was taken 0 of 17 and Stoke the Flames 1 of 19. Both carry the Exhaust rider.
- Overall, Varka's own Pyro cards were taken on about 10% of 94 offers.

**Seats pass Commons that only deal damage, in every element.** The Commons they take carry Block or draw: Jean, Crosswind, the new Rippling Guard, Lisa's cards and Charged Lunge. Kindled Edge already pays for a reaction ("If it causes an Elemental Reaction, deal 7 additional damage") and was taken 1 of 9. So paying for a reaction does not by itself make a Common worth taking.

**What Pyro alone among his elements is part of: all three damaging reactions.** Melt with Cryo, Vaporize with Hydro, Overloaded with Electro. Five of the six seats named a reaction turn as their best. The sixth named its Cycle of Seasons switching turns. None named a Strength turn.

But Melt, Vaporize and Overloaded each come up only about once a fight (0.7 to 1.1 per fight across the six runs). The first draft's "+3 to each of them this turn" would have been worth about 3 damage a fight.

**How the two amplifiers actually fire.** [USER], on the first proposal: "applying the second element instantly causes the reaction. For Overload, that's fine; for melt and vape, this would react for 0*1.5 or 0*1.75 = 0 damage." That is the code: an application reacts (`ReactionPreviewNoHitTests.cs`), and Melt and Vaporize multiply only the hit that triggers them (`AuraPower.ModifyDamageMultiplicative`).
- So a Pyro application with no hit wastes a Cryo or Hydro aura.
- It also sets the order the other way round. His Cryo and Hydro Knights (Kaeya, Barbara, Mika) apply with no hit, so a Pyro aura followed by one of them is the same 0 × 1.75.
- **Melt and Vaporize come from a Pyro hit landing on the aura a Knight left.** Pyro is the hitter, not the applier.
- Strength and "next Attack deals N additional damage" are added before the multiplier (`NextAttackUpPower.ModifyDamageAdditive`), so a Melt multiplies them too. This is why Strength, the one Pyro idea that works, belongs with the reactions.

## 2. Anemo, and the half-and-half deck

[USER] asked whether "a deck that's half Anemo and half whatever other element pieces you saw" works, or whether Anemo is only "good stuff cards helping a more coherent idea together on the side".

**Across the six runs, Anemo is the plan:**
- Anemo cards were 15 to 39% of plays and 15 to 48% of damage. With Swirl added, they made 22 to 66% of his damage.
- His starting element's own cards were 7 to 20% of plays.
- Every seat drafted the half-and-half deck, and 5 of 6 reached the act-3 boss.

So Anemo is not stuck in a supporting role. If anything, the elements are the side half, and Pyro's job should be the one that half-and-half deck already wants: a bigger hit to cash the auras his Knights leave, and Strength that every Attack in the deck uses, Anemo included.

**Oath is still unread.** Telemetry records no Oath counts. The fields are being added, and whether switch decks and mono decks both bank a lot of Oath waits for the next round.

## 3. The proposal

The first draft's pair was "Stoke the Flames: Apply Pyro to an enemy. Gain 2 [3] Pyro Oath." and "Ember Cleave: Deal 9 [12] Pyro damage. Draw 1 card." Both are withdrawn:
- Stoke's application wastes the aura it reacts with (section 1).
- On Ember Cleave, [USER]: "The new Ember Cleave sounds like an Electro card." His draw lives on Electro (Charged Lunge, Static Field, Pulsating Witch, Short Circuit).

| Card | Today | Proposed |
|---|---|---|
| **Ember Cleave** (C Attack, 1) | "Deal 9 Pyro damage. Gain 1 Pyro Oath. You may Exhaust a card for 1 additional Pyro Oath." [12] | "Deal 7 [9] Pyro damage. Gain 2 [3] Strength this turn." |
| **Stoke the Flames** (C Skill, 0) | "Gain 2 Pyro Oath. Your next Attack deals 3 additional damage. You may Exhaust a card for 1 additional Pyro Oath." [3 Oath, 5] | "Gain 2 [3] Pyro Oath. Your next Pyro Attack this turn deals 5 [7] additional damage." |

**Why these two cards:**
- **Pyro's job is Strength and the hit.** The Knights leave Cryo and Hydro; a Pyro hit cashes them at ×1.75 or ×1.5, and both cards' bonuses sit inside that multiplier.
- **Ember Cleave is the base game's Setup Strike** (Ironclad Common: 7 damage, 2 Strength this turn), in Pyro. Its Strength reaches every later Attack that turn: Diluc's two hits, Four Winds' Ascension, and his Anemo Attacks. This gives the half-and-half deck a reason to carry it. It is Pyro's own card, not a draw card.
- **Stoke keeps its shape** with the rider cut and a bigger number. It now names a Pyro Attack, so it is Pyro's setup, not a generic one. On a Melt, its 5 becomes about 9.
  - It is the weaker of the two changes: the current card (Oath plus 3) was taken 1 of 19, though the Exhaust rider was part of that card.
  - The alternative is to leave Stoke alone until your Pyro run.
- **The Exhaust rider is retired** from both. Pick 1 (b) of the Pyro pass kept it "for tactical use of Exhaust vs status enemies"; across two rounds the two cards were taken once.

**Unchanged:** Ashen Oath, Kindled Edge, Blazing Charge, Wildfire Oath, Diluc, Sharpshooter, Baron Bunny, and the starter Knight.

**Hygiene in the same PR:** Sucrose — Mollis Favonius's card already names Melt, Vaporize and Overloaded, so the BACKLOG line saying its text reads "Elemental Reactions" is out of date and goes.

## 4. Risks and checks

- **Strength this turn on a 1-cost Common is strong with multi-hit cards.** Diluc hits twice and Tempest of the Four Winds four times. Setup Strike is a base-game Common at the same numbers, so this is the base game's rate.
- **Ashen Oath plus Ember Cleave plus a Melt** is the Pyro turn this paper wants. Watch the biggest single Pyro hit per fight.
- **Check lines for the next round:**
  - The Pyro take rate pooled, against about 10% of 94 today.
  - Each changed card taken at least once.
  - Melt and Vaporize per fight in a Pyro start, against about 1 today.
- **This is judged on Sonnet take rates alone.** You haven't played the Strength pass yet. Option (b) is the honest alternative.

## For [USER]

1. **Ember Cleave.**
   - **(a) Default:** "Deal 7 [9] Pyro damage. Gain 2 [3] Strength this turn."
   - (b) A big hit instead: "Lose 2 HP. Deal 13 [17] Pyro damage." (the base game's Hemokinesis, at Common).
   - (c) Keep it until your own Pyro run.
2. **Stoke the Flames.**
   - **(a) Default:** "Gain 2 [3] Pyro Oath. Your next Pyro Attack this turn deals 5 [7] additional damage."
   - (b) Keep it until your own Pyro run.

## Ruled (2026-10-12)

[USER]: "On Varka - agreed on both options". Both defaults (a): Ember Cleave becomes "Deal 7 [9] Pyro damage. Gain 2 [3] Strength this turn."; Stoke the Flames becomes "Gain 2 [3] Pyro Oath. Your next Pyro Attack this turn deals 5 [7] additional damage." The Exhaust rider is retired from both.
