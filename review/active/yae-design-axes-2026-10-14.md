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
| **Defect** | **Free:** Lightning from the starter (Zap) | Earned: Frost orbs, drafted | Focus, Dark | Earned: Plasma and cost cuts |
| **Regent** | Earned: Sovereign Blade grows into one big hit | Earned (95) | Forge, Stars | Free: Stars, a second resource |
| **Necrobinder** | Earned: Osty attacks, Doom executes | Osty takes hits | Doom, Osty's growth | Weak: draw is the fewest of the five (4) |
| **Klee** | **Free and fast:** Bombs grow on their own | Weak by ruling ("fast and fragile") | Bomb growth, Sparks | Sparks spend as a currency |
| **Varka** | **Free:** two-handed hits; the second hit pays the current element | Earned: Frost Ward, Hydro Swirl | Oath counts per element | Retain on Ascension |
| **Kokomi** | Weak: the act-2 boss is her wall (r6, 5 of 8) | **Free:** Plans, Casket, Wards | Plan stacking, Nereid | Plans move cards across turns |
| **Furina** | Earned: guests act every turn | Weak (her run died to it) | Fanfare | **Free:** HP is a resource (Drain buys tempo) |
| **Yae, today** | Free but tiny: about 4 a turn from the shrine | Weak | Levels (capped), Publish | Weak: no Energy, little draw |

What the table says:
- **Every other kit has at least one strong free axis.** Klee, Varka and
  Defect are free on damage, Kokomi on Block, Silent and Furina on
  velocity. Defect's other solves are drafted orbs, so that is the shape
  Yae should copy without copying the orbs.
- **Yae is free on nothing that matters in act 1.** Her free damage is too
  small to end fights, so she pays for it twice: in HP while fights drag, and
  in turns spent planting instead of blocking. That is the six act-1 deaths.
- **She has two scaling axes no one else has.** A board that levels itself
  as she tends it, and a deck that improves across the run.

## 3. What the Sakura do (revised)

[USER], on the first draft of this section: "Defect has 5 types of orbs
(Lighting - the free starter that does single target damage; Frost for
defense; Glass for AoE; Dark for scaling; Plasma for energy). Currently, the
Sakura is only offering the equivalent of Lightning, which I actually
consider to be a problem ... Defect also start with just a damage source
(lightning) and has to draft the rest ... we're going for 'Defect-like, but
not literally defect' with this one; the Sakura need to also offer solves for
other issues in some way even if they look like a simple damage source on the
surface."

The first draft made Block her permanent weakness. That was the wrong
lesson, and section 2's Defect row was wrong too: Defect starts with only
Lightning and drafts his Frost. The row now reads "Earned".

### The proposal: Rites

**The shrine does one job at a time, and Yae chooses which.**
- The shrine has a **Rite**. Every combat starts in **Thunder**.
- A card that says "Rite: Warding" switches it. A Rite holds until another
  replaces it.
- Every strike, at the end of turn or from a Tenko, works under the current
  Rite.
- A Sakura's Level sets the size of its strike in every Rite.

| Rite | Each strike | Solves | Defect's nearest |
|---|---|---|---|
| **Thunder** (start) | 2 + Level Electro damage to a random enemy | damage | Lightning |
| **Warding** | Yae gains 2 + Level Block | Block | Frost |
| **Wildfire** | Level Electro damage to ALL enemies | groups | Glass |
| **Offering** | Next turn, draw 1 more card | velocity | Plasma |

**Scaling** is the Levels and Publishing, and it works under every Rite.
Levels play the role Dark plays for Defect.

**Why this is not orb types.**
- Defect owns several orbs at once, each fixed when it is channelled. Yae's
  board is one object that does one thing at a time.
- Her question each turn is "what does my shrine do this turn?"
- Tenko becomes "do it now": under Warding it is a Block spike, under
  Wildfire a sweep.
- Switching rides on ordinary cards (a Block card that says "Rite:
  Warding"), so it costs a card's slot but not an extra card.
- One Rare bends the rule (Sakura Channeling, below) and lets the shrine do
  two jobs.

**How the three halves feed the shrine.**
- **Tenko** fires it now.
- **Kitsune Mischief** cards carry the cheap Rite switches and aim it
  (Foxfire Lure).
- **Publishing** plants through Sakura Seal. Pick 1 (b) is the other
  answer, where an Annotation written on a Sakura changes what that one
  Sakura does.

### Profile

| Axis | Free (starter) | Drafted | Feel |
|---|---|---|---|
| Damage | Thunder, small early | Levels, Tenko, Attacks | a board that grows |
| Block | Defend | **Warding**, card floors | the shrine guards her, but then it is not killing |
| Groups | none | **Wildfire**, Tenko Kenshin | sweep a hallway |
| Velocity | none | **Offering**, Footnote, Retain, Energy when a Sakura withers | a slower hand that is all good cards |
| Scaling | Levels | Grove, Mooncall, Mikage Thunder, Publish | worse than everyone on floor 1, better on floor 40 |

Her weakness is that the shrine does one job a turn, and switching costs
tempo. A turn that needs both Block and damage asks the hand to cover one of
them.

## 4. Realigning the 30 (numbers pass included)

The starter is not touched: Yakan Evocation and Proofread. The game always
opens in Thunder, so there is no free setup.

**Cards that carry a Rite:**
- **Shrine Maiden's Guard** (C): "Gain 6 [9] Block. Rite: Warding." The
  per-Sakura Block it printed is now the Rite's job.
- **Thunder Rite** (C): "Deal 8 [11] Electro damage. Rite: Thunder.
  Tenko." This is the way back to damage.
- **Kitsune Guile** (U): "Apply 2 [3] Weak to ALL enemies. Rite: Wildfire."
- **Manuscript Pile** (U): "Draw 2 [3] cards. Rite: Offering." Its Retain
  Edit goes, since Deadline carries that.
- **Sakura Channeling** (R, 2 [1]), the bend: "Your Sakura also strike as
  Thunder, whatever the Rite."

**Block floor.** Each card gets a Defend-rate base, and its condition
becomes the bonus.
- **Print Run:** 6 [8] + 2 [3] per Annotated card (was 4 + 2).
- **Deadline:** 5 [8] (was 4 [6]).
- **Rooted Shrine:** "Gain 6 [9] Block. Each Sakura gains a Level." (was 3
  Block)

**The shrine:**
- Yakan Evocation and Twin Sakura read "Plant a Sakura (with 3 standing,
  each gains a Level instead)."
- **Twin Sakura** goes from 2 [1] to **1**, and its upgrade adds "Gain 4
  Block."
- **Sakura Grove:** each strike is 2 [3] bigger, in Thunder, Warding and
  Wildfire (was +1 [2]).
- **Edict of Cleansing:** "Your Sakura strikes deal 3 [5] more to an enemy
  that is Weak or has a Pyro, Hydro or Cryo aura." It works solo now.
- **Foxfire Lure:** 0 Energy (was 1).

**Damage:**
- **Sly Strike:** 7 [9] (was 5 [7]).
- **Thunderbolt Tithe:** 3 [4] plus 4 [6] per Sakura (was 4 [6] per
  Sakura).

Unchanged: Kitsune Flash, Shrine Offering, Fox Fire Draft, Fox Trick, Kitsune
Rite, Bestseller, Footnote, Sakura Seal, Serialization, and every Rare not
named above.

## 5. Batch two, Yae's own

These eight start her pool's road to 78. They fill the gaps from section 1:
Attacks, Energy, Common plant sources, and Tenko cards that scale ([USER],
2026-10-13: "we'll probably want multiple Tenko effects, and building scaling
into them makes a lot of sense"). Each was checked against base cards. Three
earlier drafts were dropped as near-copies of Ironclad's Thunderclap and
Defect's Coolheaded and Fission.

| Card | Rarity, type, cost | Text |
|---|---|---|
| Shrine Bell | C, Attack 1 | Deal 7 [10] Electro damage. Each Sakura lasts 1 more turn. |
| Grafted Branch | C, Skill 1 | Plant a Sakura. It starts at Level 2 [3]. |
| Margin Note | C, Attack 1 | Deal 5 [8] Electro damage. Edit a card in your hand: Red Ink. |
| Kitsune Pounce | C, Attack 1 | Deal 8 [11] Electro damage. If the enemy is Weak, a Sakura strikes it. |
| Foxfire Sweep | C, Attack 1 | Deal 4 [6] Electro damage to ALL enemies. Rite: Wildfire. |
| Fallen Petals | U, Power 1 | Whenever a Sakura withers, gain 1 Energy. [Also draw 1 card.] |
| Mikage Thunder | U, Attack 2 | Tenko. For the rest of this combat, your Sakura strike for 1 more. |
| Royalties | R, Skill 1 [0] | Edit a card in your hand: Royalties (when played, gain 1 Energy). Exhaust. |

The pool would be 38 (14 / 16 / 8). Rites are a rule change, so you play her
before the next batch.

## Picks

1. **How the Sakura solve more than damage.**
   - **(a) Default: Rites.** The whole shrine does one job at a time, and
     cards switch it (section 3).
   - (b) Per Sakura, through Publishing: Edit can target a Sakura, and each
     Annotation has a shrine reading (Red Ink: bigger; Fox Fire: hits ALL;
     Deadline Extension: does not wither). A defence reading would need a
     new Annotation. This is a third number on every Sakura.
   - (c) Tenko only: each Tenko card fires the shrine once as Block, a
     sweep, or draw. The shrine itself stays Thunder.
2. **The Rite list.**
   - **(a) Default:** four Rites: Thunder, Warding, Wildfire and Offering.
   - (b) Add a fifth, Mischief: each strike applies 1 Weak and deals Level
     damage.
3. **Energy when a Sakura withers** (Fallen Petals).
   - **(a) Default:** yes, in batch two.
   - (b) No.
4. **Batch two (section 5).**
   - **(a) Default:** all eight.
   - (b) The ones you name.
5. **Order.**
   - **(a) Default:** Claude builds sections 4 and 5 after your picks, while
     no lanes are running, then you play her.
   - (b) Two seats first, then you play.

## Ruled 2026-10-14

[USER]: "1) I like the idea of splitting the Shrine from the Sakura. I'm
thinking that this basically lets the Sakura have two effects - one from the
Shrine, affected by Tenko, and a second added as a sort of in-place
enchantment from some publishing style cards. If no enchantment is added,
then it just does what the shrine does. ... 2,3,4) agreed on your defaults
otherwise. 5) I think you'll probably have time to do seat rounds before I
get off of work at this rate. If we have a build we actually like, do the
full 5 - otherwise just 2 as a sanity check for 'does this survive act 1 now
and do the cards work'."

**Pick 1: Rites plus Sakura Annotations.** This combines (a) and (b).

The rule:
- **The shrine's Rite** (Thunder, Warding, Wildfire, Offering, as in
  section 3) sets what every Sakura's strike does. Tenko fires every
  Sakura now, under the current Rite.
- **A Sakura may carry one Annotation.** It is written by cards that say
  "Edit your newest Sakura", "Edit your oldest Sakura" or "Edit every
  Sakura". Each strike then does the Rite's effect and also the
  Annotation's. A new Edit on a Sakura replaces its old Annotation. The
  Annotation lasts as long as the Sakura does, and it is never Published.
- **A Sakura with no Annotation** does only what the shrine does.

**What each Annotation does on a Sakura:**

| Annotation | On a Sakura |
|---|---|
| Red Ink | Its strike is 3 bigger (not in Offering). |
| Fox Fire | When it strikes, it also deals 4 Electro damage to a random enemy. |
| Deadline Extension | It does not wither. |

Footnote, Sakura Seal and Royalties have no Sakura reading in this batch.
A card that edits a Sakura cannot give them.

**The cards that write on Sakura:**
- **Fox Fire Draft** (C, Skill 0, Exhaust) changes from "Edit a card in your
  hand: Fox Fire" to **"Edit your newest Sakura: Fox Fire."** Upgraded:
  "Edit every Sakura: Fox Fire."
- **Inked Branches** (new, U, Skill 1 [0]): "Edit every Sakura: Red Ink."
- **Evergreen Charm** (new, C, Skill 1): "Gain 5 [8] Block. Edit your
  oldest Sakura: Deadline Extension."

Picks 2 to 4 are (a): four Rites; Energy when a Sakura withers (Fallen
Petals); batch two's eight cards. With the two cards above, the pool is
40 (15 / 16 / 9).

Claude, 2026-10-14: Red Ink skips Offering, like Sakura Grove; +3 cards a
strike was too much draw. The tally reads 15 / 16 / 9, as built.

**Pick 5:** Claude builds it now. If the build plays well, five Yae seats
run before [USER] is home; if not, two seats as a sanity check ("does this
survive act 1 now and do the cards work").

## Claude, 2026-10-14 (review r1, no pick)

Four changes, built in both engines:
1. **A "Rite: X" card says what the shrine would do under X**, in combat,
   summed over the Sakura standing: "Rite: Thunder (your Sakura: 12
   damage)", "Rite: Warding (your Sakura: 5 Block)", "Rite: Wildfire (your
   Sakura: 6 to ALL)", "Rite: Offering (your Sakura: draw 3)". A sum, not
   per Sakura, because the Levels differ. Nothing is printed outside combat
   or with no Sakura standing. The Rite badge and the seat page add "Your
   Sakura now: 5 Block." for the current Rite. The sum is the Rite's own job:
   Edict, Sakura Channeling's extra Thunder strike and Fox Fire are not in it.
2. **Every Tenko card prints "Tenko (no Sakura)" while none stands**:
   Kitsune Rite, Thunder Rite, Mikage Thunder and Tenko Kenshin. None is
   gated: Kitsune Rite was first made unplayable with no Sakura, then the
   gate was dropped once it drew a card, so it still draws.
3. **Sakura Seal costs 0** (was 1 [0]). Its upgrade was the cost cut, so it
   takes Footnote's: "Edit 2 cards in your hand: Sakura Seal."
4. **Kitsune Rite: "Tenko. Draw 1 card."**, 1 [0], Exhaust, as before;
   with no Sakura it reads "Tenko (no Sakura). Draw 1 card."
