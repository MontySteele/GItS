# Kokomi round 2, 2026-10-12

**What ran.** Eight whole-run Sonnet Kokomi seats at A0 on build 0.2.5007 (`main` at bcdb04b0). The build carried:
- the round-1 bug fixes (#1134);
- the round-2 card changes (#1136): stronger jellyfish generators and payoff Powers, free generators, a Call the Generals that costs 0 this turn, Treatise counting Companions, and a tip for Nereid's Ascension.

This is the first round with the new telemetry: draws, Energy and per-card Swirl credit.

The seat records and a Fable review (`k2/fable-review-round2.md`, which this page draws on) are in the session scratchpad.

## Result: no wins

| Seed | End |
|---|---|
| EFA1KJU5TTL3 | Floor 48, act-3 boss (the Queen) |
| QL5BM83MYLNU | Floor 48, act-3 boss (the Queen) |
| NAE0U55TUDXB | Floor 38, act-3 normal fight, after three fights in a row with no rest |
| 69Q0VSPE3FR5 | Stalled in act 2 on a bridge bug (fixed in #1137) |
| SJG90CFQZHDK | Floor 33, act-2 boss (Knowledge Demon) |
| XCG22MXJRAMD | Floor 33, act-2 boss (Kaiser Crab), 1 Block short |
| 2QY727MP5XHN | Floor 17, act-1 boss (Soul Fysh, which had 8 HP left) |
| W2ELAWKFUA9A | Floor 17, act-1 boss (Waterfall Giant's Death Blow) |

**Normal fights, median by act: round 2, then round 1, then the base five:**

| | Damage a turn | HP lost |
|---|---|---|
| Act 1 | 17.0 / 18.2 / 19.0 | 9.4 / 8.8 / 10.0% |
| Act 2 | 25.0 / 25.1 / 30.2 | 14.5 / 11.9 / 15.0% |
| Act 3 | 36.8 / 22.8 / 38.2 | 12.6 / 15.6 / 10.6% |

**Bosses, damage a turn:** act 1 22.1 against the base five's 27.1; act 2 42.8 against 48.6; act 3 28.3 against 49.5.

## What played well

- **Planning stays the core decision.** Seats chose between writing a card as a Plan and playing it now, and the order Plans run in mattered. Opening Gambit then Ambush paid 54 in one Plan, and the Oath Plan killed three Exoskeletons at the start of a turn.
- **Jellyfish Drift at 8 is taken now:** 8 of 13, against 2 of 10 before. Shoal Call went from 0 of 4 to 3 of 7.
- **Hydro, then Electro or Cryo,** kept producing Poison and Frozen.

## What did not

- **Late growth is not fixed.** Act-3 normal fights reached 36.8 damage a turn, but shared Companions dealt 28% of it: Mizuki carried one run, and three Clorindes carried another. Without the Companion hits the median is 25.1, which is 66% of the base five's.
  - Lane 5, mostly her own cards, did 30 a turn in act-3 normal fights and 19 against the Queen.
  - Her own Commander cards were taken 3 of 62 offers over the two rounds.
  - In the two Companion-carried runs, no act-3 normal fight took any Plan damage.
- **Her payoff Powers are still not drafted:** 1 of 28 offers.
- **The Queen's Bound cards and permanent debuffs ended both runs that reached her.**
- **Kelp Wall** was named the weakest card or NEVER AGAIN by four seats.

**Previews and text that misled seats:**
- A Plan's face counts the target's current Vulnerable, which may be gone by the time the Plan lands. Oath read 13 and landed 9; Lance read 27 and landed 18.
- Tide Wall reads 0 when the enemy in front is not attacking.
- Coordinated Tide's hit is missing from the Plan results.
- Three seats expected Treatise to draw when they wrote a card as a Plan.

## What to change

1. **Built for round 3, all Claude's calls:**
   - Plan previews count Vulnerable only if it will still be up when the Plan lands.
   - Coordinated Tide's hit is printed with the Plan results.
   - Tide Wall reads the biggest attack any enemy intends.
   - Treatise's text says that writing a card does not count.
   - Kelp Wall's now-line becomes 5 Block and a draw.
2. **A growth test, built for round 3:** Watchful Shoal (0 of 11 offers, never played) becomes "Your Stings deal 3 additional damage. Your Wards gain 3 additional Block.", the base game's Accuracy shape. It is reversible, and it goes to [USER] in the morning with round 3's result.
3. **For [USER]: late growth.** The choice is between a growth card on her jellyfish line, which round 3 tests, and accepting that her late game comes from shared Companions as a support character's does.
4. **BACKLOG:** the Vambrace preview shows doubled Block on every Block card.
