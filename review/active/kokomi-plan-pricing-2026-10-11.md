# Kokomi: what a Plan should pay for its delay, 2026-10-11

[USER], after his Kokomi run (floor 9, Phantasmal Gardeners, the second of two elites in a row):
- "I constantly felt energy-starved for everything; I think the idea of the tension around Planning works, but the one turn penalty is currently too punishing - I couldn't afford to put plans into motion, and I couldn't afford to use the casket when I had charge."
- "None of the cards that I saw when drafting felt obviously amazing, because even though I saw synergies, the numbers didn't balance to something effective under the pressure."
- "I also agree that we should check that the Plan payoff is higher than the base rates."
- On the starter: "I'm also fine with modifying the starters if the rates are low."

The Casket half is already ruled and built separately: Open the Casket costs 0, then 1 more each time it is played that fight.

This paper is the Plan half. The census behind it is in the session scratchpad (`kokomi-plan-census.md`). It reads every Kokomi row with a Plan line in `docs/prototype-surface.yaml` and the base five's plain damage and Block cards in `game_ref/`. The base samples are small, and each median is given with its n.

## What the base game charges for a delay

The base game never delays a whole card. A delay is always a rider on top of a full on-turn effect, and it is priced at about 0.8 of the same effect now:
- Dodge and Roll: 4 Block now, and 4 Block next turn.
- Glitterstream: 11 Block now, and 5 Block next turn.

So, in the base game, Block or damage a turn later is worth about 80% of the same thing now. A card that is only delayed has to print about 1.25 times the on-turn number just to break even.

## What Kokomi's Plans pay

A card with a Plan line is played either now or as a Plan, not both. So the fair comparison is the Plan number against a base card of the same cost and target played now.

| Card (cost) | Plan | Base on-turn median, same cost and target | Ratio |
|---|---|---|---|
| Surging Shoal (2) | 22 single | 15 (n=2) | 1.47 |
| Ambush (1) | 12 single, and 2 Vulnerable now | 10 (n=7) | 1.20, plus the Vulnerable |
| Kurage's Oath (1, starter) | 7 to ALL | 7 (n=3) | 1.00 |
| Flank (1) | 8 to each enemy that intended to attack | 7 | 1.14 if all of them do |
| Signal Arrow (1) | 3 to ALL, twice (6) | 7 | 0.86 |
| Pearl Current (1) | 2 to ALL, 3 times (6) | 7 | 0.86 |
| Undertide Lance (2) | 12 single, 24 if alone | 15 | 0.80, or 1.60 if alone |
| Masterstroke (3, Rare) | 30 single | 27 (n=3) | 1.11 |
| Nip (0) | 5 single | 6 (n=5) | 0.83 |
| Jellyfish Drift (0) | 3 [4] to ALL | 5.5 (n=2) | 0.55 |
| Brine Sting (0) | 3 single, and 1 Weak | Claw 3 | 1.00 |
| Bubble Ward (0) | 4 Block next turn | Deflect 4 | 1.00 |

- **Two of the twelve pay a premium for the delay:** Surging Shoal and Ambush.
- **The rest pay the on-turn rate or less, a turn late.** That is the one-turn penalty [USER] felt.
- On top of the number, each Plan carried out adds 1 to the Casket. That is a small rider, about the size of the base game's own delayed riders, not a premium.
- **Unaffected:** Dusk Plans (Shell of Sanctuary, Breakwater, Evening Watch, Brace for the Tide) land at the end of the same turn, so they carry no delay and stay at the on-turn rate.
- **Already priced:** Read the Field, Tide Wall and Kelp Wall add scry, the incoming attack or statuses to their Block. They are at or above rate today.

## The fix: one ratio, no caps

A Plan that lands next turn prints **1.3 times** the base on-turn median for its cost and target.
- That is the 1.25 break-even plus a small premium, so writing a Plan is worth the turn it waits.
- Cost-0 Plans get the ratio against the cost-0 median, because they cost a card but no Energy.

| Card | Today | New | Upgrade |
|---|---|---|---|
| Signal Arrow | 3 to ALL twice | 4 to ALL twice | 5 twice |
| Pearl Current | 2 to ALL 3 times | 3 to ALL 3 times | 4 three times |
| Flank | 8 to attackers | 9 to attackers | 12 |
| Undertide Lance | 12, doubled if alone | 14, doubled if alone | 18 |
| Masterstroke | 30, Strength 3 times | 35, Strength 3 times | 45 |
| Nip | 5 | 7 | 9 |
| Jellyfish Drift | 3 [4] to ALL | 6 to ALL | 8 |
| Brine Sting | 3 and 1 [2] Weak | 4 and 1 [2] Weak | unchanged Weak |
| Bubble Ward | 4 Block | 5 Block | 7 |
| Kurage's Oath (starter) | 7 to ALL | 9 to ALL | 12 |

- **Not changed:** Surging Shoal and Ambush, which already pay a premium, and every on-turn number.
- **The starter is in, on [USER]'s word.**
  - **Kurage's Oath:** its Plan takes the same ratio, 9 to ALL [12]. Its 6 [8] Block now is unchanged, because it is already above a Defend.
  - **Slack Water:** its on-turn rate is low, too. It deals 4 [7] damage and applies 1 Weak for 1 Energy. The Silent pays 8 damage and 1 Weak for 1 Energy with Sucker Punch, a Common, or 3 damage and 1 Weak for 0 Energy with Neutralize, her starter (`game_ref/silent.json`). The new Slack Water deals 6 [9], with its Weak and its Plan line unchanged.

## How it is checked

- The next whole-run seat round, on the five seeds, runs after your Furina run. It includes this change and the Casket change.
- Lines:
  - act-1 normal fights cost 9.0 HP or less, against 11.0 today;
  - act-1 normal fights are not more than 10% shorter than base, so this doesn't trivialise act 1;
  - the act-2 boss damage median is at 40 a turn or more.
- If act 1 overshoots, the lever is the ratio, not a cap.

## For [USER]

1. **The Plan ratio.**
   - **(a) Default:** 1.3 times the base on-turn median, on the nine cards above.
   - (b) 1.25 times, which is exactly break-even.
   - (c) 1.5 times, as Surging Shoal already is. This is a bigger swing, so the round would check act 1 harder.
2. **The starter (ruled: "I'm also fine with modifying the starters if the rates are low").** Kurage's Oath's Plan goes to 9 [12] to ALL, and Slack Water to 6 [9] damage, as above. No pick.
