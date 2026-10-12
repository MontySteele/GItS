# Kokomi round 1 on the Plans and Ethereal build, 2026-10-12

**What ran.** Eight whole-run Sonnet Kokomi seats, plus one Silent control, all at A0. The build was 0.2.4999 (`main` at 130330e4): the re-founding in #1128 plus the pre-round fixes in #1129. It is the first round without the Casket.

The seat records, the offer output (`k1/offers.txt`), the telemetry script (`k1/kokomi_round.py`) and a Fable review (`k1/fable-review-round1.md`, which this page draws on) are in the session scratchpad.

## Result: no wins; four of eight reached act 3

| Seed | End | Came in at |
|---|---|---|
| M2DMHTB8M4UV | Floor 22, act-2 normal fight | 26/80, after a Lantern Key fight it chose |
| 1Y31DRCMCER8 | Floor 30, act-2 elite (forced) | 13/83 |
| TCD7XG26A3MQ | Floor 39, act-3 normal fight | 18/70 |
| ET6DP8PHEBDN | Floor 48, act-3 boss (Aeonglass at 96/512) | 75/78 |
| 7VLRB2ZXAWLW | Floor 48, act-3 boss (the Queen) | 80/80 |
| XG1UCXR3UF18 | Floor 48, act-3 boss (Aeonglass at 334/512) | 28/78 |
| 5SDJU6ZZP4BA | Floor 11, act-1 elite (forced) | 54/80 |
| L8BD4L2L8YC3 | Floor 33, act-2 boss; the seat miscounted lethal by 2 | 79/85 |
| Silent control, G1320SE5AVNZ | Floor 40, act-3 elite (forced) | 24/74 |

**Normal fights, median by act, with the base five in brackets:**

| | Damage a turn | HP lost | Block a turn |
|---|---|---|---|
| Act 1 | 18.2 [19.0] | 8.8% [10.0] | 2.7 [2.5] |
| Act 2 | 25.1 [30.2] | 11.9% [15.0] | 8.3 [5.7] |
| Act 3 | 22.8 [38.2] | 15.6% [10.6] | 13.6 [9.4] |

## What played well

- **The clunk is gone.** Every record names Plan-or-play-now and the order of the queue as its real decisions. No seat had a turn spent just clicking Plans.
- **Her act-1 start is fixed.** She loses 8.8% of her HP per act-1 normal fight; the Casket build lost 12.5%.
- **Both flavours show up and mix.** Every written Companion reacted with the jellyfish's Hydro. The reactions were Electro-Charged 130 times, Frozen 37 and Vaporize 32. The best turns came from Nereid's Ascension, which doubled Masterstroke to 84 and Undertide Lance to 36, and from Plans landing on turns the enemy did not attack.
- **Block is not thin.** She blocks more than the base five in every act.

## What did not

- **Late growth.** Her act-3 damage is 60% of the base five's; the Casket build managed 42.5 a turn there, against 22.8 now. Strength reached 3 or more in only 19 of 140 fights. Nothing replaced the Casket's Strength, because the engine Powers meant to were never drafted.
- **The flavour payoffs were never drafted:** 0 of 26 offers. Her own Commander cards were taken 2 of 17 times; the Commander decks ran on the shared Companion pool.
- **Dead cards:**
  - Call the Generals and Watatsumi Muster: a 1-cost card that hands you a 2- or 3-cost Ethereal card.
  - The jellyfish generators Drift and Drill, which play like a Strike minus one.
- **Ethereal:** 1.25 cards lost a fight. Seats read this as a question of Energy, not a grievance.
- **Slack Water,** a starter card, was named NEVER AGAIN twice.

## What to change

1. **Built for round 2, all Claude's calls (`kokomi-round2-changes-2026-10-12`):**
   - Jellyfish Drift deals 8, Watatsumi Drill 8, and Bubble Ward gives 7 Block.
   - Watchful Shoal 5, Coordinated Tide 6, Kurage Canopy +1, Grand Strategist 7.
   - Call the Generals' card costs 0 this turn. Watatsumi Muster and Shoal Call cost 0 and Exhaust.
   - Tideturn gets +2 per Plan, and Shoal of Spears goes to 5.
   - Nereid's Ascension gets a tip. Treatise counts Companions.
   - The Tangled name is fixed.
2. **Bugs, built in #1134:** Kelp Wall, Sea Glass Harvest, Tide Wall's text, and the Plan tip on cards that have no Plan line.
3. **For [USER]: where her late growth comes from.** Round 2 tests the changes above first. If act 3 is still low, a Common growth card or Resolve of Watatsumi at Common goes to him as a pick.
4. **BACKLOG:** on the seat page, the "face numbers leave out Vulnerable" note reads as wrong next to faces that do include it (lane 5b).
