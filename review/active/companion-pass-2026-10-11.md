# The Companion cards: a pass against [USER]'s bar, 2026-10-11

This is pick 4 of the Klee Uncommons and Rares pass (`klee-upper-pass-2026-10-11.md`, ruled).

[USER]'s bar for Companion cards:
- "I am fine with Common Companions being 'bad' (worse than base game Colorless' since you see them in a brand-new card slot; they should mostly offer off-character elements and effects at a Common-ish energy rate."
- "The Uncommons and Rares should be Colorless-tier (generally a little better than a character's own at the same rarity)."

## The evidence

The full census is `companion-census.md` in the session scratchpad. Every row's text, rate, takes and plays are there, and the code facts below are cited to file and line.

**How a Companion reaches you.**
- One Companion card is added as a fourth choice to the post-fight card reward. You never take it alongside a native card (`PoundingSurprise.cs:124-136`).
- It appears on 95% of Klee's reward screens.
- Its rarity rolls 60% Common, 35% Uncommon and 5% Rare. A boss reward always offers a Rare Companion (`CompanionSlot.cs:54-56`).
- One roster of 86 cards serves all four kits: Klee, Varka, Furina and Kokomi each host the slot through their starter relic.

**What happens to them.**
- Klee takes the Companion in 10% of 1121 offers. 54 of the 86 cards have never been taken.
- Her decks hold about 1 Companion card at the act-1 boss and 2 at the act-2 boss.
- In solo play, the Companions are her only source of enemy auras.

**The yardsticks.**
- **Commons:** the base game has no Colorless Commons. So the bar is the base characters' Common rate, 9 damage per Energy single-target. "Common-ish" is read as at least 8 with an element.
- **Uncommons and Rares:**
  - Base Colorless Uncommons deal a median of 10 damage per Energy and 10 Block per Energy.
  - Colorless Rares are mostly Powers.
  - Klee's own Uncommon attacks deal 9 per Energy.
- **Delays:** an effect that lands over later turns is priced at 1.3 times the on-turn rate, as Kokomi's Plans now are.

## What already meets the bar

- **Commons.** 24 of the 31 carry an element that reacts with Klee's Pyro: Hydro, Cryo, Electro or Anemo. Most attacks deal 8 with that element, which is the "Common-ish" rate.
- **Uncommons.** The multi-turn Exhaust Skills already pay above Colorless rate after the delay discount. For example, Kaeya's Glacial Waltz deals 18 over three turns for 1 Energy, and Lisa's Lightning Rose deals 15 and 3 Vulnerable. They stay.
- **Rares** with a clear job stay: Durin's Principle of Purity (50% taken), Albedo's Solar Isotoma (50%), Itto, Clorinde and Mona.

## Proposals

**1. A kit is not offered Commons of its own element.**

Your bar says Commons should "mostly offer off-character elements." Today Klee is offered four Pyro Commons:
- Bennett's Passion Overload (0 of 34 taken);
- two Chevreuse cards;
- Thoma's Blazing Barrier.

None of them can react with her Bombs. The rule removes those four from Klee's offers. It removes Hydro Commons from Furina's and Kokomi's offers, and Anemo Commons from Varka's.
- Uncommons and Rares are judged on power, not element, so they stay offerable. Durin, Klee's best-taken Companion, is a Pyro Rare.
- It is one check in `CompanionSlot.Roll`, next to the existing personal-pool check.

**2. Six cards below their rarity's rate:**

| Card | Rarity | Today | Rate | New |
|---|---|---|---|---|
| Freminet — Pers, Deploy! | Common | 1 Energy: deal 6 Cryo | 0.6 | Deal 8 Cryo |
| Charlotte — Freezing Point | Common | 1 Energy: deal 4 Cryo, draw 1 | 0.4 | Deal 6 Cryo, draw 1 |
| Dahlia — Sacramental Shower | Common | 1 Energy: the next time an enemy attacks you, deal 9 Hydro to it first | 0.9, a turn late | 12 Hydro (most offered Common, 0 of 45 taken) |
| Chevreuse — Ring of Bursting Grenades | Uncommon | 2 Energy: deal 10 Pyro to ALL | 0.71 | 14 to ALL |
| Lynette — Astonishing Shift | Uncommon | 1 Energy: Swirl, deal 4 to ALL | 0.57 | 6 to ALL |
| Raiden — Musou no Hitotachi | Rare | 3 Energy: deal 20, plus 5 for each Companion played this combat | 0.67 | Deal 27, the base 3-Energy median; the +5 stays |


**3. Wait one round: the cards that count Companions.**

These cards scale with how many Companions you play:
- Klee's Little Hexenzirkel, Team Effort, Come Back and Play! and Alice's Introduction Magic;
- Nicole's Ladder of Divine Ascent and Navia's Cannon Fire Support;
- Raiden's +5.

At about 2 Companions a deck, there is nothing for them to count. Tonight's ruling already raises that density: Tag Along now picks 1 of 3, and Adventure Club picks 2 of 4. Read these cards after the round that tests it, not before.

**4. Wait one round: the reaction Rares.**

Aftershock and Sparkborne Magic were each taken 0 times. In solo play, a fight with a Companion card played reacts 71% of the time, and a fight without one almost never reacts. They wait on the same round.

**Hygiene, done without a pick:** 19 Fontaine rows on the sheet have no `description`. Their text will be written from their effects so the sheet matches the game.

## How it is checked

The Klee seat round after tonight's three builds (Commons, Uncommons and Rares, Companions). Lines:
- Companion take rate of at least 15% pooled, against 10% today;
- at least 2 Companions per deck at the act-1 boss;
- the act-1 line from the Commons pass.

## For [USER]

The Companion rows sit on Klee's shipped sheet, so these are your picks.

1. **Same-element Commons.**
   - **(a) Default:** a kit is never offered a Common Companion of its own element.
   - (b) The same, at every rarity.
   - (c) No change.
2. **The six numbers in the table.**
   - **(a) Default:** all six.
   - (b) None.
3. **The Companion-count payoffs and the reaction Rares.**
   - **(a) Default:** wait for the round.
   - (b) Rework them now.
