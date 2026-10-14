# Furina sweep, 2026-10-14

Her design is final ([USER], after the 2026-10-14 run: "Overall, very fun! I
definitely like Furina's current design!"). This pass is the cleanup he asked
for in the same message: "a cleanup / dedupe pass on the cards to make space to
add a wider variety of non guest star effects that aren't just a combinatorial
verb salad of 'spend / drain / repay' + 'deal x damage' / deal x damage to
all.' It's not so much that any one card was an offender as they all
generically blurred together."

Every card text below is from `docs/prototype-surface.yaml`. Rules, guests,
starters, relics, Ancients and the Drain buffer are untouched. The pool stays
at 78.

## 1. Why the pool blurs

Of her 78 draftable cards, 58 are not Guest Stars and name one of her
resources (Drain, Spend, Repay, Fanfare), nearly all as the verb followed by a
number: damage, damage to ALL, Block or draw. They are built from the same
parts:

| Shape | Cards |
|---|---|
| Drain, then damage | Soloist's Solicitation, Undercurrent, Mademoiselle Crabaletta, Riptide Lunge, Grand Deluge, The Deluge, plus three "Drain 3: more" branches |
| Spend, then damage | Quick Flourish, Crashing Waves, Spirited Aria, Standing Ovation, Tidal Flourish, Bravura, Let the People Rejoice, Bring the House Down |
| Repay, then damage or Block | Clean Slate, Hydro Lance, Cleansing Torrent, Grand Absolution, Balance the Books, Hymn of Many Waters |
| Resource, then draw or Energy | Ousia Pledge, Salon's Tab, Interval Bell, Overdraft, All In, Soothing Waters, Pneuma Refrain |
| Power: "whenever you X, Y" | 9 of her 20 Powers: {Drain, Spend, Repay} x {3 to ALL, draw, Block, Strength} |

Two consequences beyond the blur:
- **Twins.** Several pairs differ only in a number or in which resource pays:
  The Deluge / Grand Deluge, Hydro Lance / Cleansing Torrent, Grand
  Absolution / Balance the Books, Soothing Waters / Pneuma Refrain, Salon's Tab
  / Interval Bell (your note) / Overdraft, Salon's Encore / Thunderous
  Applause, Ousia Surge / Crescendo.
- **Too many Powers.** She has 20 Powers in 78 cards, against roughly 12 to 15
  for a base character. Your run died to exactly that: "drafting too many
  powers and then not getting my block when I needed it." With 20 on offer,
  Powers fill a quarter of every reward screen.

## 2. Fifteen cuts

Each cut keeps the better twin or the more distinctive card.

| Cut | Rarity | Kept instead |
|---|---|---|
| Soloist's Solicitation | C | Undercurrent (same Drain 2, and it scales) |
| Spirited Aria | C | Crashing Waves (same "Spend up to" single-target) |
| Standing Ovation | C | Let the People Rejoice and Tidal Flourish carry Spend-to-ALL |
| Hydro Lance | C | Cleansing Torrent (same text, AoE) |
| Overdraft | C | Salon's Tab (its Drain mode is Overdraft plus draw) |
| Packed House | C | Hold the Stage and The Show Must Go On carry Fanfare-to-Block |
| Interval Bell | U | Salon's Tab (your note) |
| Soothing Waters | U | Pneuma Refrain (Repay plus draw, bigger) |
| Balance the Books | U | Grand Absolution (the same idea as the Rare) |
| Salon's Encore | U | Thunderous Applause (the same 3 to ALL, off Spend) |
| Ousia Surge | U | Crescendo (the same first-each-turn draw, off Spend) |
| High Stakes | U | Undercurrent and Regina carry "Drain makes you hit harder" |
| Pneuma Tides | U | Salon Solitaire, her starter relic, already Repays each turn |
| The Deluge | R | Grand Deluge (the same card at Uncommon) |
| Hymn of Renewal | R | Regina and Standing Room Only carry Strength |

## 3. Fifteen new cards, none of them a resource verb plus a number

Each new card does a job her pool cannot do today. Most say no Drain, Spend or
Repay at all; her identity stays in the guests and the 43 resource cards that
remain. Four add Block, because she has the thinnest Block of any character
(41 printed, `furina-wave-2026-10-13.md`) and that is how your run ended.
Numbers are set against the base card named in brackets.

**Common (6)**
| Card | Type, cost | Text | Job (base analogue) |
|---|---|---|---|
| Rain of Tears | Skill 1 | Gain 5 [8] Block. Apply Hydro to ALL enemies. | Sets up her guests' reactions (Lyney Vaporize, Wriothesley and Escoffier Freeze, Clorinde Electro-Charged) |
| Rehearsal | Skill 1 | Retain. Gain 7 [10] Block. | A Block card she can hold for the hit she sees coming |
| Silence in the Court! | Skill 1 | ALL enemies lose 6 [8] Strength this turn. Exhaust. | Defence that is not Block (Piercing Wail) |
| Pirouette | Attack 1 | Deal 4 [5] Hydro damage 3 times. | Multi-hit; each hit takes Neuvillette's Hydro bonus |
| Spotlight Grab | Attack 1 | Deal 9 [12] damage. Put a card from your Discard Pile on top of your Draw Pile. | Sets up next turn's draw (Headbutt) |
| Costume Fitting | Skill 1 | Gain 5 Block. Upgrade a card in your Hand for this combat [all of them]. | Card improvement (Armaments) |

**Uncommon (7)**
| Card | Type, cost | Text | Job (base analogue) |
|---|---|---|---|
| Quick Change | Skill 0 | Discard your Hand, then draw that many cards [+1]. Exhaust. | Dig for a guest or for Block (Calculated Gamble) |
| Read the Script | Skill 1 [0] | Look at the top 4 cards of your Draw Pile. Put 1 into your Hand; discard the rest. | Selection |
| Practiced Grace | Power 1 | Gain 2 [3] Dexterity. | Makes her few Block cards count (Footwork) |
| Mise en Scène | Skill 1 | Choose a card in your Hand. It costs 0 this turn. Draw 1 card [and it costs 0 until played]. | Cost cheating for her 2-cost payoffs |
| Intermission | Skill 2 | Gain 11 [14] Block. Retain your Hand this turn. | Big defensive turn that keeps a combo hand (Equilibrium) |
| Second Act | Skill 1 | Gain 4 [7] Block. Put a card from your Discard Pile into your Hand. Exhaust. | Replay a Guest Star or a payoff (Hologram) |
| Solo Recital | Attack X | Deal 7 [9] damage X times. | Energy sink and a single-target finisher (Skewer) |

**Rare (2)**
| Card | Type, cost | Text | Job |
|---|---|---|---|
| Pneuma and Ousia | Power 1 | Whenever you play an Attack, gain 2 [3] Block. Whenever you play a Skill, deal 2 [3] damage to a random enemy. | Her two arkhe as a Power that pays for mixing card types, not for a resource |
| Stand-In | Skill 1 [0] | Choose a card in your Hand other than Stand-In. Add a copy of it to your Hand. The copy Exhausts. | Doubles a Guest Star or a payoff (a Dual Wield bend at Rare) |

Stand-In may not copy a Stand-In (design call, 2026-10-14): two upgraded Stand-Ins copied each other forever at 0 Energy; with Pneuma and Ousia that is unlimited damage.

## 4. What the pool looks like after

| | Now | After |
|---|---|---|
| Non-guest cards naming a resource (a text search for Drain, Spend, Repay, Fanfare) | 58 | 43 |
| Powers | 20 | 17 |
| Block cards / printed Block | 12 / 41 | 16 / 68 (base five: 61 to 121), plus Practiced Grace's Dexterity |
| Rarity split | 23 / 35 / 20 | 23 / 35 / 20 |

Seventeen Powers is still at the high end. A second trim waits until seats
show whether Powers still crowd her reward screens.

## 5. Plan

Claude builds this on a branch tonight and seat-tests it with five Furina seats
after the co-op lanes free up. The build goes into your next play session; you
rule on it once you have played it. Art for the fifteen new cards is fetched
with the batch.

## Picks

1. **The batch:** **(a) all fifteen cuts and fifteen adds as written**; (b)
   the cuts, with the adds you name; (c) hold it until you have read the cards.
2. **Silence in the Court! at Common:** **(a) Common, as Piercing Wail is**;
   (b) Uncommon.
3. **Stand-In at Rare (it copies Guest Stars):** **(a) Rare, as written**; (b)
   cut it and add a third Block card at Rare instead.
