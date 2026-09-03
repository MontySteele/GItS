# KLEEMOD-KLEE — blind seat, lane 2, act 1

## Identity

- Model / seat: Claude Opus, blind TESTER seat, round 8, first seat (act 1 only)
- Lane: 2
- Character: KLEEMOD-KLEE
- Run seed: **never printed.** No screen in the run — Neow, map, battle, shop,
  rest, reward or boss — printed a seed or a run id of any kind.
- Act / boss: act 1; the map named the boss on the very first map screen,
  `At the top of this act: **Waterfall Giant**`. 17 floors.
- Actions accepted: **247 of the 250 budget.** Refused: **0** — every command I
  sent was accepted; I never hit a refusal or a tool error at any point.
- Termination reason: **stop condition (1)** — the act-1 boss was resolved and
  its reward screen fully handled, so the lane stands on the act-2 map screen.
  (3 actions remained unspent.)
- Where the run stands: the **act-2 map screen**, one node offered,
  `Ancient (path 1)` — `leads on to: Monster, Monster, Monster`. Nothing played
  on it.
- HP trajectory, every reading a screen printed, in order:
  **62/62** (fight 1 open) -> 56 -> 53 (fight 1 won) -> 52 -> 52 (fight 2 won)
  -> 50 -> 49 (fight 3 won) -> 49 -> 39 -> 29 (fight 4 won) -> 29 -> 26 -> 19
  (fight 5 won) -> 19 -> 16 -> 13 (fight 6 won) -> **13/62, the run's low**
  -> rest **31** -> rest **49** -> 46 -> 46 -> 43 (elite won) -> rest **61**
  -> 53 -> 53 (fight 7 won) -> 53 (fight 8 won, zero damage) -> 42 (boss turns
  2-7) -> boss killed. **The last HP any screen printed was 42/62**, immediately
  before the boss's 27-damage Death Blow; no screen since has printed HP, so I
  cannot state the current value. Max HP was 62 throughout.
- Gold: never displayed outside a shop. Reward screens printed 13, 11, 17, 18,
  10, 17 + 18 (stolen back), 39, 12, 10 and 100. The floor-5 shop read
  `You have 158 gold`, i.e. a **99-gold starting purse no screen ever showed**.
  I spent 150 there (Tinder Toss 25, Pop! 50, Card Removal 75), leaving 8.
- Potions held at the end: **Skill Potion** (boss reward). Used during the run:
  Vulnerable Potion, Distilled Chaos, Fysh Oil — all three on the boss.
- Relics, exactly as printed: **Pounding Surprise** — Whenever a Bomb goes off,
  gain 1 Spark. **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an
  additional Strike and Defend to your Deck. **Snecko Skull** — Whenever you
  apply Poison, apply an additional 1 Poison. **Pendulum** (1) — Every 3 turns,
  draw 1 card. **Candelabra** — At the start of your 2nd turn, gain
  [Energy][Energy]. **Lucky Fysh** — Whenever you add a card to your Deck, gain
  15 Gold.
- Deck (23 after the boss reward; the 22-card list was printed in full on the
  Smith screen, and Sparks 'n' Splash was added after):
  Strike x3, Defend x4, Duck and Cover, **Jumpy Dumpty+** (upgraded, Bomb 18),
  Ka-pow!, Kaboom!, Tinder Toss x2, Pop!, Bang Bang!, Perfect Timing x2,
  Diona — Shaken, Not Purred, Kaeya — Glacial Waltz, Barbara — Let the Show
  Begin♪, Shinobu — Grass Ring of Sanctification, Thoma — Blazing Barrier,
  Sparks 'n' Splash.
- Record of prediction accuracy: I predicted the damage or the HP taken before
  every significant play. **Every prediction came out exact** except four, all
  logged in place: fight 6 turn 2 (predicted 22, got 25 — the Mine chain),
  fight 7 turn 2 (predicted 7 remaining, got 3 — a Kaeya Melt),
  boss turn 2 (predicted 12 from Bang Bang!, got 21 — it ate the Cryo aura),
  and boss turn 5 (Distilled Chaos did nothing observable).

---

## Screen 1 — Neow

Printed:

```
# Neow

- **Precise Scissors**
    Remove 1 card from your Deck.
- **Lost Coffer**
    Gain 1 card reward and procure 1 random Potion.
- **Large Capsule**
    Obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
```

No seed printed. No HP, gold, relic or deck readout on this screen at all — the
opening screen tells a blind player nothing about the character they are about
to play.

Prediction: two relics compound across a whole run and outweigh two dead cards
in a deck that will get thinned later; I take **Large Capsule**.

Result: taken. The Neow screen never named the two relics; I only learned them
from the relic list inside the first fight (Snecko Skull, Pendulum).

---

## Screen 2 — the map

```
- 1 floor ahead: Monster, Monster
...
- 9 floors ahead: Treasure, Treasure, Treasure, Treasure, Treasure
- 16 floors ahead: Boss
At the top of this act: **Waterfall Giant**
```

Act-1 boss named up front: **Waterfall Giant**. 17 rooms deep. Only two nodes
open: Monster (path 1) → Monster, Unknown; Monster (path 2) → Monster. I took
path 1 for the extra Unknown downstream. No HP, gold, relic or potion readout
appears anywhere on the map screen — the map is the one screen a player would
route from and it prints none of the state a route depends on.

---

## Fight 1 — Seapunk (44 HP), floor 1

Opening state, first time any of it was printed:

```
- HP 62/62   Energy 3/3   Spark 1 (buff)
- Piles: 7 in the draw pile
## Your relics
- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark.
- **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
- **Snecko Skull** — Whenever you apply Poison, apply an additional 1 Poison.
- **Pendulum** (1) — Every 3 turns, draw 1 card.
```

Starting hand:

```
- **Duck and Cover** — cost 1, skill: Gain 5 Block.
- **Strike** — cost 1, attack: Deal 6 damage.
- **Ka-pow!** [Pyro] — cost 0, attack: Retain. Set off. Deal 4 damage.
- **Jumpy Dumpty** — cost 1, skill: Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies.
- **Defend** — cost 1, skill: Gain 5 Block.
```

Enemy: `Seapunk — HP 44/44, Intent: Aggressive (Attack) — the number on its
icon is 11`.

**Turn 1.** Prediction: Ka-pow! Retains and costs 0, and the Bomb "grows 4 a
turn", so holding Ka-pow! one turn turns a Bomb 8 into a Bomb 12 for free —
16 damage instead of 12 at no energy cost. I worked the two lines out: setting
off on turn 1 leaves the enemy at 29 after its attack; holding leaves it at 22
after turn 2 and still kills on turn 3. Held.

Played: Jumpy Dumpty on Seapunk (Bomb 8), Strike, Defend.
- Strike: 44 → 38. Exactly 6. Predicted 6.
- Block 5. Bomb badge printed `Bomb 8 (buff) — Set off here deals 8 Pyro damage.
  Bombs here: 1. Each grows at the start of your turn. None goes off by itself.`
- Enemy attacked 11 into 5 Block. Predicted HP 56. Actual **HP 56/62**. Exact.

**Turn 2.** `Bomb 12` — grew exactly 4, as printed. Hand: Ka-pow! (retained,
correct), Strike ×3, Defend ×2. Piles 6+2+4 = 12, so the deck is 12 cards.
Enemy intent changed to `2x4 — This enemy intends to Attack for 2 damage 4
times` (8 total, down from 11).

Predicted Ka-pow! = 12 (bomb) + 4 = 16. Actual: **38 → 22. Exactly 16.**
Three things the card text did not promise but the badges then showed:
- `Pyro Aura 2 (aura)` appeared on Seapunk — the Bomb's Pyro hit left the aura.
- `Bomb 3 ... Bombs here: 1, including 1 Mine` — Jumpy Dumpty's rider landed.
- Spark went **1 → 2**. Pounding Surprise fired once, for the Bomb, not for the
  Mine being placed.

Then Strike, Strike (22 → 10), Defend. Enemy's 2×4 into 5 Block: predicted 3
through. Actual **HP 53/62** — exactly 3.

**Turn 3.** Enemy at **7/44**: the Mine dealt exactly 3 on their attack and
Spark went 2 → 3. Note the Mine did *not* grow before firing — it grows "at the
start of your turn" and it went off during theirs. Intent flipped to
`Empower (Buff)` + `Defensive (Defend)`.

New face drawn: `**Kaboom!** [Pyro] — cost 1, attack: Deal 7 damage.`

Predicted Kaboom! for exactly lethal on 7. Actual: fight over.

**Fight 1 result: won on turn 3, HP 53/62, 9 damage taken. Every number I
predicted came out exact.**

Reward: `13 Gold` + a card. The card screen offered **four** options, not three:

```
- **Flame Dance** [Pyro] — cost 1, attack: Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies.
- **Tinder Toss** [Pyro] — cost 1 Spark, attack: Set off and deal 4 damage to a random enemy twice.
    Its 1 Spark is a price, not an Energy cost: an effect that makes a card free to play, or cuts its cost to 0, covers Energy only, and the 1 Spark is still spent.
- **Coven Errand** — cost 1, skill: Place a Bomb 5. If you played a Hexerei card this turn, place it on ALL enemies instead.
    *Hexerei* — A Companion card from the witches' circle. It does nothing by itself; Klee is one too, and her own cards pay when you play one.
- **Prune — Ring-A-Ding-Ding! Hexhunter Chime** — cost 1, attack: Deal 8 damage. Swirl. The next Bomb you set off this turn deals the swirled element instead of Pyro.
```

Took **Tinder Toss**: it is the only card offered that costs no Energy, and I
was sitting on 3 unspent Sparks with nothing in the deck that could spend them.
Coven Errand's Bomb 5 is strictly worse than the Bomb 8 I already have unless I
own Hexerei cards, and I own none.

---

## Fight 2 — two Corpse Slugs (26 + 27 HP), floor 2 — the "Unknown" node

The map's `Unknown (path 2)` opened straight into a battle, not an event. That
is a legitimate Unknown outcome, but worth logging: the map's only distinction
between a known Monster and an Unknown was resolved to Monster anyway.

```
- **Corpse Slug (1)** — HP 26/26  Intent: Strategic (Debuff)
    Ravenous 4 (buff) — When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength.
- **Corpse Slug (2)** — HP 27/27  Intent: 3x2
    Ravenous 4 (buff) — (same)
```

Ravenous is the first real *choice* the game has put in front of me: killing
one enemy is not free. The survivor is Stunned (a turn I get for nothing) but
takes +4 Strength permanently. On a 3×2 attacker that is 6 → 14 a turn.

**Turn 1.** Jumpy Dumpty on Slug 2 (Bomb 8), Strike Slug 1 (26 → 20, exactly 6),
Defend. Predicted 1 through their 3×2 into 5 Block. Actual **HP 52/62**. Exact.
Slug 1's debuff landed: `Frail 2 — Gain 25% less Block from cards for 2 turns`,
and Defend's own printed text changed from "Gain 5 Block" to **"Gain 3 Block"**
— the screen re-renders the real number rather than the printed one, which is
the single most useful thing this interface does.

**Turn 2.** Bomb 12. Ka-pow! on Slug 2: predicted 12 + 4 = 16. Actual
**27 → 11**. Exact. `Bomb 3 ... Bombs here: 1, including 1 Mine` appeared on
*both* slugs — Jumpy Dumpty's "Mine 3 on ALL enemies" is a genuine AoE rider.

Then the interesting sequencing decision: Tinder Toss hits "a random enemy", so
I killed Slug 2 **first** (Kaboom! 7 → 4, Strike 6 → dead) to make Tinder Toss
deterministic. That is a real, non-obvious play the printed text supports.

On the kill, the survivor printed:

```
- **Corpse Slug** — HP 20/26   Intent: Stunned (Stun) — This enemy can't act on its next turn.
    Bomb 6 (buff) — Set off here deals 6 Pyro damage. Bombs here: 2, including 2 Mines.
    Strength 4 (buff)
```

**It inherited the dead slug's Mine.** Ravenous says "eats it, becoming Stunned
and gaining 4 Strength" and nothing about absorbing the corpse's Bombs. It went
from `Bombs here: 1` to `Bombs here: 2`. That is a screen granting something it
did not say.

Tinder Toss into the survivor: predicted set-off of two Mines (6) + 4, then a
second hit of 4 with nothing left to set off = 14. Actual **20 → 6**. Exact.
Spark went 2 → 3: −1 for the price, +2 from the two Mines (Pounding Surprise).

**Turn 3.** Slug Stunned, so I took 0. `Strength 4` confirmed on the intent —
3×2 became `7x2`. Kaboom! (7) into 6 HP finished it.

**Fight 2 result: won turn 3, HP 52/62 — 1 damage taken in the whole fight.**

Reward: `11 Gold` + a card, from:

```
- **Witches' Circle** — cost 1, power: Whenever you play a Hexerei card, place a Bomb 3 on a random enemy.
- **Rapid Fire** [Pyro] — cost 2, attack: Deal 3 damage to a random enemy 4 times. Set off each enemy hit.
- **Flame Dance** [Pyro] — cost 1, attack: Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies.
- **Diona — Shaken, Not Purred** [Cryo] — cost 1, skill: Gain 6 Block. Apply Cryo twice. If a Bomb goes off this turn, gain 5 Block.
```

Took **Diona**. Two reasons, both from the printed text: 11 Block for 1 Energy
when a Bomb goes off is more than double a Defend, and Cryo is the only route
I had been offered to a `Melt` (1.75×) on my own Pyro bombs. Witches' Circle
was unplayable — I own no Hexerei card and nothing on offer printed the tag.

---

## Fight 3 — Sludge Spinner (39 HP), floor 3

**Turn 1 — the first genuinely interesting decision of the run.** The obvious
line was Kaboom! + Strike + Defend = 13 damage, 5 Block. Instead I played
**Diona first to paint a Cryo aura, then Kaboom! into it for a Melt.**

Predicted: Kaboom! 7 × 1.75 = 12.25 → 12. Actual **39 → 27. Exactly 12.**
The aura was consumed and, as the glossary promised, *no* Pyro aura was left
behind. Then Strike (27 → 21). Enemy hit 8 into 6 Block; predicted HP 50.
Actual **HP 50/62**. Exact.

Diona also silently gave **Spark 1 → 2**. Her card text mentions Block and Cryo
and nothing else. Second undisclosed grant of the run.

**Turn 2.** `Weak 1 — Attacks deal 25% less damage for 1 turn` landed; Strike
re-rendered to **4** and Ka-pow! to **3** (6 and 4 × 0.75, floored). Bombs are
explicitly exempt: "Its hit takes the enemy's debuffs, not yours." So I placed
Jumpy Dumpty under Weak deliberately — the Bomb's damage would not be taxed.
Played JD, weakened Strike (4), Defend. Predicted 1 through 11 − 5... the enemy
Empowered to `Strength 3` and its 6 became 11 only for the *next* turn; the
attack that landed was 6 into 5 Block. Predicted HP 49. Actual **HP 49/62**.

**Turn 3 — the best play of the run.** Enemy 17 HP with `Bomb 12` on it.
Predicted: Diona paints Cryo, Ka-pow! sets off the Bomb as a Pyro hit into a
Cryo aura → Melt → 12 × 1.75 = 21 ≥ 17 = lethal, without spending a single
attack card. **Actual: the fight ended on that Ka-pow!.** The Melt multiplier
does apply to a Bomb's set-off hit, which the Bomb glossary never states.

**Fight 3 result: won turn 3, HP 49/62.**

Reward: `17 Gold` + `Vulnerable Potion` + a card, from:

```
- **Perfect Timing** [Pyro] — cost 1, attack: Set off. Deal 8 damage. If a Bomb triggered an Elemental Reaction this turn, play this again.
- **Flame Dance** [Pyro] — cost 1, attack: Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies.
- **Pop!** — cost 0, skill: Place a Bomb 5.
- **Kaeya — Glacial Waltz** — cost 1, skill: For 3 turns, at the end of your turn deal 6 Cryo damage to a random enemy. Exhaust.
```

Took **Perfect Timing**: it is a set-off (I owned only two, Ka-pow! and Tinder
Toss), it beats Strike's rate at 8 for 1, and its rider — "If a Bomb triggered
an Elemental Reaction this turn, play this again" — is a printed reward for
exactly the Diona-into-bomb line I had just proved lethal.

Running totals here: HP 49/62, gold 41, 1 Vulnerable Potion, deck 15.

---

## Fight 4 — Punch Construct (55 HP), floor 4 — the fight that cost me the run's HP

```
- **Punch Construct** — HP 55/55  Intent: Defensive (Defend)
    Artifact 1 (buff) — Negates 1 debuff.
```

**Turn 1.** Its only intent was Defend, so Block on my side was strictly wasted
— a rare screen where the correct play is to hold no defence at all. Strike (6)
+ Kaboom! (7): 55 → 42, exact.

**Turn 2.** It came back with **Block 10**, and that is the whole fight. With
10 Block standing, chip damage is worth nothing: a Strike into it nets zero.
The only correct answer is to punch through in one turn, and I had the hand for
it. Predicted, hit by hit: Jumpy Dumpty (Bomb 8) → Perfect Timing sets it off
for 8, all absorbed (Block 10 → 2), then Perfect Timing's own 8, of which 6
lands. Predicted 42 → 36. **Actual 42 → 36. Exact.**

Note what did *not* happen: Perfect Timing's rider "If a Bomb triggered an
Elemental Reaction this turn, play this again" did not fire, correctly — the
enemy wore `Pyro Aura 1` and the Bomb's hit is Pyro, so it refreshed rather
than reacted. The card is honest about its own condition.

Then Ka-pow! (set off the Mine 3, +4), Tinder Toss (4 + 4), Strike (6).
Predicted enemy at 15. **Actual 15/55. Exact.** Took the full 5×2 = 10 with no
Block: HP 39.

**Turn 3.** Enemy 15, hitting 14. I could not reach lethal (2 Strikes = 12), so
I took the line that costs least: Strike, Strike, Diona for Block. Predicted
HP 29. **Actual 29/62.**

Two interface things showed up here that are worth keeping:

1. Diona re-rendered as `Gain 4 Block` under `Frail 1` (6 × 0.75 floored),
   the same live-arithmetic behaviour as Defend earlier.
2. A new line appeared on every elemental card: `*Reaction preview: Melt* —
   This card deals no damage. Pyro plus Cryo is still consumed, and there is no
   hit here for the 1.75x to multiply.` on Diona, versus `This card supplies
   Pyro or Cryo while an enemy has the other aura. The triggering hit deals
   1.75x damage and consumes the aura.` on Kaboom!/Perfect Timing/Tinder Toss.
   The screen was telling me, per card, whether the reaction would be wasted.
   That is the best-designed thing on any screen in this run.

**Turn 4.** Enemy at 3 with `Cryo Aura 1` (Diona's paint). Kaboom! finished it.

**Fight 4 result: won turn 4, HP 29/62 — 20 damage, more than the first three
fights put together.**

An unexplained number: Spark went **2 → 4** across turn 3, a turn in which no
Bomb went off at all. The only candidates are Diona herself (she gave +1 in
fight 3 as well) and the Melt reaction her first Cryo application triggered
against the standing Pyro aura. Neither is printed anywhere: the Spark glossary
says only "Start each combat with 1. Pounding Surprise grants more."

Reward: `18 Gold` + a card from `Sorry, Jean...` / `Bang Bang!` / a second
`Perfect Timing` / `Lynette — Magic Trick: Astonishing Shift`. Took **Bang
Bang!** (`cost 2 Sparks, attack: Set off. Deal 8 damage. Place a Bomb 4.`) — I
had ended the fight sitting on 4 unspent Sparks, and it is the only card offered
that both sets off and re-places a Bomb at zero Energy.

---

## Shop — floor 5

```
You have 158 gold.
```

**158.** My four reward screens had printed 13 + 11 + 17 + 18 = 59. There was a
99-gold starting purse and no screen in the run had ever shown it — not Neow,
not the map, not any battle. The shop is the first screen in five floors that
tells you how much money you have.

Shelves: Tinder Toss 25 · Rapid Fire 75 · Pop! 50 · Sorry, Jean... 51 ·
Witches' Circle 76 · Barbara — Melody Loop 75 · Kaeya — Glacial Waltz 73 ·
Twisted Funnel (relic) 219 · Ice Cream (relic) 272 · Screaming Flagon (relic)
219 · Swift Potion 52 · Entropic Brew 99 · Cunning Potion 72 · Card Removal 75.

Bought **Tinder Toss (25)**, **Pop! (50)**, **Card Removal (75)** = 150, leaving
8 gold. Removed a **Strike**: at 6 damage for 1 Energy it is the worst attack in
a deck that also holds Kaboom! (7/1), Perfect Timing (8/1) and two cards that
cost no Energy at all.

The removal screen is the first and only place the whole deck is printed. It
read, at 18 cards before the cut:

```
Strike ×4, Defend ×4, Duck and Cover, Jumpy Dumpty, Ka-pow!, Kaboom!,
Tinder Toss ×2, Diona — Shaken, Not Purred, Perfect Timing, Bang Bang!, Pop!
```

Deck after the cut: **17**.

Note on relics: all three relics were 219–272, so at 158 gold no relic was ever
purchasable. The shop's relic shelf was decoration for this visit.

---

## Fight 5 — Haunted Ship (63 HP), floor 6

```
- **Haunted Ship** — HP 63/63
    Intent: Strategic (Debuff)
      and also: Strategic (StatusCard) — the number on its icon is 5 — This enemy intends to give you 5 Status cards.
```

**Turn 1.** No attack in the intent, so Block was again worth nothing — but
Energy was going spare, so I spent one on Diona purely to *paint a Cryo aura*,
then Pop! for a Bomb 5, then Tinder Toss to set it off into that aura.
Predicted: Bomb 5 Melts for 5 × 1.75 = 8.75 → 8, plus 4 + 4 = 16.
**Actual 63 → 47. Exactly 16.**

Diona's rider resolved *backwards in time* and correctly: she was played before
any Bomb existed, and her buff read `Shaken, Not Purred 5 — The next time one of
your Bombs goes off this turn, gain 5 Block`. When Tinder Toss set the Bomb off
two cards later, Block went to **11** (6 + 5). Good, honest wording.

**Turn 2.** `Weak 3 — Attacks deal 25% less damage for 3 turns` and 5 Status
cards. Every attack re-rendered: Strike 6 → 4, Kaboom! 7 → 5, Perfect Timing
8 → 6, Tinder Toss 4 → 3, Bang Bang! 8 → 6. Bombs did not change — the Bomb
badge still read its full size, matching "Its hit takes the enemy's debuffs,
not yours." **Weak is the sharpest reason in the game to route damage through
Bombs**, and that is the first time the character's two damage channels
actually diverged.

Sequencing that mattered: Bang Bang! is `Set off. Deal 8 damage. Place a Bomb
4.` — the set-off resolves before the placement, so its own Bomb survives. I
played **Perfect Timing first** (its set-off found nothing, 6 damage) and Bang
Bang! second (6 damage, Bomb 4 left standing) rather than the reverse, which
would have had Perfect Timing eat the fresh Bomb 4 for 4 and leave me nothing
growing. Predicted 47 → 35 with a Bomb 4 down. **Actual 35/63.** Took 13 into
10 Block → predicted HP 26. **Actual 26/62.**

**Turn 3.** Bomb had grown 4 → 8. No set-off in hand and Spark at 0, so the
right play was to *stack*: Jumpy Dumpty put a second Bomb 8 down, Defend, and
a weakened Kaboom! (5). Enemy 35 → 30, HP 26 → 19.

**Turn 4.** `Bomb 24 (buff) — Set off here deals 24 Pyro damage. Bombs here: 2.`
Two 12s. Enemy at 30, wearing `Pyro Aura 1`.

Predicted, and this is the run's best single line: Diona applies Cryo **twice**
— the first application consumes the standing Pyro aura for a null reaction, the
second paints Cryo — so Ka-pow!'s set-off sends bomb one into a Cryo aura for
12 × 1.75 = 21 and bomb two into a bare enemy for 12, total 33 ≥ 30.
**Actual: the fight ended on that Ka-pow!.** The "twice" on Diona's card is
doing real work: it is what makes her usable on an enemy already wearing my own
Pyro.

**Fight 5 result: won turn 4, HP 19/62.**

Of the 5 Status cards, exactly one reached my hand: `Dazed — cost 0, status.
Unplayable. Ethereal.` It cost me nothing, because Ethereal exhausts it at end
of turn and I had spare cards anyway.

One thing I could not verify: **Pendulum (`Every 3 turns, draw 1 card`) did not
fire on this fight's round 3.** Hand was 5, and the piles reconcile at 1 draw +
5 hand + 16 discard = 22 with no spare draw. In fight 2 and fight 4 round 3 the
hand was 6. Either the counter is global across the run rather than per-combat,
or something else moved it. The relic prints `Pendulum (1)` and the number never
visibly changed on any screen I saw.

Reward: `10 Gold` + a card, from `Witches' Circle` / `Fish-Flavored Bait` /
`Quick Fuse` (`cost 1 Spark, skill: Each Bomb on the enemy grows by 3. Set off.`)
/ `Shinobu — Grass Ring of Sanctification` (`cost 0, skill: Gain 4 Block. If you
lost HP this turn, gain 4 additional Block.`). Took **Shinobu**: at 19/62 my
failure mode is HP, and a 0-cost Block card is the only kind that never competes
with the Energy my damage needs.

---

## Fight 6 — Gremlin Merc (48 HP), floor 7

```
- **Gremlin Merc** — HP 48/48   Intent: 7x2
    Surprise 1 (buff) — Something is off about this creature...
    Thievery 20 (buff) — Steals 20 Gold when Attacking.
```

`Surprise 1 — Something is off about this creature...` is the one badge in the
run that deliberately tells you nothing. It is not a wording defect; it is a
withheld mechanic, and it mattered (see below).

**Turn 1.** At 19 HP against 14 incoming I still took the damage line, because
Diona-into-Kaboom! is 12 damage for two Energy rather than 7. Predicted Melt
7 × 1.75 = 12. **Actual 48 → 36.** Block 11, took 3, HP 16.

**Turn 2 — the best arithmetic surprise of the run.** I predicted 22: Jumpy
Dumpty's Bomb 8, Tinder Toss setting it off (8) plus its two 4s, plus Strike 6.
**Actual 36 → 11, i.e. 25.** The extra 3 is that Tinder Toss hits *twice*, and
Jumpy Dumpty's rider places a Mine when the Bomb goes off — so Tinder Toss's
**second** set-off detonated the Mine that its **first** set-off had just
created. 8 + 4 + 3 + 4 = 19, plus Strike's 6 = 25. Nothing on either card says
they combo; it falls straight out of "Set off ... twice" meeting "When it goes
off, place a Mine 3 on ALL enemies." Spark confirms it: 2 − 1 price + 1 Bomb
+ 1 Mine = 3.

**Turn 3.** Enemy at 11. Pop! (Bomb 5) + Perfect Timing (set off 5, then 6
under Weak) = exactly 11. It "died" — and **split**:

```
- **Sneaky Gremlin** — HP 13/13   Intent: Stunned
- **Fat Gremlin** — HP 13/13      Intent: Stunned
    Heist 18 (buff) — When killed, returns all the stolen Gold.
```

That is what `Surprise` was. Both arrived Stunned, so the split cost me no
damage, but it did cost 18 gold that the Merc had stolen while attacking, and
`Heist 18` says the only way to get it back is to kill the carrier. Both were
free-hit targets that turn: Strike into Fat (13 → 9), Tinder Toss into Sneaky
(13 → 7).

**Turn 4.** Fat Gremlin's intent flipped to `Cowardly (Escape)` — a hard timer
on the 18 gold. Predicted a clean double kill: Perfect Timing 6 + Strike 4 = 10
into Fat's 9, then with Fat gone Tinder Toss's "random enemy" becomes
deterministic again, so Ka-pow! 3 + Tinder Toss 3 + 3 = 9 into Sneaky's 7.
**Actual: both dead, 0 damage taken, and the reward screen printed
`18 Gold (stolen back)`.**

**Fight 6 result: won turn 4, HP 13/62.** Gold recovered in full: 17 + 18 = 35.

Reward card taken: **Kaeya — Glacial Waltz** (`cost 1, skill: For 3 turns, at the
end of your turn deal 6 Cryo damage to a random enemy. Exhaust.`) over a second
Bang Bang!, Quick Fuse and Sizzle. Reason: Diona was my *only* Cryo card in 18,
and Cryo is what turns a Bomb into a 1.75× Bomb. Sizzle (6, +6 on a reaction)
is a strictly worse Perfect Timing (8, replayed on a reaction).

---

## Rest site (floor 8), Treasure (floor 9), Rest site (floor 10)

Rest site: `Rest — Heal for 30% of your Max HP (18)` vs `Smith — Upgrade a card
in your Deck`. At 13/62 this was not a decision. **13 → 31.**
Treasure: `Candelabra — At the start of your 2nd turn, gain [Energy][Energy].`
Free, no cost printed, taken.
Second rest site at 31/62: rested again, **31 → 49**. I passed up two Smith
upgrades and never once saw what an upgraded card looks like — worth noting that
a run can reach the act-1 boss without the upgrade system ever appearing.

---

## Elite — Skulking Colony (75 HP), floor 12

```
- **Skulking Colony** — HP 75/75   Intent: 14
    Hardened Shell 20 (buff) — Skulking Colony cannot lose more than 20 HP each turn.
```

**This is the most interesting fight in the run, because it inverts the whole
character.** Klee's engine is burst: grow a Bomb, paint an aura, set it off for
1.75×. A hard cap of 20 HP lost per turn makes every point of burst past 20
worthless. The correct play flips to: *deal exactly 20, and convert every other
card into Block.* Nothing on the screen says that; the number says it.

**Turn 1.** Pop! (Bomb 5) → Diona (Cryo, 6 Block) → Tinder Toss (Melt 8 + 4 + 4)
→ Strike → Strike. Raw ≈ 28. **Actual 75 → 55: exactly 20.** The badge then read
`Hardened Shell 0` — it is a live remaining-budget counter, not a static label,
which is genuinely useful. Block 11, took 3, HP 46.

**Turn 2.** `Energy 5/3` — Candelabra paid out. Predicted the Jumpy-Dumpty /
Tinder-Toss chain at 19 (Bomb 8, then 4, then the Mine that the first set-off
created for 3, then 4) — deliberately *just under* the cap so nothing was
wasted — and spent the other 4 Energy on 15 Block. **Actual 55 → 36. Exactly
19. Took 0 of the 14.**

**Turn 3.** Bang Bang! (8, places Bomb 4) then Perfect Timing (sets that Bomb
off for 4, then 8) = **exactly 20**, the cap hit on the nose, with 2 Energy left
for 10 Block. **Actual 36 → 16. Took 0 of the 9.**

**Turn 4.** Enemy 16, wearing `Pyro Aura 1`. Diona's two Cryo applications strip
the Pyro and repaint Cryo, so Ka-pow! Melts: predicted 4 × 1.75 = 7.
**Actual 16 → 9, and `Hardened Shell 13` — i.e. 20 − 7 remaining.** Then Kaeya
(`Glacial Waltz 3 — At the end of your turn, deal 6 Cryo damage to a random
enemy. Lasts for 3 turns.`) ticked for 6 at end of turn: 9 → 3. Block 15 against
9×2 = 18 (`Strength 2`), took 3, HP 43.

**Turn 5.** Tinder Toss into the Cryo aura Kaeya had left: dead.

**Elite result: won turn 5, HP 43/62 — six HP lost to a 75-HP elite.** The cap
made the fight *safer*, not harder, because surplus damage became Block.

Spark evidence for the undisclosed income, cleanest instance: on turn 4 Spark
went **2 → 4** with no Bomb going off at all — one Diona (whose first Cryo
reacted off the Pyro aura) and one Ka-pow! Melt. Two reactions, two Sparks.

Reward: `39 Gold` + `Distilled Chaos` + `Lucky Fysh` + a card. Took **Barbara —
Let the Show Begin♪** (`cost 1, skill: Gain 6 Block. Apply Hydro.`) over
Catalytic Converter, Quick Fuse and Fish-Flavored Bait: she is a straight
upgrade on a Defend (6 vs 5) and, per the glossary, Hydro plus Cryo on a boss
"is consumed and applies 2 Vulnerable instead" — which is the boss I am walking
toward.

---

## Rest site (floor 13) and Fight 7 — three Corpse Slugs (26 + 27 + 25), floor 14

Rested 43 → 61. I chose Rest over Smith both times a rest site offered the
choice, because the map guaranteed another rest site immediately before the
boss and 18 HP beats one upgraded card at 43/62. **Consequence: I never saw the
Smith screen, and this record contains nothing about upgrades.**

Three slugs, 78 HP total, every one carrying `Ravenous 4`.

**Turn 1.** Jumpy Dumpty's Bomb 8 onto slug 3, Diona's Cryo onto the *same*
slug so the Bomb would Melt next turn, and Kaeya to start an 18-damage clock.
Kaeya's end-of-turn tick hit slug 3 for 6 (25 → 19) and, being Cryo onto Cryo,
refreshed rather than reacted — exactly as the glossary says. Took 8, HP 53.

**Turn 2.** `Energy 5/3` (Candelabra). Bomb 12 under `Cryo Aura 1`. Predicted
Perfect Timing's set-off to Melt for 12 × 1.75 = 21 into 19 HP. **It killed slug
3** — and then both survivors printed:

```
Intent: Stunned (Stun)   Strength 4 (buff)
Bomb 3 (buff) — ... Bombs here: 1, including 1 Mine.
```

**But Perfect Timing's own 8 damage, and its replay, were entirely wasted.**
Both survivors were still at 26/26 and 27/27. The card's whole rider — "If a
Bomb triggered an Elemental Reaction this turn, play this again" — fired on a
target that the set-off had already killed, and neither the 8 nor the replayed
8 spilled onto a living enemy. That is the sharpest efficiency trap I found:
**Perfect Timing is at its worst exactly when its own combo works best.**

Kaboom! (7) + Strike (6) into slug 1 = 13, then Kaeya's tick. Predicted slug 1
at 7. **Actual 3.** The 4-point gap: Kaboom! had painted Pyro on a bare slug,
so Kaeya's Cryo tick Melted — 6 × 1.75 = 10.5 → 10, not 6. Kaeya and Kaboom!
combo without either card mentioning the other.

**Turn 3.** Both slugs would have hit for 14 + 12 = 26. Instead I killed slug 1
(3 HP) with a Strike, which made slug 2 eat it — **Stunned again**, so I took
**0**. The Ravenous chain is a genuine two-way mechanic: every kill buys a free
turn at the price of +4 Strength on whatever is left. Slug 2 ended at
`Strength 8` and, again, absorbed the corpse's Mine: `Bomb 22, Bombs here: 2`.
I also spent an idle Energy on Barbara's Hydro so Kaeya's last Cryo tick would
Frozen it.

**Turn 4.** Ka-pow! set off `Bomb 22` into 15 HP. Over.

**Fight 7 result: won turn 4, HP 53/62 — 8 damage, all of it on turn 1.**

Reward `12 Gold` + a card, from a second Perfect Timing / `Chain Fuse` (`Each
Bomb on the enemy grows by 6`) / `Pocket Fireworks` (9 damage for 1) / `Razor —
Lightning Fang`. Took the second **Perfect Timing**.

---

## Fight 8 — Calcified Cultist (41) + Damp Cultist (52), floor 15

Both opened on `Empower (Buff)` — no attack, so Block was worthless and turn 1
was a free setup turn. Jumpy Dumpty's Bomb 8 and Diona's Cryo both onto the
Calcified Cultist, then Perfect Timing.

Predicted 33 on Calcified: Bomb 8 Melts (8 x 1.75 = 14), then 8, then — because
a Bomb triggered a reaction — the replay's set-off catches the Mine for 3 and
deals another 8. **Actual 41 -> 8. Exactly 33.** This is Perfect Timing working
as designed, and the contrast with fight 7 is the whole point: the same card
wasted 16 damage there because the set-off killed the target first.

Then both cultists revealed `Ritual 2` and `Ritual 5` — +2 and +5 Strength at
the end of every one of their turns. The Damp Cultist's printed attack was `1`
on turn 1 and `6` on turn 2; left alone it would have been 11, 16, 21. That is a
clean, readable timer and it correctly forced me to kill fast rather than block.

Turn 2: Perfect Timing finished Calcified (8), then — deliberately — **Tinder
Toss before Bang Bang!**, so Tinder Toss's set-offs found nothing and Bang
Bang!'s Bomb 4 survived to grow. Damp 41 -> 25 with a Bomb 8 building, Ka-pow!
retained. Blocked its 6 for 0.

Turn 3: Ka-pow! set off Bomb 8 (12 total), Kaboom! 7, Strike 6 = lethal on 25.

**Fight 8 result: won turn 3, HP 53/62 — zero damage taken.**

Reward `10 Gold` + `Fysh Oil` + a card; took **Thoma — Blazing Barrier**
(`Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block.`).

---

## Rest site (floor 16) — the Smith, at last

At 53/62 a Rest heals 18 but caps at 62, so it was worth only 9. **Smith was
worth more, and this is the first screen where Rest vs Smith was a real
decision rather than an obvious one.**

The Smith screen lists all 22 cards **with their current text and no preview of
what the upgrade would do.** I picked blind. I upgraded **Jumpy Dumpty**,
reasoning that bomb size is the quantity my 1.75x Melt multiplies, so a point
added there is worth more than a point added anywhere else.

I only learned the result mid-boss: **`Jumpy Dumpty+` places a Bomb 18, against
the base card's Bomb 8.** That is a very large upgrade and nothing on the Smith
screen hinted at it.

Deck at the boss (22): Strike x3, Defend x4, Duck and Cover, Jumpy Dumpty+,
Ka-pow!, Kaboom!, Tinder Toss x2, Pop!, Bang Bang!, Perfect Timing x2, Diona,
Kaeya, Barbara, Shinobu, Thoma.

---

## BOSS — Waterfall Giant (240 HP), floor 17

```
- **Waterfall Giant** — HP 240/240   Intent: Empower (Buff)
```

and, from turn 1 onward:

```
Steam Eruption 15 (buff) — When killed, deals 15 damage at the end of your next turn.
```

**That number grew every single turn: 15 -> 18 -> 21 -> 24 -> 27.** It is a timer
on my own victory — the longer the fight runs, the bigger the bill I pay for
winning it. It is the best-designed thing in the fight, and I played the last
three turns around it.

**Turn 1** (boss buffing, no attack, Block worthless). Barbara's Hydro, then
Diona's Cryo. The glossary had told me what to expect: *"Bosses cannot be
Frozen: Hydro plus Cryo is consumed and applies 2 Vulnerable instead."* It did:
`Vulnerable 1` on the badge after one tick, and Diona's **second** Cryo
application then repainted a `Cryo Aura`. Strike landed for 9 = 6 x 1.5.
240 -> 231.

**Turn 2.** `Energy 5/3` (Candelabra). Vulnerable Potion took Vulnerable from
1 to **4** — it added rather than replaced, buying three more multiplied turns
for one action. Then a mistake worth recording: I played **Bang Bang! before
the bombs**, and Bang Bang! is a *Pyro attack*, so it ate the Cryo aura itself —
`231 -> 210`, i.e. 8 x 1.75 (Melt) x 1.5 (Vulnerable) = 21. Good damage, but it
spent the Melt on an 8-damage card instead of on a bomb. Jumpy Dumpty+ then
showed its size: `Bomb 22 ... Bombs here: 2` on top of Bang Bang!'s Bomb 4.

The Bomb badge also changed wording under Vulnerable: `Set off here deals 22
Pyro damage **after Vulnerable**` — the badge quotes the number I will actually
see, not the raw one. Perfect Timing + Tinder Toss took 210 -> 158.

**Turn 3.** `Weak 1` on me. Bombs are exempt, so this was a build turn: Pop!
placed a bomb, Kaboom! chipped, Thoma blocked. 158 -> 151.

**Turn 4.** Boss intent was `Heal` — no attack at all, so a pure damage turn.
Perfect Timing set off the bomb, Tinder Toss, Ka-pow!, and Kaeya's tick.
**151 -> 103**, out-pacing whatever it healed.

**Turn 5.** Vulnerable's last turn. Diona repainted Cryo; Distilled Chaos
(`Play the top 3 cards of your Draw Pile`) then did **nothing I could see** —
the boss stayed at 103, my Block did not move, and three cards left the draw
pile without arriving in the discard. Perfect Timing Melted into the fresh Cryo,
Tinder Toss followed. **103 -> 37, and I took 0.**

**Turn 6 — the kill.** Boss at 37, bare, no Vulnerable left, and Steam Eruption
already at 27. Waiting was strictly worse, so I went all in: Fysh Oil (`Gain 1
Strength and 1 Dexterity`), Barbara's Hydro, Kaboom! Vaporizing off it, Tinder
Toss, Ka-pow!. **37 -> 10.** Then Thoma for Block and end turn, so that Kaeya's
last `Glacial Waltz` tick — 6 Cryo into the Pyro aura my own attacks had left —
would Melt for 6 x 1.75 = 10.5 -> 10, exactly lethal. **It was.**

**Turn 7** printed something no other screen did:

```
- **Waterfall Giant** — HP 999999999/999999999
    Intent: Death Blow (DeathBlow) — the number on its icon is 27 —
    This creature is trying to take you down with it. It will attack you for 27 damage before being destroyed.
```

The boss was dead; the corpse stood on a sentinel HP value of 999999999 to
collect its 27. I had no Block card in hand and ended the turn into it at 42 HP.

**BOSS DEFEATED.** Reward: `100 Gold` + `Skill Potion` + a card, from
`Sparks 'n' Splash` / `Alice's Introduction Magic` / `Sugar Rush` /
`Clorinde — Impale the Night`. Took **Sparks 'n' Splash** (`cost 2, power: At
the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on
it`) — it turns the bomb-growth engine into repeating damage *without consuming
the bombs*, which is the one thing this deck could not previously do.

The lane now stands on the **act-2 map**, first node `Ancient (path 1)`.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Four, and they were genuinely different from each other.

1. **Holding Ka-pow! on fight 1 turn 1.** `Retain. Set off. Deal 4 damage` at
   cost 0, against `Bomb 8 ... grows 4 a turn`. Holding one turn converted a
   12-damage line into a 16-damage line for free. The trade is tempo against
   bomb size, and the numbers are printed clearly enough to compute it.
2. **Kill-order sequencing to make "random" deterministic.** Tinder Toss reads
   "a random enemy twice". On fight 2 I killed Corpse Slug 2 *first* so that
   Tinder Toss had only one legal target. Same again on fight 6 turn 4. That is
   a real, non-obvious play the text supports without stating.
3. **The Hardened Shell inversion.** `cannot lose more than 20 HP each turn`
   made every point of burst past 20 worthless, so the correct play flipped from
   "build the biggest bomb" to "deal exactly 20 and turn the rest into Block".
   I hit 20, 19, 20 on three consecutive turns and lost 6 HP to a 75-HP elite.
4. **Ravenous.** `When an enemy dies, Corpse Slug immediately eats it, becoming
   Stunned and gaining 4 Strength` makes killing a thing you *choose*. A kill
   buys a whole free turn and costs +4 Strength forever. On fight 7 turn 3 I
   killed a 3-HP slug specifically to buy a stun, and took 0 instead of 26.

### (b) What felt automatic, and what never seemed worth playing

**Strike and Defend were automatic and mostly filler.** `Deal 6 damage` for 1
Energy is the worst attack rate in the deck by the fourth floor — Kaboom! is
7, Perfect Timing is 8 with a set-off attached, and Tinder Toss and Bang Bang!
cost no Energy at all. I paid 75 gold to delete one and would have deleted more.

**Duck and Cover is a Defend.** `Duck and Cover — cost 1, skill: Gain 5 Block.`
against `Defend — cost 1, skill: Gain 5 Block.` I never once had a reason to
prefer one, and I never found any text distinguishing them.

**Snecko Skull did nothing all run.** `Whenever you apply Poison, apply an
additional 1 Poison` — I was never offered a single card that applies Poison.
It was one of my two Neow relics and it was inert for 17 floors.

The genuinely automatic *good* play was blocking nothing when the intent showed
no attack — which happened on five separate screens (`Defensive`, `Empower`,
`Heal`, `StatusCard`, `Stunned`) and always paid.

### (c) What I could not understand, or that contradicted its own text

1. **Spark income is not explained by anything printed.** The glossary says
   `Start each combat with 1. Pounding Surprise grants more.` Diona grants one
   too — fight 3 turn 1 (1 -> 2), fight 5 turn 1 (1 -> 2), boss turn 5 (3 -> 4),
   every time, and her card mentions only Block and Cryo. And on Elite turn 4
   Spark went **2 -> 4 with no Bomb going off at all**. I could not reconcile
   that with any printed rule.
2. **Corpses transfer their Bombs.** `Ravenous 4` says the eater becomes Stunned
   and gains 4 Strength. It says nothing about inheriting the corpse's Mines,
   but it happened twice: `Bombs here: 1` -> `Bombs here: 2` (fight 2), and
   `Bomb 22 ... Bombs here: 2` (fight 7).
3. **`Surprise 1 — Something is off about this creature...`** is a badge that
   refuses to say what it does. It meant the Gremlin Merc splits into two
   13-HP gremlins on death. Deliberate, but it is the one thing in the run I
   could not have priced.
4. **Distilled Chaos did nothing observable.** Three cards left my draw pile,
   the boss's HP did not move, my Block did not move, and the three cards did
   not appear in the discard count.
5. **`Pendulum (1) — Every 3 turns, draw 1 card`** fired on round 3 of fights
   2, 4 and 8 but *not* on round 3 of fight 5, where the piles reconcile to
   exactly 5 drawn. The `(1)` beside its name never changed on any screen.

### (d) The card I never wanted, and the one I was happiest to draw

**Never wanted: Strike.** Six damage for the same Energy that buys eight and a
set-off. It is the card I paid to remove and the card I most often let discard
unplayed.

**Happiest to draw: Diona — Shaken, Not Purred.** She is the only card that
does three jobs at once: 6 Block (11 when a Bomb goes off), and *two* Cryo
applications, which is precisely what lets her work on an enemy already wearing
my own Pyro — the first application burns the Pyro off, the second paints Cryo.
Every one of my four biggest turns began with her.

### (e) Did the first turn of the first fight already present a decision

**Yes, and a good one.** The opening hand held `Jumpy Dumpty` (Bomb 8),
`Ka-pow!` (Retain, Set off, 0 cost) and three vanilla cards, against a Seapunk
telegraphing 11. Ka-pow!'s Retain plus the Bomb's "grows 4 a turn" makes turn 1
a genuine question: cash the Bomb now for 12, or hold a free card one turn and
cash it for 16. I worked both lines out before acting. That is a real decision
on turn one of floor one, which is more than most opening hands offer.

### (f) Anything a screen granted or changed without saying so

- **The two Neow relics were never named.** `Large Capsule — Obtain 2 random
  Relics` resolved silently; I first learned they were Snecko Skull and Pendulum
  from the relic list *inside the first fight*.
- **99 starting gold.** Four reward screens had printed 13 + 11 + 17 + 18 = 59.
  The shop, on floor 5, opened with `You have 158 gold.`
- **Diona grants Spark** (see (c)).
- **Corpses hand over their Bombs** (see (c)).
- **Vulnerable Potion added to the existing stack** rather than replacing it —
  `Vulnerable 1` became `Vulnerable 4` from a potion that reads `Apply 3
  Vulnerable`. In my favour, but not stated.
- **`Jumpy Dumpty+` places a Bomb 18**, up from 8. The Smith screen showed only
  the un-upgraded text, so the size of what I was buying was hidden at the
  moment of buying it.

---

## Findings, ranked by sharpness

**1. Perfect Timing is at its worst exactly when its own combo works.**
Fight 7 turn 2: the set-off Melted for 21 and killed Corpse Slug 3, and then
both the card's own 8 damage *and* the replay its "If a Bomb triggered an
Elemental Reaction this turn, play this again" rider granted were thrown away —
the two surviving slugs were still on 26/26 and 27/27. Compare fight 8 turn 1,
where the identical card against a target that survived the set-off delivered
the full 33 (41 -> 8). Same card, same combo, 16 damage of difference decided by
whether the set-off overkilled. The card pays out least when it triggers best.

**2. Spark income is undocumented, and one turn of it is unexplained.**
Printed rule: `Start each combat with 1. Pounding Surprise grants more.`
Observed: Diona grants +1 on play in every instance (fight 3 turn 1, 1 -> 2;
fight 5 turn 1, 1 -> 2; boss turn 5, 3 -> 4) with no mention on her card. And on
Elite turn 4 Spark went **2 -> 4 across a turn in which no Bomb went off** —
Diona plus a Ka-pow! Melt. I could not derive a rule that fits both that turn
and fight 7 turn 2, where a Bomb went off *and* Melted and Spark rose by only 1.

**3. Hardened Shell inverts the character, and the game never says so.**
`cannot lose more than 20 HP each turn` on a 75-HP elite. My raw turn-1 output
was about 28 and delivered exactly 20 (75 -> 55). Every point of Klee's whole
design — bomb growth, 1.75x Melt, the replay riders — is dead weight against
it, and the correct play becomes "deal exactly 20, bank the rest as Block." I
hit 20 / 19 / 20 on three straight turns and finished the elite having lost
**6 HP**. The mechanic is good; it is also the single largest strategy change in
the run and it is communicated only by a number.

**4. Steam Eruption grows while you fight it, which prices the whole boss.**
`When killed, deals 15 damage at the end of your next turn` read 15, 18, 21, 24,
27 on successive turns. Killing the Waterfall Giant on turn 6 cost me 27 HP;
killing it two turns later would have cost 33 and I would have had less HP to
pay it with. It converts "grind it down safely" into a losing plan, and it is
why I went all-in at 37 HP rather than blocking another turn.

**5. Two Bomb interactions fall out of the text that no card mentions.**
(i) Tinder Toss's *second* set-off detonates the Mine that its *first* set-off
created via Jumpy Dumpty — fight 6 turn 2 predicted 22 and delivered **25**
(8 + 4 + 3 + 4, plus Strike's 6), with Spark confirming it at 2 - 1 + 1 + 1 = 3.
(ii) Kaeya's end-of-turn Cryo Melts off a Pyro aura that Kaboom! left earlier
the same turn — fight 7 turn 2 predicted 7 HP remaining and delivered **3**,
because 6 became 6 x 1.75 = 10. Both are good. Both are invisible until you see
them happen.

**6. The per-card `Reaction preview` line is the best thing on any screen.**
From Elite turn 3 onward every elemental card carried its own verdict:
`*Reaction preview: Melt* — This card deals no damage. Pyro plus Cryo is still
consumed, and there is no hit here for the 1.75x to multiply.` on Diona, versus
`... The triggering hit deals 1.75x damage and consumes the aura.` on Kaboom!.
It answers the exact question the aura system makes you ask, per card, at the
moment you ask it. The same quality shows in cards re-rendering their real
numbers under Weak and Frail (Strike printing `Deal 4 damage`, Defend printing
`Gain 3 Block`) and in `Hardened Shell 20` counting down to `Hardened Shell 13`
as I spent the budget.

**7. Gold, HP and relics are invisible on the screens where they matter.**
The map — the one screen you route from — prints no HP, no gold, no relics, no
potions. Gold appeared for the first time on floor 5 and only because I entered
a shop, where it read 158 against the 59 I had counted. And after the boss died,
**no screen printed HP again**, so this record cannot state the HP the lane is
standing on: the last reading was 42/62 immediately before a 27-damage Death
Blow.

**8. The Smith screen sells an upgrade without showing it.**
It listed all 22 cards in their *current* wording. I upgraded Jumpy Dumpty on
reasoning alone and only discovered mid-boss that `Jumpy Dumpty+` places a
**Bomb 18** rather than a Bomb 8 — a 125% increase, and the largest single power
gain of the run, chosen blind.

**9. Duck and Cover and Defend are the same card.**
`Duck and Cover — cost 1, skill: Gain 5 Block.` / `Defend — cost 1, skill: Gain
5 Block.` Identical cost, type and text on every screen that printed them,
including the full deck list at the shop and the Smith. I never found a reason
to prefer either.

**10. Snecko Skull was dead for the entire act.**
`Whenever you apply Poison, apply an additional 1 Poison.` Across 8 fights, 1
elite, 1 boss, 2 shops and 9 card-reward screens, **not one card that applies
Poison was ever offered to me.** Half of the Neow relic payout did nothing.

**11. Where I could not tell.**
I cannot say whether Distilled Chaos malfunctioned or merely played three
skills whose effects I could not see — I did not have the actions to test it.
I cannot explain the Pendulum inconsistency. I cannot say whether the boss's
`999999999` HP sentinel is intentional presentation or a leaked internal value.
And I never saw an Electro or a Hydro *enemy* aura, so Overloaded,
Superconduct, Electro-Charged and Frozen were glossary entries I never used —
only Melt (many times), Vaporize (once) and the boss's Hydro+Cryo->Vulnerable
substitution ever fired.

---

## Non-blindness declaration

- Commands run: **only** `GITS_LANE=2 python -m understudy.blindplay observe`
  and `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, from the
  repo root. No other `understudy` subcommand was run at any point.
- Tools used: **Bash** (to run the two allowed commands, piped through
  `sed`/`grep`/`head` purely to trim output, and heredocs to append to this
  record) and **Write** (to create this record file, and to stage two sections
  of it in the session scratchpad after a heredoc failed to parse). Nothing else.
- Repo files read: **none.** No source, no YAML, no docs, no rulings, no
  backlog, no earlier records, no logs. No `git` command was run.
- I never launched, closed, restarted or tore down the game, and never touched
  lane 1.
- Everything in this record comes from screens printed by `observe` and `act`.
- **The lane was left standing** on the act-2 map screen, with `Ancient (path
  1)` as the only available node, immediately after the act-1 boss reward screen
  was fully handled (gold, potion and card all taken). Nothing was played on
  that screen.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
