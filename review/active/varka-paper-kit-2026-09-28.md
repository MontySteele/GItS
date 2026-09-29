# Varka: the Four Winds (paper kit)

**Ask ([USER], 2026-09-28):** paper kits for Nahida, Zhongli and Varka that
assume the element changes. [USER] ranks Varka at the top with Yae. His kit
facts come from a research packet built from secondary sources (Fandom and
official pages were not reachable): the Skill "Windbound Execution" puts him
in **Stormward Charge**, where his attacks take an ally's element, and
**Four Winds' Ascension** deals Anemo plus that element together. His passives
reward Swirl.

**Stage:** Paper. A concept, not yet a brief. Card numbers are placeholders
for the sim.

## 1. The promise

The Grand Master fights with every wind in Mondstadt. Varka takes the elements
others leave on the field and makes them his own.

## 2. His element: Anemo, with the new Swirl

Anemo leaves no aura. Under the element review
(`review/ruled/element-home-review-2026-09-28.md`), an Anemo hit on a fresh
aura **Swirls** it:
- the aura spreads to every enemy that lacks it;
- the enemy that was hit keeps it;
- every enemy takes a flat 2;
- the aura is spent for triggers.

`LAW.md` §Economy already imagines him: "a hypothetical swirl-fisher", an
archetype where fishing for companions may be the dominant plan.

**Element changes he needs:** the shared rule and change A, both ruled. One
new hook, the Absorb in §3. The engine already has a Swirl event that
remembers its element (`tier0/constants.py`, the Mondstadt workshop's hooks).
The spread reacting where it lands is **not** needed. It stays the separate,
later candidate.

## 3. The signature: the Four Winds

- **Absorb:** some of Varka's own cards say **Absorb**. An Absorb Swirl works
  like any Swirl, except that it **takes the aura off the enemy it hit**
  instead of leaving it spent there. The copies it spread to the others still
  arrive spent. This is a card effect, not a change to the shared rule, and it
  is canon: an Anemo absorption removes the element it took. The first time
  each fight he absorbs Pyro, Hydro, Electro or Cryo, he gains that element's
  **Wind** for the rest of the fight. Each Wind is small, flat and of its own
  kind (placeholders):
  - **Pyro Wind:** your Attacks deal +2.
  - **Hydro Wind:** gain 2 Block whenever you Swirl.
  - **Electro Wind:** your first Swirl each turn draws a card.
  - **Cryo Wind:** each Swirl applies 1 Weak to the enemy it hit.
- **Four Winds' Ascension** (his signature Attack): 6 damage, plus 6 per Wind
  you hold. Exhaust.

**The tension is now or later.** Ascension with two Winds today, or another
turn to catch a third? That is Klee's "detonate or wait" shape, fed by variety
instead of stockpiling. Which aura to Swirl first matters too, because each
Wind comes once.

**Why Absorb takes the aura (GPT's audit).** If the aura only went spent, the
next Knight would react with it: Hydro on a spent Pyro Vaporizes both away,
and he needs another application before he can absorb Hydro. Taking the aura
leaves the enemy clean for the next colour.

**A worked solo sequence against a boss,** with the starter plus one drafted
Knight (Barbara) and one Windbound Execution:
1. **Turn 1:** Knights' Muster, choosing Amber, paints Pyro. A Strike, the
   turn's first Attack on a fresh aura, Absorbs through the relic: Pyro Wind.
   The boss is clean.
2. **Turn 2:** Barbara paints Hydro. Windbound Execution Absorbs it: Hydro
   Wind. Then Ascension now for 18, or hold it for a third Wind at 24.

With the bare starter the same loop runs through Muster alone: paint and
Strike on the turns Muster is drawn, one Wind per shuffle. That is the
intended weakness. The first round has to read whether it feels deliberate or
starved.

**Against a pack it is a targeting puzzle.** The spread copies land spent on
the other enemies, so a new Knight aimed at one of them reacts instead of
painting. You aim the next colour at the enemy you absorbed from, the one left
clean.

**In co-op the choice is sharper.** His partner's auras are his Winds, but an
Absorb takes them away. A plain Swirl leaves Klee's Pyro for her Vaporize and
gets no Wind; an Absorb gets the Wind and costs her the aura. Deciding between
them is the co-op decision, and it is Genshin's Stormward Charge with a price.

## 4. His first colour: the Knights of Favonius

Varka *is* reaction-centred, so he needs a dependable second element (the
element review, §1). Mondstadt's Knights supply it, which is lore-true: the
Grand Master commands them.
- **Personal-pool companions** (`LAW.md`: they "are the character's kit, and
  may carry"): Amber (Pyro), Barbara (Hydro), Lisa (Electro), Kaeya (Cryo).
  Each is a Varka-only card that paints its element.
- **In the starter: Knights' Muster**, a companion card. Choose a Knight: deal
  4 of their element.

The draft then decides how fast he reaches four Winds. His deck wants
**variety**, which no current kit wants: Klee, Kokomi and Furina all paint one
colour.

## 5. The three archetypes

1. **Four Winds (default, the simple path).** One element at a time: paint,
   Absorb, collect, finish with Ascension. Signposts: cheap Knights, and a
   Common that Swirls **every** enemy carrying a fresh aura (one aura cannot be
   Swirled twice).
2. **Gale (the ceiling: payoff for handling complexity).** Many Swirls instead
   of many Winds, and multi-element boards. This is where the element review's
   later candidate lives, **as a card and not a shared rule**: *Converging
   Winds (Rare, Power): your Swirls react where they land.* Rarity makes it
   earned but does not bound it, so it carries its own rules:
   - The spread hit is the flat 2, carrying the swirled element.
   - A reaction it sets off lands on **that enemy only**, so Overload does not
     splash. The three-Overload case becomes 6 on each Electro-marked enemy,
     not 18 on every enemy.
   - A reaction set off by a spread never Swirls again. It also
   reuses the Mondstadt companion **Sturm und Drang** (a Swirl makes your next
   Attack deal +6 of the swirled element). This follows [USER]'s framing:
   make Swirl useful on its own, and make multi-reaction Swirls "an archetype
   or payoff for handling complexity vs a simpler 'just do one-element swirls'
   main path".
3. **Grand Master (provisional).** Command the Knights: companions cost 0 this
   turn, replay the last companion. GPT's audit is right that discounts and
   replays so far support both plans rather than making a third. It stays
   provisional until it shows a turn the other two would not play.

**Bridges:** every Knight feeds both Winds and Gale. A Grand Master replay
turns one Knight into two colours.

**Flavour for the relic and potion pass:** Dandelion Wine (a potion), and
**The Untitled Question** (a Rare that sets three tasks for the fight: Varka's
witch's homework, from his Hexerei quest).

## 6. Starter (sketch)

Strike ×4, Defend ×4, and two of his own:
- **Knights' Muster** (1, companion): choose a Knight; deal 4 of their
  element.
- **Four Winds' Ascension** (2): the payoff, in the starter so it is reached
  from fight one. Exhaust, so the "now or wait" decision is one per fight.

**Starting relic: Boreas's Fang.** Each turn, your first Attack that hits a
fresh aura Absorbs. An Attack on an enemy with no fresh aura does not use it
up. So the bare starter can collect a Wind every turn it paints one, which
makes the Absorb verb repeatable from fight one (GPT's second audit: a
once-per-fight relic capped the bare starter at one Wind). Windbound Execution
(deal 6 Anemo, Absorb) is a Common in the pool, for a second Absorb in a turn.

The first draft discounted Ascension with its relic but left Ascension out of
the starter (GPT's audit). Now the payoff is in the deck, and the relic teaches
the verb that feeds it.

## 7. Intended weakness and failure modes

- **Weakness:** a slow start. Turn one has no Winds, and a draw without a
  Knight is a Strike deck.
- **Failure mode, companions carry:** the delete-test in `LAW.md` deletes his
  personal Knights along with his other cards, because they are his kit (GPT's
  correction). The real check is universal companions: if Sturm und Drang
  and other Mondstadt universals win without any Varka card, that is
  `SUPPORT_CARRY`.
- **Failure mode, the same fight every time:** collect four, fire, every fight.
  Winds reset each fight, Ascension exhausts, and which Knight you draw varies
  the order. The first round should read whether the order felt chosen.
- **Failure mode, the Gale wall:** the flat 2 to every enemy on every Swirl
  against packs. The once-per-aura rule bounds it to one Swirl per fresh aura.

## 8. What it costs to build

Medium, mostly in cards. The element review's change A, one Absorb hook (a
Swirl that removes its source aura), the Wind powers, four personal-pool
Knights, and Converging Winds as a card-scoped switch. He is the character that tests
the new Swirl hardest.

## 9. Revision two (2026-09-29): Swirl distributes, Absorb collects

**Ask ([USER], 2026-09-29):** "I think you're good to do a round of revision
and polish on this in parallel to the Furina pass and see how the sims look,
and then we can prototype that if it seems promising." He wants to playtest
"to see if the Absorb mechanic is fun or repetitive in its current design."

**What the sim found** (draft #753, n = 400 per cell):
- Boreas's Fang makes Absorb compulsory, so the plain-Swirl choice (§3 co-op,
  the Gale deck) does not exist: even Gale Absorbs 6.1 of its 7.0 Swirls.
- An Absorb still spreads spent copies. In packs, 64-74% of the Knight hits
  after an Absorb react with those copies instead of painting. Aiming does not
  fix it.
- Pyro Wind ("Attacks deal +2", on from about turn 1.5) is worth 179 of 400
  boss wins. The pilot always took Pyro first, so this shows Pyro is strong,
  not that choosing a Wind is interesting (GPT's review).
- Against bosses waiting to fire Ascension wins on average at every count;
  against packs the choice never comes up.

**GPT's two reviews, adopted:** keep the structure; make Absorb optional;
show a Wind choice that depends on the encounter, the hand, the enemy's intent
or the partner's plan; show recognisable turns where waiting to fire
Ascension is wrong; and add no machinery before the problem is understood.

### 9.1 The two verbs

- **Swirl** is the shared rule, unchanged: an Anemo hit on a fresh aura leaves
  it spent on that enemy, spreads spent copies to every enemy lacking it (a
  copy replaces whatever aura that enemy wore), and deals a flat 2 to every
  enemy.
- **Absorb** is Varka's own verb, and it is **not a Swirl**. An Absorb on an
  enemy with a fresh aura takes that aura off the enemy and gives you its
  element's **Wind** if you do not hold it. It spreads nothing and deals no
  flat 2. The card's own damage still lands. An Absorb on an enemy with no
  fresh aura, or with an element whose Wind you hold, does only the card's
  damage.
- **The choice per aura:** Absorb it (a new Wind, that enemy clean for your
  next colour, and nobody else's aura touched), or Swirl it (2 to every enemy
  and your Winds' effects, but spent copies over every other enemy's aura).
  Absorb sets up; Swirl pays off.

What Absorb does *not* clean: auras already on the board from earlier Swirls,
companions or a partner stay where they are. §9.4's sequence starts from that
board.

### 9.2 Winds: every Wind pays on a Swirl

A Wind is collected by Absorbing and used by Swirling, so after the first few
Absorbs the deck turns to Swirling. All four trigger on the same event, so
none is on from turn 1 while the others wait (placeholders):
- **Pyro Wind:** whenever you Swirl, deal 3 damage to the enemy you hit.
- **Hydro Wind:** whenever you Swirl, gain 3 Block.
- **Electro Wind:** your first Swirl each turn draws a card.
- **Cryo Wind:** whenever you Swirl, the enemy you hit gains 1 Weak.

The order is meant to follow the fight: Pyro against a race or a pack, Hydro
against a heavy single hitter, Cryo against multi-hit attacks. Which Wind is
*available* this turn follows the fresh auras on the board: the Knights in
hand, and the partner's paint.

### 9.3 Boreas's Fang, optional

**Boreas's Fang (starting relic):** "Once each turn, when an Attack hits an
enemy with a fresh aura, you may Absorb it." The player chooses; the seat page
and the mod offer it as a choice on that hit. Base Strike is not Anemo, so a
Strike on a fresh aura either Absorbs through the Fang or lands as a plain
hit.

### 9.4 Worked sequence: three enemies, a board already in use

Board: enemy A wears **fresh Pyro** (the partner's), B wears **spent Hydro**
(a copy from last turn's Swirl), C is clean. Varka holds Hydro Wind. Hand:
Lisa (Electro, Skill), Windbound Execution (6 Anemo, Absorb), Tempest Charge
(8 Anemo, draw 1 if it Swirls), Strike. 3 Energy.

- **Line 1, take and pay off:** Windbound on A Absorbs Pyro: Pyro Wind, and A
  is clean. Lisa paints fresh Electro on C. Tempest Charge on C Swirls it: 8,
  2 to every enemy, Pyro Wind's 3 on C, Hydro Wind's 3 Block, a card. A and B
  take spent Electro copies. The most this turn, and the partner loses her
  Pyro.
- **Line 2, leave the partner's Pyro:** Lisa paints fresh Electro on C.
  Windbound on C Absorbs it: Electro Wind, C clean. Strike on B. No Swirl, so
  no spread: A's Pyro is still there for the partner's reaction. Less damage
  now, a third Wind, and the partner's turn intact.
- **Line 3, the trap:** Tempest Charge on A first, a plain Swirl of Pyro.
  Spent Pyro lands on B and C. Lisa on C now Overloads the spent Pyro instead
  of painting, and nothing fresh is left to Absorb or Swirl this turn.

What a player should read from the page: Absorb first, Swirl last, and never
Swirl while your next colour still has to land. The sim checks how often line
1 or line 2 is right, and whether line 3 is avoidable in play.

### 9.5 Ascension: two versions to test

- **A (kept):** Deal 6, plus 6 per Wind you hold. Exhaust. Early firing is
  right only on a kill or a lethal intent it prevents. The sim counts those
  turns.
- **B (candidate; GPT's second review calls it legitimate if waiting still
  dominates):** Four Winds' Ascension (2): Deal 6, plus 8 per Wind you hold.
  **You lose those Winds.** No Exhaust. A lost Wind can be Absorbed again.
  Firing at two Winds twice is meant to compete with firing once at four,
  against giving up the Swirl effects in between. The risk is that rebuilding
  every fight turns repetitive.

B replaces A only if A leaves waiting dominant and B makes the choice depend on
the fight.

### 9.6 Loose ends settled

- **Knights are Skills.** The Fang reads Attacks, so a Knight never Absorbs its
  own paint.
- **Gale Sweep** Swirls every enemy that had a fresh aura **when it was
  played**, in enemy order; a spread from an earlier Swirl in the sweep does
  not cancel a later one.
- **Grand Master's Order** repeats the next Knight card; Knights' Muster
  counts, and the repeat may choose a different Knight.
- **Barbara** (Apply Hydro to ALL) stays. On a board of spent copies it is the
  deliberate reaction card, not the painter; the painters are the
  single-target Knights.
- **Converging Winds:** the struck enemy's own flat 2 carries no element.

### 9.7 What the sim must show before a prototype

1. Absorb against Swirl: how often a sensible pilot takes each, and whether
   "Swirl only" or "Absorb whenever possible" is dominated.
2. Wind choice: single-Wind runs (one Wind held from turn 1) per encounter.
   It passes if the best Wind differs by encounter and by enemy intent.
3. Ascension A against B, firing thresholds 1-4, paired by seed: any
   encounter where early firing wins more than a quarter of pairs.
4. The Knight hits that react instead of painting, re-measured (target: well
   under 64-74%).
5. §9.4's three lines as scenarios, with their outcomes.
6. Turns to kill and boss wins beside Klee, Kokomi and Furina, as before.
   Pilot-dependent; they rank nothing.

### 9.8 What the sim showed (revisions 2, 2.1, 2.2; draft #753)

n = 400 per cell; placeholder numbers and a heuristic pilot, so nothing here
ranks the kit.
- **The spread fix works.** Knight hits that react instead of painting after
  an Absorb fell from 64-74% to 1-10%.
- **Absorb or Swirl depends on the fight.** Swirl-only is the fastest plan
  against packs and loses bosses (40% on tank_boss, against 89% for the smart
  pilot); the smart pilot Absorbs about 8% of the time in big packs, half the
  time on tank_boss, three quarters on punisher.
- **The best Wind depends on the fight:** Hydro in every pack, Cryo on every
  boss (it beats the runner-up in 63-97% of paired fights). Pyro has no niche
  and Electro is last everywhere, at one card or two: Electro needs a
  different effect, not a bigger number.
- **Revision two's own fault:** with Winds paying only on a Swirl, the bare
  starter never Swirled (0.0-0.4 a fight) and its Winds were dead. Revision
  2.1 made the Fang the fork (Absorb or Swirl) and an Absorb on a held Wind a
  Swirl; built decks went from 51% to 89% on tank_boss.
- **The starter sits on a knife edge.** A free Knights' Muster takes punisher
  from 5% to 99.5% (Ironclad's starter: 54%). The battery cannot place the
  starter; play has to.
- **Spent copies react in full**, so Swirl-then-Knight is the biggest damage
  line (§9.4 line 3: 43, against 28 and 17). The three lines are three plans:
  damage now, Winds, or the partner's aura. Line 3 is not a trap.
- **Ascension:** waiting still wins where a boss fight is in doubt. Version B
  (spend the Winds) only tied A and added rebuilding, so it is dropped.
  Ascension is a finisher; the first playtest judges whether that is enough.

## 10. Prototype, batch one (2026-09-29)

**Ask ([USER], 2026-09-29):** "You're good to go on building the Varka
prototype!" Numbers are first-guess placeholders for play. A number in
brackets is the upgrade.

### 10.1 The rules as built

- **Swirl** (shared rule): an Anemo hit on a fresh aura leaves it spent on
  that enemy, spreads spent copies to every enemy lacking it (a copy replaces
  what that enemy wore), deals a flat 2 to every enemy. Spent copies react
  with a new element as normal.
- **Absorb** (his cards' keyword): on a fresh aura, takes the aura off that
  enemy and gives you its Wind. No spread, no flat 2. If you already hold that
  Wind, the hit **Swirls** instead. With no fresh aura, only the card's
  damage.
- **Winds**, for the rest of the fight, each paid on every Swirl you make:
  - **Pyro Wind:** deal 3 damage to the enemy you Swirled.
  - **Hydro Wind:** gain 3 Block.
  - **Cryo Wind:** the enemy you Swirled gains 1 Weak.
  - **Electro Wind:** your first Swirl each turn gives 1 Energy. (Untested;
    the sim's draw versions were last everywhere.)
- **Boreas's Fang** (starting relic), as built: "Once each turn, the first
  non-Anemo Attack that hits a fresh aura Absorbs it." It reads Absorb's rule,
  so on a held Wind it Swirls. The choice lives in which card you aim at an
  aura: a Strike collects, an Anemo Attack Swirls. This drops §9.3's in-hit
  prompt for the prototype; a prompt comes back only if play asks for it.
- **Knights** are Varka's personal-pool companions, all Skills.

### 10.2 The starter (Varka, 80 HP, 99 gold)

Strike ×4, Defend ×4 (base game), and:
- **Knights' Muster** (Skill, 1): Choose a Knight: deal 4 [6] of their element.
- **Four Winds' Ascension** (Attack, 2): Deal 6 [9] Anemo, plus 6 for each Wind
  you hold. Exhaust.

### 10.3 The pool, batch one (19 cards)

Common (10):
- **Windbound Execution** (Attack, 1): Deal 6 [9] Anemo. Absorb.
- **Squall** (Attack, 1): Deal 4 [5] Anemo twice.
- **Updraft** (Attack, 1): Deal 8 [11] Anemo.
- **Gale Sweep** (Attack, 1): Deal 3 [5] Anemo to every enemy that has a fresh
  aura. (Snapshot when played; each Swirls.)
- **Wind Wall** (Skill, 1): Gain 7 [10] Block. If you hold a Wind, gain 3 more.
- **Favonius Drill** (Skill, 1): Gain 6 [9] Block. Choose a Knight: apply
  their element to an enemy.
- **Amber: Baron Bunny** (Knight, Skill, 1): Deal 6 [9] Pyro.
- **Barbara: Let the Show Begin** (Knight, Skill, 1): Apply Hydro to ALL
  enemies. Gain 3 [5] Block.
- **Lisa: Violet Arc** (Knight, Skill, 1): Deal 5 [7] Electro. Draw 1.
- **Kaeya: Frostgnaw** (Knight, Skill, 1): Deal 6 [9] Cryo.

Uncommon (7):
- **Tempest Charge** (Attack, 1): Deal 8 [11] Anemo. If it Swirls, draw 1.
- **Favonius Cut** (Attack, 2): Deal 14 [19] Anemo. Absorb.
- **Grand Master's Order** (Skill, 0): The next Knight you play this turn is
  played twice. Exhaust. [Retain.]
- **Knights' Roll Call** (Skill, 1): Add a random Knight to your hand. It costs
  0 this turn. [Choose the Knight.]
- **Eye of the Storm** (Skill, 1): Gain 4 [5] Block for each Wind you hold.
- **Stormward Stance** (Power, 1 [0]): While you hold 2 or more Winds, your
  Anemo Attacks deal 3 more.
- **Tailwind Stride** (Skill, 1): Draw 2. If you hold a Wind, draw 1 more.
  [Cost 0.]

Rare (2):
- **Converging Winds** (Power, 2 [1]): Your Swirls react where they land
  (§5's rules: the spread hit is the flat 2 carrying the swirled element; a
  reaction it sets off lands on that enemy only; a reaction from a spread
  never Swirls again; the struck enemy's own flat 2 carries no element).
- **Boreas Unbound** (Power, 2 [1]): Whenever you Absorb, gain 1 Energy.

The Mondstadt universal **Sturm und Drang** is already on the surface and
supports Gale. Grand Master stays provisional (§5). Pool target 78 comes later.

### 10.4 What the first seat round asks

One question: **is choosing between Absorb and Swirl a decision on the turn,
or a chore?** Two seats, a one-page record. [USER]'s playtest follows.

## Picks

1. **Winds.** (1) *Four different flat effects, one per element* [default].
   (2) One generic stack per distinct element (simpler, less flavour).
2. **His first colour.** (1) *Knights' Muster in the starter* [default].
   (2) An optional run-start offer of one Knight (`LAW.md`'s R160 route).
   (3) No starter source; the Knights come through the draft.
3. **Grand Master.** (1) *Provisional third archetype, until it shows a
   distinct turn* [default]. (2) Drop it now; a third archetype comes from his
   Hexerei homework instead.
