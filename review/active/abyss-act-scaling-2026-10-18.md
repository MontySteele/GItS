# Spiral Abyss: "This act" entries scale with the act, 2026-10-18

The user, on Bulwark (2026-10-18): "4 is fine for now, but we probably need to make per-act effects scale by
act. That's a high amount in act 1 and trivial in act 3."

The flat numbers were set against act 1. A "This act" entry is only in force in the act it was taken in
(`AbyssDurations.InForce`, `klee-mod/KleeCode/Abyss/AbyssEntries.cs`). So an entry taken in act 3 meets
act-3 fights with an act-1 number. This paper sets one number per act for each of those entries.

## 1. How much the fights grow

These are the base five's normal fights, all bot runs since 2026-09-01, from `tools/telemetry_report.py
--character base5 --since 2026-09-01 --feed bot` and the scratch ramp script. Medians, except HP lost (a
mean):

| Act | Enemy HP per fight | Your damage per turn | Your Block per turn | HP lost per fight |
|---|---|---|---|---|
| 1 | 60 | 15.8 | 2.5 | 5.9 |
| 2 | 105 | 29.0 | 6.0 | 11.1 |
| 3 | 159 | 37.1 | 9.4 | 16.5 |

Fights grow by about **1.8× into act 2 and 2.5× into act 3**. An act-1 number that's fair in act 1 is worth
about half as much in act 2, and less than half in act 3.

## 2. The numbers

**The rule:** act 1 keeps today's number, since that's what the first paper tuned. Act 2 and act 3 numbers
keep the entry at about the same share of a fight. The entry's card and the strip show the number for the
act it was taken in, so the text stays one sentence with one number.

**Shadows:**

| Entry | Text | Act 1 / 2 / 3 | Why |
|---|---|---|---|
| Bulwark | "each enemy gains N Block" at the start of your turn | **4 / 7 / 10** | about a quarter of your damage per turn in every act (4/15.8, 7/29, 10/37) |
| Frenzy | "enemies start each combat with N Strength" | **2 / 3 / 4** | per enemy hit: +25% in act 1, about +20% in acts 2 and 3 |
| Thorny Ground | "enemies start each combat with N Thorns" | **2 / 3 / 4** | Thorns hit once per hit you deal, and you deal about as many hits in every act. So it grows with enemy damage, not with enemy HP |
| Riptide | "that enemy gains 1 Strength" per unblocked hit | **1 / 1 / 1** | unchanged: it already grows with how often you get hit |

**Blessings:**

| Entry | Text | Act 1 / 2 / 3 | Why |
|---|---|---|---|
| Vigor of the Abyss | "your Attacks deal N additional damage" above half HP | **3 / 4 / 6** | per hit, the same rule as Frenzy |
| Moonlit Spring | "heal N HP at the end of each combat" | **8 / 11 / 14** | act 1's 8 already covers a normal fight. Acts 2 and 3 cover most of one (11 of 11.1, 14 of 16.5), so it never becomes free healing |
| Battle Rhythm | "N Strength and N Dexterity" each combat | **1 / 2 / 2** | Strength multiplies across hits, so this rises more slowly |
| Overflow | "Elemental Reactions deal double damage" | unchanged | a multiplier already grows with the act |

All the act-2 and act-3 numbers are first guesses for the Abyss seats to test. Act-1 numbers don't move.

## 3. The Whole run entries

Most Whole run entries are flat too, and they fade the same way:
- Crystallize's 8 Block;
- Moonlit Rest's 4 HP;
- Elemental Burst's 6 and Abyssal Moon's 4 damage;
- Sheer Cold's 3 HP;
- The Clock's and Rally's 2 Strength;
- Fatui Skirmishers' 3 Plated Armor.

Herald (+15% HP) and First Strike (an Attack played twice) already grow with the act.

There are two ways to treat them:
- **Leave them flat.** This is the base game's own model. A relic like Anchor's 10 Block is worth less every
  act, and you take it for the early acts. A Whole run entry taken in act 1 has done its work by act 3.
- **Read the current act**, so each would show "8 (act 2: 14)". That makes their texts longer, and an
  entry taken early gets stronger for free.

I'd leave them flat.

## 4. Build

- `AbyssNumbers` gets one value per act for each entry above. Its text reads the act the entry was taken
  in, which the run record already keeps, so the save format doesn't change.
- The tests that pin each text word for word get one row per act.
- `review/ruled/abyss-pools-2-2026-10-12.md` gets a dated line under each changed entry.
- An Abyss seat round on a base character checks the act-3 picks.

## Picks

1. **Scale the This act entries.**
   - **(a, default)** Use the numbers in sec.2.
   - (b) One multiplier for all of them: act 1 × 1, act 2 × 1.5, act 3 × 2, rounded. That's simpler, but
     Moonlit Spring would heal 16 in act 3.
2. **Whole run entries.**
   - **(a, default)** Leave them flat, as the base game's relics are.
   - (b) Scale them by the current act too.
