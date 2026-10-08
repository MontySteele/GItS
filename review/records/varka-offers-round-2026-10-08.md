# Varka Pyro/Cryo round with card offers logged, 2026-10-08

Project review 2026-10-08, pick 10: "Run the Pyro/Cryo round with card offers
logged. Payoffs offered and passed means fix the cards; payoffs never offered
means move one payoff per element to Common." Varka is at Prototype, so
nothing here binds; it is a reading.

**What ran.**
- Solo Varka on the five base-five baseline seeds at A0, on staging build
  0.2.4590+next. Varka's kit is the same there as on `main`.
- One Sonnet seat (medium) per act, each handed the previous act's record.
- Every card reward, shop shelf and event chooser went to
  `understudy/logs/offers/` (#980). The reader is
  `tools/offer_report.py --character VARKA`.
- Telemetry run instances: `20261008-1153`/`-1154`.

| Seed (base character) | Starting Knight | Varka ended | Solo check, 10-07 | Base character |
|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | Kaeya, Cryo | floor 44, Slimed Berserker | floor 48 | floor 48 |
| CYHZM9S0VPW6 (Silent) | Kaeya, Cryo | floor 48, the Queen (214/400 left) | floor 17 | floor 48 |
| DJCAV76ZKAUN (Defect) | Barbara, Hydro | floor 40, Soul Nexus elite | **won** | floor 48 |
| YEWA0B7AVE45 (Necrobinder) | Amber, Pyro | floor 48, Test Subject | floor 46 | floor 46 |
| R41TX5Q0ZQYN (Regent) | Kaeya, Cryo | floor 48, Aeonglass (215/512 left) | floor 33 | floor 48 |

All five cleared act 2, which no earlier Varka round did. There were no wins;
three runs died at the final boss.

## The offers: payoffs were offered and passed

There were 611 card offers across the five runs, and seats took 18% of them.
Varka's own cards, by element:

| Element | Offered | Taken | Rate |
|---|---|---|---|
| Anemo | 83 | 23 | 28% |
| Cryo | 69 | 15 | 22% |
| Hydro | 46 | 9 | 20% |
| Electro | 57 | 9 | 16% |
| **Pyro** | 69 | 7 | **10%** |

The payoff cards, the ones that pay for an element rather than apply it:

| Card | Text, in short | Offered | Taken | Played |
|---|---|---|---|---|
| Pyre Oath | Power: Exhaust a card, gain 1 Pyro Oath | 9 | 0 | — |
| Stoke the Flames | Exhaust a card, +2 Pyro Oath, Pyro current | 9 | 1 | never; removed at a shop |
| Ember Cleave | 9 Pyro, Exhaust a card | 12 | 1 | 9 plays |
| Blazing Charge | 5 Pyro + 2 per Pyro Oath | 5 | 0 | — |
| Wildfire Oath (rare) | Power: applying Pyro deals Pyro Oath | 6 | 0 | once, from a Power Potion |
| Deep Freeze | Apply Cryo, double Weak and Vulnerable | 7 | 0 | — |
| Glacial Edict | Cryo, 1 Weak + 1 Vulnerable, +1 each per 4 Cryo Oath | 8 | 1 | once |
| Absolute Zero (rare) | Power: Weak or Vulnerable deals Cryo Oath | 2 | 1 | never ("needs Weak/Vulnerable spam") |

Nothing in either element went unoffered. The cards seats did take for Cryo
and Pyro were its appliers: Kaeya, Icebreaker, Mika, Kindled Edge and Amber.
Kindled Edge+ did 21 to 23 a play in acts 2 and 3. **So by the pick's rule,
the cards are what needs fixing.** Access does not.

**Why the seats passed, in their words.**
- **Pyro's payoffs are an Exhaust deck nobody was building.** Pyre Oath,
  Stoke and Ember Cleave all ask for a card to Exhaust. One seat "never wanted
  to exhaust anything"; another removed Stoke at a shop.
- **Cryo's payoffs multiply debuffs the deck doesn't stack.** Deep Freeze
  doubles Weak and Vulnerable that are rarely there. Absolute Zero is a
  2-cost Power that "needs Weak/Vulnerable spam".
- **Both rares are 2-cost Powers** that the round's tempo had no room for.

## Telemetry: normal fights against the base five

The base column pools the 10-05 baseline and the 10-08 control on the same
seeds. Varka reached act 3 on all five.

| Act | Varka damage a turn | Ratio | Varka HP lost, % of max | Ratio | Solo check HP ratio |
|---|---|---|---|---|---|
| 1 | 21.0 | 1.06 | 3.8 | 0.66 | 0.61 |
| 2 | 39.5 | 1.20 | 4.7 | 0.38 | 0.43 |
| 3 | 39.1 | 0.97 | 14.7 | **1.23** | 0.69 |

- Acts 1 and 2 repeat the solo check: Varka is far sturdier than base.
- Act 3 does not: Varka lost more HP there than the base characters, and
  every run ended in it.
- Four Winds' Ascension remains the engine: 21 to 26 a play, and the top
  damage source in every act.
- Reactions ran at 1.18 a turn (Swirl 0.70, Frozen 0.13, Melt 0.09). The
  solo check had 1.00.

## What played well
- **Setting up one card's reaction with the one before it**, named on every
  lane: Kaeya's Cryo then Amber's Melt; Barbara's Hydro then Icebreaker's
  Frozen; Lisa then Windbound's Swirl.
- **Frozen used as defence** (Hydro on a Cryo aura, or the reverse). It was
  the most reliable damage cut in act 3 on two lanes.
- **Choosing the current element before Four Winds' Ascension or Northwind
  Avatar.** Lane 1 survived act 2 on that turn, at 1 HP.
- **Cycle of Seasons.** Two copies made every Knight a 14-damage button on
  lane 5.

## What did not
- **Sucrose — Mollis Favonius's +4 never showed.** Two seats said so. The
  card reads "This turn, Elemental Reactions deal 4 additional damage", but
  the bonus reaches only Melt, Vaporize and Overload
  (`CompanionHexerei.cs`, `DamagingReactions`). Its own Swirl also resolves
  before the bonus is applied.
- **Wolfpack's copy is invisible.** It goes to the discard pile. One seat
  played it twice and another named it NEVER AGAIN; neither saw the copy.
- **The element switch still surprises.** Charged Lunge, Kaeya and Barbara
  moved the current element off the highest Oath, and three seats paid for
  it with a weaker Ascension.
- **Wildfire Oath's hit has no preview.** A seat mis-added a lethal by 1.

## What to change
1. **Rework the Pyro and Cryo payoffs** (pick 10's first branch). A short
   card paper comes next, built on the two findings above:
   - Pyro's payoffs should pay for Pyro being played, not for Exhaust;
   - Cryo's should read the debuffs his own Cryo cards apply.
2. **Correct Mollis Favonius's text to what it does**, or widen the rule. It
   is a companion card in Klee's pool too, so it waits for the next
   `klee-next` batch (`BACKLOG.md`).
3. Wolfpack's copy and Wildfire Oath's preview become BACKLOG lines.
4. **Varka's act 3 needs a Balance suite before anything is concluded.** HP
   loss jumped from 0.69 to 1.23 between two rounds on the same seeds, which
   is inside the spread `stage-gate.md` records.
