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
- **Powers: at the top of the base range, not over it.** She has 20 Powers in
  78 cards (26%). The base five have 17 to 20 in 85 draftable cards, 20 to
  24% (`game_ref/<character>.json`, Ancients excluded). An earlier draft of
  this page said "12 to 15"; that was wrong, and [USER] caught it (2026-10-14:
  "most base game characters have 18 to 21 powers, counting multiplayer and
  ancient cards"). The Power cuts below stand as dedupes, not as a count
  target. Your run's death ("drafting too many powers and then not getting
  my block when I needed it") is the thin Block pool more than the Power
  count.

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

## 3. Fifteen new cards, Furina's own

**Second set (2026-10-14).** The first fifteen were base cards renamed
(Piercing Wail, Headbutt, Armaments, Calculated Gamble, Footwork,
Equilibrium, Hologram, Skewer, Dual Wield). [USER]: "I do like the proposed
cards, but I think that most of them are duplicates of another character's.
Can we come up with distinct ideas for Furina, instead?" This set is built
from what only she has: HP loss she chooses (Drain), her two arkhe, the trial
and the Oratrice, the opening and the encore. On it: "The Ousia / Pneuma idea
of flipped cards is very interesting! Generally, great ideas all around!";
"Trial by Water sounds a little underpowered" (now carries Vulnerable); and
"Water Ballet - isn't that a Necrobinder card?" (replaced by Arkhe in
Balance; the Necrobinder's Danse Macabre carries a 2-Energy value in
`game_ref/necrobinder.json`).

**Common (6)**
| Card | Type, cost | Text |
|---|---|---|
| Ousia / Pneuma | Attack 1 | Two faces, starts on Ousia. **Ousia:** Deal 8 [11] damage. Flip. **Pneuma:** Gain 7 [10] Block. Flip. |
| Objection! | Skill 1 | Gain 5 [8] Block. The next time an enemy's attack makes you lose HP this turn, it takes twice that much. |
| Tearful Monologue | Skill 1 | Gain 6 [9] Block. If you lost HP last turn, draw 2 cards. |
| Stage Directions | Skill 1 | Gain 5 [8] Block. Put a card from your Hand on top of your Draw Pile. It costs 0 next turn. |
| Opening Number | Attack 1 | Innate. Deal 7 [10] damage. On your first turn, deal 7 [10] more. |
| Façade | Skill 1 | Gain Block equal to the HP you have lost this combat, up to 12 [16]. |

**Uncommon (7)**
| Card | Type, cost | Text |
|---|---|---|
| Trial by Water | Skill 1 | Apply 2 [3] Vulnerable. Until end of turn, whenever that enemy takes damage, gain 2 Fanfare. |
| Rainfall Overture | Skill 1 [0] | Apply Hydro to ALL enemies. Your next Attack this turn hits ALL enemies. |
| Encore Performance | Skill 1 | Play the top card of your Discard Pile for free. Exhaust it. [cost 0] |
| Arkhe in Balance | Power 1 | Whenever you play an Attack, gain 2 [3] Block. Whenever you play a Skill, deal 2 [3] damage to a random enemy. |
| Crowd Favorite | Power 1 | At the start of your turn, if your HP is below half, gain 1 Energy. [Innate] |
| The Show's Not Over | Skill 0 | Can be played only if you lost HP this turn. Gain 2 [3] Energy. Exhaust. |
| Understudy's Debut | Attack 1 | Deal 6 [8] damage. If your HP is below half, deal 6 [8] more and gain 6 [8] Block. |

The Show's Not Over keeps Exhaust when upgraded: without it, a 0-cost repeatable +2 Energy made 13 thin-deck loops in the probe.

**Rare (2)**
| Card | Type, cost | Text |
|---|---|---|
| Verdict of the Oratrice | Skill 2 [1] | Choose an enemy. If its HP is no higher than your Fanfare, it dies. Otherwise deal damage equal to your Fanfare. Exhaust. |
| Plot Twist | Skill 1 [0] | Choose an enemy that intends to attack. This turn its attack hits itself instead of you. Exhaust. |

The first set's Stand-In loop (two upgraded copies copying each other) goes
with it.

## 4. What the pool looks like after

| | Now | After |
|---|---|---|
| Non-guest cards naming a resource (a text search for Drain, Spend, Repay, Fanfare) | 58 | 45 |
| Powers | 20 | 17 |
| Block cards / printed Block | 12 / 41 | 17 / 59, plus Façade (up to 12) and Arkhe in Balance (base five: 61 to 121) |
| Rarity split | 23 / 35 / 20 | 23 / 35 / 20 |

Seventeen Powers sits at the low end of the base range (17 to 20). If you
want more Power variety, restoring one of the overlap cuts (High Stakes,
Pneuma Tides, Hymn of Renewal) costs nothing else.

**Ruled 2026-10-14:** the cuts and the second set, with the two changes
above; the first set's picks 2 and 3 fall away with its cards.

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
