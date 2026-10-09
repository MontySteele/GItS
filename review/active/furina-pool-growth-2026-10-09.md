# Furina: the pool to 75, and Guests as an archetype

Paper, 2026-10-09. Main session design. It comes from the human co-op run
(`review/records/coop-human-playtest-2026-10-09.md`, pick 4) and [USER]'s
ruling: "start with these trims and readjust after the card pool expands."
The counts are from a census of `docs/prototype-surface.yaml` and
`game_ref/*.json`, with the 2026-10-09 trims applied (PR #988). Card rows go
in `docs/prototype-surface.yaml` once ruled.

## 1. What the play asked for

- **Guests should be a plan of their own.** They were "insane" in act 1 and
  faded by act 3. The friend's suggestion was to let them spend Fanfare.
- **She needs scaling outside the Fanfare bank.**
- **Drain should sometimes put her in danger,** and Repay should matter
  more.
- **The pool is small.** It has 34 cards, against 78 for the other kits.

## 2. Where the gaps are

| | Furina now | Base five | Klee / Kokomi / Varka |
|---|---|---|---|
| Common / Uncommon / Rare | 10 / 17 / 7 | 20 / 38 / 27 | about 21 / 34 / 21 |
| Common Skills | 3 | 7–11 | — |
| Uncommon / Rare Powers | 4 / 4 | 7–10 / 9–10 | 4–8 / 10–14 |
| Scaling sources | 8 | 18–22 | 15–26 |
| Common AoE attacks | 2 | 1–2 | 0–2 |

- **Archetype sizes:**
  - Drain (Ousia): 9.
  - Repay (Pneuma): 6, the smallest, with 2 Commons.
  - Fanfare (the Crowd): 10.
  - Guests: 7.
  - Bridges: 2.
- **What this means:** Common Skills, Powers and Pneuma are the holes.
  Common AoE is already full, so none is added.

## 3. How Guests scale

Guests scale by **acting more often, paid for with Fanfare.** A guest's
own numbers never grow. This keeps the line from 2026-09-07: "must not be
a Defect with Fanfare for Focus."

Fanfare grows across a fight. A guest act bought with Fanfare is therefore
worth more in act 3 than in act 1, which is the fade the play reported.

- **Common:**
  - Encore!, one bought act.
  - Casting Call, which finds a guest.
- **Uncommon:**
  - Tutti!, every guest acts.
  - Final Bow, one guest acts twice and leaves.
  - Grand Entrance, guests feed Fanfare.
- **Rare:**
  - Showstopper, every turn's acts are bought again.
  - Ensemble Cast, a fourth seat. It bends the three-seat rule.

**Fanfare still comes only from HP.** Every new source goes through Drain,
Repay or HP lost. Grand Entrance Repays; it does not print Fanfare.

## 4. Scaling outside the bank

Each archetype gets one permanent scaler at Rare and one Uncommon Power:
- **Ousia:** Regina of All Waters, Strength paid for with a Drain each
  turn.
- **Pneuma:** Hymn of Renewal, Vigor from Repay.
- **Crowd:** Standing Room Only, Strength from cashing everything in.

Two cards reward being at the Drain line: Against the Tide and High Stakes.
That is the danger the play asked for, kept inside the line, which stays
(ruled pick 3).

## 5. The 41 new cards

Upgrades are in brackets. "Oldest guest" is the one a fourth summon would
remove.

**Guests and stage (11): 2 Common, 4 Uncommon, 5 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Casting Call | Skill 1, C | Choose 1 of 3 random Guest Stars. It costs 0 this turn. Exhaust. [of 4] |
| Encore! | Skill 0, C | Spend 4. Your oldest guest acts. Draw 1 card. [Spend 3] |
| Tutti! | Skill 1, U | Each guest acts. Retain. [cost 0] |
| Final Bow | Skill 1, U | Your oldest guest acts twice, then leaves. [3 times] |
| Grand Entrance | Power 1, U | Whenever you play a Guest Star, Repay 2. [3] |
| Guest Star: Freminet | Skill 1 [0], U | Line: the first time a guest leaves each turn, draw 2 cards. Act: deal 5 Cryo damage to a random enemy. |
| Showstopper | Power 2 [1], R | At the end of your turn, if you have 5 Fanfare, Spend 5: your guests act again. |
| Ensemble Cast | Power 2 [1], R | You have 4 guest seats. |
| Guest Star: Navia | Skill 1 [0], R | Line: your first Spend each turn costs 2 less. Act: deal Geo damage to a random enemy equal to the Fanfare you spent this turn. |
| Guest Star: Neuvillette | Skill 2 [1], R | Line: your Hydro damage deals 2 more. Act: deal Hydro damage to ALL enemies equal to the HP you Drained this turn. |
| Guest Star: Escoffier | Skill 1 [0], R | Line: whenever a guest acts, Repay 1. Act: deal 4 Cryo damage to ALL enemies. |

**The Crowd (9): 3 Common, 3 Uncommon, 3 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Crashing Waves | Attack 1, C | Deal 4 Hydro damage twice. Spend 4: three times instead. [5] |
| Bubble Aria | Skill 1, C | Gain 6 Block. Spend 3: also draw 2 cards. [8] |
| Commanding Gaze | Skill 1, C | Apply 1 Vulnerable. Spend 4: apply 2 Vulnerable and 2 Weak instead. [3 and 2] |
| Star Turn | Attack 2, U | Deal 15 damage. Costs 1 less for every 6 Fanfare you have. [20] |
| Sold Out | Skill 1, U | Spend 6. Gain 1 Energy. Draw 2 cards. [Spend 4] |
| Crescendo | Power 1, U | The first time you Spend each turn, draw 1 card. [Innate] |
| Prima Donna | Power 1, R | At the start of your turn, if you have 10 or more Fanfare, gain 1 Energy. [Innate] |
| Standing Room Only | Power 2 [1], R | Whenever you Spend all your Fanfare, gain 1 Strength. |
| Bring the House Down | Attack 2 [1], R | Spend all your Fanfare. Deal that much damage. Each guest acts. |

**Ousia, Drain (10): 3 Common, 4 Uncommon, 3 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Undercurrent | Attack 1, C | Drain 2. Deal 5 damage, plus 1 for each time you have Drained this combat. [7] |
| Overdraft | Skill 0, C | Drain 4. Gain 1 Energy. [Drain 3] |
| Ousia Pledge | Skill 1, C | Drain 3. Draw 2 cards. [3 cards] |
| Against the Tide | Attack 1, U | Deal 8 damage. If you are at your Drain line, deal 14 instead. [11 / 18] |
| Pay the Tab | Skill 1, U | Drain down to your line. Draw 1 card for every 4 HP drained. Exhaust. [every 3] |
| Riptide Lunge | Attack 1, U | Drain 3. Deal 10 damage. If this kills an enemy, Repay 6. [13] |
| High Stakes | Power 1, U | While you are at your Drain line, your Attacks deal 4 more damage. [6] |
| Regina of All Waters | Power 2 [1], R | At the start of your turn, Drain 3. If you do, gain 1 Strength. |
| The Deluge | Attack 2 [1], R | Drain down to your line. Deal that much damage to ALL enemies. Exhaust. |
| All In | Skill 1, R | Drain down to your line. Gain 1 Energy for every 6 HP drained. Exhaust. [every 4] |

**Pneuma, Repay (10): 4 Common, 4 Uncommon, 2 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Soothing Waters | Skill 0, C | Repay 2. Draw 1 card. [Repay 3] |
| Gentle Current | Skill 1, C | Gain 5 Block. Next turn, Repay 4. [7 and 5] |
| Clean Slate | Attack 1, C | Deal 7 damage. Repay 3. If you have no drained HP left, draw 1 card. [10] |
| Hydro Lance | Attack 2, C | Deal 14 Hydro damage. Repay 4. [18] |
| Cleansing Torrent | Attack 2, U | Deal 10 Hydro damage to ALL enemies. Repay 4. [14] |
| Balance the Books | Skill 1, U | Deal damage to ALL enemies equal to your drained HP. Repay 4. [Repay 6] |
| Rising Tide | Attack 1, U | Deal 6 damage, plus 3 for each time you Repaid this turn. [4 per] |
| Pneuma Tides | Power 1, U | At the start of your turn, Repay 2. [3] |
| Hymn of Renewal | Power 2 [1], R | Whenever you Repay, gain that much Vigor. |
| Grand Absolution | Attack 2 [1], R | Repay all your drained HP. Deal that much damage to ALL enemies. Exhaust. |

**Bridge (1):** Ebb and Flow (Skill 1, U): "Drain 4, then Repay 4."
[Drain 6, Repay 6] It nets no HP and makes 8 Fanfare.

**After this batch:**

| | Common / Uncommon / Rare | Common Skills | Uncommon / Rare Powers | Common AoE |
|---|---|---|---|---|
| Furina | 22 / 33 / 20 (75) | 11 | 8 / 10 | 2 |

Three slots, one at each rarity, are held for what the first seat round
shows is missing.

## 6. Risks, checked before seats

- **Loops.** The build runs the loop probe on these combinations:
  - Encore! with Escoffier;
  - Tutti!, Showstopper and Bring the House Down together;
  - Freminet with 0-cost upgraded guests.

  Freminet draws once a turn, and Casting Call exhausts, so neither can
  chain.
- **Guests react most to the Drain line.** In the 2026-10-09 Drain-line
  sim the built guest deck won act 1 57% of the time, below the balanced
  deck's 64%. With the line at 1 HP it rose to 76%, and its act-2 boss wins
  went from 8% to 57%. Seats are asked whether a guest deck still needs
  Fanfare by act 3.
- **More Energy cards.** Overdraft, Sold Out, Prima Donna and All In bring
  her to 6, within the base range of 3 to 7. The play asked whether
  Fanfare has become a second Energy; the seats get that question.

## Picks

1. **Guests scale by acting more often, paid in Fanfare, never by a guest
   stat.** The other way would reopen the 2026-09-07 "not Focus" ruling.
   **Default: yes.**
2. **Fanfare still comes only from HP.** New Fanfare sources go through
   Drain, Repay or HP lost. **Default: yes.**
3. **The pool targets 75, with 3 slots held** for the first seat round.
   **Default: yes.**
4. **The 41 cards above, built as one batch.** Then the loop probe, then a
   solo Furina seat round with an Ironclad control, then [USER]'s play.
   **Default: yes, as written.**
