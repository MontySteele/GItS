# Yae: what she gets free, and what a run asks of her

[USER], 2026-10-14: "In terms of damage / block / scaling / velocity, which
are her strengths and weaknesses? What is she inherently good at, and where
is she expected to struggle? ... Let's compare her against the base 5 as well
as our 4 in each category ... Not every archetype needs to be the full
package, but they should read a little differently to produce different
gameplay feels. Then, once we've identified what her scaling axes should be,
think of how to manifest that through her card pool, realigning what the
prototype built as needed, then do the numbers pass."

Sources:
- **Her cards:** the 32 `character: yae` rows of
  `docs/prototype-surface.yaml`.
- **Base counts:** `game_ref/<character>.json`, over the 80 Common, Uncommon
  and Rare cards, with multiplayer cards left out.
- **Seat evidence:** `review/records/yae-sanity-2026-10-14.md`, six runs,
  all lost in act 1.

## 1. How she works today

**Damage.**
- **The shrine:** each Sakura deals 2 + its Level at the end of her turn,
  into a random enemy, so 3 to 5 each and 15 a turn at most.
- **Tenko** fires the shrine early and resets its timers.
- **Only 6 of her 30 cards are Attacks (20%).** The base five run 30 to 42%
  (Silent 24, Defect 28, Regent 29, Necrobinder 32, Ironclad 34 of 80).
- **The shrine rarely matures.** In the sim it averaged 1.7 Sakura standing
  by turn 5, and the seats saw hits of 3 to 5.

**Block.**
- **Her own Block cards** are Defend plus 5 cards that print 21 Block between
  them: Shrine Offering 6, Deadline 4, Shrine Maiden's Guard 4, Print Run 4
  and Rooted Shrine 3.
- **Two Powers give Block per event:** Serialization (per Edit) and Sakura
  Channeling (per strike).
- **The base five, by comparison,** run 11 or 12 Block cards each: Silent 61
  printed, Necrobinder 75, Defect 80, Regent 95, Ironclad 106. Scaled to
  80 cards, Yae's would be about 13 cards at roughly 4 each: as many Block
  cards as the base five, but smaller.
- **Weak** is her other defence: 5 cards (Sly Strike, Fox Trick, Kitsune
  Guile, Foxfire Lure, Mischievous Teasing).

**Scaling.**
- **Within a fight:** Sakura Levels (by planting), Sakura Grove (+1 a
  strike) and Fox's Mooncall (Level 4).
- **Within a hand:** Red Ink (+3 on one card) and Bestseller (+3 per
  Annotated card).
- **Across the run:** Publishing, which keeps one Edit for good at a rest
  site. No other character in the game has this.

**Velocity.**
- **Energy:** no card gives any.
- **Draw:** three cards (Fox Trick 1, Manuscript Pile 2, Mischievous Teasing
  2), plus the Footnote Annotation.
- **Retain:** Deadline Extension. The base five have 2 to 4 Energy cards and
  4 to 10 draw cards each.

**What the seats felt.** Too little Block early, Sakura hits that are small
and slow, and two cards that silently do nothing on a full shrine.

## 2. The ten characters, axis by axis

"Free" means the kit hands it to you from the starter or the core rule.
"Earned" means a run has to draft for it. "Weak" means a run cannot rely on
it.

| | Damage | Block | Scaling | Velocity |
|---|---|---|---|---|
| **Ironclad** | Free: big Attacks, Strength | Earned: highest printed Block (106), Exhaust engines | Strength, Exhaust payoffs | Weak: pays HP for Energy |
| **Silent** | Earned: Shivs (many small hits) or Poison (ticks, ignores Block) | Weak printed (61), so Dexterity and Weak carry it | Poison stacks, Accuracy | **Free:** draw and discard, Sly |
| **Defect** | Earned: Lightning orbs, Claw | **Free: Frost orbs Block every turn** | Focus | Earned: Energy from Plasma and cost cuts |
| **Regent** | Earned: Sovereign Blade grows into one big hit | Earned (95) | Forge, Stars | Free: Stars, a second resource |
| **Necrobinder** | Earned: Osty attacks, Doom executes | Osty takes hits | Doom, Osty's growth | Weak: draw is the fewest of the five (4) |
| **Klee** | **Free and fast:** Bombs grow on their own | Weak by ruling ("fast and fragile") | Bomb growth, Sparks | Sparks spend as a currency |
| **Varka** | **Free:** two-handed hits; the second hit pays the current element | Earned: Frost Ward, Hydro Swirl | Oath counts per element | Retain on Ascension |
| **Kokomi** | Weak: the act-2 boss is her wall (r6, 5 of 8) | **Free:** Plans, Casket, Wards | Plan stacking, Nereid | Plans move cards across turns |
| **Furina** | Earned: guests act every turn | Weak (her run died to it) | Fanfare | **Free:** HP is a resource (Drain buys tempo) |
| **Yae, today** | Free but tiny: about 4 a turn from the shrine | Weak | Levels (capped), Publish | Weak: no Energy, little draw |

What the table says:
- **Every other kit has at least one strong free axis.** Klee and Varka are
  free on damage, Kokomi and Defect on Block, Silent and Furina on velocity.
- **Yae is free on nothing that matters in act 1.** Her free damage is too
  small to end fights, so she pays for it twice: in HP while fights drag, and
  in turns spent planting instead of blocking. That is the six act-1 deaths.
- **She has two scaling axes no one else has.** A board that levels itself
  as she tends it, and a deck that improves across the run.

## 3. Proposed profile

| | Role | Feel |
|---|---|---|
| **Scaling (strength)** | **Two axes, both free to start:** the shrine within a fight, Publishing across the run | She plays worse than everyone at floor 1 and better at floor 40 |
| **Damage (strength, late)** | Passive and spread across enemies, then one Tenko spike | You set up the board and ration its cash-ins; you seldom aim a big Attack |
| **Velocity (her own kind)** | **Hand quality, not hand size:** Retain, 0-cost Edits, Footnote, and Energy from Sakura that wither | An editor with a short deadline, not a flood of cards |
| **Block (the challenge)** | A floor at a Defend's rate, then Weak as mitigation; real Block from the shrine only late (Sakura Channeling) | Survive the setup turns by blunting attacks, not by out-blocking them |

How she reads differently from the rest:
- **Against Defect** (the itch she scratches): Defect's board is free Block
  from turn one; hers is free damage that grows. Her defence is Weak and
  timing, not Frost.
- **Against Klee:** Klee ends fights early and is fragile. Yae ends them
  late and is fragile early. The two are opposite curves.
- **Against Kokomi:** Kokomi's defence is free and her damage is the run's
  problem. Yae is the reverse.
- **Against Furina:** both have a weak Block pool. Furina buys tempo with HP;
  Yae buys it with time (the shrine's Levels and Retain).

The one new mechanic here is **Energy from withering.** Today a Sakura that
withers is a pure loss, which is why Tenko's refresh is the only play.
Paying a little when a Sakura withers creates a real choice each turn:
refresh the elders for damage, or let them lapse for Energy and replant.
Tenko keeps the board; withering spends it.

## 4. Realigning the 30 (numbers pass included)

The starter is not touched: Yakan Evocation and Proofread.

**Block floor.** Each card gets a Defend-rate base, and its condition
becomes the bonus.
- **Shrine Maiden's Guard:** 4 + 2 per Sakura becomes **6 [8] + 2 [3] per
  Sakura**.
- **Print Run:** 4 + 2 per Annotated card becomes **6 [8] + 2 [3] per
  Annotated card**.
- **Deadline:** 4 [6] becomes **5 [8]**.
- **Rooted Shrine:** "Each Sakura gains a Level. Gain 3 Block." becomes
  **"Gain 6 [9] Block. Each Sakura gains a Level."**

**Planting into a full shrine says what it does.** Yakan Evocation and Twin
Sakura read "Plant a Sakura (with 3 standing, each gains a Level instead)."
**Twin Sakura** goes from cost 2 [1] to **1, and its upgrade adds "Gain 4
Block."** One plant a card at 2 Energy is why the shrine starved.

**Damage numbers:**
- **Sly Strike:** 5 [7] with 1 [2] Weak becomes **7 [9]**, Weak unchanged.
- **Thunderbolt Tithe:** "4 [6] per Sakura" becomes **"3 [4], plus 4 [6]
  per Sakura"**, so it is not blank on an empty shrine.
- **Sakura Grove:** +1 [2] a strike becomes **+2 [3]**. At the shrine's
  average of 1.7 Sakura, +1 was worth under 2 a turn.

**Weak joins the shrine.** Edict of Cleansing is blank solo. It becomes
**"Your Sakura strikes deal 3 [5] more to an enemy that is Weak or has a
Pyro, Hydro or Cryo aura."** That is one card bridging Mischief to the
shrine, and it keeps the reaction nod for co-op.

**Two smaller changes:**
- **Foxfire Lure** goes from 1 to **0** Energy. Aiming the shrine is a rider,
  and a 1-Energy rider is never played.
- **Sakura Channeling:** 2 [3] Block a strike becomes **3 [4]**, about 9 a
  turn on a full shrine for 2 Energy. This is her late defence.

Unchanged: Kitsune Flash, Thunder Rite, Shrine Offering, Fox Fire Draft, Fox
Trick, Kitsune Rite, Bestseller, Footnote, Sakura Seal, Serialization,
Manuscript Pile, Kitsune Guile, and every Rare not named above.

## 5. Batch two, Yae's own

These eight start her pool's road to 78. They fill the gaps from section 1:
Attacks, Energy, Common plant sources, and Tenko cards that scale (you asked
for that on 2026-10-13: "we'll probably want multiple Tenko effects, and
building scaling into them makes a lot of sense"). Each was checked against base cards. Three first drafts were dropped as
near-copies: an AoE plus Weak Attack (Ironclad's Thunderclap), plant plus
draw (Defect's Coolheaded), and "every Sakura strikes then withers, gain
Energy" (Defect's Fission). Names are first drafts.

| Card | Rarity, type, cost | Text |
|---|---|---|
| Shrine Bell | C, Attack 1 | Deal 7 [10] Electro damage. Each Sakura lasts 1 more turn. |
| Grafted Branch | C, Skill 1 | Plant a Sakura. It starts at Level 2 [3]. |
| Margin Note | C, Attack 1 | Deal 5 [8] Electro damage. Edit a card in your hand: Red Ink. |
| Kitsune Pounce | C, Attack 1 | Deal 8 [11] Electro damage. If the enemy is Weak, a Sakura strikes it. |
| Fallen Petals | U, Power 1 | Whenever a Sakura withers, gain 1 Energy. [Also draw 1 card.] |
| Last Petal | U, Skill 1 [0] | Your oldest Sakura strikes 3 times, then withers. |
| Mikage Thunder | U, Attack 2 | Tenko. For the rest of this combat, your Sakura strike for 1 more. |
| Royalties | R, Skill 1 [0] | Edit a card in your hand: Royalties (when played, gain 1 Energy). Exhaust. |

How these fit together:
- **Fallen Petals and Last Petal** are the withering half. Last Petal is
  a single-target spike from the oldest Sakura, and Petals pays for the
  Sakura it spends. Together they are the counterweight to Tenko keeping
  the board.
- **Kitsune Pounce** links Weak to the shrine, and **Grafted Branch** gives
  Common a plant that starts high.
- **Mikage Thunder** is the scaling Tenko: each play leaves the shrine one
  stronger, and it repeats.
- **Royalties** is a sixth Annotation, Rare. Published, it makes one card
  refund its Energy for the rest of the run: the run-long scaling axis
  reaching velocity.

That brings the pool to 38 (13 / 17 / 8). The rest of the road to 78 comes
after these are played.

## Picks

1. **Her profile (section 3): strong on scaling (shrine and Publish), damage
   late, velocity as hand quality, Block as the challenge.**
   - **(a) Default:** as written.
   - (b) Defect-like: make the shrine her free defence too (Sakura Channeling
     at Common) and her damage the challenge.
   - (c) A profile you name.
2. **Energy from withering** (Fallen Petals, with Last Petal), a second
   cash-in beside Tenko.
   - **(a) Default:** yes, in batch two.
   - (b) No; Tenko stays the only cash-in.
3. **Batch two (section 5).**
   - **(a) Default:** all eight as written.
   - (b) The ones you name.
4. **Order.** The section 4 changes are numbers and text at Prototype, so
   Claude builds them without a pick once today's lanes are down.
   - **(a) Default:** build section 4 now, batch two after your picks, then
     two Yae seats on the next free night.
   - (b) Hold everything for your own first Yae run.
