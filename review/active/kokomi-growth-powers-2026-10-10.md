# Kokomi: two Powers that grow with the fight, 2026-10-10

[USER] on the Kokomi round (#1055), pick 1, replacing the default he first accepted:
- "My intuition: doubling the casket scaling trivialize act 1 but won't solve the later game issues."
- On "the Casket keeps its count": "Idea 1 sounds like a very interesting rare power but too good to be a starter deck mechanic. This all feels like a problem to be solved through the power pool."

So the Casket rule stays at 1 per Plan, and the long-fight fix goes into her Powers.

## The census

My working is in the session scratchpad (`kokomi-power-census.md`). Base-five texts are from memory and are unverified; names, rarities and counts come from `game_ref`.

| | Powers | Powers that grow a stat every turn |
|---|---|---|
| Ironclad | 20 | Demon Form (R), Rupture (U) |
| Silent | 18 | Serpent Form (R), Noxious Fumes (U) |
| Defect | 21 | Echo Form (R), Creative AI (R) |
| Necrobinder | 20 | Reaper Form (R), Countdown (U) |
| Regent | 19 | Genesis (R), Arsenal (R) |
| **Kokomi** | **15 (4 U, 11 R)** | **none** |

- Every base character has at least two, and every other kit has some: Klee 14, Varka 8, Furina 6.
- Kokomi's only growth is the Casket, which costs 1 Energy per cash-in. Her Strength reached 3 or more on 18% of turns.
- The round's Power offers: 26 offered, 4 taken. **No Rare Power was played in five runs.**

## The two cards

**1. Rising Tide (new Uncommon; replaces The General's Banner).**
- Cost 1, Power: "At the start of your turn, the Casket gains 1." Upgrade: Innate.
- It adds 3 points in a 3-turn hallway and 9 in a 9-turn boss. It grows with fight length, and it feeds the Casket she already has, so Open the Casket, Driftglass, Shell Guard and Depths' Judgment all read it.
- The General's Banner ("first Companion card each turn applies 1 Weak to the front enemy") was offered 3 times and never taken. Its Weak job is covered by Ambush, Feint and Slack Water.

**2. Grand Design becomes "the Casket keeps its count" (Rare, bent).**
- Today: "Whenever the Bake-Kurage carries out a Plan, the Casket gains 1 more for each Energy paid for it." It was offered once and never taken.
- New: Power, cost 2 [1]: "Open the Casket no longer empties the Casket."
- The core decision stays a Casket Rare that makes the Casket grow, which is what "Rares bend" asks for.
- **The risk:** with the count kept, each Open gives more than the last, so Strength grows faster than linearly. Opening every turn at about 1.5 Plans a turn could reach roughly 50 Strength by turn 9. Demon Form reaches about 18.
- So it is **simmed before it ships**, with the same marginal-value tool used for Converging Winds (#1042): deck plus card against deck plus Strike, across hallway and boss fights, with Demon Form as the reference.
- The tuning lever is the ratio: Open gives Strength equal to half the count, rounded down. There is no cap.

## Not changed

- The Casket rule (1 per Plan, Open empties it).
- The starter.
- The other 13 Powers.
- The ruled swap of Abyssal Salvage and Tidecleanse still happens after [USER]'s run (#1055, pick 3).

## When it ships

1. Tier-0 sim of both cards, now. Grand Design's ratio is set so it lands between Varka's best Rares and Demon Form against bosses, and adds about nothing in hallways.
2. If it is ruled, build both.
3. The next whole-run Kokomi round runs on the five seeds, graded on four lines:
   - act-2 boss damage a turn is above 40 (today 26.9; base 58.4);
   - act-1 normal fights do not speed up by more than 10%, which tests [USER]'s "trivialise act 1" concern;
   - Rising Tide is taken when offered and played when held;
   - when Grand Design is drafted and played, its fight's top Strength stays under 30.

## For [USER]

1. **These two Powers.**
   - **Default:** yes, sim-gated as above. Grand Design's ratio is set by the sim, and the cards are built after the sim.
   - Alternative: a different growth Power at Uncommon, such as "Your Plans deal 1 more damage each turn" (Rupture-like, no Casket).
2. **Rising Tide replaces The General's Banner.** **Default:** yes. Alternative: it replaces Kurage Canopy instead (also 0 of 3 offers taken, a 1-Block-per-Plan Power).
