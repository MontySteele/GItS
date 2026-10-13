# The Fontaine Companions: a sanity check, 2026-10-12

This is the first instalment of the nation sweep that the two Companion papers left owed (`companion-pass-2026-10-11.md`, `companion-upper-pass-2026-10-11.md`). It answers your ask: "a sanity check of the Fontaine companions (their quality / power level / how well they fit today's characters as draft cards)". You also asked, at the first pass: "Separately we can look and see if some companion cards are just bad and need buffs to be brought up to par for their rarity."

**Evidence.** The packet is in the session scratchpad (`fontaine-census/packet.md`, gitignored). Offer logs cover 2026-10-08 to 2026-10-12 (`understudy/logs/offers/`). Telemetry comes from `tools/telemetry_report.py`, base-game numbers from `tools/colorless_census.py` and `game_ref/`. The sheet and the C# agree on every number.

**Same-element offers stay as ruled:** "it's fine if Commons of the same element can just be bad drafts". That is not reopened here.

## What Fontaine has

There are 16 offerable cards: 8 Common, 4 Uncommon and 4 Rare. Mondstadt has 12, 18 and 11. Furina's own Neuvillette Guest Star rows are hers and are not counted.

| Card | Cost | Today | Offered / taken |
|---|---|---|---|
| Chevreuse — Interdiction Fire | 1 | Deal 7 Pyro damage | 51 / 2 |
| Chevreuse — Vanguard's Valor | 0 | Next Attack +3 damage, +3 more if a reaction happened this turn | 59 / **0** |
| Lynette — Enigmatic Feint | 1 | Swirl the enemy; gain 5 Block | 72 / 2 |
| Lynette — Bogglecat Box | 1 | Draw 2 cards | 75 / **0** |
| Charlotte — Freezing Point | 1 | Deal 6 Cryo damage; draw 1 | 65 / 2 |
| Charlotte — First-Person Shutter | 1 | Gain 4 Block now and 4 next turn | 50 / **0** |
| Freminet — Pers, Deploy! | 1 | Deal 8 Cryo damage | 28 / 3 |
| Freminet — Pressurized Floe | 2 | Deal 10 damage (no element); gain 6 Block | 59 / 5 |
| Chevreuse — Bursting Grenades (U) | 2 | Deal 14 Pyro damage to ALL | 113 / 13 |
| Lynette — Astonishing Shift (U) | 1 | Swirl; deal 8 to ALL | 144 / 6 |
| Charlotte — Snappy Silhouette (U) | 0 | Apply 1 Vulnerable; draw 1 | 94 / 6 |
| Freminet — Shattering Pressure (U) | 1 | Power: your Shatters deal 4 more | 132 / **0** |
| Navia — Cannon Fire Support (R) | 1 | Power: whenever you play a Companion card, gain 3 Block | 62 / **0** |
| Clorinde — Impale the Night (R) | 2 | Deal 20 Electro; Attacks vs an aura deal 6 more | 57 / 9 |
| Neuvillette — Heir (R) | 1 | Power: start of turn, 5 Hydro to a random enemy; auras last 1 turn longer | 62 / 11 |
| Arlecchino — Masque (R) | 1 | Power: start of turn, lose 1 HP, gain 1 Strength | 60 / **0** |

## Quality and power

**The Uncommons and Rares mostly work.**
- Bursting Grenades, Clorinde and Neuvillette are taken.
- Neuvillette's change to "deal 5 Hydro" landed: since 2026-10-12 it went 4 of 8 for Kokomi and 4 of 8 for Furina, up from 0 of 6.
- Clorinde carried a Kokomi run on its own (`kokomi-round-2-2026-10-12.md:42`).
- Astonishing Shift and Snappy Silhouette were raised on 2026-10-11 and are now taken (4 of 18 since). No change to these.

**The Commons are the problem.** Three were never taken, and they are weak for a plain reason:
- **Bogglecat Box is a strictly worse Backflip.** Silent's Common Backflip is 5 Block and draw 2 for 1 Energy (`game_ref/silent-cards.yaml`).
- **First-Person Shutter is Silent's Dodge and Roll, number for number,** but as Charlotte's Cryo card it applies no Cryo. Split Block is a low pick even for Silent. Without an element it gives a reaction deck no reason to take it.
- **Vanguard's Valor is 0 cost but doesn't replace itself.** It spends a card slot for +3 damage.

Two more trail their neighbors:
- **Freezing Point is 6 damage and draw 1.** Ironclad's Common Pommel Strike is 9 and draw 1.
- **Interdiction Fire is 7** where Freminet's Pers, Deploy! is 8. The first pass read "Common-ish" as at least 8 damage per Energy with an element.
- **Pressurized Floe**, Freminet's own Cryo card, applies no Cryo.

**One Uncommon is dead by rule, not by number.**
- Shattering Pressure pays only on a Shatter.
- A Shatter needs a Frozen non-boss enemy and an Attack. Boss rooms freeze only minions (`LAW.md`, "Canonical Frozen").
- So it is a 1-Energy Power that does nothing against most bosses, and it was skipped all 132 times.

**One Rare is the held Companion-count Rare.** Navia was held at the last pass (pick 2 (a), "hold, and re-measure"). Re-measured since, she was offered 6 times and taken 0, and she has never been taken (0 of 62).
- Kokomi now takes many Companions (15 of 81 since 2026-10-12), because she can play any Companion on her jellyfish.
- But Klee, Furina and Varka still hold about one per deck.
- Navia is a Geo character whose kit is built on Crystallize, so a reaction trigger is closer to her than a Companion count.

**Arlecchino stays as is.** The HP-for-Strength version is one day old and has 8 offers, too few to judge. It is a 1-cost Power giving +1 Strength a turn, which on paper beats Inflame (+2 once, `game_ref/ironclad-cards.yaml`) by turn 3.

## How Fontaine fits today's four

- **Furina (home Fontaine) sees these cards most.** Half of her Companion draws come from Fontaine's 16 cards, so she meets each Fontaine Common about 5 times as often as the other kits do (0.048 vs 0.010 per roll). She was offered Fontaine cards 840 times against 48 for Klee.
  - So the dead cards cost Furina most: she skipped Shattering Pressure 103 times.
  - Fixing the Commons is mostly a Furina fix.
- **Kokomi** fits Fontaine well. Clorinde's Electro and Freminet's Cryo react with her jellyfish's Hydro (Electro-Charged and Frozen). She takes Fontaine cards at 15 of 81.
- **Varka** takes the element-appliers (Bursting Grenades, Astonishing Shift, Enigmatic Feint), because any Pyro, Hydro, Cryo or Electro applied sets his element (`STATE.md`). An element on Shutter and Floe helps him directly.
- **Klee** rarely meets them (48 offers in four days), and that is fine.
- **One flavor note, no pick.** Furina's Guest Stars include Clorinde, Navia, Neuvillette, Lynette, Charlotte, Chevreuse and Freminet. Her deck can hold "Guest Star: Clorinde" and "Clorinde — Impale the Night" side by side. The names read as two different things, and I'll watch the seat pages for confusion.

**Fontaine is small:** 4 Uncommons against Mondstadt's 18. Growing it belongs to the rest of the nation sweep, which this paper does not try. One more fact for that sweep: the Featured Banner shows 3 of Fontaine's 4 Rares each run, so one is always missing.

## Ruled 2026-10-12

[USER]: "On the Fontaine cards - I don't like to have cycling at Common, so Vanguard's Valor either needs a rarity bump or a power-up minus the draw effect. Otherwise looks good!"

- **Pick 1 (a), with one change:** Vanguard's Valor stays a Common and does not draw. It becomes "Your next Attack deals 6 [8] additional damage, plus 3 if an Elemental Reaction triggered this turn." The other five Commons are as listed.
- **Picks 2 and 3, (a).**

## For [USER] (ruled above)

1. **The six Commons**, each about one upgrade's worth:
   - Interdiction Fire: 7 → 8 [10] Pyro damage, in line with Pers, Deploy!.
   - Vanguard's Valor: "Your next Attack deals 3 [5] additional damage, plus 3 if an Elemental Reaction triggered this turn. Draw 1 card." It replaces itself.
   - Bogglecat Box: "Gain 4 Block. Draw 2 [3] cards." Backflip, with Backflip's Block point moved into Lynette's upgrade.
   - Freezing Point: 6 → 7 [9] Cryo damage, draw 1.
   - First-Person Shutter: adds "Apply Cryo to an enemy". Block unchanged at 4 [6] now and next turn.
   - Pressurized Floe: its 10 damage becomes Cryo damage.
   - **(a) Default:** all six.
   - (b) Only the three never taken (Valor, Box, Shutter).
2. **Freminet — Shattering Pressure** becomes an Uncommon Attack: "Deal 5 [7] Cryo damage twice." That is 10 per Energy, the Colorless Uncommon level (9.8 per Energy, `colorless_census`). Against a Hydro-wet enemy the first hit Freezes, so the second can Shatter. That is Freminet's Genshin trick in one card. I check in the engine that a second hit may Shatter a freeze the first hit made; if not, the card still stands at 10 per Energy.
   - **(a) Default:** yes.
   - (b) Keep the Power and leave it for the nation sweep.
3. **Navia — Cannon Fire Support** triggers on reactions: "Whenever an Elemental Reaction happens, gain 4 [6] Block." This is the last paper's pick 2 (b), for Navia only. Nicole's Ladder and Raiden are not Fontaine and stay held.
   - **(a) Default:** yes.
   - (b) Hold again until the whole sweep.
