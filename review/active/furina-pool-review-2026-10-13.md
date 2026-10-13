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

[USER] then: "Escoffier still looks a bit underpowered. 'Whenever a guest
acts, Repay 1' is typically 'repay 3 at end of turn', vs 'Repay 2 [4]' for
Siegwinne. Neuvillette's passive 'Your Hydro damage deals 2 [3] more' also
seems low, but his end of turn effect looks quite good. Can you send this
whole thing off to a Fable reviewer to come up with a Guest Star package
with effects that make sense for each character's lore and are also balanced
for their rarity and their card cost?"

The Fable package is `furina-guest-package-2026-10-13.md` beside this file:
orb numbers read from the game's DLL, a yardstick per rarity, every guest
priced, loops walked. Its anchor: the Defect's Fusion (1 Energy, Exhaust,
Uncommon, a Plasma orb) is the one base card shaped like a Guest Star. Bands,
as damage-equivalent a turn: **Common 5 to 6, Uncommon 7 to 9, Rare 10 to 13
alone and more with company.** Today, Charlotte (3.5) and Sigewinne (5) sit
under their bands, Lyney (14) and Neuvillette (20+) over, Escoffier at the
bottom of hers.

**Proposal (the package, with my changes to it):**

| Guest | Change |
|---|---|
| Charlotte (C) | Act Repay 2 [4] becomes **Repay 3 [5]** |
| Wriothesley (C) | Act 4 [7] becomes **5 [8]** |
| Lynette (U) | Act 3 [6] becomes **5 [8]**; line reworded "gain that much Fanfare again" |
| Chevreuse (U) | Act 4 becomes **5** |
| Freminet (U) | Act Block 3 [6] becomes **4 [7]** |
| Sigewinne (U) | Act Repay 2 [4] becomes **Repay 3 [5]** |
| Lyney (U) | Act 8 [11] to ALL becomes **5 [7] to ALL**; Drain 2 and the buffer line stay |
| Navia (U) | Act becomes **"Spend a third of your Fanfare, rounded down: deal twice that much Geo damage to a random enemy"** (today: half, 1 for 1) |
| Clorinde (R) | No change: Rare-sized once Charlotte and Sigewinne Repay 3 |
| Neuvillette (R) | No change (below) |
| Escoffier (R) | Line becomes **"Your guests' acts deal 2 [3] more damage."** Act 4 [6] to ALL stays, and her own line lifts it to 6 [9] |
| Leading Lady | **Gain 2 [3] Strength** (up from 1 [2]) |

Where I differ from the package:
- **Lyney flat, not growing.** The package makes him 3 [5] to ALL, growing 1
  a turn on stage (a Dark orb). That needs a counter on him and a rule to
  track, which you have pushed back on before; flat 5 [7] lands within a
  point of it over a normal fight. The growing shape is pick 4.
- **Neuvillette unchanged,** with the package's reason: his +2 is per hit,
  and Bravura is one hit per 3 Fanfare spent, so a 36-Fanfare Bravura gets
  +24. His act is already the biggest in the cast.

Escoffier's new line is the stage's Defragment: a Rare that makes every other
guest worth seating, which is what the guest style lacked. The guest deck it
makes (Wriothesley, Lyney, Escoffier) deals about 23 a turn from three
exhausted cards before Tutti!, Encore! or Showstopper multiply it. The
package walks seven loops (sec.4 there); none makes a resource from itself.

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

## Ruled 2026-10-13

[USER]: "On the four Furina picks: 1) a 2) b but I may revisit Wriotheslet
later 3) a 4) I think a is fine for now." And: "one thing I noticed is that
Wriothesley (a 5 star) is at Common. We must have bumped him down at some
point." (He went to Common in the diversity pass, as the company's Common
damage star; a rarity question for later.)

Built from this:
- **Fountain of Lucine:** "Gain 8 [11] Block. Next turn, Repay 3."
- **Leading Lady:** "Gain 2 [3] Strength. Your Attacks deal 1 additional
  damage for each guest on stage."
- **Escoffier's line:** "Your guests' acts deal 2 [3] more damage." Her act
  stays 4 [6] to ALL.
- **Lyney's act:** 5 [7] to ALL (from 8 [11]); Drain 2 and the buffer line
  stay.
- The rest of the guest package, as in section 2's table (corrected: [USER]:
  "Oh, sorry, On Furina 2, I meant a)").

## For [USER] (ruled above)

1. **Uncommon Block.**
   - **(a) Default:** Fountain of Lucine "Gain 8 [11] Block. At the start of
     your next turn, Repay 3." Private Box unchanged.
   - (b) No change.
2. **The guest package.**
   - **(a) Default:** the table above.
   - (b) Leading Lady only.
   - (c) Leave the guests until your playtest.
3. **Escoffier's line** (if 2a).
   - **(a) Default:** "Your guests' acts deal 2 [3] more damage."
   - (b) "Whenever a guest acts, Repay 2 [3]": dead with nothing drained, 6
     Repay a turn with three guests.
4. **Lyney's shape** (if 2a).
   - **(a) Default:** flat 5 [7] to ALL.
   - (b) 3 [5] to ALL, growing 1 each turn he is on stage.

After the build, a five-seat Furina round reads both: Block cards in the
death hands, and the guests' share of damage.
