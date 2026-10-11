# Uncommon and Rare Companions: a pricing pass, 2026-10-11

This is the Klee pass round record's pick 1, ruled (a): the next Companion paper starts with the Uncommon and Rare Companions, priced card by card against the native cards they lost to. The nation sweep and the dead cards are its second half, in a later paper.

**The bar** is yours (2026-10-11): "The Uncommons and Rares should be Colorless-tier (generally a little better than a character's own at the same rarity)."

## The evidence

The packet is `companion-ur-packet.md` in the session scratchpad, which is gitignored. It covers 28 whole-run seat runs from tonight: Klee 10, Kokomi 10 and Furina 8, with the Ironclad control excluded. That is 545 reward screens and 544 fights.

| | Companion | The kit's own card |
|---|---|---|
| Uncommon, taken (non-boss screens) | 9 of 152, 5.9% | 124 of 541, 22.9% |
| Rare, taken on boss screens | 4 of 44, 9% (see below) | 33 of 121, 27.3% |

- **On boss screens the gap is the same in every kit.** Klee took 1 of 23 Rare Companions, Kokomi 2 of 17 and Furina 1 of 11.
- **Every one of the 44 boss screens showed at least one Rare Companion.** So a dead Rare Companion costs the player a quarter of the most important card reward in the act.
- **Working:** Clorinde (2 of 7, both at boss), Itto (1 of 1), Mona (1 of 4), Chevreuse's Ring of Bursting Grenades (4 of 11) and Yae Miko (1 of 3). No change.
- **Too few offers to judge (2 or fewer):** Ayaka, Eula, Albedo's Solar Isotoma, Nicole's Revelation, Raiden (repriced to 27 tonight), Durin's Binary Form, Jean's Gale Blade, Barbara's Melody Loop and others. No change.

Single cards have small samples, 3 to 11 offers each. What the paper leans on is the shape: whole groups of cards share one reason to lose.

## Three of these are Klee's own cards

Since 2026-10-03, Prune's Hexhunter Chime, Albedo's Dust of Purification and Jean's Lion's Fang have been in Klee's own card pool, not the Companion slot (`KleeOverhaulRoster.cs`, `KLEE_OWN_COMPANION_IDS`).
- Kokomi met Dust of Purification once, through a reward that draws from other characters' pools. That is working as intended.
- The packet counted their offers as Companion offers. Without them, Rare Companions were taken 4 of 44 times on boss screens, not 4 of 51. Every boss screen still showed at least one Rare Companion.
- They are priced below anyway, as Klee cards.

## Shape 1: "For 3 turns" cards pay too slowly

Seven Uncommons spend 1 Energy now and pay a small number for each of the next 3 turns, and most of them Exhaust:

| Card | Today | Taken |
|---|---|---|
| Lisa — Lightning Rose | 5 Electro damage and 1 Vulnerable to a random enemy, 3 turns | 0 of 10 |
| Kaeya — Glacial Waltz | 6 Cryo damage to a random enemy, 3 turns | 0 of 4 |
| Gorou — Juuga | 6 Geo damage to a random enemy, 3 turns | 0 of 3 |
| Chiori — Fluttering Hasode | 6 Geo damage ignoring Block, 3 turns | 0 of 1 |
| Shinobu — Sanctifying Ring | Lose 3 HP; 5 Electro damage to ALL enemies and 5 Block, 3 turns | 1 of 6, played in 12 of 16 fights held |
| Qiqi — Herald of Frost | Cryo twice on a random enemy and 3 Block, 3 turns | 0 of 1 |
| Barbara — Melody Loop | 4 Block; Hydro on the enemy, 3 turns | not offered |

**Totals are fair; tempo is not.** Glacial Waltz deals 18, more than Colorless Ultimate Strike's 14. But a third of it arrives two turns late, often into a dead enemy, and the face shows a 6. Klee is a tempo kit: she ends fights by turn 3. Kokomi's 1.3 delay ratio was priced for one turn of wait, and these wait for two.

**The rule:** the same card over 2 turns, with each number raised so the total is about 10% above today's.
- Glacial Waltz, Juuga, Hasode: 10 a turn for 2 turns (20, up from 18).
- Lightning Rose: 8 damage and 2 Vulnerable a turn for 2 turns.
- Sanctifying Ring: lose 3 HP; 8 to ALL enemies and 8 Block a turn for 2 turns.
- Herald of Frost: Cryo twice and 5 Block a turn for 2 turns.
- Melody Loop: 6 Block; Hydro on the enemy for 2 turns.
- Upgrades keep their current deltas.

## Shape 2: Rares that trail the native Rare they lost to

Each change is about one upgrade's worth:

| Card (cost) | Today | Taken | Lost to | New |
|---|---|---|---|---|
| Arlecchino — Masque of the Red Death (1, Power) | Start of turn: 1 Strength. Your Bond of Life eats the first 5 Block you gain each turn. | 0 of 10 (8 at boss) | Bis!, Prima Donna, Spring Tide; three times the seat took nothing rather than it | "At the start of your turn, lose 1 HP and gain 1 Strength." A Defend a turn was too steep a tax, and HP is Arlecchino's own price |
| Venti — Wind's Grand Ode (2, Exhaust) | 8 Anemo damage to ALL; Swirl ALL at end of turn, 2 turns | 0 of 4 | Sparks 'n' Splash, Dodoco, Kurage Swarm | 14 to ALL. Today it is 4 per Energy; Riptide Ruin is 9 |
| Yumemizuki Mizuki — Anraku (2, Exhaust) | Swirl ALL. Above 70% HP: 18 to ALL; otherwise Mend 10 | 0 of 6, all at boss | Blazing Delight, Grand Design, Singer of Many Waters (twice) | "Swirl ALL enemies. Deal 14 damage to ALL enemies and Mend 6." Boss screens come after a boss fight, when the 70% branch rarely holds |
| Durin — Principle of Purity (2, Power) | Start of turn: 4 Pyro to a random enemy, plus a White or Dark choice | 0 of 6 | Red Knight (twice) | 7 a turn |
| Jean — Dandelion Breeze (2, Power) | End of turn: Swirl the enemy with the most auras; 6 Block | 0 of 4 | (not offered at a boss) | Costs 1 |
| Jean — Lion's Fang (2 [1], Power; Klee only) | Start of turn: if no Bomb of yours went off last turn, 8 Block and draw 1 | 0 of 5 | Blazing Delight, Half a Mountain | Costs 1 [0]. Patience stays the price |
| Varka — Sturm und Drang (2, Power) | Whenever a Swirl happens, your next Attack deals 6 more of that element | 0 of 7 | Blazing Delight, Fireworks Finale, Masterstroke | Adds "At the start of your turn, Swirl a random enemy." Solo decks rarely Swirl, so it needs a source of its own |
| Neuvillette — Heir to the Ancient Sea (1, Power) | Start of turn: Hydro on a random enemy. Auras you apply last 1 more turn | 0 of 6 | Grand Design, Riptide Ruin, Singer of Many Waters | "Deal 5 Hydro damage to a random enemy" in place of "apply Hydro". The damage applies the Hydro |
| Albedo — Dust of Purification (1; Klee only) | Exhaust every status in your hand; largest Bomb grows 6 for each | 0 of 5 | Half a Mountain, Red Knight | Adds "Draw 1 card for each." A status becomes a card as well as growth |

## Shape 3: Uncommons a step short

| Card | Today | Taken | New |
|---|---|---|---|
| Lynette — Astonishing Shift (1) | Swirl the enemy; 6 to ALL | 0 of 10 | 8 to ALL. The ALL-enemies yardstick is 7 per Energy |
| Charlotte — Snappy Silhouette (1) | Apply 2 Vulnerable; draw 1 | 0 of 8 | Costs 0. Shockwave gives 3 Weak and 3 Vulnerable to ALL for 2 |
| Sayu — Muji-Muji Daruma (1, Exhaust) | 2 turns: 6 to a random enemy above 70% HP, else 6 Block | 0 of 8 | 9 either way |
| Prune — Hexhunter Chime (1; Klee only) | 8 [11] Anemo and Swirl; the next Bomb deals that element | 0 of 10 | 10 [13] |

**Left for the nation sweep:**
- the four Sucrose Uncommons (0 of 20 between them);
- Freminet's Shattering Pressure;
- Noelle's Sweeping Time;
- Yoimiya, Diona's Signature Mix and Razor's Lightning Fang.

Mondstadt holds 18 of the 34 Uncommons, so its overlaps are the sweep's question, not a pricing one.

## Not proposed

**Companion-count Rares** (Navia's Cannon Fire Support 0 of 11, Nicole's Ladder of Divine Ascent 0 of 3, Raiden):
- Each pays per Companion card played, and decks hold about 1 Companion at the act-1 boss.
- They are dead because Companions are rarely taken, not because their numbers are low.
- This pass is aimed at that take rate, so re-measure after it lands. That is pick 2.

## For [USER]

1. **Shape 1, the "For 3 turns" rule.** Seven Uncommons pay over 2 turns at about 10% more in total.
   - **(a) Default:** yes.
   - (b) Keep 3 turns and raise the per-turn numbers instead.
2. **Companion-count Rares** (Navia, Nicole's Ladder).
   - **(a) Default:** hold, and re-measure after this pass.
   - (b) Trigger on "whenever an Elemental Reaction happens" instead of "whenever you play a Companion card".
3. **Shapes 2 and 3 as listed:** nine Rares and four Uncommons.
   - **(a) Default:** yes.
   - (b) Rares only, and leave the Uncommons for the nation sweep.

The same-element question (companion paper, pick 1, still open) moves to the nation sweep with your note on Nicole, Durin and Neuvillette.
