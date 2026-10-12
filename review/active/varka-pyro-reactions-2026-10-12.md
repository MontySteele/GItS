# Varka: Pyro's Commons set up the reactions (2026-10-12)

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

**What gives him more of those reactions is putting Pyro on an enemy.** His Knights already leave Cryo, Hydro and Electro behind them. Wildfire Oath, Sharpshooter and Kindled Edge all want Pyro on the target.

## 2. Anemo, and the half-and-half deck

[USER] asked whether "a deck that's half Anemo and half whatever other element pieces you saw" works, or whether Anemo is only "good stuff cards helping a more coherent idea together on the side".

**Across the six runs, Anemo is the plan:**
- Anemo cards were 15 to 39% of plays and 15 to 48% of damage. With Swirl added, they made 22 to 66% of his damage.
- His starting element's own cards were 7 to 20% of plays.
- Every seat drafted the half-and-half deck, and 5 of 6 reached the act-3 boss.

So Anemo is not stuck in a supporting role. If anything, the elements are the side half, and Pyro's job should be the one that half-and-half deck already wants: more reactions.

**Oath is still unread.** Telemetry records no Oath counts. The fields are being added, and whether switch decks and mono decks both bank a lot of Oath waits for the next round.

## 3. The proposal

| Card | Today | Proposed |
|---|---|---|
| **Stoke the Flames** (C Skill, 0) | "Gain 2 Pyro Oath. Your next Attack deals 3 additional damage. You may Exhaust a card for 1 additional Pyro Oath." [3 Oath, 5] | "Apply Pyro to an enemy. Gain 2 [3] Pyro Oath." |
| **Ember Cleave** (C Attack, 1) | "Deal 9 Pyro damage. Gain 1 Pyro Oath. You may Exhaust a card for 1 additional Pyro Oath." [12] | "Deal 9 [12] Pyro damage. Draw 1 card." |

**Why these two cards:**
- **Stoke makes its own reaction.** Played after a Knight's Cryo, Hydro or Electro, it turns that aura into a Melt, Vaporize or Overloaded on the next hit, for 0 Energy. It also arms Wildfire Oath, Sharpshooter and Kindled Edge, and gives a Swirl a Pyro aura to spread. This is the shape of Pathfinder's Mark, which applies an element.
- **Ember Cleave gets a floor with a job:** a Pyro hit that replaces itself. It is the Pyro twin of Charged Lunge and the base game's Pommel Strike (9 damage, draw 1). It is no longer a second reaction-conditional Common; Kindled Edge keeps that job.
- **The Exhaust rider is retired** from both. Pick 1 (b) kept it "for tactical use of Exhaust vs status enemies"; across two rounds the two cards were taken once.

**Unchanged:** Ashen Oath, Kindled Edge, Blazing Charge, Wildfire Oath, Diluc, Sharpshooter, Baron Bunny, and the starter Knight.

**Hygiene in the same PR:** Sucrose — Mollis Favonius's card already names Melt, Vaporize and Overloaded, so the BACKLOG line saying its text reads "Elemental Reactions" is out of date and goes.

## 4. Risks and checks

- **A free Pyro application can stack with his apply-to-ALL cards:** Gleeful Songs, Pulsating Witch, Pathfinder's Mark+ and Tempest. Watch damaging reactions per turn on the turns Stoke is played.
- **Check lines for the next round:**
  - The Pyro take rate pooled, against about 10% of 94 today.
  - Each changed card taken at least once.
  - Damaging reactions per fight in a Pyro start, against about 1 today.
- **This is judged on Sonnet take rates alone.** You haven't played the Strength pass yet; your last Pyro run came before it. Option (b) is the honest alternative.

## For [USER]

1. **Pyro's Commons.**
   - **(a) Default:** Stoke the Flames becomes "Apply Pyro to an enemy. Gain 2 [3] Pyro Oath." Ember Cleave becomes "Deal 9 [12] Pyro damage. Draw 1 card." Strength stays on Ashen Oath.
   - (b) Keep the current pass until your own Pyro run reads it.
   - (c) Something else (say what).
