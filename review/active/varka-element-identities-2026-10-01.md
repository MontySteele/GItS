# Varka: four element identities

Paper, 2026-10-01. Main session design, on [USER]'s direction. **Picks 1 to 5
RULED at their defaults, 2026-10-01, [USER]: "Overall looks reasonable,
though Violet Storm looks undertuned."** Violet Storm raised (§3).

## 1. Why

The expansion sim (`tools/varka_expansion_sim.py`, PR #789) found Electro mono
21.6 points behind the default drafter, and two sweeps of number patches
closed only a third of that. [USER]: "Overall sounds like a design problem
being patched by printing commons with big numbers." His direction:

> Pyro becomes "hit for very big single target number by oath or strength
> stacking", Hydro gets "get a big block" and probably needs its own payoff
> tied to block generation / oath count (maybe a Rare that deals damage equal
> to Block every turn, max = to oath count?), Cryo deals with statuses and has
> payoffs related to status stacking, and electro has things like "deal x
> damage, draw a card" and payoffs related to big energy or draw effects.

And the guard: "giving one engine both big energy AND card draw becomes
degenerate very quickly, so either the engine pieces need some kind of limit,
or we shouldn't give both without relying on a super-specific high rarity
combo." Varka "doesn't do anything with exhaust or discard effects, and we
could steal that here".

The pool stays 78 (20 / 35 / 23). Each new card replaces one.

## 2. The rule that keeps Electro honest

**Below Rare, no card gains Energy without discarding a card for it.** Draw
is free at Common and Uncommon. Energy costs a card. A draw-and-discard loop
is limited by hand size, so it never makes both resources at once. The
spend-everything payoffs sit at Rare. Two existing cards break the rule and
change with it:

- **Dawn Patrol** (U, 0: gain 1 Energy, draw 1 [2]) gains **Exhaust**. Silent's
  Adrenaline is a Rare Exhaust. A seat called Dawn Patrol+ "the turn engine".
- **Diluc** (U: Energy if a hit reacts) stays as it is. It pays once per play,
  only on a reaction, and it is Pyro's.

## 3. Electro: draw and AoE low, discard into Energy in the middle, spend it at Rare

| Card | Type, cost, rarity | Text | Replaces |
|---|---|---|---|
| Charged Lunge | Attack, 1, C | Deal 6 [9] Electro damage. Draw 1 card. | Updraft (C, a plain "deal 9") |
| Short Circuit | Skill, 0, U | Discard 3 [2] cards. Gain 2 Energy. Apply Electro to an enemy. | Pressure Front (U; seats: "dead except as a combo piece") |
| Chain Lightning | Attack, 2, U | Costs 1 less for each card you discarded this turn. Deal 8 [11] Electro damage to ALL enemies. | Unfurled Banner (U; played in 23% of fights where held) |
| Thundering Verdict (re-aimed) | Attack, X, R | Deal 6 [8] Electro damage to ALL enemies X times, plus 1 for each Electro Oath each time. | the old AoE-plus-Oath card |
| Violet Storm | Attack, 1, R | Discard your hand. Deal 8 [11] Electro damage to a random enemy for each card discarded. | Four Winds' Accord (R; played in 29%) |

Kept as they are: Razor: Awakening and Lisa: Infinite Circuit (Commons, AoE
and Block), Static Field (U, draw on the first Electro each turn), Lisa:
Pulsating Witch (U, AoE apply and draw per enemy), and the Electro Swirl (3 to
ALL).

- **The Energy loop:** Static Field and Charged Lunge draw, Short Circuit turns
  the extra cards into Energy, and the Rares spend it. Thundering Verdict's X
  is the "spend X energy for big damage" payoff. Violet Storm is the "discard
  cards for a big effect" one. It was 6 [8], a Skill; [USER] found it
  undertuned. Ironclad's Fiend Fire (Rare, 2: Exhaust your hand, 7 [10] per
  card, Exhaust) is the yardstick: Violet Storm costs 1, discards instead of
  exhausting, and pays 8 [11] on a random enemy, since it also feeds Chain
  Lightning.
- **The guard:** Short Circuit is Silent's Concentrate (Uncommon, discard 3
  [2], gain 2 Energy) with an Electro rider. Nothing below Rare gives Energy
  for free.

## 4. Hydro: Block, and a payoff that turns it into damage

| Card | Type, cost, rarity | Text | Replaces |
|---|---|---|---|
| Retaliating Tide | Power, 2 [1], R | At the end of your turn, deal damage equal to your Block, up to your Hydro Oath, to a random enemy. | Unbroken Tide (R, 3: keep your Block while Hydro) |

The cap is the guard [USER] named: the payoff grows with Hydro commitment, not
with stacked Block. Unbroken Tide goes because "keep all your Block" plus
Tidal Bulwark (57 Block at Oath 25 in lane 1's act 2) is the wall that cannot
lose. The sim's only turn-cap fights were Block decks that could not kill.
Dusk Guard's guards for Kokomi set the precedent.

## 5. Pyro: one very big hit

| Card | Type, cost, rarity | Text | Was |
|---|---|---|---|
| Wildfire Oath (re-aimed) | Power, 2, R [Innate] | While your current element is Pyro, your first Attack each turn deals additional damage equal to your Pyro Oath. | "Your Swirls' damage hits ALL enemies, plus 1 for each Pyro Oath" (AoE, which is Electro's job now) |

One hit a turn, so multi-hit cards (Squall, Tempest) do not multiply it.
Blazing Charge (U, plus per Pyro Oath) and Sharpshooter (C, hits twice on
Pyro) already make the single big hit.

## 6. Cryo: statuses (check only)

Mika (Weak), Kaeya (Vulnerable), Eula (Cryo Oath per Cryo aura), Glacial Edict
(U, Weak and Vulnerable scaling with Cryo Oath) and Absolute Zero (R, Swirls
debuff ALL) already stack statuses. What is missing is a payoff for stacked
statuses below Rare. It goes on the next Varka batch's list rather than a swap
here, because Cryo mono passed (−8.7).

## 7. Losing your element silently

Four times today a seat played a card of another element and lost the Oath it
was building (Baron Bunny, Mika, Blazing Charge, Favonius Drill). Two fixes
ask nothing of the rules:

1. The card's hover says "Switches your element to Pyro" when it would.
2. The Oath panel flashes the old element's count when it stops being
   current.

## 8. The sim before the build

Rerun `tools/varka_expansion_sim.py` with Electro's focus list updated. The
bars are Electro mono within 10 points, the other decks unmoved, and no new
card dominant or dead. With Short Circuit and Violet Storm, discarding enters
the sim, so check the pilot plays them, or mark them unread as the Kokomi sim
did for Coral Tithe.

## Picks

1. **The rule (§2): below Rare, Energy only by discarding; Dawn Patrol gains
   Exhaust.** Default: yes.
2. **Electro's five cards (§3), replacing Updraft, Pressure Front, Unfurled
   Banner and Four Winds' Accord.** Default: yes.
3. **Retaliating Tide replaces Unbroken Tide (§4).** Default: yes.
4. **Wildfire Oath re-aimed to one big hit (§5).** Default: yes.
5. **The element-switch warnings (§7).** Default: yes (no rule change).
