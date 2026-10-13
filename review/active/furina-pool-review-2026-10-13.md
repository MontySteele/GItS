# Furina pool review, 2026-10-13

From the overnight wave (`review/records/furina-wave-2026-10-13.md`, six
seats, one win) and its Block census (same record). Every card text below is
from `docs/prototype-surface.yaml`; guest numbers are from
`FurinaStageLaw.cs`. Your rulings this pass stays inside: no Fanfare-scaled
Block on a Common ("that Furina block card sounds too good", 2026-10-12), no
cycling at Common, starters untouched, the Drain buffer stays at a quarter.

## 1. Block: the gap is at Uncommon

Five of six deaths came on a hand with no Block card. The census says why it
is the pool and not only the draft:

| | Block cards | Printed Block | Cards printing 8+ |
|---|---|---|---|
| Base five | 11 to 18 | 61 to 121 | 2 to 8 |
| Klee / Kokomi / Varka | 13 / 15 / 17 | 62 / 84 / 85 | 3 / 5 / 2 |
| Furina | 12 | **41** | **0** |

Her Commons are fine: five Block cards at 6.0 Block per Energy, in line with
base Commons (4.2 to 6.7). The hole is her **Uncommons: six Block cards
printing 11 Block in all**, against 36 to 52 for the base five's Uncommons.
Four of the six print nothing at play:

| Uncommon | Text | Printed |
|---|---|---|
| Fountain of Lucine | For 3 turns, at the start of your turn Repay 3. Gain 1 Block for any HP it could not Repay. | 0 |
| Grand Entrance (Power) | Whenever you play a Guest Star, Repay 4. Gain 1 Block for any HP it could not Repay. | 0 |
| The Masquerade (Power) | Whenever you Drain, gain that much Block. | 0 |
| Guest Star: Freminet | Act: gain 3 Block, and more for Fanfare. | 0 |
| Hold the Stage | Gain 6 Block. Spend up to 16: gain 1 more for each. | 6 |
| Private Box | Gain 5 Block, plus 3 for each guest on stage. | 5 |

Hold the Stage is the good one (taken 21 of 42 before this wave; the
winner used it, two seats skipped it). The
Powers and Freminet are engines and can stay engines. Fountain of Lucine is
the one the seats called dead ("never again: repay with nothing drained"),
and Private Box is a worse Defend with no guest out.

**Proposal:** Fountain of Lucine gets a real number at play: "Gain 8 [11]
Block. At the start of your next turn, Repay 3." It keeps the Repay, and is
never blank. That takes her Uncommon printed Block from 11 to 19, still the
lowest, which fits a character meant to take hits for Fanfare. It does not
scale with Fanfare.

Private Box stays. It is a guest payoff: [USER] (2026-10-13) "Private Box
would read 'gain 17 Block' with 3 guest stars deployed", and a higher base
would make that 17.

## 2. The guest-star style, again

Asked on 2026-10-12 (you ruled Encore! only and "leave her alone for now").
**New fact:** a second wave in a row passed on the guests. Charlotte was
skipped 8 times and taken twice, Lynette 4 of 4, Leading Lady and Encore!
every time.

Every Guest Star costs 1 and Exhausts. A guest stays on stage (three seats)
and has a **line**, a passive while it is on stage, and an **act** at the
end of each of your turns. The first draft of this section listed the acts
only. The full texts (`FurinaStageBadges.ActText`, numbers from
`FurinaStageLaw.cs`; upgrades in brackets):

| Guest | Line (passive) | Act (each turn) |
|---|---|---|
| Charlotte (C) | First time each turn a card Repays, draw 1 | Repay 2 [4] |
| Wriothesley (C) | Whenever you Drain, that much Cryo to a random enemy | 4 [7] Cryo, random enemy |
| Lynette (U) | First time each turn you lose HP to an enemy, double Fanfare | 3 [6] Anemo, an enemy with an aura |
| Chevreuse (U) | Whenever you Spend, 1 Vulnerable [and 1 Weak] to a random enemy | 4, random enemy |
| Freminet (U) | Whenever you Drain, gain that much Block | 3 [6] Block, plus a quarter of your Fanfare spent as Block |
| Sigewinne (U) | Whenever you Repay, gain that much Block | Repay 2 [4] |
| Lyney (U) | Drain buffer 10 larger | Drain 2, 8 [11] Pyro to ALL |
| Navia (U) | First Spend each turn costs 2 [3] less | Spend half your Fanfare as Geo damage, random enemy |
| Clorinde (R) | Whenever you Repay, twice that much Electro, random enemy | 6 [9] Electro, random enemy |
| Neuvillette (R) | Your Hydro damage deals 2 [3] more | Hydro to ALL equal to HP lost since your last turn |
| Escoffier (R) | Whenever a guest acts, Repay 1 | 4 [6] Cryo to ALL |

[USER] (2026-10-13), against a Defect orb: "Lyney is clearly extremely
strong. Escoffier is priced close to a Glass orb. Wriothesley, Lynette
Chevreuse are all priced close to the going rate of a Lightning orb.
Freminet is close to a Frost orb. Charlotte, Siegwinne are lower, but priced
in Drain / Repay. These don't line up at all with their rarities."

The lines are where most of the value is, and they mostly do line up: the
Rares' lines scale (Clorinde doubles every Repay, Neuvillette every Hydro
hit). The acts do not. Lyney, an Uncommon, has the biggest act in the cast,
and the Rare Escoffier's ALL act is half of it. A flat +2 (the 2026-10-12
proposal) would widen that gap, so it is withdrawn.

**Proposal:** price the acts by rarity, lines unchanged.
- **Lyney:** 8 [11] to ALL becomes 5 [7] to ALL. Still the only Uncommon that
  hits ALL, with the bigger buffer.
- **Escoffier:** 4 [6] to ALL becomes 7 [10] to ALL, above Lyney.
- **Lynette:** 3 [6] becomes 5 [8], the Uncommon rate (her target needs an
  aura).
- **Leading Lady:** "Gain 2 [3] Strength. Your Attacks deal 1 additional
  damage for each guest on stage." Up from 1 [2], in line with the
  Ironclad's Inflame, also a 1-Energy Uncommon Strength Power.
- The rest stay: Charlotte and Wriothesley are Commons at the Lightning rate
  with build-around lines; Chevreuse, Freminet, Sigewinne and Navia are paid
  through their lines.

## 3. Looked at, not changed

- **Soothing Waters** (0: Repay 2. Draw 1 card.): "Repays 0" with nothing
  drained. Its missing floor is on purpose: with a payout it looped
  (2026-10-09). It is a 0-cost draw-1 at Uncommon, which is allowed.
- **Tutti!** (1: Each guest acts. Draw 1 card.): a guest payoff, dead without
  guests like any payoff. Rises with section 2.
- **Standing Ovation** (Common, 1: Spend half your Fanfare, that much to ALL):
  called worse than Let the People Rejoice and Bravura+, a Rare and an
  upgraded Uncommon. A Common should be.
- **Packed House** (Gain 5 Block, plus 1 for every 4 Fanfare): you kept it at
  4 on 2026-10-12.
- **Encore!, Bis!**: changed or new since the last round; read again after
  the next.

## For [USER]

1. **Uncommon Block.**
   - **(a) Default:** Fountain of Lucine "Gain 8 [11] Block. At the start of
     your next turn, Repay 3." Private Box unchanged.
   - (b) No change.
2. **The guest style.**
   - **(a) Default:** Lyney 5 [7] to ALL, Escoffier 7 [10] to ALL, Lynette
     5 [8], Leading Lady 2 [3] Strength.
   - (b) Leading Lady only.
   - (c) Leave the guests until your playtest.

After the build, a five-seat Furina round reads both: Block cards in the
death hands, and the guests' share of damage.
