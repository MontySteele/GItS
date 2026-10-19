# The Fontaine companion pool, reworked (2026-10-19)

[USER], 2026-10-19: "at some point we should give the Fontaine companion pool
the same treatment we just gave Inazuma's. I think it's also currently
undersized." On the audit (`review/active/fontaine-companions-audit-2026-10-19.md`):
"while the (a) picks are largely fine, we may still want to leave some
Companions at multiple Commons so the Common pool has more than 4 cards in
it." Picks 2 (guest stars may also be companions) and 3 (even out the
elements) went (a).

So the direction is ruled: about 30 cards, 8 Commons, the five missing 5-stars
added, and fewer Cryo cards. The card designs below are mine and carry no
pick. The numbers are first-pass and go to a seat round. Yardsticks are base
cards from the decompiled game: Pommel Strike (1, 9 and draw 1), Iron Wave
(1, 5 and 5 Block), Backflip (1, 5 Block and draw 2), Burning Pact (1,
Exhaust a card, draw 2), Hemokinesis (1, lose 2 HP, 14), Disarm (1, -2
Strength, Exhausts), Feel No Pain (1, 3 Block per Exhaust), Adrenaline (0,
+1 Energy and draw 2, Exhausts).

## A theme the pool did not have: paying HP

Fontaine's fighters spend their own health (Arlecchino's Bond of Life,
Lyney's Prop, Wriothesley's Chilling Penalty). The pool already has one such
card, Arlecchino's Masque of the Red Death. Three more cost HP, and
Wriothesley's Rare pays off any HP lost, including to enemy attacks, so it is
never dead.

## The pool after: 30 cards (8 / 13 / 9), 5 Powers

**Kept as they are (5):** Chevreuse, Ring of Bursting Grenades (taken 24%);
Charlotte, Snappy Silhouette; Clorinde, Impale the Night (13%); Neuvillette,
Heir to the Ancient Sea's Authority (29%); Arlecchino, Masque of the Red
Death.

### Commons (8: two each for the four 4-stars)

| Card | Cost | Text (upgrade) | Was |
|---|---|---|---|
| Chevreuse, Interdiction Fire | 1 Attack | Deal 7 [9] Pyro damage. Apply 1 Vulnerable. | 8, nothing else |
| Chevreuse, Vanguard's Valor | 0 Skill | Your next Attack this turn deals 6 [9] additional damage. | +3 more after a reaction |
| Lynette, Enigmatic Feint | 1 Skill | Gain 8 [11] Block. Swirl the enemy. | 5 Block |
| Lynette, Bogglecat Box | 1 Skill | Gain 5 [8] Block. Draw 2 cards. | 4 Block, upgrade drew 3 |
| Charlotte, Framing: Freezing Point | 1 Attack | Deal 8 [10] Cryo damage. Draw 1 card. | 7 |
| Charlotte, First-Person Shutter | 1 Skill | Gain 6 [9] Block. Apply 1 Weak. | Dodge and Roll with Cryo |
| Freminet, Pers, Deploy! | 0 Attack | Deal 4 [6] Cryo damage. | 1 cost, 8 |
| Freminet, Pressurized Floe | 2 Attack | Deal 12 [16] Cryo damage. Gain 6 [8] Block. | 10 and 6 |

- **Feint** used to need an aura to be more than 5 Block. Now the Block is the
  card and the Swirl is the bonus.
- **Bogglecat Box** is Backflip.
- **Shutter** loses its Cryo (one fewer Cryo card) and gains the pool's first
  Weak.
- **Pers** becomes a 0-cost aura applier, the cheapest way into a reaction in
  the pool. It draws nothing, so it does not cycle.

### Uncommons (13)

| Card | Cost | Text (upgrade) |
|---|---|---|
| Chevreuse, Ring of Bursting Grenades (kept) | 2 Attack | Deal 14 Pyro damage to ALL enemies. |
| Lynette, Magic Trick: Astonishing Shift (rebuilt) | 1 Skill | Swirl the enemy. Deal 6 [8] damage to ALL enemies. Apply 1 Weak to ALL enemies. |
| Charlotte, Snappy Silhouette (kept) | 0 Skill | Apply 1 Vulnerable. Draw 1 card. |
| Freminet, Shattering Pressure (rebuilt) | 1 Attack | Retain. Deal 8 [10] damage. Each time you Retain this, it deals 5 more this combat. |
| Navia, Ceremonial Crystalshot (new) | 1 Attack | Deal 10 [13] Geo damage. If this triggers Crystallize, draw 1 card. |
| Clorinde, Hunter's Vigil (new) | 1 Skill | Draw 2 [3] cards. Your next Attack this turn applies Electro. |
| Neuvillette, O Tears, I Shall Repay (new) | 1 Attack | Deal 7 [10] Hydro damage to ALL enemies. |
| Arlecchino, Balemoon Rising (new) | 1 Attack | Lose 2 HP. Deal 12 [16] Pyro damage. |
| Wriothesley, Gracious Rebuke (new) | 1 Attack | Deal 7 [9] Cryo damage. The enemy loses 1 Strength. |
| Lyney, Grin-Malkin Hat (new) | 1 Power | Whenever you Exhaust a card, deal 4 [6] Pyro damage to a random enemy. |
| Sigewinne, Rebound Hydrotherapy (new) | 1 Power | At the start of your turn, gain 3 [4] Block and apply Hydro to a random enemy. |
| Escoffier, Low-Temperature Cooking (new) | 1 Skill | Gain 8 [11] Block. Next turn, draw 1 card. |
| Emilie, Lumidouce Legacy (new) | 1 Skill | Exhaust a card in your hand. Draw 2 [3] cards. |

- **Astonishing Shift** was a Common number at Uncommon. Weak to everyone is
  what lifts it.
- **Shattering Pressure** is Freminet's pressure gauge: held, it grows. It is
  the pool's Retain card. In the game it is Physical, so it has no element.
- **Crystalshot:** a Geo hit on an aura is Crystallize, which already gives
  Block (`ReactionTable.cs` line 78). Navia now applies Geo; she used to apply
  nothing.
- **Hunter's Vigil** is the pool's first draw at Uncommon.
- **Gracious Rebuke** takes Strength for good, 1 at a time, and does not
  Exhaust: Disarm takes 2 and Exhausts.
- **Balemoon Rising** is Hemokinesis at 12 with a Pyro aura.
- **Grin-Malkin Hat** and **Lumidouce Legacy** are the pool's Exhaust synergy;
  Lyney's Rare feeds the Hat.
- **Rebound Hydrotherapy** is the Block Power and a free Hydro aura each turn,
  like Neuvillette's.

### Rares (9)

| Card | Cost | Text (upgrade) |
|---|---|---|
| Navia, Cannon Fire Support (rebuilt) | 2 Power | At the start of your turn, deal 5 [7] Geo damage to ALL enemies. |
| Clorinde, Impale the Night (kept) | 2 Attack | Deal 20 Electro damage. Your later Attacks against enemies holding an aura deal 6 additional damage. |
| Neuvillette, Heir to the Ancient Sea's Authority (kept) | 1 Power | At the start of your turn, deal 5 Hydro damage to a random enemy. Auras you apply last 1 additional turn. |
| Arlecchino, Masque of the Red Death (kept) | 1 Power | At the start of your turn, lose 1 HP and gain 1 Strength. |
| Wriothesley, Chilling Penalty (new) | 1 Power | Whenever you lose HP, deal 5 [7] Cryo damage to a random enemy. |
| Lyney, Wondrous Trick: Miracle Parade (new) | 0 Skill | Lose 4 HP. Gain 2 Energy. Draw 2 [3] cards. Exhaust. |
| Sigewinne, Super-Saturated Syringing (new) | 2 Attack | Deal 10 [13] Hydro damage to ALL enemies. Gain 4 Block for each enemy hit. |
| Escoffier, Rehab Diet (new) | 1 Skill | Gain 10 [13] Block. Mend 6 [9]. Exhaust. |
| Emilie, Aromatic Explication (new) | 1 [0] Power | At the start of your turn, Exhaust a Status or Curse from your hand or draw pile. If you did, gain 1 Energy. |

- **Cannon Fire Support** was the lowest Rare take (3%): Block only after a
  reaction. Now it hits everyone every turn, and on an aura each hit is a
  Crystallize.
- **Miracle Parade** is Adrenaline with a second Energy for 4 HP, and it
  Exhausts into the Hat.
- **Chilling Penalty** pays off the HP cards and enemy attacks alike.
- **Rehab Diet** is the pool's one heal, Exhausting, like Mizuki's Anraku.
- **Aromatic Explication** turns the Wounds and Dazed the game hands you into
  Energy. Emilie is Dendro, which the mod has no aura for, so her cards have no
  element.

## What changes in the numbers

| | Before | After |
|---|---|---|
| Cards (C / U / R) | 16 (8 / 4 / 4) | 30 (8 / 13 / 9) |
| Characters | 8 | 13 |
| Cards that apply Cryo / Hydro | 6 / 1 | 5 / 4 |
| Apply Pyro / Geo / Electro; Swirl | | 4 / 2 / 2; 2 |
| No element | | 11 |
| Weak, Strength loss, Retain, Exhaust, Energy, Block Power | none | 2, 1, 1, 3, 2, 1 |

Furina's guest stars stay as they are. Each overlapping companion has a
different job from its guest star: Escoffier's guest deals Cryo to ALL, her
companions Block and heal; Lyney's guest Drains, his companions Exhaust and
make Energy.

## The order of work

1. **Build** the 11 rebuilt rows and the 14 new ones on the sheet,
   with codegen, tests, and companion art for the five new characters.
2. **Then a seat round** (a new card batch): two seats, each with a one-page
   record, on kits that draft companions.

No picks.
